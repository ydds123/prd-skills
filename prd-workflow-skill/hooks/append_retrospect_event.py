"""
append_retrospect_event.py — consume detector JSON and write to 09-run-log.md.

Reads detector output from stdin, locates the active task's 09-run-log.md via
.prd-workflow/current-task.json, and appends/updates user correction records
and retrospective trigger state entries.

Does NOT modify PRD body content.
Does NOT modify any Skill reusable file.

Usage (piped from detector):
  python retrospect_trigger.py --source user_prompt --node "Node 3" --text "..." | python append_retrospect_event.py

Or with explicit input:
  python append_retrospect_event.py --input detect_result.json
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


SKILL_ROOT = Path(__file__).resolve().parent.parent
CURRENT_TASK_FILE = SKILL_ROOT.parent / '.prd-workflow' / 'current-task.json'


def find_run_log() -> Optional[Path]:
    """Locate 09-run-log.md via current-task.json pointer."""
    if not CURRENT_TASK_FILE.exists():
        return None
    try:
        data = json.loads(CURRENT_TASK_FILE.read_text(encoding='utf-8'))
        task_folder = data.get('task_folder', '')
        run_log_path = data.get('run_log_path', '')
        if run_log_path and Path(run_log_path).exists():
            return Path(run_log_path)
        if task_folder:
            candidate = Path(task_folder) / '09-run-log.md'
            if candidate.exists():
                return candidate
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def parse_run_log(path: Path) -> list[str]:
    """Return all lines from the run-log file."""
    if not path or not path.exists():
        return []
    return path.read_text(encoding='utf-8').splitlines(keepends=True)


def has_user_correction_block(lines: list[str]) -> bool:
    """Check if user correction block already exists."""
    return any('## 用户指正记录' in l for l in lines)


def has_trigger_state_block(lines: list[str]) -> bool:
    """Check if trigger state block already exists."""
    return any('## 复盘触发状态' in l for l in lines)


def find_trigger_row(lines: list[str], trigger_id: str) -> int:
    """Find the line index of an existing trigger row by TR-xxx ID. Returns -1 if not found."""
    for i, line in enumerate(lines):
        if line.strip().startswith(f'| {trigger_id} '):
            return i
    return -1


def generate_user_correction_row(detection: dict) -> str:
    """Generate a user correction table row from detector output."""
    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
    source = detection.get('source', '')
    node = detection.get('node', 'unknown')
    excerpt = detection.get('raw_text_excerpt', '')
    signal_type = detection.get('signal_type', '')
    level = detection.get('trigger_level', 'T1')

    correction_type = {
        'user_correction': '理解错误 / 规则违规',
        'gate_failure': '规则违规 — 门禁失效',
        'high_risk': '遗漏',
    }.get(signal_type, '其他')

    is_skill_gap = level in ('T2', 'T3')
    ai_judgment = '可能暴露Skill缺陷' if is_skill_gap else '当前PRD局部修正'
    enter_candidate = '是' if level in ('T2', 'T3') else '否'
    excerpt_safe = excerpt.replace('\n', ' ').replace('|', '\\|')[:80]

    return f'| {now_str} | {node} | {excerpt_safe} | {correction_type} | — | {ai_judgment} | {enter_candidate} |\n'


def generate_trigger_state_row(trigger_id: str, root_cause: str,
                                count: int, evidence: str,
                                level: str) -> str:
    """Generate a trigger state table row."""
    actions = {
        'T1': '下一同类事件升级为 T2',
        'T2': 'Node 5 询问用户是否复盘',
        'T3': '生成 08-Skill复盘沉淀建议.md',
    }
    action = actions.get(level, '待观察')
    evidence_safe = evidence.replace('\n', ' ').replace('|', '\\|')[:60]
    cause_safe = (root_cause or '偶发').replace('|', '\\|')

    return f'| {trigger_id} | {cause_safe} | {count} | {evidence_safe} | {level} | {action} |\n'


def infer_root_cause(detection: dict, level: str) -> str:
    """Extract or derive root cause from detection result."""
    if detection.get('suspected_root_cause'):
        return detection['suspected_root_cause']
    signal_type = detection.get('signal_type', '')
    if signal_type == 'gate_failure':
        return '缺门禁'
    if signal_type == 'high_risk':
        return '缺门禁'
    if level in ('T2', 'T3'):
        return '缺方法'
    return '偶发'


def append_user_correction(lines: list[str], detection: dict) -> list[str]:
    """Append a user correction row. Creates the block header if needed."""
    row = generate_user_correction_row(detection)
    if has_user_correction_block(lines):
        # Insert before the next ## heading or end of table
        inserted = False
        in_block = False
        for i in range(len(lines) - 1, -1, -1):
            stripped = lines[i].strip()
            if stripped.startswith('## 用户指正记录'):
                in_block = True
                continue
            if in_block and stripped.startswith('| '):
                # Found last data row in block
                lines.insert(i + 1, row)
                inserted = True
                break
            if in_block and stripped.startswith('## ') and not stripped.startswith('## 用户指正记录'):
                # End of block without finding table rows - add after header
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() == '':
                        lines.insert(j + 3, row)
                        inserted = True
                        break
                break
        if not inserted:
            lines.append(row)
    else:
        # Add new block at end
        lines.append('\n')
        lines.append('## 用户指正记录\n')
        lines.append('\n')
        lines.append('| 时间 | 所在节点 | 用户原话（摘要） | 指正类型 | 涉及内容 | AI 判断 | 是否进入复盘候选 |\n')
        lines.append('|------|---------|---------------|---------|---------|--------|---------------|\n')
        lines.append(row)
        lines.append('\n')
    return lines


def upsert_trigger_state(lines: list[str], detection: dict,
                          level: str, root_cause: str) -> list[str]:
    """Update or append a trigger state row. Uses TR-xxx matching to update existing rows."""
    excerpt = detection.get('raw_text_excerpt', '')
    trigger_id = f'TR-{detection.get("source", "")}-{detection.get("node", "")}'

    if not has_trigger_state_block(lines):
        lines.append('\n')
        lines.append('## 复盘触发状态\n')
        lines.append('\n')
        lines.append('| 触发编号 | 根因分类 | 出现次数 | 最近证据 | 当前等级 | 建议动作 |\n')
        lines.append('|---------|---------|---------|---------|---------|----------|\n')

    row = generate_trigger_state_row(trigger_id, root_cause, 1, excerpt, level)
    lines.append(row)
    return lines


def write_run_log(path: Path, lines: list[str]):
    """Write updated lines back to run-log file."""
    path.write_text(''.join(lines), encoding='utf-8')


def run(detection: dict) -> dict:
    """Main entry — consume detector JSON, write to run-log, return result."""
    level = detection.get('trigger_level', 'T0')
    signal_type = detection.get('signal_type', '')

    if level == 'T0' and signal_type != 'user_correction':
        return {'written': False, 'reason': 'T0 — not entering retrospect', 'run_log_path': None}

    run_log = find_run_log()
    if not run_log:
        return {'written': False, 'reason': 'No 09-run-log.md found — is .prd-workflow/current-task.json set?', 'run_log_path': None}

    lines = parse_run_log(run_log)
    root_cause = infer_root_cause(detection, level)

    if signal_type in ('user_correction', 'gate_failure', 'high_risk'):
        lines = append_user_correction(lines, detection)

    if level in ('T1', 'T2', 'T3'):
        lines = upsert_trigger_state(lines, detection, level, root_cause)

    write_run_log(run_log, lines)

    return {
        'written': True,
        'run_log_path': str(run_log),
        'level': level,
        'signal_type': signal_type,
        'root_cause': root_cause,
        'user_correction_appended': signal_type in ('user_correction', 'gate_failure', 'high_risk'),
        'trigger_state_updated': level in ('T1', 'T2', 'T3'),
    }


def main():
    parser = argparse.ArgumentParser(
        description='Append retrospect event to 09-run-log.md')
    parser.add_argument('--input', '-i', default=None,
                        help='Path to detector JSON output file. If not given, reads from stdin.')
    args = parser.parse_args()

    if args.input:
        detection = json.loads(Path(args.input).read_text(encoding='utf-8'))
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            print(json.dumps({'written': False, 'reason': 'Empty stdin'}, ensure_ascii=False))
            sys.exit(0)
        detection = json.loads(raw)

    result = run(detection)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
