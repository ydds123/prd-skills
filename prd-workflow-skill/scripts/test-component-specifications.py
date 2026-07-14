#!/usr/bin/env python3
"""Regression tests for the centralized component specification."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-component-specifications.py"
SOURCE = ROOT / "05_context" / "writing-standards" / "component-specifications.json"
OUTPUT = ROOT / "05_context" / "writing-standards" / "component-specifications.md"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8", env=env)


def main() -> int:
    result = run("--check")
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    print("PASS canonical source and generated Markdown match")

    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    components = {item["id"]: item for item in data["components"]}
    multiline = components["multi_line_text"]
    expected = {"short_note", "operation_opinion", "long_text"}
    if set(multiline["semantic_profiles"]) != expected:
        raise AssertionError("multi_line_text semantic profiles are incomplete")
    for phrase in ("允许换行", "首尾空行", "每个换行计1个字符"):
        if phrase not in multiline["content_rule_template"]:
            raise AssertionError(f"multi_line_text template missing: {phrase}")
    print("PASS multi-line text component contract")

    with tempfile.TemporaryDirectory(prefix="component-spec-") as temp:
        temp_root = Path(temp)
        bad_source = temp_root / "bad.json"
        bad_output = temp_root / "bad.md"
        bad = json.loads(SOURCE.read_text(encoding="utf-8"))
        bad["components"] = [item for item in bad["components"] if item["id"] != "multi_line_text"]
        bad_source.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
        result = run("--source", str(bad_source), "--out", str(bad_output))
        if result.returncode != 1 or "multi_line_text" not in result.stderr:
            raise AssertionError(result.stderr)
        print("PASS missing required component rejected")

        stale_output = temp_root / "stale.md"
        stale_output.write_text("stale", encoding="utf-8")
        result = run("--source", str(SOURCE), "--out", str(stale_output), "--check")
        if result.returncode != 1 or "已过期" not in result.stderr:
            raise AssertionError(result.stderr)
        print("PASS stale generated view rejected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
