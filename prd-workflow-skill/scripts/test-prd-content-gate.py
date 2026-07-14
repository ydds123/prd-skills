#!/usr/bin/env python3
"""Forward tests for prd-content-gate.py using isolated temporary files."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "prd-content-gate.py"


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
        env=env,
    )


def evidence(summary: str) -> list[dict[str, str]]:
    return [{"location": "§1", "summary": summary}]


def gate_rules() -> dict:
    return {
        "review_conclusion": {
            "rules": [
                {"id": "block_p0", "metric": "open_p0", "operator": ">", "value": 0, "result": "block"},
                {"id": "block_p1", "metric": "open_p1", "operator": ">", "value": 0, "result": "block"},
                {"id": "pending_check", "metric": "pending_check", "operator": ">", "value": 0, "result": "incomplete"},
                {"id": "pending_supplement", "metric": "pending_supplement", "operator": ">", "value": 0, "result": "incomplete"},
            ],
            "default_result": "pass",
            "allowed_results": ["block", "incomplete", "pass"],
        },
        "priority_rules": {
            "P0": {"rank": 0},
            "P1": {"rank": 1},
            "P2": {"rank": 2},
            "P3": {"rank": 3},
        },
        "risk_acceptance": {
            "allowed_severities": ["P1"],
            "forbidden_severities": ["P0"],
            "required_fields": ["accepted_by", "accepted_at", "reason", "owner", "follow_up", "deadline"],
        },
    }


def base_review() -> dict:
    return {
        "schema_version": "2.0.0",
        "generated_at": "2026-07-14 10:00:00",
        "review_revision": 1,
        "reviewer": {
            "mode": "independent",
            "writer_ref": "writer-1",
            "reviewer_ref": "reviewer-1",
        },
        "prd": {"path": "05-完整PRDv1.md", "complexity": "L3"},
        "review_report": {"path": "06-审核报告.md"},
        "checklist_version": "test-1.0",
        "items": [
            {"id": "C01", "applicability": "applicable", "result": "pass", "evidence": evidence("问题定义完整"), "reason": "", "finding_ids": []},
            {"id": "C02", "applicability": "applicable", "result": "pass", "evidence": evidence("范围明确"), "reason": "", "finding_ids": []},
            {"id": "C03", "applicability": "not_applicable", "result": "not_applicable", "evidence": [], "reason": "本需求不涉及删除", "finding_ids": []},
        ],
        "findings": [],
        "consistency_sweep": {
            "status": "not_required",
            "change_types": ["no_content_change"],
            "dimensions_checked": [],
            "evidence": [],
            "reason": "未发生内容修订",
        },
    }


def finding(finding_id: str, severity: str, status: str) -> dict:
    value = {
        "id": finding_id,
        "severity": severity,
        "status": status,
        "title": "范围规则缺失",
        "locations": ["§1"],
        "minimum_fix": "补充明确规则",
        "checklist_item_ids": ["C02"],
        "resolution_evidence": [],
    }
    if status == "risk_accepted":
        value["risk_acceptance"] = {
            "accepted_by": "PM-A",
            "accepted_at": "2026-07-14 10:30:00",
            "reason": "本期接受",
            "owner": "PM-A",
            "follow_up": "二期补充",
            "deadline": "2026-08-01",
        }
    return value


def assert_case(condition: bool, name: str, details: str = "") -> None:
    if not condition:
        raise AssertionError(f"{name} failed\n{details}")
    print(f"PASS {name}")


def seal(root: Path, review: dict, name: str) -> subprocess.CompletedProcess[str]:
    review_path = root / f"{name}-review.json"
    gate_path = root / f"{name}-gate.json"
    write_json(review_path, review)
    return run(
        "seal", "--review", str(review_path), "--out", str(gate_path),
        "--checklist", str(root / "checklist.json"), "--force",
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="prd-content-gate-") as temp:
        root = Path(temp)
        (root / "05-完整PRDv1.md").write_text("# Test PRD\n\n## 1. Scope\nContent.\n", encoding="utf-8")
        (root / "06-审核报告.md").write_text("# Review\n\nAll items reviewed.\n", encoding="utf-8")
        checklist = {
            "meta": {"version": "test-1.0", "total_items": 3},
            "items": [
                {"id": "C01", "priority": "P0", "hierarchy": "gate"},
                {"id": "C02", "priority": "P1", "hierarchy": "gate"},
                {"id": "C03", "priority": "P2", "hierarchy": "extended"},
            ],
            "gate_rules": gate_rules(),
        }
        write_json(root / "checklist.json", checklist)

        result = seal(root, base_review(), "pass")
        assert_case(result.returncode == 0, "pass seal", result.stderr)
        result = run("validate", "--gate", str(root / "pass-gate.json"), "--checklist", str(root / "checklist.json"))
        assert_case(result.returncode == 0, "pass validate", result.stderr)

        original_prd = (root / "05-完整PRDv1.md").read_text(encoding="utf-8")
        (root / "05-完整PRDv1.md").write_text(original_prd + "Changed after seal.\n", encoding="utf-8")
        result = run("validate", "--gate", str(root / "pass-gate.json"), "--checklist", str(root / "checklist.json"))
        assert_case(result.returncode == 1 and "封印后发生变化" in result.stderr, "stale PRD blocked", result.stderr)
        result = run(
            "seal", "--review", str(root / "pass-review.json"),
            "--out", str(root / "pass-gate.json"),
            "--checklist", str(root / "checklist.json"), "--force",
        )
        assert_case(result.returncode == 1 and "review_revision" in result.stderr, "unchanged review cannot reseal changed PRD", result.stderr)
        (root / "05-完整PRDv1.md").write_text(original_prd, encoding="utf-8")

        p0 = base_review()
        p0["items"][0].update({"result": "fail", "evidence": evidence("缺失"), "finding_ids": ["F-P0"]})
        p0["findings"] = [finding("F-P0", "P0", "open") | {"checklist_item_ids": ["C01"]}]
        result = seal(root, p0, "p0")
        assert_case(result.returncode == 1 and json.loads((root / "p0-gate.json").read_text(encoding="utf-8"))["conclusion"] == "block", "open P0 blocked", result.stderr)

        p1 = base_review()
        p1["items"][1].update({"result": "fail", "finding_ids": ["F-P1"]})
        p1["findings"] = [finding("F-P1", "P1", "open")]
        result = seal(root, p1, "p1")
        assert_case(result.returncode == 1, "unaccepted P1 blocked", result.stderr)

        accepted = deepcopy(p1)
        accepted["findings"] = [finding("F-P1", "P1", "risk_accepted")]
        result = seal(root, accepted, "accepted")
        assert_case(result.returncode == 0, "complete P1 acceptance passes", result.stderr)

        missing = base_review()
        missing["items"].pop()
        result = seal(root, missing, "missing")
        assert_case(result.returncode == 1 and "未处置" in result.stderr, "missing checklist item blocked", result.stderr)

        pending = base_review()
        pending["items"][0].update({"applicability": "pending", "result": "pending_check", "evidence": [], "reason": "待来源确认"})
        result = seal(root, pending, "pending")
        assert_case(result.returncode == 1 and json.loads((root / "pending-gate.json").read_text(encoding="utf-8"))["conclusion"] == "incomplete", "pending review blocked", result.stderr)

        bad_acceptance = base_review()
        bad_acceptance["items"][0].update({"result": "fail", "finding_ids": ["F-BAD"]})
        bad_acceptance["findings"] = [finding("F-BAD", "P0", "risk_accepted") | {"checklist_item_ids": ["C01"]}]
        result = seal(root, bad_acceptance, "bad-acceptance")
        assert_case(result.returncode == 1 and "仅 P1 可以风险接受" in result.stderr, "P0 acceptance rejected", result.stderr)

        same_context = base_review()
        same_context["reviewer"]["reviewer_ref"] = same_context["reviewer"]["writer_ref"]
        result = seal(root, same_context, "same-context")
        assert_case(result.returncode == 1 and "不能相同" in result.stderr, "same review context rejected", result.stderr)

        incomplete_sweep = base_review()
        incomplete_sweep["consistency_sweep"] = {
            "status": "complete",
            "change_types": ["role_change"],
            "dimensions_checked": ["role"],
            "evidence": evidence("已检查角色定义"),
            "reason": "",
        }
        result = seal(root, incomplete_sweep, "incomplete-sweep")
        assert_case(
            result.returncode == 1 and "缺少本次变更必查维度" in result.stderr,
            "incomplete sweep coverage blocked",
            result.stderr,
        )

        complete_sweep = base_review()
        complete_sweep["consistency_sweep"] = {
            "status": "complete",
            "change_types": ["role_change"],
            "dimensions_checked": ["role", "permission", "acceptance"],
            "evidence": evidence("角色、权限和验收已完成回扫"),
            "reason": "",
        }
        result = seal(root, complete_sweep, "complete-sweep")
        assert_case(result.returncode == 0, "complete sweep coverage passes", result.stderr)

        unknown_dimension = deepcopy(complete_sweep)
        unknown_dimension["consistency_sweep"]["dimensions_checked"].append("unknown")
        result = seal(root, unknown_dimension, "unknown-dimension")
        assert_case(
            result.returncode == 1 and "未知维度" in result.stderr,
            "unknown sweep dimension blocked",
            result.stderr,
        )

        p2 = base_review()
        p2["items"][2] = {
            "id": "C03", "applicability": "applicable", "result": "fail",
            "evidence": [], "reason": "", "finding_ids": ["F-P2"],
        }
        p2["findings"] = [finding("F-P2", "P2", "open") | {"checklist_item_ids": ["C03"]}]
        result = seal(root, p2, "p2-default")
        assert_case(result.returncode == 0, "P2 follows default JSON policy", result.stderr)

        custom_checklist = deepcopy(checklist)
        custom_checklist["meta"]["version"] = "test-1.0-custom"
        custom_checklist["gate_rules"]["review_conclusion"]["rules"][0]["metric"] = "open_p2"
        custom_checklist_path = root / "custom-checklist.json"
        write_json(custom_checklist_path, custom_checklist)
        p2["checklist_version"] = "test-1.0-custom"
        custom_review_path = root / "p2-custom-review.json"
        custom_gate_path = root / "p2-custom-gate.json"
        write_json(custom_review_path, p2)
        result = run(
            "seal", "--review", str(custom_review_path), "--out", str(custom_gate_path),
            "--checklist", str(custom_checklist_path), "--force",
        )
        assert_case(
            result.returncode == 1
            and json.loads(custom_gate_path.read_text(encoding="utf-8"))["conclusion"] == "block",
            "changing JSON policy changes gate result",
            result.stderr,
        )

        gate_hash = hashlib.sha256((root / "checklist.json").read_bytes()).hexdigest()
        checklist["meta"]["version"] = "test-1.1"
        write_json(root / "checklist.json", checklist)
        result = run("validate", "--gate", str(root / "accepted-gate.json"), "--checklist", str(root / "checklist.json"))
        assert_case(result.returncode == 1 and "checklist" in result.stderr and gate_hash != hashlib.sha256((root / "checklist.json").read_bytes()).hexdigest(), "changed checklist blocked", result.stderr)

    print("All PRD content gate tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
