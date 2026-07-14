#!/usr/bin/env python3
"""Regression tests for canonical table routing and checklist references."""

import copy
import importlib.util
import json
import sys
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT / "04_templates" / "table-templates"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    validator = load_module(
        "validate_json_execution_layer", ROOT / "scripts" / "validate-json-execution-layer.py")
    generator = load_module(
        "generate_table_contract_index", ROOT / "scripts" / "generate-table-contract-index.py")

    index_path = INDEX_DIR / "table-template-index.json"
    index_bytes = index_path.read_bytes()
    index = json.loads(index_bytes)
    errors, _ = validator.check_template_index(index, str(INDEX_DIR))
    if errors:
        raise AssertionError(f"canonical table index failed validation: {errors}")

    generated = generator.render(index, index_bytes)
    actual = (INDEX_DIR / "table-template-index.md").read_text(encoding="utf-8")
    if generated != actual:
        raise AssertionError("generated table contract index is stale")
    if generated == actual + "\nmanual edit":
        raise AssertionError("stale-view negative control did not diverge")

    checklist_path = ROOT / "05_context" / "prd-standards" / "checklist-v3.3.json"
    checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
    invalid_checklist = copy.deepcopy(checklist)
    invalid_checklist["items"][0]["template_ref"] = "missing_contract"
    errors, _ = validator.check_checklist(invalid_checklist, str(checklist_path.parent))
    if not any("unknown table contract" in error for error in errors):
        raise AssertionError(f"unknown checklist contract was not rejected: {errors}")

    removed_paths = [
        ROOT / "05_context" / "writing-standards" / "interaction-logic-writing.md",
        ROOT / "05_context" / "writing-standards" / "table-format-schemas.json",
        ROOT / "scripts" / "build_checklist.py",
        ROOT / "scripts" / "fill_template_refs.py",
    ]
    leftovers = [str(path.relative_to(ROOT)) for path in removed_paths if path.exists()]
    if leftovers:
        raise AssertionError(f"retired duplicate sources still exist: {leftovers}")

    legacy_header = " | ".join(["步骤", "触发起点", "用户动作", "系统响应", "业务规则"])
    hits = []
    for pattern in ("*.md", "*.json"):
        for path in ROOT.rglob(pattern):
            if legacy_header in path.read_text(encoding="utf-8"):
                hits.append(str(path.relative_to(ROOT)))
    if hits:
        raise AssertionError(f"legacy five-column interaction table remains in: {hits}")

    print("PASS: canonical table routing, generated view, checklist refs, and retired-source checks")


if __name__ == "__main__":
    main()
