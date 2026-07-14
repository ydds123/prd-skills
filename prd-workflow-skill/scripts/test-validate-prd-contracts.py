#!/usr/bin/env python3
"""Regression tests for deterministic validation of real ledger PRD output."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "occupational-health-ledger-valid.md"
EXPECTATIONS = ROOT / "tests" / "fixtures" / "occupational-health-ledger.expectations.json"


def load_validator():
    path = ROOT / "scripts" / "validate-prd-contracts.py"
    spec = importlib.util.spec_from_file_location("validate_prd_contracts", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_text(validator, directory: Path, name: str, text: str) -> list[str]:
    path = directory / name
    path.write_text(text, encoding="utf-8")
    _, errors = validator.validate_prd(path, ["8.2", "8.3"], EXPECTATIONS)
    return errors


def assert_rejected(errors: list[str], expected: str, case: str) -> None:
    if not any(expected in error for error in errors):
        raise AssertionError(f"{case} was not rejected as expected: {errors}")


def replace_once(text: str, old: str, new: str, case: str) -> str:
    if old not in text:
        raise AssertionError(f"{case} fixture anchor was not found: {old!r}")
    return text.replace(old, new, 1)


def main() -> None:
    validator = load_validator()
    valid = FIXTURE.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="prd-contracts-") as temp:
        directory = Path(temp)

        errors = validate_text(validator, directory, "valid.md", valid)
        if errors:
            raise AssertionError(f"real 8.2/8.3 fixture must pass: {errors}")

        bad_headers = replace_once(
            valid,
            "| 字段 | 数据来源 | 展示规则 | 空值规则 |",
            "| 字段 | 展示内容 |",
            "list header",
        )
        assert_rejected(
            validate_text(validator, directory, "bad-headers.md", bad_headers),
            "expected exactly one table with headers",
            "list header",
        )

        bad_component = replace_once(
            valid,
            "| 部门/车间 | 下拉单选 | 是 | 请选择部门/车间 |",
            "| 部门/车间 | 自由文本 | 是 | 请选择部门/车间 |",
            "unknown component",
        )
        assert_rejected(
            validate_text(validator, directory, "bad-component.md", bad_component),
            "unknown component type",
            "unknown component",
        )

        missing_evidence = replace_once(
            valid,
            "只能选择一个下拉选项，不接受自定义文本；必填，不支持清空后保存",
            "必填",
            "component evidence",
        )
        assert_rejected(
            validate_text(validator, directory, "missing-evidence.md", missing_evidence),
            "lacks evidence",
            "component evidence",
        )

        bad_order = replace_once(
            valid,
            "##### 8.2.6.2 批量导入",
            "##### 8.2.6.2 查询/查看",
            "operation order first heading",
        )
        bad_order = replace_once(
            bad_order,
            "##### 8.2.6.3 查询/查看",
            "##### 8.2.6.3 批量导入",
            "operation order second heading",
        )
        assert_rejected(
            validate_text(validator, directory, "bad-order.md", bad_order),
            "violates canonical order",
            "operation order",
        )

        file_atomic = (
            "导入按文件进行原子处理：HSE 先校验文件内全部数据，只有所有数据行均校验通过时才允许确认导入并一次性写入。"
            "任一数据行校验失败时，本次文件整批不导入、零行写入；HSE 在导入预览中保留全部错误行、失败字段、失败原因和修改动作，"
            "安环部修正原文件后重新上传。"
        )
        row_atomic = (
            "导入按行进行原子处理：校验通过的行正常导入，失败行不写入；HSE 在导入预览中展示失败字段、失败原因和修改动作，"
            "安环部修正原文件后重新上传。"
        )
        bad_atomicity = valid.replace(file_atomic, row_atomic)
        if bad_atomicity == valid:
            raise AssertionError("atomicity fixture anchor was not found")
        assert_rejected(
            validate_text(validator, directory, "bad-atomicity.md", bad_atomicity),
            "atomicity is conflict, expected file",
            "batch import atomicity",
        )

    print("PASS: real 8.2/8.3 PRD fixture and five negative contract cases")


if __name__ == "__main__":
    main()
