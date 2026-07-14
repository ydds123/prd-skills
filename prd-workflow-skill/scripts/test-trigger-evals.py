#!/usr/bin/env python3
"""Static checks for the Skill routing contract and its trigger examples."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    data = json.loads((ROOT / "evals" / "trigger-evals.json").read_text(encoding="utf-8"))
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = re.match(r"^---\s*\n(.*?)\n---", skill, re.DOTALL)
    if not frontmatter:
        raise AssertionError("SKILL.md frontmatter is missing")
    description_match = re.search(r"^description:\s*(.+)$", frontmatter.group(1), re.MULTILINE)
    if not description_match:
        raise AssertionError("SKILL.md description is missing")
    description = description_match.group(1)

    positive = data.get("positive", [])
    negative = data.get("negative", [])
    if not positive or not negative:
        raise AssertionError("trigger evals must contain positive and negative examples")
    if any(item.get("route") != "prd-workflow" for item in positive):
        raise AssertionError("all positive examples must route to prd-workflow")
    if any(item.get("preferred_route") == "prd-workflow" for item in negative):
        raise AssertionError("negative examples must route outside prd-workflow")
    inputs = [item.get("input", "") for item in positive + negative]
    if any(not item.strip() for item in inputs) or len(inputs) != len(set(inputs)):
        raise AssertionError("trigger inputs must be non-empty and unique")

    required_signals = ["写前对齐", "决策账本", "质量门禁", "修订闭环", "skill 复盘"]
    missing = [signal for signal in required_signals if signal.lower() not in description.lower()]
    if missing:
        raise AssertionError(f"SKILL description misses positive routing signals: {missing}")
    for exclusion in ["one-shot PRD draft", "standalone PRD review"]:
        if exclusion.lower() not in description.lower():
            raise AssertionError(f"SKILL description misses route exclusion: {exclusion}")

    print("PASS: trigger eval schema and static SKILL routing boundaries")


if __name__ == "__main__":
    main()
