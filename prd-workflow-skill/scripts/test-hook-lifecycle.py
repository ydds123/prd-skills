#!/usr/bin/env python3
"""Exercise Hook preview, install, check, runtime, and uninstall in temp files."""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANAGER = ROOT / "scripts" / "manage-hooks.py"
TASK_MANAGER = ROOT / "scripts" / "manage-current-task.py"
CLAUDE_HOOK = ROOT / "hooks" / "claude_hook.py"


def run(command: list[str], *, stdin: str | None = None, expected: int = 0) -> subprocess.CompletedProcess:
    result = subprocess.run(
        command,
        input=stdin,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == expected, result.stdout
    return result


def manager_args(action: str, project: Path, settings: Path, pointer: Path) -> list[str]:
    return [
        sys.executable, str(MANAGER), action,
        "--scope", "project",
        "--project-dir", str(project),
        "--settings-file", str(settings),
        "--current-task-file", str(pointer),
        "--python-command", sys.executable,
    ]


def main() -> None:
    expected_default_pointer = (Path.home() / ".claude" / ".prd-workflow" / "current-task.json").resolve()
    task_globals = runpy.run_path(str(TASK_MANAGER))
    gate_globals = runpy.run_path(str(ROOT / "scripts" / "prd-content-gate.py"))
    recorder_globals = runpy.run_path(str(ROOT / "hooks" / "append_retrospect_event.py"))
    assert task_globals["DEFAULT_POINTER"].resolve() == expected_default_pointer
    assert gate_globals["DEFAULT_CURRENT_TASK"].resolve() == expected_default_pointer
    assert recorder_globals["CURRENT_TASK_FILE"].resolve() == expected_default_pointer

    with tempfile.TemporaryDirectory(prefix="prd-hook-test-") as raw:
        project = Path(raw)
        settings = project / ".claude" / "settings.json"
        pointer = project / ".prd-workflow" / "current-task.json"
        settings.parent.mkdir(parents=True)
        original = {
            "env": {"KEEP": "yes"},
            "hooks": {
                "PostToolUse": [{
                    "matcher": "Write",
                    "hooks": [{"type": "command", "command": "existing-hook"}]
                }]
            }
        }
        settings.write_text(json.dumps(original, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        run(manager_args("install", project, settings, pointer) + ["--dry-run"])
        assert json.loads(settings.read_text(encoding="utf-8")) == original

        run(manager_args("install", project, settings, pointer))
        installed_text = settings.read_text(encoding="utf-8")
        installed = json.loads(installed_text)
        assert installed["env"] == original["env"]
        assert installed["hooks"]["PostToolUse"] == original["hooks"]["PostToolUse"]
        assert len(installed["hooks"]["UserPromptSubmit"]) == 1
        assert len(installed["hooks"]["Stop"]) == 1
        run(manager_args("check", project, settings, pointer))
        run(manager_args("install", project, settings, pointer))
        assert settings.read_text(encoding="utf-8") == installed_text

        task = project / "task"
        task.mkdir()
        run_log = task / "09-run-log.md"
        run_log.write_text("# Run Log\n", encoding="utf-8")
        run([
            sys.executable, str(TASK_MANAGER), "activate",
            "--task-folder", str(task), "--node", "Node 3", "--pointer", str(pointer)
        ])
        prompt_payload = json.dumps({"user_prompt": "不对，这里应该是必填项校验。"}, ensure_ascii=False)
        hook_result = run([
            sys.executable, str(CLAUDE_HOOK), "--event", "user-prompt",
            "--current-task-file", str(pointer), "--managed-id", "prd-workflow:user-prompt"
        ], stdin=prompt_payload)
        run_log_text = run_log.read_text(encoding="utf-8")
        assert "用户指正记录" in run_log_text, (
            f"hook_output={hook_result.stdout!r}; pointer={pointer.read_text(encoding='utf-8')!r}; "
            f"run_log={run_log_text!r}")

        pointer_data = json.loads(pointer.read_text(encoding="utf-8"))
        pointer_data["current_node"] = "Node 5"
        pointer.write_text(json.dumps(pointer_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        run([
            sys.executable, str(CLAUDE_HOOK), "--event", "stop",
            "--current-task-file", str(pointer), "--managed-id", "prd-workflow:stop"
        ], stdin="{}", expected=2)

        run(manager_args("uninstall", project, settings, pointer) + ["--dry-run"])
        assert json.loads(settings.read_text(encoding="utf-8")) == installed
        run(manager_args("uninstall", project, settings, pointer))
        assert json.loads(settings.read_text(encoding="utf-8")) == original
        run([sys.executable, str(TASK_MANAGER), "deactivate", "--pointer", str(pointer)])
        assert not pointer.exists()

    print("PASS: Hook preview/install/check/runtime/block/uninstall preserves unrelated settings")


if __name__ == "__main__":
    main()
