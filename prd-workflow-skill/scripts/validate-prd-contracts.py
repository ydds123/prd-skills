#!/usr/bin/env python3
"""Validate deterministic PRD contracts for ledger-oriented feature sections."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TABLE_INDEX = ROOT / "04_templates" / "table-templates" / "table-template-index.json"
LEDGER_CONTRACT = ROOT / "05_context" / "writing-standards" / "ledger-feature-contract.json"
COMPONENTS = ROOT / "05_context" / "writing-standards" / "component-specifications.json"
HEADING = re.compile(r"^(#{1,6})\s+(\d+(?:\.\d+)*)\s+(.+?)\s*$")
NUMBERED_STEP = re.compile(r"^\s*(\d+)\.\s+\S")
SEPARATOR_CELL = re.compile(r"^:?-{3,}:?$")


@dataclass
class Section:
    level: int
    number: str
    title: str
    start: int
    end: int


@dataclass
class Table:
    line: int
    headers: list[str]
    rows: list[tuple[int, list[str]]]


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON top level must be an object: {path}")
    return data


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def is_separator(line: str) -> bool:
    cells = split_row(line)
    return bool(cells) and all(SEPARATOR_CELL.fullmatch(cell) for cell in cells)


def parse_sections(lines: list[str]) -> list[Section]:
    raw = []
    for index, line in enumerate(lines):
        match = HEADING.match(line.strip())
        if match:
            raw.append((len(match.group(1)), match.group(2), match.group(3), index))
    sections = []
    for index, (level, number, title, start) in enumerate(raw):
        end = len(lines)
        for next_level, _, _, next_start in raw[index + 1:]:
            if next_level <= level:
                end = next_start
                break
        sections.append(Section(level, number, title, start, end))
    return sections


def parse_tables(lines: list[str], start: int, end: int) -> list[Table]:
    tables = []
    index = start
    while index < end - 1:
        if lines[index].strip().startswith("|") and is_separator(lines[index + 1]):
            headers = split_row(lines[index])
            rows = []
            row_index = index + 2
            while row_index < end and lines[row_index].strip().startswith("|"):
                rows.append((row_index + 1, split_row(lines[row_index])))
                row_index += 1
            tables.append(Table(index + 1, headers, rows))
            index = row_index
        else:
            index += 1
    return tables


def direct_child(sections: list[Section], parent: Section, title: str) -> Section | None:
    for section in sections:
        if (
            section.level == parent.level + 1
            and parent.start < section.start < parent.end
            and section.title == title
        ):
            return section
    return None


def direct_children(sections: list[Section], parent: Section) -> list[Section]:
    return [
        section for section in sections
        if section.level == parent.level + 1 and parent.start < section.start < parent.end
    ]


def load_table_contracts() -> dict[str, dict[str, Any]]:
    index = load_json(TABLE_INDEX)
    contracts = {}
    for route in index["template_routes"]:
        schema_path = TABLE_INDEX.parent / route["schema_file"]
        contracts[route["id"]] = load_json(schema_path)
    return contracts


def terms_satisfied(text: str, requirement: dict[str, Any]) -> bool:
    all_terms = requirement.get("all_terms", [])
    any_terms = requirement.get("any_terms", [])
    return all(term in text for term in all_terms) and (
        not any_terms or any(term in text for term in any_terms)
    )


def find_contract_table(
    lines: list[str], section: Section, contract: dict[str, Any], errors: list[str]
) -> Table | None:
    expected = [column["name"] for column in contract["columns"]]
    tables = parse_tables(lines, section.start + 1, section.end)
    matches = [table for table in tables if table.headers == expected]
    if len(matches) != 1:
        actual = [table.headers for table in tables]
        errors.append(
            f"{section.number} {section.title}: expected exactly one table with headers {expected}, got {actual}")
        return None
    table = matches[0]
    allowed_by_column = {
        column["name"]: set(column.get("allowed_values", []))
        for column in contract["columns"]
    }
    required = {
        column["name"] for column in contract["columns"] if column.get("required")
    }
    for line_number, cells in table.rows:
        if len(cells) != len(table.headers):
            errors.append(
                f"line {line_number}: table has {len(cells)} cells; expected {len(table.headers)}")
            continue
        if not any(cells):
            continue
        row = dict(zip(table.headers, cells))
        for column in required:
            if not row[column] or row[column] in {"—", "-"}:
                errors.append(f"line {line_number}: required column {column!r} is empty")
        for column, allowed in allowed_by_column.items():
            if allowed and row[column] not in allowed:
                errors.append(
                    f"line {line_number}: {column!r} value {row[column]!r} is outside {sorted(allowed)!r}")
    return table


def validate_form_components(
    lines: list[str], section: Section, table: Table, registry: dict[str, Any], errors: list[str]
) -> None:
    by_type = {}
    for component in registry["components"]:
        for component_type in component["prd_component_types"]:
            by_type[component_type] = component
    section_text = "\n".join(lines[section.start:section.end])
    for line_number, cells in table.rows:
        if len(cells) != len(table.headers) or not any(cells):
            continue
        row = dict(zip(table.headers, cells))
        component_type = row.get("组件类型", "")
        component = by_type.get(component_type)
        if not component:
            errors.append(f"line {line_number}: unknown component type {component_type!r}")
            continue
        for requirement in component.get("prd_evidence_requirements", []):
            if requirement["scope"] == "section":
                evidence_text = section_text
            else:
                evidence_text = " ".join(row.get(column, "") for column in requirement["columns"])
            if not terms_satisfied(evidence_text, requirement):
                errors.append(
                    f"line {line_number}: field {row.get('字段', '')!r} using {component_type!r} "
                    f"lacks evidence {requirement['id']!r}")


def detect_atomicity(text: str) -> str | None:
    compact = re.sub(r"\s+", "", text)
    file_patterns = [
        r"任一(?:数据)?行.*?(?:失败|错误).*?(?:整批|全部|本次文件).*?(?:不导入|不写入)",
        r"所有(?:数据)?行.*?校验通过.*?(?:才|后).*?(?:导入|写入)",
    ]
    has_file = any(re.search(pattern, compact) for pattern in file_patterns)
    row_patterns = [
        r"按行进行原子处理",
        r"其他(?:完全)?正确(?:的)?行(?:可)?继续导入",
        r"正确行(?:正常)?导入.{0,30}失败行(?:不写入|不导入)",
    ]
    has_row = any(re.search(pattern, compact) for pattern in row_patterns)
    if has_file and has_row:
        return "conflict"
    if has_file:
        return "file"
    if has_row:
        return "row"
    if "按字段" in compact:
        return "field"
    return None


def detect_carriers(text: str) -> set[str]:
    carriers = set()
    if "导入预览" in text:
        carriers.add("preview")
    if "页面结果" in text or "页面提示" in text:
        carriers.add("page")
    if "失败文件" in text or "失败明细文件" in text:
        carriers.add("failure_file")
    return carriers


def validate_batch_import(
    lines: list[str], operation: Section, contract: dict[str, Any], expectation: dict[str, Any], errors: list[str]
) -> None:
    text = "\n".join(lines[operation.start:operation.end])
    batch = contract["batch_import"]
    for requirement in batch["required_evidence"]:
        if not terms_satisfied(text, requirement):
            errors.append(f"{operation.number} 批量导入: missing evidence {requirement['id']!r}")
    feedback = batch["feedback_evidence"]
    if not all(term in text for term in feedback["all_terms"]):
        errors.append("批量导入反馈必须定位行号、字段和原因")
    if not any(term in text for term in feedback["action_terms"]):
        errors.append("批量导入反馈必须给出可执行的下一步")

    actual_atomicity = detect_atomicity(text)
    expected_atomicity = expectation.get("atomicity")
    if actual_atomicity is None:
        errors.append(f"{operation.number} 批量导入: write atomicity is not explicit")
    elif expected_atomicity and actual_atomicity != expected_atomicity:
        errors.append(
            f"{operation.number} 批量导入: atomicity is {actual_atomicity}, expected {expected_atomicity}")
    carriers = detect_carriers(text)
    expected_carrier = expectation.get("failure_carrier")
    if not carriers:
        errors.append(f"{operation.number} 批量导入: failure carrier is not explicit")
    elif expected_carrier and expected_carrier not in carriers:
        errors.append(
            f"{operation.number} 批量导入: carriers are {sorted(carriers)}, expected {expected_carrier}")


def validate_operation_flows(
    lines: list[str], sections: list[Section], operation_section: Section,
    ledger: dict[str, Any], contracts: dict[str, dict[str, Any]],
    expectation: dict[str, Any], errors: list[str]
) -> None:
    operations = direct_children(sections, operation_section)
    canonical = ledger["canonical_operation_order"]
    names = [operation.title for operation in operations]
    unknown = [name for name in names if name not in canonical]
    if unknown:
        errors.append(f"{operation_section.number}: unknown ledger operations {unknown}")
    indexes = [canonical.index(name) for name in names if name in canonical]
    if indexes != sorted(indexes):
        errors.append(f"{operation_section.number}: operation order {names} violates canonical order {canonical}")

    flow = ledger["operation_flow"]
    branch_headers = [
        column["name"] for column in contracts[flow["branch_contract"]]["columns"]
    ]
    decision_headers = [
        column["name"] for column in contracts[flow["decision_contract"]]["columns"]
    ]
    legacy_headers = ["步骤", "触发起点", "用户动作", "系统响应", "业务规则"]
    for operation in operations:
        text = "\n".join(lines[operation.start:operation.end])
        if flow["main_path_heading"] not in text:
            errors.append(f"{operation.number} {operation.title}: missing main path heading")
        steps = [
            int(match.group(1)) for line in lines[operation.start:operation.end]
            if (match := NUMBERED_STEP.match(line))
        ]
        if not steps:
            errors.append(f"{operation.number} {operation.title}: numbered main path is missing")
        elif steps != list(range(1, len(steps) + 1)):
            errors.append(f"{operation.number} {operation.title}: main path numbering is not continuous: {steps}")
        for table in parse_tables(lines, operation.start + 1, operation.end):
            if table.headers == legacy_headers:
                errors.append(f"line {table.line}: legacy five-column interaction table is forbidden")
            if table.headers[:1] == ["分支与异常"] and table.headers != branch_headers:
                errors.append(f"line {table.line}: branch table headers must be {branch_headers}")
            if table.headers[:1] == ["关键决策点"] and table.headers != decision_headers:
                errors.append(f"line {table.line}: decision table headers must be {decision_headers}")
        if operation.title == "批量导入":
            validate_batch_import(
                lines, operation, ledger, expectation.get("batch_import", {}), errors)


def validate_module(
    lines: list[str], sections: list[Section], module: Section,
    ledger: dict[str, Any], contracts: dict[str, dict[str, Any]],
    components: dict[str, Any], expectation: dict[str, Any]
) -> list[str]:
    errors = []
    found = {}
    for required in ledger["required_sections"]:
        section = direct_child(sections, module, required["suffix"])
        if not section:
            errors.append(f"{module.number}: missing section {required['suffix']!r}")
            continue
        found[required["suffix"]] = section
        contract_id = required.get("table_contract")
        if contract_id:
            table = find_contract_table(lines, section, contracts[contract_id], errors)
            if table and contract_id == "form_modal_field_table":
                validate_form_components(lines, section, table, components, errors)

    operation_section = found.get("操作流程")
    if operation_section:
        validate_operation_flows(
            lines, sections, operation_section, ledger, contracts, expectation, errors)
    return errors


def validate_prd(path: Path, section_numbers: list[str], expectations_path: Path | None = None):
    lines = path.read_text(encoding="utf-8").splitlines()
    sections = parse_sections(lines)
    ledger = load_json(LEDGER_CONTRACT)
    contracts = load_table_contracts()
    components = load_json(COMPONENTS)
    expectations = load_json(expectations_path) if expectations_path else {"modules": {}}
    module_expectations = expectations.get("modules", {})

    if not section_numbers:
        section_numbers = list(module_expectations)
    if not section_numbers:
        required_titles = {item["suffix"] for item in ledger["required_sections"]}
        for section in sections:
            child_titles = {child.title for child in direct_children(sections, section)}
            if required_titles.issubset(child_titles):
                section_numbers.append(section.number)

    results = {}
    all_errors = []
    for number in section_numbers:
        module = next((section for section in sections if section.number == number), None)
        if not module:
            errors = [f"module section {number} not found"]
        else:
            errors = validate_module(
                lines, sections, module, ledger, contracts, components,
                module_expectations.get(number, {}),
            )
        results[number] = errors
        all_errors.extend(f"{number}: {error}" for error in errors)
    return results, all_errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate deterministic ledger PRD contracts")
    parser.add_argument("prd", help="Path to the PRD Markdown file")
    parser.add_argument("--sections", help="Comma-separated module section numbers, for example 8.2,8.3")
    parser.add_argument("--expectations", help="Optional module-specific expectation JSON")
    args = parser.parse_args()

    path = Path(args.prd).resolve()
    if not path.is_file():
        print(f"[ERROR] PRD not found: {path}")
        return 1
    sections = [item.strip() for item in (args.sections or "").split(",") if item.strip()]
    expectations = Path(args.expectations).resolve() if args.expectations else None
    try:
        results, errors = validate_prd(path, sections, expectations)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"[ERROR] cannot validate PRD contracts: {exc}")
        return 1

    print(f"PRD contract validation: {path}")
    for number, module_errors in results.items():
        status = "PASS" if not module_errors else "FAIL"
        print(f"[{status}] {number}: {len(module_errors)} issue(s)")
    for error in errors:
        print(f"[ERROR] {error}")
    print(f"Summary: modules={len(results)} errors={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
