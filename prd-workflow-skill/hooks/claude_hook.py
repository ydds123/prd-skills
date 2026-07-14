#!/usr/bin/env python3
"""Claude hook wrapper for optional PRD correction logging and final-gate blocking."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from append_retrospect_event import run as append_event
from retrospect_trigger import run as detect_event


SKILL_ROOT = Path(__file__).resolve().parents[1]


for stream in (sys.stdin, sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


def read_input() -> dict:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    data = json.loads(raw)
    return data if isinstance(data, dict) else {}


def allow() -> int:
    print(json.dumps({"continue": True, "suppressOutput": True}, ensure_ascii=False))
    return 0


def load_pointer(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def handle_user_prompt(payload: dict, pointer_path: Path) -> int:
    pointer = load_pointer(pointer_path)
    if pointer is None:
        return allow()
    prompt = str(payload.get("user_prompt", ""))
    if prompt:
        detection = detect_event("user_prompt", str(pointer.get("current_node", "unknown")), prompt)
        append_event(detection, pointer_path)
    return allow()


def handle_stop(pointer_path: Path) -> int:
    pointer = load_pointer(pointer_path)
    if pointer is None or str(pointer.get("current_node", "")) != "Node 5":
        return allow()
    gate_script = SKILL_ROOT / "scripts" / "prd-content-gate.py"
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(gate_script), "validate", "--current-task", "--current-task-file", str(pointer_path)],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode == 0:
        return allow()
    message = result.stdout.strip() or "内容质量门禁未通过"
    print(f"prd-workflow 阻止最终交付：{message}", file=sys.stderr)
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="prd-workflow Claude hook")
    parser.add_argument("--event", required=True, choices=["user-prompt", "stop"])
    parser.add_argument("--current-task-file", required=True)
    parser.add_argument("--managed-id", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = read_input()
    pointer = Path(args.current_task_file).expanduser().resolve()
    if args.event == "user-prompt":
        return handle_user_prompt(payload, pointer)
    return handle_stop(pointer)


if __name__ == "__main__":
    sys.exit(main())
