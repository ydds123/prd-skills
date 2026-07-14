#!/usr/bin/env python3
"""Create and verify the machine-readable PRD content quality gate.

The reviewer owns semantic judgment. This script owns deterministic checks:
complete checklist disposition, evidence shape, blocking rules, and stale-file
detection through SHA-256 seals.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CHECKLIST = SKILL_ROOT / "05_context" / "prd-standards" / "checklist-v3.3.json"
DEFAULT_CONSISTENCY_RULES = SKILL_ROOT / "01_workflow" / "consistency-sweep-rules.json"
DEFAULT_CURRENT_TASK = Path(
    os.environ.get(
        "PRD_WORKFLOW_CURRENT_TASK",
        str(Path.home() / ".claude" / ".prd-workflow" / "current-task.json"),
    )
).expanduser().resolve()
REVIEW_SCHEMA_VERSION = "2.0.0"
GATE_SCHEMA_VERSION = "2.0.0"
FINDING_STATUSES = {"open", "fixed", "risk_accepted"}
RESULTS = {"pass", "fail", "pending_check", "pending_supplement", "not_applicable"}
OPERATORS = {
    ">": lambda left, right: left > right,
    ">=": lambda left, right: left >= right,
    "==": lambda left, right: left == right,
    "<=": lambda left, right: left <= right,
    "<": lambda left, right: left < right,
}


class GateError(Exception):
    pass


def now_text() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GateError(f"文件不存在：{path}") from exc
    except UnicodeDecodeError as exc:
        raise GateError(f"文件不是 UTF-8 编码：{path}") from exc
    except json.JSONDecodeError as exc:
        raise GateError(f"JSON 格式错误：{path}（{exc}）") from exc
    if not isinstance(data, dict):
        raise GateError(f"JSON 顶层必须是对象：{path}")
    return data


def write_json(path: Path, data: dict[str, Any], force: bool = False) -> None:
    if path.exists() and not force:
        raise GateError(f"输出文件已存在；如确认覆盖请使用 --force：{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(base: Path, raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def portable_path(path: Path, base: Path) -> str:
    try:
        return os.path.relpath(path, base).replace("\\", "/")
    except ValueError:
        return str(path)


def require_nonempty_file(path: Path, label: str) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"{label}不存在：{path}"]
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{label}不是 UTF-8 编码：{path}"]
    if not text.strip():
        errors.append(f"{label}为空：{path}")
    return errors


def load_checklist(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    data = load_json(path)
    raw_items = data.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise GateError(f"checklist.items 必须是非空数组：{path}")
    items: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw_items):
        if not isinstance(item, dict) or not item.get("id"):
            raise GateError(f"checklist.items[{index}] 缺少 id")
        item_id = str(item["id"])
        if item_id in items:
            raise GateError(f"checklist 存在重复 id：{item_id}")
        items[item_id] = item
    return data, items


def load_consistency_policy(path: Path) -> dict[str, Any]:
    data = load_json(path)
    dimensions = data.get("dimensions")
    routes = data.get("change_routes")
    if not isinstance(dimensions, list) or not isinstance(routes, list):
        raise GateError("一致性规则必须定义 dimensions 和 change_routes")
    dimension_ids = {
        item.get("id") for item in dimensions
        if isinstance(item, dict) and item.get("id")
    }
    route_map = {}
    for route in routes:
        if not isinstance(route, dict) or not route.get("id"):
            raise GateError("一致性规则存在缺少 id 的 change_route")
        required = route.get("required_dimensions")
        if not isinstance(required, list) or set(required) - dimension_ids:
            raise GateError(f"change_route {route['id']} 的 required_dimensions 非法")
        route_map[route["id"]] = set(required)
    not_required = set(data.get("not_required_change_types", []))
    if not not_required:
        raise GateError("一致性规则必须定义 not_required_change_types")
    return {
        "data": data,
        "dimensions": dimension_ids,
        "routes": route_map,
        "not_required": not_required,
    }


def load_gate_policy(checklist: dict[str, Any]) -> dict[str, Any]:
    gate_rules = checklist.get("gate_rules")
    if not isinstance(gate_rules, dict):
        raise GateError("checklist.gate_rules 必须是对象")
    priority_rules = gate_rules.get("priority_rules")
    if not isinstance(priority_rules, dict) or not priority_rules:
        raise GateError("checklist.gate_rules.priority_rules 必须是非空对象")
    ranks = {}
    for severity, rule in priority_rules.items():
        rank = rule.get("rank") if isinstance(rule, dict) else None
        if not isinstance(rank, int):
            raise GateError(f"priority_rules.{severity}.rank 必须是整数")
        if rank in ranks.values():
            raise GateError("priority_rules.rank 不能重复")
        ranks[severity] = rank

    conclusion = gate_rules.get("review_conclusion")
    if not isinstance(conclusion, dict):
        raise GateError("checklist.gate_rules.review_conclusion 必须是对象")
    rules = conclusion.get("rules")
    allowed_results = set(conclusion.get("allowed_results", []))
    if not isinstance(rules, list) or not rules or not allowed_results:
        raise GateError("review_conclusion 必须定义 rules 和 allowed_results")
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise GateError(f"review_conclusion.rules[{index}] 必须是对象")
        if rule.get("operator") not in OPERATORS:
            raise GateError(f"review_conclusion.rules[{index}].operator 不支持")
        if rule.get("result") not in allowed_results:
            raise GateError(f"review_conclusion.rules[{index}].result 不在 allowed_results 中")
        if not str(rule.get("metric", "")).strip() or not isinstance(rule.get("value"), int):
            raise GateError(f"review_conclusion.rules[{index}] 必须定义 metric 和整数 value")
    default_result = conclusion.get("default_result")
    if default_result not in allowed_results:
        raise GateError("review_conclusion.default_result 不在 allowed_results 中")

    acceptance = gate_rules.get("risk_acceptance")
    if not isinstance(acceptance, dict):
        raise GateError("checklist.gate_rules.risk_acceptance 必须是对象")
    allowed_acceptance = set(acceptance.get("allowed_severities", []))
    forbidden_acceptance = set(acceptance.get("forbidden_severities", []))
    required_fields = acceptance.get("required_fields")
    severities = set(priority_rules)
    if not allowed_acceptance or allowed_acceptance - severities:
        raise GateError("risk_acceptance.allowed_severities 必须引用已定义严重度")
    if forbidden_acceptance - severities:
        raise GateError("risk_acceptance.forbidden_severities 包含未知严重度")
    if not isinstance(required_fields, list) or not required_fields:
        raise GateError("risk_acceptance.required_fields 必须是非空数组")
    return {
        "severities": severities,
        "ranks": ranks,
        "conclusion_rules": rules,
        "default_result": default_result,
        "allowed_acceptance": allowed_acceptance,
        "forbidden_acceptance": forbidden_acceptance,
        "acceptance_fields": required_fields,
    }


def evaluate_conclusion(summary: dict[str, int], policy: dict[str, Any]) -> str:
    for rule in policy["conclusion_rules"]:
        metric = rule["metric"]
        if metric not in summary:
            raise GateError(f"门禁规则引用未知统计指标：{metric}")
        if OPERATORS[rule["operator"]](summary[metric], rule["value"]):
            return rule["result"]
    return policy["default_result"]


def valid_evidence(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    return all(
        isinstance(entry, dict)
        and str(entry.get("location", "")).strip()
        and str(entry.get("summary", "")).strip()
        for entry in value
    )


def validate_review(
    review_path: Path, checklist_path: Path, consistency_rules_path: Path = DEFAULT_CONSISTENCY_RULES
) -> tuple[list[str], dict[str, Any], dict[str, Any]]:
    errors: list[str] = []
    review = load_json(review_path)
    checklist, checklist_items = load_checklist(checklist_path)
    policy = load_gate_policy(checklist)
    consistency_policy = load_consistency_policy(consistency_rules_path)
    severities = policy["severities"]
    severity_rank = policy["ranks"]

    if review.get("schema_version") != REVIEW_SCHEMA_VERSION:
        errors.append(f"审查文件 schema_version 必须为 {REVIEW_SCHEMA_VERSION}")
    checklist_version = checklist.get("meta", {}).get("version", "unknown")
    if review.get("checklist_version") != checklist_version:
        errors.append(f"审查文件 checklist_version 必须为当前版本 {checklist_version}")
    review_revision = review.get("review_revision")
    if not isinstance(review_revision, int) or review_revision < 1:
        errors.append("review_revision 必须是大于等于 1 的整数")

    reviewer = review.get("reviewer")
    if not isinstance(reviewer, dict):
        errors.append("reviewer 必须是对象")
        reviewer = {}
    if reviewer.get("mode") != "independent":
        errors.append("reviewer.mode 必须为 independent")
    writer_ref = str(reviewer.get("writer_ref", "")).strip()
    reviewer_ref = str(reviewer.get("reviewer_ref", "")).strip()
    if not writer_ref or not reviewer_ref:
        errors.append("reviewer.writer_ref 和 reviewer.reviewer_ref 均不能为空")
    elif writer_ref == reviewer_ref:
        errors.append("writer_ref 与 reviewer_ref 不能相同；请切换独立审查上下文")

    prd = review.get("prd")
    if not isinstance(prd, dict) or not str(prd.get("path", "")).strip():
        errors.append("prd.path 不能为空")
        prd = {}
    complexity = str(prd.get("complexity", ""))
    if complexity not in {"L1", "L2", "L3", "L4"}:
        errors.append("prd.complexity 必须为 L1、L2、L3 或 L4")

    report = review.get("review_report")
    if not isinstance(report, dict) or not str(report.get("path", "")).strip():
        errors.append("review_report.path 不能为空")
        report = {}

    dispositions = review.get("items")
    if not isinstance(dispositions, list):
        errors.append("items 必须是数组")
        dispositions = []

    seen: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(dispositions):
        prefix = f"items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        item_id = str(item.get("id", "")).strip()
        if not item_id:
            errors.append(f"{prefix}.id 不能为空")
            continue
        if item_id in seen:
            errors.append(f"审查项重复：{item_id}")
            continue
        seen[item_id] = item
        if item_id not in checklist_items:
            errors.append(f"审查项不在当前 checklist 中：{item_id}")
            continue

        applicability = item.get("applicability")
        result = item.get("result")
        reason = str(item.get("reason", "")).strip()
        finding_ids = item.get("finding_ids", [])
        if not isinstance(finding_ids, list) or not all(isinstance(x, str) and x for x in finding_ids):
            errors.append(f"{item_id}.finding_ids 必须是非空字符串组成的数组")
            finding_ids = []
        if result not in RESULTS:
            errors.append(f"{item_id}.result 非法：{result}")

        if applicability == "not_applicable":
            if result != "not_applicable":
                errors.append(f"{item_id} 标记不适用时 result 必须为 not_applicable")
            if not reason:
                errors.append(f"{item_id} 标记不适用时必须说明原因")
        elif applicability == "applicable":
            if result == "not_applicable":
                errors.append(f"{item_id} 标记适用时不能使用 not_applicable")
            if result == "pass" and not valid_evidence(item.get("evidence")):
                errors.append(f"{item_id} 通过时至少需要一条包含 location 和 summary 的证据")
            if result == "fail" and not finding_ids:
                errors.append(f"{item_id} 失败时必须关联 finding_ids")
            if result in {"pending_check", "pending_supplement"} and not reason:
                errors.append(f"{item_id} 待处理时必须说明原因")
        elif applicability == "pending":
            if result not in {"pending_check", "pending_supplement"}:
                errors.append(f"{item_id} applicability 为 pending 时 result 必须为待检查或待补充")
            if not reason:
                errors.append(f"{item_id} 待判断适用性时必须说明原因")
        else:
            errors.append(f"{item_id}.applicability 必须为 applicable、not_applicable 或 pending")

    missing = sorted(set(checklist_items) - set(seen))
    if missing:
        errors.append("未处置的 checklist 项：" + ", ".join(missing))

    findings = review.get("findings")
    if not isinstance(findings, list):
        errors.append("findings 必须是数组")
        findings = []
    finding_map: dict[str, dict[str, Any]] = {}
    for index, finding in enumerate(findings):
        prefix = f"findings[{index}]"
        if not isinstance(finding, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        finding_id = str(finding.get("id", "")).strip()
        if not finding_id:
            errors.append(f"{prefix}.id 不能为空")
            continue
        if finding_id in finding_map:
            errors.append(f"问题编号重复：{finding_id}")
            continue
        finding_map[finding_id] = finding
        severity = finding.get("severity")
        status = finding.get("status")
        if severity not in severities:
            errors.append(f"{finding_id}.severity 不在当前 priority_rules 中")
        if status not in FINDING_STATUSES:
            errors.append(f"{finding_id}.status 必须为 open/fixed/risk_accepted")
        for field in ("title", "minimum_fix"):
            if not str(finding.get(field, "")).strip():
                errors.append(f"{finding_id}.{field} 不能为空")
        locations = finding.get("locations")
        if not isinstance(locations, list) or not any(str(x).strip() for x in locations):
            errors.append(f"{finding_id}.locations 至少需要一个定位")

        linked_ids = finding.get("checklist_item_ids", [])
        if not isinstance(linked_ids, list) or not all(isinstance(x, str) and x for x in linked_ids):
            errors.append(f"{finding_id}.checklist_item_ids 必须是字符串数组")
            linked_ids = []
        unknown = sorted(set(linked_ids) - set(checklist_items))
        if unknown:
            errors.append(f"{finding_id} 关联未知 checklist 项：{', '.join(unknown)}")
        expected = [checklist_items[x].get("priority") for x in linked_ids if x in checklist_items]
        expected = [x for x in expected if x in severities]
        if severity in severities and expected:
            required_rank = min(severity_rank[x] for x in expected)
            if severity_rank[severity] > required_rank:
                errors.append(f"{finding_id}.severity 低于关联 checklist 项的最低严重度")

        if status == "fixed" and not valid_evidence(finding.get("resolution_evidence")):
            errors.append(f"{finding_id} 标记 fixed 时必须提供 resolution_evidence")
        if status == "risk_accepted":
            if severity not in policy["allowed_acceptance"]:
                allowed = "、".join(sorted(policy["allowed_acceptance"], key=severity_rank.get))
                errors.append(f"{finding_id} 仅 {allowed} 可以风险接受")
            acceptance = finding.get("risk_acceptance")
            required = policy["acceptance_fields"]
            if not isinstance(acceptance, dict) or any(
                not str(acceptance.get(field, "")).strip() for field in required
            ):
                errors.append(f"{finding_id}.risk_acceptance 必须包含 {', '.join(required)}")

    referenced: set[str] = set()
    for item_id, item in seen.items():
        ids = item.get("finding_ids", []) if isinstance(item.get("finding_ids", []), list) else []
        for finding_id in ids:
            referenced.add(finding_id)
            if finding_id not in finding_map:
                errors.append(f"{item_id} 关联的问题不存在：{finding_id}")
        if item.get("result") == "fail":
            active = [
                finding_map[x] for x in ids
                if x in finding_map and finding_map[x].get("status") in {"open", "risk_accepted"}
            ]
            if not active:
                errors.append(f"{item_id} 标记 fail 时必须关联 open 或 risk_accepted 问题")
    for finding_id, finding in finding_map.items():
        if finding.get("status") in {"open", "risk_accepted"} and finding_id not in referenced:
            errors.append(f"活动问题未被审查项引用：{finding_id}")

    sweep = review.get("consistency_sweep")
    if not isinstance(sweep, dict):
        errors.append("consistency_sweep 必须是对象")
        sweep = {}
    sweep_status = sweep.get("status")
    change_types = sweep.get("change_types")
    dimensions = sweep.get("dimensions_checked")
    if sweep_status == "complete":
        if not isinstance(change_types, list) or not change_types:
            errors.append("一致性扫描完成时 change_types 不能为空")
            change_types = []
        unknown_changes = set(change_types) - set(consistency_policy["routes"])
        if unknown_changes:
            errors.append("一致性扫描包含未知 change_types：" + ", ".join(sorted(unknown_changes)))
        if not isinstance(dimensions, list) or not dimensions:
            errors.append("一致性扫描完成时 dimensions_checked 不能为空")
            dimensions = []
        unknown_dimensions = set(dimensions) - consistency_policy["dimensions"]
        if unknown_dimensions:
            errors.append("一致性扫描包含未知维度：" + ", ".join(sorted(unknown_dimensions)))
        required_dimensions = set()
        for change_type in change_types:
            required_dimensions.update(consistency_policy["routes"].get(change_type, set()))
        missing_dimensions = required_dimensions - set(dimensions)
        if missing_dimensions:
            errors.append("一致性扫描缺少本次变更必查维度：" + ", ".join(sorted(missing_dimensions)))
        if not valid_evidence(sweep.get("evidence")):
            errors.append("一致性扫描完成时至少需要一条包含 location 和 summary 的证据")
    elif sweep_status == "not_required":
        if not str(sweep.get("reason", "")).strip():
            errors.append("一致性扫描不需要执行时必须说明原因")
        if not isinstance(change_types, list) or not change_types:
            errors.append("一致性扫描不需要执行时仍须声明 change_types")
        elif set(change_types) - consistency_policy["not_required"]:
            errors.append("not_required 仅允许无内容变化、错别字、格式或布局变更")
        if dimensions not in ([], None):
            errors.append("一致性扫描不需要执行时 dimensions_checked 必须为空")
    else:
        errors.append("consistency_sweep.status 必须为 complete 或 not_required")

    review_dir = review_path.parent
    prd_path = resolve_path(review_dir, str(prd.get("path", ""))) if prd.get("path") else review_dir
    report_path = resolve_path(review_dir, str(report.get("path", ""))) if report.get("path") else review_dir
    errors.extend(require_nonempty_file(prd_path, "PRD"))
    errors.extend(require_nonempty_file(report_path, "审核报告"))
    if prd_path.is_file():
        text = prd_path.read_text(encoding="utf-8")
        if not any(line.lstrip().startswith("#") for line in text.splitlines()):
            errors.append("PRD 至少需要一个 Markdown 标题")
        if any(marker in text for marker in ("<<<<<<<", ">>>>>>>")):
            errors.append("PRD 中存在未解决的合并冲突标记")

    pending = sum(
        1 for item in seen.values()
        if item.get("result") in {"pending_check", "pending_supplement"}
    )
    summary = {
        "total_checklist_items": len(checklist_items),
        "passed_items": sum(1 for item in seen.values() if item.get("result") == "pass"),
        "not_applicable_items": sum(1 for item in seen.values() if item.get("result") == "not_applicable"),
        "failed_items": sum(1 for item in seen.values() if item.get("result") == "fail"),
        "pending_items": pending,
        "pending_check": sum(1 for item in seen.values() if item.get("result") == "pending_check"),
        "pending_supplement": sum(1 for item in seen.values() if item.get("result") == "pending_supplement"),
    }
    for severity in severities:
        key = severity.lower()
        summary[f"open_{key}"] = sum(
            1 for item in finding_map.values()
            if item.get("severity") == severity and item.get("status") == "open"
        )
        summary[f"accepted_{key}"] = sum(
            1 for item in finding_map.values()
            if item.get("severity") == severity and item.get("status") == "risk_accepted"
        )
    conclusion = evaluate_conclusion(summary, policy)

    context = {
        "review": review,
        "checklist": checklist,
        "consistency_rules": consistency_policy["data"],
        "prd_path": prd_path,
        "report_path": report_path,
        "summary": summary,
        "conclusion": conclusion,
    }
    return errors, context, checklist_items


def init_review(args: argparse.Namespace) -> int:
    prd_path = Path(args.prd).resolve()
    checklist_path = Path(args.checklist).resolve()
    review_path = Path(args.out).resolve()
    report_path = Path(args.review_report).resolve()
    errors = require_nonempty_file(prd_path, "PRD")
    if args.writer_ref == args.reviewer_ref:
        errors.append("writer-ref 与 reviewer-ref 不能相同")
    if errors:
        raise GateError("；".join(errors))
    checklist, items = load_checklist(checklist_path)
    review = {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "generated_at": now_text(),
        "review_revision": 1,
        "reviewer": {
            "mode": "independent",
            "writer_ref": args.writer_ref,
            "reviewer_ref": args.reviewer_ref,
        },
        "prd": {
            "path": portable_path(prd_path, review_path.parent),
            "complexity": args.complexity,
        },
        "review_report": {
            "path": portable_path(report_path, review_path.parent),
        },
        "checklist_version": checklist.get("meta", {}).get("version", "unknown"),
        "items": [
            {
                "id": item_id,
                "applicability": "pending",
                "result": "pending_check",
                "evidence": [],
                "reason": "待独立审查",
                "finding_ids": [],
            }
            for item_id in items
        ],
        "findings": [],
        "consistency_sweep": {
            "status": "not_required",
            "change_types": ["no_content_change"],
            "dimensions_checked": [],
            "evidence": [],
            "reason": "尚未发生内容修订",
        },
    }
    write_json(review_path, review, args.force)
    print(f"已生成审查骨架：{review_path}")
    print(f"待处置 checklist 项：{len(items)}")
    return 0


def seal_gate(args: argparse.Namespace) -> int:
    review_path = Path(args.review).resolve()
    checklist_path = Path(args.checklist).resolve()
    consistency_rules_path = Path(args.consistency_rules).resolve()
    gate_path = Path(args.out).resolve()
    errors, context, _ = validate_review(review_path, checklist_path, consistency_rules_path)
    if errors:
        print("内容质量审查契约校验失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    prd_path = context["prd_path"]
    report_path = context["report_path"]
    checklist = context["checklist"]
    current_hashes = {
        "prd": file_hash(prd_path),
        "review": file_hash(review_path),
        "review_report": file_hash(report_path),
        "checklist": file_hash(checklist_path),
        "consistency_rules": file_hash(consistency_rules_path),
    }
    if gate_path.exists() and args.force:
        previous = load_json(gate_path)
        previous_inputs = previous.get("inputs", {})
        previous_prd_hash = previous_inputs.get("prd", {}).get("sha256")
        previous_checklist_hash = previous_inputs.get("checklist", {}).get("sha256")
        previous_review_hash = previous_inputs.get("review", {}).get("sha256")
        previous_revision = previous_inputs.get("review", {}).get("revision", 0)
        source_changed = (
            previous_prd_hash != current_hashes["prd"]
            or previous_checklist_hash != current_hashes["checklist"]
            or previous_inputs.get("consistency_rules", {}).get("sha256") != current_hashes["consistency_rules"]
        )
        if source_changed and (
            previous_review_hash == current_hashes["review"]
            or context["review"].get("review_revision", 0) <= previous_revision
        ):
            raise GateError(
                "PRD 或 checklist 已变化，但审查记录未形成更高 review_revision；"
                "请重新审查受影响内容、更新证据并递增 review_revision"
            )
    gate = {
        "schema_version": GATE_SCHEMA_VERSION,
        "sealed_at": now_text(),
        "inputs": {
            "prd": {"path": portable_path(prd_path, gate_path.parent), "sha256": current_hashes["prd"]},
            "review": {
                "path": portable_path(review_path, gate_path.parent),
                "sha256": current_hashes["review"],
                "revision": context["review"]["review_revision"],
            },
            "review_report": {"path": portable_path(report_path, gate_path.parent), "sha256": current_hashes["review_report"]},
            "checklist": {
                "version": checklist.get("meta", {}).get("version", "unknown"),
                "sha256": current_hashes["checklist"],
            },
            "consistency_rules": {
                "version": context["consistency_rules"].get("meta", {}).get("version", "unknown"),
                "sha256": current_hashes["consistency_rules"],
            },
        },
        "summary": context["summary"],
        "conclusion": context["conclusion"],
    }
    write_json(gate_path, gate, args.force)
    print(f"已生成内容质量门禁凭证：{gate_path}")
    print(json.dumps({"conclusion": gate["conclusion"], **gate["summary"]}, ensure_ascii=False))
    return 0 if gate["conclusion"] == "pass" else 1


def current_task_gate(pointer_path: Path) -> tuple[Path, Path | None, Path | None]:
    pointer = load_json(pointer_path)
    task_folder = Path(str(pointer.get("task_folder", ""))).resolve() if pointer.get("task_folder") else None
    raw_gate = str(pointer.get("content_gate_path", "")).strip()
    if not raw_gate:
        raise GateError("current-task.json 缺少 content_gate_path")
    gate_path = Path(raw_gate)
    if not gate_path.is_absolute():
        if task_folder is None:
            raise GateError("content_gate_path 为相对路径时必须提供 task_folder")
        gate_path = task_folder / gate_path
    raw_checklist = str(pointer.get("checklist_path", "")).strip()
    checklist_path = Path(raw_checklist).resolve() if raw_checklist else None
    raw_consistency = str(pointer.get("consistency_rules_path", "")).strip()
    consistency_path = Path(raw_consistency).resolve() if raw_consistency else None
    return gate_path.resolve(), checklist_path, consistency_path


def validate_gate(args: argparse.Namespace) -> int:
    checklist_path = Path(args.checklist).resolve()
    consistency_rules_path = Path(args.consistency_rules).resolve()
    if args.current_task:
        pointer_path = Path(args.current_task_file).resolve()
        gate_path, pointer_checklist, pointer_consistency = current_task_gate(pointer_path)
        if pointer_checklist is not None:
            checklist_path = pointer_checklist
        if pointer_consistency is not None:
            consistency_rules_path = pointer_consistency
    elif args.gate:
        gate_path = Path(args.gate).resolve()
    else:
        raise GateError("validate 必须提供 --gate 或 --current-task")

    gate = load_json(gate_path)
    errors: list[str] = []
    if gate.get("schema_version") != GATE_SCHEMA_VERSION:
        errors.append(f"门禁凭证 schema_version 必须为 {GATE_SCHEMA_VERSION}")
    inputs = gate.get("inputs")
    if not isinstance(inputs, dict):
        raise GateError("门禁凭证缺少 inputs")

    resolved: dict[str, Path] = {}
    for key in ("prd", "review", "review_report"):
        entry = inputs.get(key)
        if not isinstance(entry, dict) or not entry.get("path") or not entry.get("sha256"):
            errors.append(f"inputs.{key} 必须包含 path 和 sha256")
            continue
        path = resolve_path(gate_path.parent, str(entry["path"]))
        resolved[key] = path
        if not path.is_file():
            errors.append(f"{key} 文件不存在：{path}")
        elif file_hash(path) != entry["sha256"]:
            errors.append(f"{key} 已在门禁封印后发生变化，请重新独立审查并封印")

    checklist_entry = inputs.get("checklist")
    if not isinstance(checklist_entry, dict):
        errors.append("inputs.checklist 必须是对象")
    elif checklist_path.is_file():
        checklist_data, _ = load_checklist(checklist_path)
        if file_hash(checklist_path) != checklist_entry.get("sha256"):
            errors.append("checklist 已在门禁封印后发生变化，请按当前版本重新审查")
        if checklist_data.get("meta", {}).get("version") != checklist_entry.get("version"):
            errors.append("checklist 版本与门禁凭证不一致")
    else:
        errors.append(f"checklist 文件不存在：{checklist_path}")

    consistency_entry = inputs.get("consistency_rules")
    if not isinstance(consistency_entry, dict):
        errors.append("inputs.consistency_rules 必须是对象")
    elif consistency_rules_path.is_file():
        consistency_data = load_json(consistency_rules_path)
        if file_hash(consistency_rules_path) != consistency_entry.get("sha256"):
            errors.append("一致性规则已在门禁封印后发生变化，请重新执行回扫和审查")
        if consistency_data.get("meta", {}).get("version") != consistency_entry.get("version"):
            errors.append("一致性规则版本与门禁凭证不一致")
    else:
        errors.append(f"一致性规则文件不存在：{consistency_rules_path}")

    if "review" in resolved and resolved["review"].is_file() and checklist_path.is_file():
        review_errors, context, _ = validate_review(
            resolved["review"], checklist_path, consistency_rules_path)
        errors.extend(review_errors)
        if gate.get("summary") != context["summary"]:
            errors.append("门禁 summary 与当前审查结果不一致")
        if gate.get("conclusion") != context["conclusion"]:
            errors.append("门禁 conclusion 与当前阻断公式不一致")

    if errors:
        print("内容质量门禁未通过：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    conclusion = gate.get("conclusion")
    print(json.dumps({"gate": str(gate_path), "conclusion": conclusion, **gate.get("summary", {})}, ensure_ascii=False))
    if conclusion != "pass":
        print(f"门禁结论为 {conclusion}，阻断最终输出。", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PRD 内容质量门禁")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="生成覆盖全部 checklist 项的审查骨架")
    init_parser.add_argument("--prd", required=True)
    init_parser.add_argument("--review-report", required=True)
    init_parser.add_argument("--out", required=True)
    init_parser.add_argument("--complexity", required=True, choices=["L1", "L2", "L3", "L4"])
    init_parser.add_argument("--writer-ref", required=True)
    init_parser.add_argument("--reviewer-ref", required=True)
    init_parser.add_argument("--checklist", default=str(DEFAULT_CHECKLIST))
    init_parser.add_argument("--consistency-rules", default=str(DEFAULT_CONSISTENCY_RULES))
    init_parser.add_argument("--force", action="store_true")
    init_parser.set_defaults(handler=init_review)

    seal_parser = subparsers.add_parser("seal", help="校验审查结果并生成哈希门禁凭证")
    seal_parser.add_argument("--review", required=True)
    seal_parser.add_argument("--out", required=True)
    seal_parser.add_argument("--checklist", default=str(DEFAULT_CHECKLIST))
    seal_parser.add_argument("--consistency-rules", default=str(DEFAULT_CONSISTENCY_RULES))
    seal_parser.add_argument("--force", action="store_true")
    seal_parser.set_defaults(handler=seal_gate)

    validate_parser = subparsers.add_parser("validate", help="复验门禁凭证和最终 PRD 快照")
    validate_parser.add_argument("--gate")
    validate_parser.add_argument("--current-task", action="store_true")
    validate_parser.add_argument("--current-task-file", default=str(DEFAULT_CURRENT_TASK))
    validate_parser.add_argument("--checklist", default=str(DEFAULT_CHECKLIST))
    validate_parser.add_argument("--consistency-rules", default=str(DEFAULT_CONSISTENCY_RULES))
    validate_parser.set_defaults(handler=validate_gate)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.handler(args)
    except GateError as exc:
        print(f"内容质量门禁错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
