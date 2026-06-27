#!/usr/bin/env python3
"""
Validate prd-workflow-skill JSON execution layer.

Checks:
  - All .json files parse correctly
  - Execution layer JSONs have meta.version, meta.source, meta.purpose
  - meta.source paths resolve to real Markdown files
  - Specialized structural checks for template-index, conventions, trigger-rules

Usage:
  python3 prd-workflow-skill/scripts/validate-json-execution-layer.py
"""

import json, os, sys, re
from collections import defaultdict

# ── helpers ──────────────────────────────────────────────

def red(s):   return s  # keep output plain; caller can pipe to color
def green(s): return s
def yellow(s): return s

def find_skill_root():
    """Locate the prd-workflow-skill/ root from cwd or script dir."""
    for start in [os.getcwd(), os.path.dirname(os.path.abspath(__file__))]:
        p = start
        for _ in range(6):
            if os.path.isdir(os.path.join(p, "04_templates")) and \
               os.path.isfile(os.path.join(p, "SKILL.md")):
                return p
            parent = os.path.dirname(p)
            if parent == p:
                break
            p = parent
    return None

def resolve_source_path(meta_source, json_dir, skill_root):
    """Resolve meta.source to an absolute path, or return None."""
    if not meta_source:
        return None
    candidates = []
    # 1. Relative from skill root
    candidates.append(os.path.join(skill_root, meta_source))
    # 2. Relative from JSON's own directory
    candidates.append(os.path.join(json_dir, meta_source))
    # 3. If it starts with prd-workflow-skill/, strip and retry
    if meta_source.startswith("prd-workflow-skill/"):
        candidates.append(os.path.join(skill_root, meta_source[len("prd-workflow-skill/"):]))
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None

# ── generic checks ───────────────────────────────────────

def check_generic(path, data, skill_root, is_execution_layer):
    errors, warnings = [], []
    json_dir = os.path.dirname(path)

    # Top-level must be object
    if not isinstance(data, dict):
        errors.append("top-level is not an object (dict)")
        return errors, warnings

    meta = data.get("meta", {})

    # meta.version
    if not meta.get("version"):
        if is_execution_layer:
            errors.append("meta.version is missing or empty")
        else:
            warnings.append("meta.version is missing")
    # meta.source
    if not meta.get("source"):
        if is_execution_layer:
            errors.append("meta.source is missing or empty")
        else:
            warnings.append("meta.source is missing")
    else:
        resolved = resolve_source_path(meta["source"], json_dir, skill_root)
        if resolved:
            if not resolved.endswith(".md"):
                warnings.append(f"meta.source '{meta['source']}' does not point to a .md file")
        else:
            if is_execution_layer:
                errors.append(f"meta.source '{meta['source']}' cannot be resolved to an existing file")
            else:
                warnings.append(f"meta.source '{meta['source']}' cannot be resolved")
    # meta.purpose
    if not meta.get("purpose"):
        if is_execution_layer:
            errors.append("meta.purpose is missing or empty")
        else:
            warnings.append("meta.purpose is missing; allowed for non-execution-layer JSON in this pass")

    return errors, warnings

# ── specialized checks ───────────────────────────────────

def check_template_index(data, json_dir):
    errors, warnings = [], []
    routes = data.get("template_routes")
    if not isinstance(routes, list) or not routes:
        errors.append("template_routes must be a non-empty list")
        return errors, warnings

    seen_ids = set()
    for i, r in enumerate(routes):
        prefix = f"template_routes[{i}]"
        if not isinstance(r, dict):
            errors.append(f"{prefix} is not an object"); continue
        rid = r.get("id")
        if not rid:
            errors.append(f"{prefix}.id is missing")
        elif rid in seen_ids:
            errors.append(f"{prefix}.id '{rid}' is duplicated")
        else:
            seen_ids.add(rid)
        kw = r.get("keywords", [])
        if not isinstance(kw, list) or not kw:
            errors.append(f"{prefix}.keywords is missing or empty")
        tf = r.get("template_file", "")
        if not tf:
            errors.append(f"{prefix}.template_file is missing")
        else:
            tf_path = os.path.join(json_dir, tf)
            if not os.path.isfile(tf_path):
                errors.append(f"{prefix}.template_file '{tf}' does not exist at {tf_path}")

    ntf = data.get("non_template_formats")
    if ntf is not None:
        if not isinstance(ntf, list):
            warnings.append("non_template_formats is not a list")
        else:
            ntf_ids = set()
            for i, n in enumerate(ntf):
                if isinstance(n, dict) and n.get("id"):
                    if n["id"] in ntf_ids:
                        warnings.append(f"non_template_formats[{i}].id '{n['id']}' is duplicated")
                    ntf_ids.add(n["id"])

    ar = data.get("agent_rules")
    if ar is not None and not isinstance(ar, list):
        warnings.append("agent_rules is not a list")

    return errors, warnings

