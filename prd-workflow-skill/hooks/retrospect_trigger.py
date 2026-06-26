"""
Retrospect Trigger Detector — lightweight signal detector for prd-workflow-skill.

Captures user corrections, retrospective intent, gate failures, and high-risk signals.
Outputs structured JSON for Agent consumption. Does NOT modify any Skill or PRD files.

Usage:
  python retrospect_trigger.py --source user_prompt --node "Node 3" --text "<user input>"
  python retrospect_trigger.py --source review_result --node "Node 4" --text "<finding>"
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from typing import Optional


# ── Signal definitions ──────────────────────────────────────────────

USER_CORRECTION = [
    r'不对', r'不是这个意思', r'你理解错了', r'我刚才说的是', r'我之前说过',
    r'怎么又', r'不要这样', r'这个不能这么写', r'应该放到', r'这里应该是',
    r'这个是错的', r'重新写', r'搞错了', r'你漏了', r'这里少了',
    r'你没有', r'你怎么', r'这个不是', r'为什么要',
]

RETROSPECT_INTENT = [
    r'这个可以写进\s*[Ss]kill', r'这个要沉淀', r'下次遇到这种情况',
    r'以后都要', r'这里应该有门禁', r'这里应该自动触发',
    r'这个应该作为模板', r'这个可以作为规则', r'写进[Ss]kill',
    r'沉淀到[Ss]kill', r'优化下[Ss]kill', r'完善下[Ss]kill',
    r'这是[Ss]kill待完善吗',
]

HIGH_RISK = [
    r'P0', r'P1', r'阻塞', r'漏了', r'没覆盖',
    r'不一致', r'前后矛盾', r'旧说法', r'术语混用',
    r'范围冲突', r'权限冲突', r'状态冲突', r'数据口径冲突',
    r'门禁失效', r'checklist.*未覆盖', r'清单.*遗漏',
]

GATE_FAILURE = [
    r'P0.*没.*拦住', r'P0.*门禁.*失效', r'本该.*阻塞.*没有',
    r'checklist.*本应覆盖', r'应该被.*拦截',
]

# ── Root cause classification ───────────────────────────────────────

ROOT_CAUSE_KEYWORDS = {
    '缺知识': [r'不知道.*业务', r'缺.*业务.*知识', r'缺.*行业.*背景', r'上下文.*缺失'],
    '缺方法': [r'没有.*规则', r'没有.*要求', r'没有.*方法', r'protocol.*没有', r'SKILL.*没有', r'Node.*没有.*强制', r'未强制', r'没有.*约束'],
    '缺模板': [r'没有.*模板', r'缺.*表格', r'缺.*模板', r'模板.*缺', r'格式.*不对', r'表头.*不'],
    '缺门禁': [r'没有.*门禁', r'门禁.*没有', r'gate.*没有', r'本应.*检查', r'应该.*拦截', r'没有.*拦住', r'缺.*门禁'],
    '缺案例': [r'没有.*示例', r'没有.*例子', r'缺少.*示例', r'不知道.*怎么写'],
}


def classify_root_cause(text: str) -> Optional[str]:
    """Heuristic root cause classification from text content."""
    scores = {}
    for cause, patterns in ROOT_CAUSE_KEYWORDS.items():
        score = sum(1 for p in patterns if re.search(p, text))
        if score:
            scores[cause] = score
    if not scores:
        return None
    return max(scores, key=scores.get)


def detect_signals(text: str) -> list[str]:
    """Detect which signal types are present in the text."""
    signals = []
    for pattern in USER_CORRECTION:
        if re.search(pattern, text):
            signals.append('user_correction')
            break
    for pattern in RETROSPECT_INTENT:
        if re.search(pattern, text):
            signals.append('retrospect_intent')
            break
    for pattern in GATE_FAILURE:
        if re.search(pattern, text):
            signals.append('gate_failure')
            break
    if not signals:
        for pattern in HIGH_RISK:
            if re.search(pattern, text):
                signals.append('high_risk')
                break
    return signals


def matched_keywords(text: str) -> list[str]:
    """Return which keywords matched in the text."""
    all_patterns = USER_CORRECTION + RETROSPECT_INTENT + HIGH_RISK + GATE_FAILURE
    matches = []
    for pattern in all_patterns:
        m = re.search(pattern, text)
        if m:
            matches.append(m.group(0))
    return matches[:5]


def determine_level(signal_type: str, root_cause: str | None,
                    occurrence_count: int = 1) -> str:
    """Determine T0-T3 trigger level."""
    if signal_type == 'gate_failure':
        return 'T3'
    if signal_type == 'retrospect_intent':
        return 'T2'
    if signal_type == 'high_risk':
        if occurrence_count >= 3:
            return 'T3'
        if occurrence_count >= 2:
            return 'T2'
        return 'T1'
    if signal_type == 'user_correction':
        if occurrence_count >= 3:
            return 'T3'
        if occurrence_count >= 2:
            return 'T2'
        return 'T1'
    # No signal detected
    if root_cause:
        return 'T1'
    return 'T0'


def suggested_action(level: str) -> str:
    """Map trigger level to suggested action."""
    return {
        'T0': 'none',
        'T1': 'append_run_log_observation',
        'T2': 'mark_retrospect_candidate',
        'T3': 'generate_skill_retrospect_proposal',
    }.get(level, 'none')


def run(source: str, node: str, text: str,
        occurrence_count: int = 1) -> dict:
    """Main entry point — analyze input and return structured result."""
    if not text or not text.strip():
        return {'triggered': False, 'source': source, 'node': node,
                'signal_type': None, 'trigger_level': 'T0',
                'suggested_action': 'none'}

    excerpt = text[:200]
    signals = detect_signals(text)
    signal_type = signals[0] if signals else None
    root_cause = classify_root_cause(text) if signal_type else None
    level = determine_level(signal_type or 'none', root_cause, occurrence_count)

    return {
        'triggered': signal_type is not None,
        'source': source,
        'node': node,
        'signal_type': signal_type,
        'trigger_level': level,
        'suspected_root_cause': root_cause,
        'suggested_action': suggested_action(level),
        'matched_keywords': matched_keywords(text),
        'raw_text_excerpt': excerpt,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(
        description='Retrospect Trigger Detector for prd-workflow-skill')
    parser.add_argument('--source', required=True,
                        choices=['user_prompt', 'user_directive', 'review_result',
                                 'sweep_result', 'node_complete'],
                        help='Event source')
    parser.add_argument('--node', default='unknown',
                        help='Current workflow node (e.g. Node 3)')
    parser.add_argument('--text', required=True,
                        help='Input text to analyze')
    parser.add_argument('--count', type=int, default=1,
                        help='Occurrence count for same root cause')
    args = parser.parse_args()

    result = run(args.source, args.node, args.text, args.count)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
