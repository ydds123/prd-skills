#!/usr/bin/env python3
"""Validate a prd-workflow 09-run-log.md against its canonical schema."""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


FULL_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
LEGACY_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEPARATOR_CELL = re.compile(r"^:?-{3,}:?$")
EMPTY_VALUES = {"", "—", "-"}


def default_schema_path():
    return Path(__file__).resolve().parents[1] / "04_templates" / "run-log.schema.json"


def load_schema(path=None):
    schema_path = Path(path) if path else default_schema_path()
    schema_path = schema_path.resolve()
    return json.loads(schema_path.read_text(encoding="utf-8")), schema_path


def load_workflow_manifest(schema, schema_path):
    manifest_path = Path(schema["workflow_manifest"])
    if not manifest_path.is_absolute():
        manifest_path = schema_path.parents[1] / manifest_path
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def split_row(line):
    value = line.strip().strip("|")
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", value)]


def is_separator(line):
    cells = split_row(line)
    return bool(cells) and all(SEPARATOR_CELL.fullmatch(cell) for cell in cells)


def parse_document(lines):
    headings = []
    tables = []
    heading = ""
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("## "):
            heading = stripped[3:].strip()
            headings.append((heading, index + 1))
        if stripped.startswith("|") and index + 1 < len(lines) and is_separator(lines[index + 1]):
            headers = split_row(lines[index])
            rows = []
            row_index = index + 2
            while row_index < len(lines) and lines[row_index].strip().startswith("|"):
                rows.append((row_index + 1, split_row(lines[row_index])))
                row_index += 1
            tables.append({
                "heading": heading,
                "header_line": index + 1,
                "headers": headers,
                "rows": rows,
            })
            index = row_index
            continue
        index += 1
    return headings, tables


def nonempty(value):
    return value.strip() not in EMPTY_VALUES


def level_code(value, allowed_levels):
    for level in allowed_levels:
        if re.match(rf"^{re.escape(level)}(?:\s|$)", value):
            return level
    return None


def required_level(count, thresholds):
    eligible = [item for item in thresholds if count >= item["min_count"]]
    return max(eligible, key=lambda item: item["min_count"])["level"] if eligible else None


