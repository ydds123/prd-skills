#!/usr/bin/env python3
"""Run the canonical deterministic regression suite for prd-workflow-skill."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "evals" / "regression-suite.json"


def load_suite() -> list[dict]:
    data = json.loads(SUITE.read_text(encoding="utf-8"))
    tests = data.get("tests")
    if not isinstance(tests, list) or not tests:
        raise ValueError("regression-suite.json tests must be a non-empty list")
    ids = [test.get("id") for test in tests]
    if any(not test_id for test_id in ids) or len(ids) != len(set(ids)):
        raise ValueError("regression test ids must be non-empty and unique")

    eval_files = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "evals").glob("*.json")
        if path.name != SUITE.name
    }
    mapped = []
    for test in tests:
        command = test.get("command")
        if not isinstance(command, list) or len(command) < 2 or command[0] != "${PYTHON}":
            raise ValueError(f"{test.get('id')}: command must start with ${{PYTHON}}")
        script = ROOT / command[1]
        if not script.is_file():
            raise ValueError(f"{test.get('id')}: script does not exist: {command[1]}")
        covered = test.get("covers_eval_files")
        if not isinstance(covered, list):
            raise ValueError(f"{test.get('id')}: covers_eval_files must be a list")
        mapped.extend(covered)
    missing = sorted(eval_files - set(mapped))
    unknown = sorted(set(mapped) - eval_files)
    duplicates = sorted({item for item in mapped if mapped.count(item) > 1})
    if missing or unknown or duplicates:
        raise ValueError(
            f"eval mapping invalid: missing={missing}, unknown={unknown}, duplicates={duplicates}")
    return tests


def main() -> int:
    try:
        tests = load_suite()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[ERROR] cannot load regression suite: {exc}")
        return 1

    failures = []
    started = time.monotonic()
    for index, test in enumerate(tests, start=1):
        command = [sys.executable, *test["command"][1:]]
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        test_started = time.monotonic()
        result = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        elapsed = time.monotonic() - test_started
        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"[{status}] {index}/{len(tests)} {test['id']} ({elapsed:.2f}s)")
        output = result.stdout.strip()
        if output:
            print(output)
        if result.returncode != 0:
            failures.append(test["id"])

    elapsed = time.monotonic() - started
    print(f"Regression summary: tests={len(tests)} failures={len(failures)} elapsed={elapsed:.2f}s")
    if failures:
        print(f"Failed tests: {', '.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
