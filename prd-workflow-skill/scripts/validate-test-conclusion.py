#!/usr/bin/env python3
"""Validate the plain-language PRD quality-check conclusion structure."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = [
    "## 1. 结论",
    "## 2. 需要你决定的事情",
    "## 3. 不用你决定，我会直接完善",
    "## 4. 你回复后我会怎么处理",
    "## 5. 什么时候算完成",
    "## 6. 详细检查依据（可以不看）",
]
VERDICTS = {
    "可以继续",
    "可以继续，但有已接受风险",
    "暂时不能继续",
    "还不能判断",
}
FORBIDDEN_MAIN_TERMS = ("P0", "P1", "checklist", "hash", "seal", "validate", "退出码", "Review revision")


def validate(path: Path) -> tuple[list[str], str | None]:
    errors: list[str] = []
    if not path.is_file():
        return [f"文件不存在：{path}"], None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"文件不是 UTF-8 编码：{path}"], None
    if not text.strip():
        return [f"文件为空：{path}"], None

    positions: list[int] = []
    for heading in REQUIRED_HEADINGS:
        position = text.find(heading)
        if position < 0:
            errors.append(f"缺少必需章节：{heading}")
        else:
            positions.append(position)
    if len(positions) == len(REQUIRED_HEADINGS) and positions != sorted(positions):
        errors.append("必需章节顺序不符合检查结论模板")

    match = re.search(
        r"^结论：\*\*(可以继续|可以继续，但有已接受风险|暂时不能继续|还不能判断)\*\*\s*$",
        text,
        flags=re.MULTILINE,
    )
    verdict = match.group(1) if match else None
    if verdict not in VERDICTS:
        errors.append("结论必须明确使用：可以继续 / 可以继续，但有已接受风险 / 暂时不能继续 / 还不能判断")

    if all(heading in text for heading in REQUIRED_HEADINGS):
        main_end = text.find(REQUIRED_HEADINGS[-1])
        main_text = text[:main_end]
        for term in FORBIDDEN_MAIN_TERMS:
            if re.search(re.escape(term), main_text, flags=re.IGNORECASE):
                errors.append(f"面向用户的正文不应出现技术检查术语：{term}")

    decision_section = _section(text, REQUIRED_HEADINGS[1], REQUIRED_HEADINGS[2])
    if "没有" not in decision_section and "**请回复：**" not in decision_section:
        errors.append("需要用户决定的事项必须提供可直接复制的回复格式；没有事项时应明确写“没有”")

    direct_fix_section = _section(text, REQUIRED_HEADINGS[2], REQUIRED_HEADINGS[3])
    if not direct_fix_section.strip():
        errors.append("必须说明哪些事项会直接完善；没有时应明确写“没有”")

    completion_section = _section(text, REQUIRED_HEADINGS[4], REQUIRED_HEADINGS[5])
    if "可以继续" not in completion_section:
        errors.append("完成标准必须说明重新检查后达到“可以继续”")

    return errors, verdict


def _section(text: str, start: str, end: str) -> str:
    start_pos = text.find(start)
    end_pos = text.find(end)
    if start_pos < 0 or end_pos < 0 or end_pos <= start_pos:
        return ""
    return text[start_pos + len(start):end_pos]


def main() -> int:
    parser = argparse.ArgumentParser(description="校验面向用户的大白话内容质量检查结论")
    parser.add_argument("--file", required=True, help="检查结论 Markdown 文件")
    args = parser.parse_args()
    path = Path(args.file).resolve()
    errors, verdict = validate(path)
    if errors:
        print("检查结论结构校验失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(json.dumps({"file": str(path), "verdict": verdict, "structure": "pass"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
