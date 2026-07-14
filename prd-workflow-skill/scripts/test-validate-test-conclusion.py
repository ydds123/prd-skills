#!/usr/bin/env python3
"""Regression tests for validate-test-conclusion.py."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "validate-test-conclusion.py"


def run(path: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--file", str(path)],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
        env=env,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="test-conclusion-") as temp:
        root = Path(temp)
        good = root / "good.md"
        good.write_text(
            "# 功能检查结论\n\n"
            "## 1. 结论\n\n结论：**暂时不能继续**\n\n仍有一个业务选择需要确认。\n\n"
            "## 2. 需要你决定的事情\n\n### 事情 1：删除怎么处理\n\n"
            "**建议选 A：整批不删除**\n\n结果更清楚。\n\n"
            "**也可以选 B：删除未使用项**\n\n需要展示处理明细。\n\n"
            "**请回复：** `1：选 A` 或 `1：选 B`\n\n"
            "## 3. 不用你决定，我会直接完善\n\n1. 补齐空页面的操作入口。\n\n"
            "## 4. 你回复后我会怎么处理\n\n1. 同步正文和验收内容。\n\n"
            "## 5. 什么时候算完成\n\n- 重新检查后的结论为“可以继续”。\n\n"
            "## 6. 详细检查依据（可以不看）\n\n- 详细检查报告\n",
            encoding="utf-8",
        )
        result = run(good)
        if result.returncode != 0:
            raise AssertionError(result.stderr)
        print("PASS plain-language decision sheet")

        machine_only = root / "machine-only.md"
        machine_only.write_text("# 测试输出\n\nP0=2，P1=3。\n", encoding="utf-8")
        result = run(machine_only)
        if result.returncode != 1 or "缺少必需章节" not in result.stderr:
            raise AssertionError(result.stderr)
        print("PASS machine-only summary rejected")

        technical_main = root / "technical-main.md"
        technical_main.write_text(good.read_text(encoding="utf-8").replace("仍有一个业务选择需要确认。", "P0 仍有一个。"), encoding="utf-8")
        result = run(technical_main)
        if result.returncode != 1 or "技术检查术语" not in result.stderr:
            raise AssertionError(result.stderr)
        print("PASS technical jargon rejected from main sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
