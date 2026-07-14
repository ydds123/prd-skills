#!/usr/bin/env python3
"""Create, inspect, or remove the active PRD task pointer."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POINTER = Path.home() / ".claude" / ".prd-workflow" / "current-task.json"


def pointer_path(raw: str | None) -> Path:
    configured = raw or os.environ.get("PRD_WORKFLOW_CURRENT_TASK")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_POINTER.resolve()


def portable_child(task_folder: Path, raw: str | None, default_name: str) -> str:
    path = Path(raw) if raw else Path(default_name)
    if not path.is_absolute():
        path = task_folder / path
    return str(path.resolve())


def write_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def activate(args: argparse.Namespace) -> int:
    task_folder = Path(args.task_folder).expanduser().resolve()
    if not task_folder.is_dir():
        print(f"任务目录不存在：{task_folder}", file=sys.stderr)
        return 1
    run_log = Path(portable_child(task_folder, args.run_log, "09-run-log.md"))
    if not run_log.is_file():
        print(f"Run Log 不存在：{run_log}", file=sys.stderr)
        return 1
    data = {
        "schema_version": "1.0.0",
        "task_folder": str(task_folder),
        "run_log_path": str(run_log),
        "content_gate_path": portable_child(task_folder, args.content_gate, "06-content-gate.json"),
        "checklist_path": str((SKILL_ROOT / "05_context" / "prd-standards" / "checklist-v3.3.json").resolve()),
        "consistency_rules_path": str((SKILL_ROOT / "01_workflow" / "consistency-sweep-rules.json").resolve()),
        "current_node": args.node,
        "updated_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S"),
    }
    target = pointer_path(args.pointer)
    if args.dry_run:
        print(f"目标指针：{target}")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    write_atomic(target, data)
    print(f"已激活 PRD 任务指针：{target}")
    return 0


def show(args: argparse.Namespace) -> int:
    target = pointer_path(args.pointer)
    if not target.is_file():
        print(f"未激活：{target}")
        return 1
    print(target.read_text(encoding="utf-8"), end="")
    return 0


def deactivate(args: argparse.Namespace) -> int:
    target = pointer_path(args.pointer)
    if not target.exists():
        print(f"无需停用，指针不存在：{target}")
        return 0
    if args.dry_run:
        print(f"将删除任务指针：{target}")
        return 0
    target.unlink()
    print(f"已停用 PRD 任务指针：{target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="管理 prd-workflow 当前任务指针")
    sub = parser.add_subparsers(dest="command", required=True)

    activate_parser = sub.add_parser("activate", help="激活一个已创建 Run Log 的 PRD 任务")
    activate_parser.add_argument("--task-folder", required=True)
    activate_parser.add_argument("--run-log")
    activate_parser.add_argument("--content-gate")
    activate_parser.add_argument("--node", default="Boot")
    activate_parser.add_argument("--pointer")
    activate_parser.add_argument("--dry-run", action="store_true")
    activate_parser.set_defaults(handler=activate)

    show_parser = sub.add_parser("show", help="显示当前任务指针")
    show_parser.add_argument("--pointer")
    show_parser.set_defaults(handler=show)

    deactivate_parser = sub.add_parser("deactivate", help="移除当前任务指针")
    deactivate_parser.add_argument("--pointer")
    deactivate_parser.add_argument("--dry-run", action="store_true")
    deactivate_parser.set_defaults(handler=deactivate)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
