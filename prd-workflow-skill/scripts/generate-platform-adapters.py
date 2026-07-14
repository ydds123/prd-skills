#!/usr/bin/env python3
"""Generate or check the Codex and Claude adapter views from shared sources."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IR_PATH = ROOT / "skill-ir" / "examples" / "prd-workflow.json"
INTERFACE_PATH = ROOT / "agents" / "interface.yaml"


def load_interface() -> dict[str, str]:
    text = INTERFACE_PATH.read_text(encoding="utf-8")
    result = {}
    for key in ("display_name", "short_description", "default_prompt"):
        match = re.search(rf"^\s+{key}:\s+\"(.*)\"\s*$", text, re.MULTILINE)
        if not match:
            raise ValueError(f"agents/interface.yaml 缺少 {key}")
        result[key] = match.group(1)
    return result


def json_text(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def generate_outputs() -> dict[Path, str]:
    skill_ir = json.loads(IR_PATH.read_text(encoding="utf-8"))
    interface = load_interface()
    targets = skill_ir.get("targets")
    if targets != ["openai", "claude"]:
        raise ValueError("Skill IR targets 必须按 openai、claude 顺序声明")

    openai_yaml = (
        "interface:\n"
        f"  display_name: {json.dumps(interface['display_name'], ensure_ascii=False)}\n"
        f"  short_description: {json.dumps(interface['short_description'], ensure_ascii=False)}\n"
        f"  default_prompt: {json.dumps(interface['default_prompt'], ensure_ascii=False)}\n"
        "policy:\n"
        "  allow_implicit_invocation: true\n"
    )
    common = {
        "schema_version": "1.0.0",
        "skill": skill_ir["name"],
        "entrypoint": "../../SKILL.md",
        "skill_ir": "../../skill-ir/examples/prd-workflow.json",
        "workflow_manifest": "../../01_workflow/workflow-manifest.json",
        "generated_from": [
            "skill-ir/examples/prd-workflow.json",
            "agents/interface.yaml"
        ],
        "mandatory_fallback": "Execute every workflow gate inline when native hooks are absent or disabled."
    }
    codex = {
        **common,
        "target": "openai",
        "runtime": "codex",
        "interface_metadata": "../../agents/openai.yaml",
        "hook_support": {
            "managed_by_package": False,
            "reason": "This package does not install a Codex-native hook."
        }
    }
    claude = {
        **common,
        "target": "claude",
        "runtime": "claude-code",
        "interface_metadata": "../../agents/interface.yaml",
        "hook_support": {
            "managed_by_package": True,
            "optional": True,
            "manager": "../../scripts/manage-hooks.py"
        }
    }
    return {
        ROOT / "agents" / "openai.yaml": openai_yaml,
        ROOT / "adapters" / "codex" / "adapter.json": json_text(codex),
        ROOT / "adapters" / "claude" / "adapter.json": json_text(claude),
    }


def write(outputs: dict[Path, str]) -> int:
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"已生成：{path.relative_to(ROOT)}")
    return 0


def check(outputs: dict[Path, str]) -> int:
    stale = []
    for path, expected in outputs.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            stale.append(path.relative_to(ROOT).as_posix())
    if stale:
        print("平台适配器缺失或已过期：", file=sys.stderr)
        for path in stale:
            print(f"- {path}", file=sys.stderr)
        return 1
    print("PASS：Codex/Claude 适配器与 Skill IR、interface.yaml 一致")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="生成或检查 prd-workflow 平台适配器")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        outputs = generate_outputs()
        return write(outputs) if args.write else check(outputs)
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"平台适配器错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