def check_conventions(data, json_dir):
    errors, warnings = [], []
    for key in ["field_length_defaults", "input_handling_defaults", "selection_control_defaults",
                 "list_display_defaults", "action_defaults"]:
        val = data.get(key)
        if not isinstance(val, list):
            errors.append(f"{key} is missing or not a list")
    fld = data.get("field_length_defaults", [])
    if isinstance(fld, list):
        seen = set()
        for i, f in enumerate(fld):
            if not isinstance(f, dict): continue
            fid = f.get("id", f"<index-{i}>")
            if fid in seen:
                errors.append(f"field_length_defaults[{i}].id '{fid}' is duplicated")
            seen.add(fid)
            mn, mx = f.get("min"), f.get("max")
            if isinstance(mn, (int, float)) and isinstance(mx, (int, float)) and mx < mn:
                errors.append(f"field_length_defaults[{i}] max({mx}) < min({mn})")
    ov = data.get("override_rule")
    if not isinstance(ov, dict):
        errors.append("override_rule is missing or not an object")
    return errors, warnings

def check_trigger_rules(data, json_dir):
    errors, warnings = [], []
    sigs = data.get("trigger_signals", [])
    if not isinstance(sigs, list) or not sigs:
        errors.append("trigger_signals is missing or empty")
    else:
        seen = set()
        for i, s in enumerate(sigs):
            if isinstance(s, dict):
                sid = s.get("id", f"<index-{i}>")
                if sid in seen:
                    errors.append(f"trigger_signals[{i}].id '{sid}' is duplicated")
                seen.add(sid)

    esc = data.get("escalation_levels", [])
    if isinstance(esc, list):
        found = {e["level"] for e in esc if isinstance(e, dict)}
        for req in ["T0","T1","T2","T3"]:
            if req not in found:
                errors.append(f"escalation_levels must include '{req}'")

    rcs = data.get("root_causes", [])
    if not isinstance(rcs, list) or not rcs:
        errors.append("root_causes is missing or empty")
    else:
        seen = set()
        for i, r in enumerate(rcs):
            if isinstance(r, dict):
                rid = r.get("id", f"<index-{i}>")
                if rid in seen:
                    errors.append(f"root_causes[{i}].id '{rid}' is duplicated")
                seen.add(rid)

    hcb = data.get("human_confirm_boundary", {})
    for key in ["auto_allowed", "forbidden_without_confirmation"]:
        if not isinstance(hcb.get(key), list):
            errors.append(f"human_confirm_boundary.{key} is missing or not a list")
    return errors, warnings

# ── execution layer file list ────────────────────────────

EXECUTION_LAYER_PATHS = {
    "04_templates/table-templates/table-template-index.json",
    "05_context/writing-standards/global-component-conventions.json",
    "05_context/optimization-standards/retrospect-trigger-rules.json",
}

SPECIAL_VALIDATORS = {
    "table-template-index.json": check_template_index,
    "global-component-conventions.json": check_conventions,
    "retrospect-trigger-rules.json": check_trigger_rules,
}

# ── main ─────────────────────────────────────────────────

def main():
    skill_root = find_skill_root()
    if not skill_root:
        print("ERROR: cannot locate prd-workflow-skill root", file=sys.stderr)
        sys.exit(1)

    # collect .json files
    json_files = []
    for root, dirs, files in os.walk(skill_root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]  # skip .git etc.
        json_files.extend(
            os.path.join(root, f) for f in files if f.endswith(".json")
        )

    if not json_files:
        print("No .json files found under", skill_root)
        sys.exit(0)

    print(f"JSON execution layer validation\n")
    print(f"Skill root: {skill_root}\n")

    total_errors = 0
    total_warnings = 0
    checked = 0

    for path in sorted(json_files):
        checked += 1
        rel = os.path.relpath(path, skill_root).replace("\\", "/")
        fname = os.path.basename(path)
        json_dir = os.path.dirname(path)

        # 1. parse
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as e:
            print(f"[ERROR] {rel}")
            print(f"  JSON parse error: {e}")
            total_errors += 1
            continue

        # 2. generic checks
        is_exec = rel in EXECUTION_LAYER_PATHS
        ge, gw = check_generic(path, data, skill_root, is_exec)

        # 3. specialized checks
        se, sw = [], []
        validator = SPECIAL_VALIDATORS.get(fname)
        if validator:
            se, sw = validator(data, json_dir)

        errors = ge + se
        warnings = gw + sw
        total_errors += len(errors)
        total_warnings += len(warnings)

        if errors or warnings:
            if errors:
                print(f"[ERROR] {rel}")
            elif warnings:
                print(f"[WARN]  {rel}")
            else:
                print(f"[WARN]  {rel}")
            for e in errors:
                print(f"  - {e}")
            for w in warnings:
                print(f"  - [WARN] {w}")
        else:
            print(f"[OK]    {rel}")

    print(f"\nSummary:")
    print(f"  Checked:  {checked} JSON files")
    print(f"  Errors:   {total_errors}")
    print(f"  Warnings: {total_warnings}")

    if total_errors > 0:
        print(f"\nValidation FAILED — {total_errors} error(s) found.")
        sys.exit(1)
    else:
        print(f"\nValidation PASSED.")
        sys.exit(0)

if __name__ == "__main__":
    main()
