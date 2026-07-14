#!/usr/bin/env python3
"""Validate the canonical component specification JSON and render its Markdown view."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "05_context" / "writing-standards" / "component-specifications.json"
DEFAULT_OUTPUT = ROOT / "05_context" / "writing-standards" / "component-specifications.md"
REQUIRED_COMPONENT_FIELDS = {
    "id", "name", "category", "prd_component_types", "applies_to", "default_behavior", "must_specify",
    "semantic_profiles", "content_rule_template", "validation_message_template", "invalid_examples",
}


def load_and_validate(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if not isinstance(data, dict):
        raise ValueError("组件规范顶层必须是对象")
    meta = data.get("meta", {})
    for key in ("version", "purpose", "generated_view"):
        if not str(meta.get(key, "")).strip():
            errors.append(f"meta.{key} 不能为空")

    profiles = data.get("field_semantic_profiles")
    if not isinstance(profiles, list) or not profiles:
        errors.append("field_semantic_profiles 必须是非空数组")
        profiles = []
    profile_ids: set[str] = set()
    for index, profile in enumerate(profiles):
        pid = str(profile.get("id", "")).strip() if isinstance(profile, dict) else ""
        if not pid:
            errors.append(f"field_semantic_profiles[{index}].id 不能为空")
            continue
        if pid in profile_ids:
            errors.append(f"字段语义编号重复：{pid}")
        profile_ids.add(pid)
        if not isinstance(profile.get("min"), int) or not isinstance(profile.get("max"), int):
            errors.append(f"{pid} 的 min/max 必须是整数")
        elif profile["max"] < profile["min"]:
            errors.append(f"{pid} 的 max 不能小于 min")

    components = data.get("components")
    if not isinstance(components, list) or len(components) < 10:
        errors.append("components 至少包含10类常用组件")
        components = []
    component_ids: set[str] = set()
    for index, component in enumerate(components):
        if not isinstance(component, dict):
            errors.append(f"components[{index}] 必须是对象")
            continue
        missing = sorted(REQUIRED_COMPONENT_FIELDS - set(component))
        if missing:
            errors.append(f"components[{index}] 缺少字段：{', '.join(missing)}")
        cid = str(component.get("id", "")).strip()
        if not cid:
            errors.append(f"components[{index}].id 不能为空")
        elif cid in component_ids:
            errors.append(f"组件编号重复：{cid}")
        component_ids.add(cid)
        for key in ("prd_component_types", "applies_to", "default_behavior", "must_specify", "semantic_profiles", "invalid_examples"):
            if not isinstance(component.get(key), list):
                errors.append(f"{cid or index}.{key} 必须是数组")
        unknown = sorted(set(component.get("semantic_profiles", [])) - profile_ids)
        if unknown:
            errors.append(f"{cid} 引用未知字段语义：{', '.join(unknown)}")
        for key in ("content_rule_template", "validation_message_template"):
            if not str(component.get(key, "")).strip():
                errors.append(f"{cid}.{key} 不能为空")

    required_ids = {
        "single_line_text", "multi_line_text", "numeric_input", "dropdown_single", "dropdown_multi",
        "radio_group", "checkbox_group", "date_time_picker", "switch", "file_upload",
    }
    missing_ids = sorted(required_ids - component_ids)
    if missing_ids:
        errors.append("缺少首期组件：" + ", ".join(missing_ids))
    if errors:
        raise ValueError("\n".join(errors))
    return data


def cell(value: Any) -> str:
    if isinstance(value, list):
        value = "；".join(str(item) for item in value)
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def render(data: dict[str, Any], source_bytes: bytes) -> str:
    digest = hashlib.sha256(source_bytes).hexdigest()
    meta = data["meta"]
    lines = [
        "# 集中组件规范",
        "",
        "> 本文件由 `component-specifications.json` 自动生成，请勿手工编辑。",
        f"> 规范版本：{meta['version']}",
        f"> 源文件 SHA-256：`{digest}`",
        "",
        "## 使用原则",
        "",
    ]
    lines.extend(f"- {item}" for item in data["principles"])
    lines.extend(["", "## 覆盖优先级", ""])
    lines.extend(f"{index}. {item}" for index, item in enumerate(data["override_priority"], start=1))
    lines.extend(["", "## 公共输入规则", "", "| 编号 | 规则 |", "|---|---|"])
    lines.extend(f"| {cell(item['id'])} | {cell(item['rule'])} |" for item in data["shared_input_rules"])
    lines.extend(["", "## 字段语义默认值", "", "| 编号 | 字段语义 | 默认长度 | 示例 | 例外 |", "|---|---|---:|---|---|"])
    for item in data["field_semantic_profiles"]:
        length = f"{item['min']}～{item['max']}{item['unit']}"
        lines.append(f"| {cell(item['id'])} | {cell(item['name'])} | {cell(length)} | {cell(item['examples'])} | {cell(item['fallback'])} |")
    lines.extend(["", "## 组件规范", ""])
    for component in data["components"]:
        lines.extend([
            f"### {component['name']}（`{component['id']}`）",
            "",
            f"- **分类：** {component['category']}",
            f"- **PRD组件名称：** {cell(component['prd_component_types'])}",
            f"- **适用场景：** {cell(component['applies_to'])}",
            f"- **可用字段语义：** {cell(component['semantic_profiles']) if component['semantic_profiles'] else '不适用'}",
            "",
            "**默认行为**",
            "",
        ])
        lines.extend(f"- {item}" for item in component["default_behavior"])
        lines.extend([
            "",
            f"**必须明确：** {cell(component['must_specify'])}",
            "",
            f"**表单内容规则模板：** {component['content_rule_template']}",
            "",
            f"**校验提示模板：** {component['validation_message_template']}",
            "",
            f"**不合法示例：** {cell(component['invalid_examples'])}",
            "",
        ])
    for title, key in (("列表展示默认规则", "list_display_defaults"), ("操作默认规则", "action_defaults")):
        lines.extend([f"## {title}", "", "| 编号 | 规则 |", "|---|---|"])
        lines.extend(f"| {cell(item['id'])} | {cell(item['rule'])} |" for item in data[key])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="生成或校验集中组件规范 Markdown")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--check", action="store_true", help="只检查生成结果是否与源文件一致")
    args = parser.parse_args()
    source = Path(args.source).resolve()
    output = Path(args.out).resolve()
    try:
        source_bytes = source.read_bytes()
        data = load_and_validate(source)
        expected = render(data, source_bytes)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"组件规范校验失败：{exc}", file=sys.stderr)
        return 1
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != expected:
            print("组件规范 Markdown 缺失或已过期，请重新生成。", file=sys.stderr)
            return 1
        print(json.dumps({"source": str(source), "output": str(output), "status": "pass"}, ensure_ascii=False))
        return 0
    output.write_text(expected, encoding="utf-8", newline="\n")
    print(f"已生成组件规范：{output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
