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
from datetime import datetime
from pathlib import Path
from typing import Optional


SKILL_ROOT = Path(__file__).resolve().parent.parent
CURRENT_TASK_FILE = Path(
    os.environ.get(
        'PRD_WORKFLOW_CURRENT_TASK',
        str(Path.home() / '.claude' / '.prd-workflow' / 'current-task.json'),
    )
).expanduser().resolve()


def find_run_log(current_task_file: Path = CURRENT_TASK_FILE) -> Optional[Path]:
    """Locate 09-run-log.md via current-task.json pointer."""
    if not current_task_file.exists():
        return None
    try:
        data = json.loads(current_task_file.read_text(encoding='utf-8'))
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


ROOT_CAUSE_TRIGGER_IDS = {
    '缺知识': 'TR-missing-knowledge',
    '缺方法': 'TR-missing-method',
    '缺模板': 'TR-missing-template',
    '缺门禁': 'TR-missing-gate',
    '缺案例': 'TR-missing-example',
    '偶发': 'TR-one-off',
}


def trigger_id_for_root_cause(root_cause: str) -> str:
    """Return a stable trigger ID for the governed root-cause taxonomy."""
    return ROOT_CAUSE_TRIGGER_IDS.get(root_cause or '偶发', 'TR-other')


def level_for_count(count: int) -> str:
    """Escalate repeated evidence from T1 to T3 by occurrence count."""
    if count >= 3:
        return 'T3'
    if count >= 2:
        return 'T2'
    return 'T1'


def max_level(*levels: str) -> str:
    """Keep an explicit high-severity level even when the count is lower."""
    rank = {'T0': 0, 'T1': 1, 'T2': 2, 'T3': 3}
    return max(levels, key=lambda value: rank.get(value, 0))


def insert_table_row(lines: list[str], heading: str, row: str) -> list[str]:
    """Insert a row at the end of the table belonging to a Markdown heading."""
    heading_index = next(
        (index for index, line in enumerate(lines) if heading in line), -1)
    if heading_index < 0:
        lines.append(row)
        return lines

    section_end = len(lines)
    for index in range(heading_index + 1, len(lines)):
        if lines[index].strip().startswith('## '):
            section_end = index
            break

    table_rows = [
        index for index in range(heading_index + 1, section_end)
        if lines[index].strip().startswith('|')
    ]
    insert_at = table_rows[-1] + 1 if table_rows else section_end
    lines.insert(insert_at, row)
    return lines


def generate_user_correction_row(detection: dict) -> str:
    """Generate a user correction table row from detector output."""
    now_str = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')
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

    return f'| {now_str} | {node} | {excerpt_safe} | {correction_type} | — | {ai_judgment} | — | {enter_candidate} |\n'


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
    if not has_user_correction_block(lines):
        lines.extend([
            '\n',
            '## 用户指正记录\n',
            '\n',
            '| 时间 | 所在节点 | 用户原话（摘要） | 指正类型 | 关联决策编号 | AI 判断 | 处理结果 | 是否进入复盘候选 |\n',
            '|------|---------|---------------|---------|-------------|--------|---------|------------------|\n',
        ])
    return insert_table_row(lines, '## 用户指正记录', row)

def upsert_trigger_state(lines: list[str], detection: dict,
                         level: str, root_cause: str) -> list[str]:
    """Aggregate evidence by root cause and update one stable trigger row."""
    excerpt = detection.get('raw_text_excerpt', '')
    trigger_id = trigger_id_for_root_cause(root_cause)

    if not has_trigger_state_block(lines):
        lines.extend([
            '\n',
            '## 复盘触发状态\n',
            '\n',
            '| 触发编号 | 根因分类 | 出现次数 | 最近证据 | 当前等级 | 建议动作 |\n',
            '|---------|---------|---------|---------|---------|----------|\n',
        ])

    existing_index = find_trigger_row(lines, trigger_id)
    count = 1
    if existing_index >= 0:
        cells = [cell.strip() for cell in lines[existing_index].strip().strip('|').split('|')]
        if len(cells) >= 3:
            try:
                count = int(cells[2]) + 1
            except ValueError:
                count = 1

    effective_level = max_level(level, level_for_count(count))
    row = generate_trigger_state_row(
        trigger_id, root_cause, count, excerpt, effective_level)

    if existing_index >= 0:
        lines[existing_index] = row
        return lines
    return insert_table_row(lines, '## 复盘触发状态', row)

def write_run_log(path: Path, lines: list[str]):
    """Write updated lines back to run-log file."""
    path.write_text(''.join(lines), encoding='utf-8')


def run(detection: dict, current_task_file: Path = CURRENT_TASK_FILE) -> dict:
    """Main entry — consume detector JSON, write to run-log, return result."""
    level = detection.get('trigger_level', 'T0')
    signal_type = detection.get('signal_type', '')

    if level == 'T0' and signal_type != 'user_correction':
        return {'written': False, 'reason': 'T0 — not entering retrospect', 'run_log_path': None}

    run_log = find_run_log(current_task_file)
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
    parser.add_argument('--current-task-file', default=str(CURRENT_TASK_FILE),
                        help='Path to the active task pointer JSON.')
    args = parser.parse_args()

    if args.input:
        detection = json.loads(Path(args.input).read_text(encoding='utf-8'))
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            print(json.dumps({'written': False, 'reason': 'Empty stdin'}, ensure_ascii=False))
            sys.exit(0)
        detection = json.loads(raw)

    result = run(detection, Path(args.current_task_file).expanduser().resolve())
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()



