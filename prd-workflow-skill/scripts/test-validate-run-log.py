#!/usr/bin/env python3
"""Regression tests for validate-run-log.py."""

import importlib.util
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "validate_run_log", SCRIPT_DIR / "validate-run-log.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


VALID_RUN_LOG = """# Run Log

## 运行时间线

| 时间 | 节点 | 动作 | 发现 / 决策 |
|---|---|---|---|
| 2026-07-14 13:50:34 | Node 1 | 开始需求对齐 | — |

## 修订记录

| 轮次 | 时间 | 触发 | 修改范围 | 根因分类 | checklist 模块 | 关联决策编号 |
|---|---|---|---|---|---|---|
| 1 | 2026-07-14 14:00:00 | 用户指正 | 操作流程 | 缺模板 | ledger_feature | D-001 |

## 痛点日志

| 发现时机 | 痛点 | 初版为什么漏了 | 涉及 checklist 模块 | 严重程度 |
|---|---|---|---|---|
| Node 4.5 | 流程结构不统一 | 缺少唯一契约 | ledger_feature | P0 |

## Node 完成记录

| 节点 | 开始时间 | 完成时间 | checklist 模块加载 | 阻断遗漏数 | 备注 |
|---|---|---|---|---|---|
| Node 1 | 2026-07-14 13:50:34 | 2026-07-14 13:55:00 | — | 0 | — |
| Node 2 | 2026-07-14 13:55:01 | 2026-07-14 14:00:00 | — | 0 | — |
| Node 3 | 2026-07-14 14:00:01 | 2026-07-14 14:05:00 | ledger_feature | 0 | — |
| Node 4 | 2026-07-14 14:05:01 | 2026-07-14 14:10:00 | ledger_feature | 0 | — |
| Node 4.5 | 2026-07-14 14:10:01 | 2026-07-14 14:15:00 | quality_gate | 0 | — |
| Node 5 | 2026-07-14 14:15:01 | 2026-07-14 14:20:00 | — | 0 | — |

## 用户指正记录

| 时间 | 所在节点 | 用户原话（摘要） | 指正类型 | 涉及内容 | AI 判断 | 关联决策编号 | 是否进入复盘候选 |
|---|---|---|---|---|---|---|---|
| 2026-07-14 14:00:00 | Node 3 | 流程结构需要统一 | 结构错误 | 操作流程 | 暴露 Skill 缺陷 | D-001 | 是 |

## 复盘触发状态

| 触发编号 | 根因分类 | 出现次数 | 最近证据 | 当前等级 | 建议动作 |
|---|---|---|---|---|---|
| TR-001 | 缺模板 | 2 | D-001 | T2 复盘候选 | Node 5 发起复盘 |
"""


def run_case(name, content, expected_error=None, allow_legacy_date=False, expected_warning=None):
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "09-run-log.md"
        path.write_text(content, encoding="utf-8")
        errors, warnings, _ = VALIDATOR.validate(path, allow_legacy_date)
    if expected_error is None and errors:
        raise AssertionError(f"{name}: expected pass, got errors: {errors}")
    if expected_error and not any(expected_error in error for error in errors):
        raise AssertionError(f"{name}: missing expected error {expected_error!r}; got {errors}")
    if expected_warning and not any(expected_warning in warning for warning in warnings):
        raise AssertionError(f"{name}: missing expected warning {expected_warning!r}; got {warnings}")


def main():
    run_case("valid", VALID_RUN_LOG)
    run_case(
        "arbitrary table is not a run log",
        "# arbitrary\n\n| A | B |\n|---|---|\n| 1 | 2 |\n",
        "missing required section: 运行时间线",
    )
    run_case(
        "missing Node 4.5",
        VALID_RUN_LOG.replace(
            "| Node 4.5 | 2026-07-14 14:10:01 | 2026-07-14 14:15:00 | quality_gate | 0 | — |\n",
            "",
        ),
        "Node 完成记录 is missing required nodes: Node 4.5",
    )
    run_case(
        "minute timestamp",
        VALID_RUN_LOG.replace("2026-07-14 13:50:34", "2026-07-14 13:50", 1),
        "must use YYYY-MM-DD HH:mm:ss",
    )
    run_case(
        "illegal root cause",
        VALID_RUN_LOG.replace("| 缺模板 | 2 |", "| 临时问题 | 2 |"),
        "unknown root cause '临时问题'",
    )
    run_case(
        "illegal severity",
        VALID_RUN_LOG.replace("| ledger_feature | P0 |", "| ledger_feature | 紧急 |"),
        "unknown severity '紧急'",
    )
    run_case(
        "duplicate trigger id",
        VALID_RUN_LOG.replace(
            "| TR-001 | 缺模板 | 2 | D-001 | T2 复盘候选 | Node 5 发起复盘 |",
            "| TR-001 | 缺模板 | 2 | D-001 | T2 复盘候选 | Node 5 发起复盘 |\n"
            "| TR-001 | 缺方法 | 1 | D-002 | T1 观察中 | 继续观察 |",
        ),
        "duplicate trigger ID 'TR-001'",
    )
    run_case(
        "legacy date migration",
        VALID_RUN_LOG.replace("2026-07-14 13:50:34", "2026-07-14", 1),
        allow_legacy_date=True,
        expected_warning="legacy date-only values allowed for migration",
    )
    print("PASS: 8 run-log validation cases")


if __name__ == "__main__":
    main()
