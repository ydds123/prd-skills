#!/usr/bin/env python3
"""Install, inspect, or uninstall the optional Claude hooks owned by prd-workflow."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
HOOK_SCRIPT = SKILL_ROOT / "hooks" / "claude_hook.py"
MARKER_PREFIX = "prd-workflow:"
EVENTS = {
    "UserPromptSubmit": ("user-prompt", "prd-workflow:user-prompt"),
    "Stop": ("stop", "prd-workflow:stop"),
}


class HookConfigError(Exception):
    pass


def quote(value: Path | str) -> str:
    return '"' + str(value).replace('"', '\\"') + '"'


def resolve_locations(args: argparse.Namespace) -> tuple[Path, Path]:
    if args.scope == "user":
        root = Path.home() / ".claude"
        default_settings = root / "settings.json"
        default_pointer = root / ".prd-workflow" / "current-task.json"
    else:
        project = Path(args.project_dir or Path.cwd()).expanduser().resolve()
        default_settings = project / ".claude" / "settings.json"
        default_pointer = project / ".prd-workflow" / "current-task.json"
    settings = Path(args.settings_file).expanduser().resolve() if args.settings_file else default_settings.resolve()
    pointer = Path(args.current_task_file).expanduser().resolve() if args.current_task_file else default_pointer.resolve()
    return settings, pointer


def read_settings(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HookConfigError(f"Claude settings.json 不是合法 JSON：{path}（{exc}）") from exc
    if not isinstance(data, dict):
        raise HookConfigError(f"Claude settings.json 顶层必须是对象：{path}")
    hooks = data.get("hooks", {})
    if hooks is not None and not isinstance(hooks, dict):
        raise HookConfigError("settings.json 的 hooks 必须是对象")
    return data


def render(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def managed_command(event_name: str, pointer: Path, python_command: str) -> str:
    event, marker = EVENTS[event_name]
    return " ".join([
        quote(python_command),
        quote(HOOK_SCRIPT.resolve()),
        "--event", event,
        "--current-task-file", quote(pointer),
        "--managed-id", marker,
    ])


def is_managed_hook(hook: object) -> bool:
    return isinstance(hook, dict) and MARKER_PREFIX in str(hook.get("command", ""))


def remove_managed(data: dict) -> dict:
    result = json.loads(json.dumps(data, ensure_ascii=False))
    hooks_root = result.get("hooks")
    if not isinstance(hooks_root, dict):
        return result
    for event_name in list(hooks_root):
        matchers = hooks_root.get(event_name)
        if not isinstance(matchers, list):
            continue
        kept_matchers = []
        for matcher in matchers:
            if not isinstance(matcher, dict):
                kept_matchers.append(matcher)
                continue
            inner = matcher.get("hooks")
            if not isinstance(inner, list):
                kept_matchers.append(matcher)
                continue
            kept_inner = [hook for hook in inner if not is_managed_hook(hook)]
            if kept_inner:
                matcher["hooks"] = kept_inner
                kept_matchers.append(matcher)
        if kept_matchers:
            hooks_root[event_name] = kept_matchers
        else:
            hooks_root.pop(event_name, None)
    if not hooks_root:
        result.pop("hooks", None)
    return result


def desired_settings(data: dict, pointer: Path, python_command: str) -> dict:
    result = remove_managed(data)
    hooks_root = result.setdefault("hooks", {})
    for event_name in EVENTS:
        hooks_root.setdefault(event_name, []).append({
            "matcher": "*",
            "hooks": [{
                "type": "command",
                "command": managed_command(event_name, pointer, python_command),
                "timeout": 15,
            }],
        })
    return result


def show_diff(path: Path, before: dict, after: dict) -> None:
    print(f"目标配置：{path}")
    diff = difflib.unified_diff(
        render(before).splitlines(),
        render(after).splitlines(),
        fromfile=str(path) + " (before)",
        tofile=str(path) + " (after)",
        lineterm="",
    )
    lines = list(diff)
    print("\n".join(lines) if lines else "无配置差异")


def write_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(render(data), encoding="utf-8")
    temporary.replace(path)


def install(args: argparse.Namespace) -> int:
    settings, pointer = resolve_locations(args)
    before = read_settings(settings)
    after = desired_settings(before, pointer, args.python_command)
    show_diff(settings, before, after)
    if args.dry_run or before == after:
        print("未写入配置。" if args.dry_run else "Hook 已是目标状态。")
        return 0
    write_atomic(settings, after)
    print(f"已安装 prd-workflow Hook；任务指针位置：{pointer}")
    return 0


def check(args: argparse.Namespace) -> int:
    settings, pointer = resolve_locations(args)
    current = read_settings(settings)
    expected = desired_settings(current, pointer, args.python_command)
    if current == expected:
        print(f"PASS：prd-workflow Hook 已正确安装在 {settings}")
        print(f"任务指针：{pointer}")
        return 0
    show_diff(settings, current, expected)
    print("FAIL：Hook 缺失、重复或与当前 Skill 路径不一致。", file=sys.stderr)
    return 1


def uninstall(args: argparse.Namespace) -> int:
    settings, _ = resolve_locations(args)
    before = read_settings(settings)
    after = remove_managed(before)
    show_diff(settings, before, after)
    if args.dry_run or before == after:
        print("未写入配置。" if args.dry_run else "未发现 prd-workflow Hook。")
        return 0
    write_atomic(settings, after)
    print("已卸载 prd-workflow Hook；其他 Hook 和设置保持不变。")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="管理 prd-workflow 的 Claude Hook")
    sub = parser.add_subparsers(dest="command", required=True)
    for command, handler in (("install", install), ("check", check), ("uninstall", uninstall)):
        item = sub.add_parser(command)
        item.add_argument("--scope", required=True, choices=["user", "project"])
        item.add_argument("--project-dir")
        item.add_argument("--settings-file", help=argparse.SUPPRESS)
        item.add_argument("--current-task-file", help=argparse.SUPPRESS)
        item.add_argument("--python-command", default=sys.executable, help=argparse.SUPPRESS)
        if command != "check":
            item.add_argument("--dry-run", action="store_true")
        item.set_defaults(handler=handler)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.handler(args)
    except HookConfigError as exc:
        print(f"Hook 配置错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