def validate_timestamp(value, line_number, column, allow_legacy_date, errors, legacy_lines):
    if not nonempty(value):
        return
    if FULL_TIMESTAMP.fullmatch(value):
        try:
            datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return
        except ValueError:
            pass
    if allow_legacy_date and LEGACY_DATE.fullmatch(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            legacy_lines.append(line_number)
            return
        except ValueError:
            pass
    errors.append(
        f"line {line_number}: {column} must use YYYY-MM-DD HH:mm:ss, got {value!r}")


def validate(path, allow_legacy_date=False, schema_path=None):
    schema, resolved_schema_path = load_schema(schema_path)
    workflow = load_workflow_manifest(schema, resolved_schema_path)
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    headings, tables = parse_document(lines)
    errors = []
    warnings = []
    legacy_lines = []

    heading_counts = {}
    for heading, _ in headings:
        heading_counts[heading] = heading_counts.get(heading, 0) + 1

    required_sections = {item["heading"]: item for item in schema["required_sections"]}
    optional_sections = {}
    for item in schema.get("optional_sections", []):
        optional_sections[item["heading"]] = item
        for alias in item.get("aliases", []):
            optional_sections[alias] = item

    section_tables = {}
    for table in tables:
        section_tables.setdefault(table["heading"], []).append(table)

    for heading, contract in required_sections.items():
        count = heading_counts.get(heading, 0)
        if count == 0:
            errors.append(f"missing required section: {heading}")
            continue
        if count > 1:
            errors.append(f"required section is duplicated: {heading}")
        matches = section_tables.get(heading, [])
        if len(matches) != 1:
            errors.append(f"section {heading!r} must contain exactly one Markdown table")
            continue
        if matches[0]["headers"] != contract["columns"]:
            errors.append(
                f"line {matches[0]['header_line']}: section {heading!r} headers must be {contract['columns']!r}")

    for heading, tables_in_section in section_tables.items():
        if heading in required_sections:
            continue
        if heading not in optional_sections:
            continue
        contract = optional_sections[heading]
        for table in tables_in_section:
            if table["headers"] != contract["columns"]:
                errors.append(
                    f"line {table['header_line']}: section {heading!r} headers must be {contract['columns']!r}")

    allowed_nodes = set(workflow["node_sequence"])
    allowed_root_causes = set(schema["root_causes"])
    allowed_severities = set(schema["severity_values"])
    allowed_levels = schema["trigger_levels"]
    level_rank = {level: index for index, level in enumerate(allowed_levels)}
    thresholds = schema["trigger_level_thresholds"]
    trigger_ids = set()
    completion_nodes = set()

    for table in tables:
        heading = table["heading"]
        headers = table["headers"]
        for line_number, cells in table["rows"]:
            if len(cells) != len(headers):
                errors.append(
                    f"line {line_number}: table {heading!r} has {len(cells)} cells; expected {len(headers)}")
                continue
            row = dict(zip(headers, cells))

            for column in ("时间", "开始时间", "完成时间"):
                if column in row:
                    validate_timestamp(
                        row[column], line_number, column, allow_legacy_date, errors, legacy_lines)

            if heading == "运行时间线" and nonempty(row.get("节点", "")):
                if row["节点"] not in allowed_nodes:
                    errors.append(f"line {line_number}: unknown node {row['节点']!r}")

            if heading == "用户指正记录" and nonempty(row.get("所在节点", "")):
                if row["所在节点"] not in allowed_nodes:
                    errors.append(f"line {line_number}: unknown node {row['所在节点']!r}")

            if heading == "Node 完成记录" and nonempty(row.get("节点", "")):
                node = row["节点"]
                if node not in allowed_nodes:
                    errors.append(f"line {line_number}: unknown completion node {node!r}")
                elif node in completion_nodes:
                    errors.append(f"line {line_number}: duplicate completion node {node!r}")
                completion_nodes.add(node)

            if heading == "修订记录" and nonempty(row.get("根因分类", "")):
                if row["根因分类"] not in allowed_root_causes:
                    errors.append(f"line {line_number}: unknown root cause {row['根因分类']!r}")

            if heading == "痛点日志" and nonempty(row.get("严重程度", "")):
                if row["严重程度"] not in allowed_severities:
                    errors.append(f"line {line_number}: unknown severity {row['严重程度']!r}")

            if heading == "复盘触发状态" and any(nonempty(value) for value in cells):
                trigger_id = row.get("触发编号", "")
                if not nonempty(trigger_id):
                    errors.append(f"line {line_number}: 触发编号 is required")
                elif trigger_id in trigger_ids:
                    errors.append(f"line {line_number}: duplicate trigger ID {trigger_id!r}")
                else:
                    trigger_ids.add(trigger_id)

                root_cause = row.get("根因分类", "")
                if root_cause not in allowed_root_causes:
                    errors.append(f"line {line_number}: unknown root cause {root_cause!r}")

                try:
                    count = int(row.get("出现次数", ""))
                    if count < 1:
                        raise ValueError
                except ValueError:
                    errors.append(f"line {line_number}: 出现次数 must be a positive integer")
                    continue

                actual_level = level_code(row.get("当前等级", ""), allowed_levels)
                expected_level = required_level(count, thresholds)
                if actual_level is None:
                    errors.append(f"line {line_number}: unknown trigger level {row.get('当前等级', '')!r}")
                elif expected_level and level_rank[actual_level] < level_rank[expected_level]:
                    errors.append(
                        f"line {line_number}: count {count} requires at least {expected_level}, got {actual_level}")

    missing_nodes = [
        node for node in workflow["required_completion_nodes"] if node not in completion_nodes
    ]
    if missing_nodes:
        errors.append(f"Node 完成记录 is missing required nodes: {', '.join(missing_nodes)}")

    if legacy_lines:
        sample = ", ".join(str(line) for line in legacy_lines[:5])
        suffix = "..." if len(legacy_lines) > 5 else ""
        warnings.append(
            f"{len(legacy_lines)} legacy date-only values allowed for migration; lines {sample}{suffix}")
    return errors, warnings, len(tables)


def main():
    parser = argparse.ArgumentParser(description="Validate 09-run-log.md against run-log.schema.json")
    parser.add_argument("run_log", help="Path to 09-run-log.md")
    parser.add_argument("--schema", help="Override the canonical run-log schema path")
    parser.add_argument(
        "--allow-legacy-date",
        action="store_true",
        help="Allow pre-migration YYYY-MM-DD values as warnings; new tasks must not use this flag.",
    )
    args = parser.parse_args()

    path = Path(args.run_log)
    if not path.exists():
        print(f"[ERROR] run log not found: {path}")
        return 1

    try:
        errors, warnings, table_count = validate(path, args.allow_legacy_date, args.schema)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"[ERROR] cannot validate run log: {exc}")
        return 1

    print(f"Run log validation: {path}")
    print(f"Tables: {table_count}  Errors: {len(errors)}  Warnings: {len(warnings)}")
    for warning in warnings:
        print(f"[WARN] {warning}")
    for error in errors:
        print(f"[ERROR] {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
