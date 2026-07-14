#!/usr/bin/env python3
"""Verify that both target adapters are current and semantically bounded."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-platform-adapters.py"


def main() -> None:
    spec = importlib.util.spec_from_file_location("platform_adapter_generator", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    outputs = module.generate_outputs()
    for path, expected in outputs.items():
        assert path.is_file(), f"missing generated adapter: {path}"
        assert path.read_text(encoding="utf-8") == expected, f"stale generated adapter: {path}"

    codex = json.loads((ROOT / "adapters" / "codex" / "adapter.json").read_text(encoding="utf-8"))
    claude = json.loads((ROOT / "adapters" / "claude" / "adapter.json").read_text(encoding="utf-8"))
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    description = re.search(r"^description:\s*(.+)$", skill, re.MULTILINE).group(1)
    skill_ir = json.loads((ROOT / "skill-ir" / "examples" / "prd-workflow.json").read_text(encoding="utf-8"))
    assert skill_ir["trigger_surface"]["description"] == description
    assert codex["target"] == "openai" and codex["runtime"] == "codex"
    assert claude["target"] == "claude" and claude["runtime"] == "claude-code"
    assert codex["skill_ir"] == claude["skill_ir"]
    assert codex["workflow_manifest"] == claude["workflow_manifest"]
    assert codex["mandatory_fallback"] == claude["mandatory_fallback"]
    assert codex["hook_support"]["managed_by_package"] is False
    assert claude["hook_support"]["optional"] is True
    print("PASS: Codex and Claude adapters share one Skill IR and preserve inline fallback")


if __name__ == "__main__":
    main()
