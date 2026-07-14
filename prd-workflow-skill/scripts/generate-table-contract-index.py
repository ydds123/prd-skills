#!/usr/bin/env python3
"""Generate or verify the human-readable table contract index."""

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "04_templates" / "table-templates" / "table-template-index.json"
OUTPUT = ROOT / "04_templates" / "table-templates" / "table-template-index.md"


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def render(data, source_bytes):
    meta = data["meta"]
    digest = hashlib.sha256(source_bytes).hexdigest()
    lines = [
        "# 表格契约索引",
        "",
        f"> Generated from: `04_templates/table-templates/table-template-index.json`",
        f"> Version: `{meta['version']}`",
        f"> Source SHA256: `{digest}`",
        "> 本文件由脚本生成，请勿直接编辑。固定列以各路由的 `schema_file` 为准。",
        "",
        "## 使用规则",
        "",
    ]
    lines.extend(f"- {rule}" for rule in data.get("agent_rules", []))
    lines.extend([
        "",
        "## 表格契约",
        "",
        "| Contract ID | 匹配关键词 | 模板 | Schema | 适用场景 |",
        "|---|---|---|---|---|",
    ])
    for route in data["template_routes"]:
        lines.append(
            "| {id} | {keywords} | [{template}]({template}) | `{schema}` | {use_case} |".format(
                id=cell(route["id"]),
                keywords=cell("、".join(route["keywords"])),
                template=cell(route["template_file"]),
                schema=cell(route["schema_file"]),
                use_case=cell(route["use_case"]),
            )
        )
    lines.extend([
        "",
        "## 非表格呈现方式",
        "",
        "| ID | 建议形式 | 含义 | 落地方式 |",
        "|---|---|---|---|",
    ])
    for item in data.get("non_template_formats", []):
        lines.append(
            f"| {cell(item['id'])} | {cell(item['suggested_format'])} | "
            f"{cell(item['meaning'])} | {cell(item['rendering'])} |"
        )
    return "\n".join(lines) + "\n"


def load_source():
    source_bytes = SOURCE.read_bytes()
    return json.loads(source_bytes.decode("utf-8")), source_bytes


def main():
    parser = argparse.ArgumentParser(description="Generate or verify the table contract index")
    parser.add_argument("--check", action="store_true", help="Fail when the generated view is stale")
    args = parser.parse_args()

    data, source_bytes = load_source()
    expected = render(data, source_bytes)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            print("table-template-index.md is missing or stale", file=sys.stderr)
            return 1
        print("PASS table contract index is current")
        return 0

    OUTPUT.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Generated {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
