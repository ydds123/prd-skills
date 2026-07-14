#!/usr/bin/env python3
"""
Validate prd-workflow-skill JSON execution layer.

Checks:
  - All .json files parse correctly
  - Execution assets declare an authoritative, generated, or reference role
  - Table routes, schemas, examples, and generated index stay aligned
  - Checklist contract references resolve to the canonical table index

Usage:
  python3 prd-workflow-skill/scripts/validate-json-execution-layer.py
"""

import importlib.util
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
    authority = meta.get("authority")
    if authority == "authoritative":
        if meta.get("source"):
            warnings.append("authoritative asset should not declare another file as meta.source")
    elif meta.get("source"):
        resolved = resolve_source_path(meta["source"], json_dir, skill_root)
        if resolved:
            pass
        else:
            if is_execution_layer:
                errors.append(f"meta.source '{meta['source']}' cannot be resolved to an existing file")
            else:
                warnings.append(f"meta.source '{meta['source']}' cannot be resolved")
    elif is_execution_layer:
        errors.append("execution asset must declare meta.authority='authoritative' or a resolvable meta.source")
    else:
        warnings.append("meta.source is missing")
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
    seen_keywords = {}
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
        else:
            for keyword in kw:
                previous = seen_keywords.get(keyword)
                if previous:
                    errors.append(f"keyword '{keyword}' is routed by both '{previous}' and '{rid}'")
                else:
                    seen_keywords[keyword] = rid
        tf = r.get("template_file", "")
        if not tf:
            errors.append(f"{prefix}.template_file is missing")
        else:
            tf_path = os.path.join(json_dir, tf)
            if not os.path.isfile(tf_path):
                errors.append(f"{prefix}.template_file '{tf}' does not exist at {tf_path}")

        sf = r.get("schema_file", "")
        if not sf:
            errors.append(f"{prefix}.schema_file is missing")
        elif not sf.endswith(".schema.json"):
            errors.append(f"{prefix}.schema_file '{sf}' must end with .schema.json")
        else:
            sf_path = os.path.join(json_dir, sf)
            if not os.path.isfile(sf_path):
                errors.append(f"{prefix}.schema_file '{sf}' does not exist at {sf_path}")
            else:
                try:
                    with open(sf_path, "r", encoding="utf-8") as fh:
                        schema = json.load(fh)
                    if schema.get("template_id") != rid:
                        errors.append(
                            f"{prefix}.schema_file template_id '{schema.get('template_id')}' does not match route id '{rid}'")
                    expected_headers = [c.get("name") for c in schema.get("columns", [])]
                    template_path = os.path.join(json_dir, tf)
                    template_headers = extract_table_headers(template_path)
                    if expected_headers not in template_headers:
                        errors.append(
                            f"{prefix}.template_file has no example matching schema headers {expected_headers!r}")
                except (OSError, json.JSONDecodeError) as exc:
                    errors.append(f"{prefix} cannot validate schema/template pair: {exc}")

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

    skill_root = os.path.dirname(os.path.dirname(json_dir))
    generator_path = os.path.join(skill_root, "scripts", "generate-table-contract-index.py")
    output_path = os.path.join(json_dir, "table-template-index.md")
    if not os.path.isfile(generator_path):
        errors.append("generate-table-contract-index.py is missing")
    else:
        try:
            spec = importlib.util.spec_from_file_location("table_contract_generator", generator_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            source_path = os.path.join(json_dir, "table-template-index.json")
            source_bytes = open(source_path, "rb").read()
            expected = module.render(data, source_bytes)
            actual = open(output_path, "r", encoding="utf-8").read()
            if actual != expected:
                errors.append("table-template-index.md is stale or manually modified")
        except Exception as exc:
            errors.append(f"cannot validate generated table contract index: {exc}")

    return errors, warnings


def extract_table_headers(path):
    if not path or not os.path.isfile(path):
        return []
    lines = open(path, "r", encoding="utf-8").read().splitlines()
    headers = []
    for index, line in enumerate(lines[:-1]):
        if not line.strip().startswith("|"):
            continue
        if re.fullmatch(r"[|:\-\s]+", lines[index + 1].strip()):
            value = line.strip().strip("|")
            headers.append([cell.strip() for cell in value.split("|")])
    return headers


def check_checklist(data, json_dir):
    errors, warnings = [], []
    items = data.get("items")
    if not isinstance(items, list) or not items:
        return ["items is missing or not a non-empty list"], warnings

    skill_root = os.path.dirname(os.path.dirname(json_dir))
    index_path = os.path.join(
        skill_root, "04_templates", "table-templates", "table-template-index.json")
    try:
        with open(index_path, "r", encoding="utf-8") as fh:
            contract_ids = {route["id"] for route in json.load(fh)["template_routes"]}
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        return [f"cannot load canonical table contract index: {exc}"], warnings

    seen_ids = set()
    for index, item in enumerate(items):
        item_id = item.get("id")
        if not item_id:
            errors.append(f"items[{index}].id is missing")
        elif item_id in seen_ids:
            errors.append(f"items[{index}].id '{item_id}' is duplicated")
        seen_ids.add(item_id)
        template_ref = item.get("template_ref")
        if template_ref and template_ref not in contract_ids:
            errors.append(
                f"items[{index}] '{item_id}' references unknown table contract '{template_ref}'")

    declared_total = data.get("meta", {}).get("total_items")
    if declared_total != len(items):
        errors.append(f"meta.total_items is {declared_total}; actual items count is {len(items)}")
    return errors, warnings

def check_component_specifications(data, json_dir):
    errors, warnings = [], []
    for key in ["principles", "override_priority", "shared_input_rules", "field_semantic_profiles",
                "components", "list_display_defaults", "action_defaults"]:
        val = data.get(key)
        if not isinstance(val, list) or not val:
            errors.append(f"{key} is missing or not a non-empty list")
    profiles = data.get("field_semantic_profiles", [])
    profile_ids = set()
    if isinstance(profiles, list):
        for i, profile in enumerate(profiles):
            if not isinstance(profile, dict):
                errors.append(f"field_semantic_profiles[{i}] is not an object"); continue
            fid = profile.get("id", f"<index-{i}>")
            if fid in profile_ids:
                errors.append(f"field_semantic_profiles[{i}].id '{fid}' is duplicated")
            profile_ids.add(fid)
            mn, mx = profile.get("min"), profile.get("max")
            if isinstance(mn, (int, float)) and isinstance(mx, (int, float)) and mx < mn:
                errors.append(f"field_semantic_profiles[{i}] max({mx}) < min({mn})")
    required_components = {
        "single_line_text", "multi_line_text", "numeric_input", "dropdown_single", "dropdown_multi",
        "radio_group", "checkbox_group", "date_time_picker", "switch", "file_upload"
    }
    components = data.get("components", [])
    component_ids = set()
    if isinstance(components, list):
        for i, component in enumerate(components):
            if not isinstance(component, dict):
                errors.append(f"components[{i}] is not an object"); continue
            cid = component.get("id", f"<index-{i}>")
            if cid in component_ids:
                errors.append(f"components[{i}].id '{cid}' is duplicated")
            component_ids.add(cid)
            for key in ["name", "category", "content_rule_template", "validation_message_template"]:
                if not component.get(key):
                    errors.append(f"components[{i}].{key} is missing or empty")
            for key in ["prd_component_types", "applies_to", "default_behavior", "must_specify", "semantic_profiles", "invalid_examples"]:
                if not isinstance(component.get(key), list):
                    errors.append(f"components[{i}].{key} is missing or not a list")
            evidence_requirements = component.get("prd_evidence_requirements")
            if not isinstance(evidence_requirements, list) or not evidence_requirements:
                errors.append(f"components[{i}].prd_evidence_requirements is missing or empty")
            else:
                requirement_ids = set()
                for j, requirement in enumerate(evidence_requirements):
                    prefix = f"components[{i}].prd_evidence_requirements[{j}]"
                    if not isinstance(requirement, dict):
                        errors.append(f"{prefix} is not an object")
                        continue
                    requirement_id = requirement.get("id")
                    if not requirement_id:
                        errors.append(f"{prefix}.id is missing")
                    elif requirement_id in requirement_ids:
                        errors.append(f"{prefix}.id {requirement_id!r} is duplicated")
                    requirement_ids.add(requirement_id)
                    if requirement.get("scope") not in {"row", "section"}:
                        errors.append(f"{prefix}.scope must be row or section")
                    columns = requirement.get("columns")
                    if not isinstance(columns, list):
                        errors.append(f"{prefix}.columns is missing or not a list")
                    elif requirement.get("scope") == "row" and not columns:
                        errors.append(f"{prefix}.columns must not be empty for row scope")
                    all_terms = requirement.get("all_terms", [])
                    any_terms = requirement.get("any_terms", [])
                    if not isinstance(all_terms, list) or not isinstance(any_terms, list):
                        errors.append(f"{prefix}.all_terms and any_terms must be lists")
                    elif not all_terms and not any_terms:
                        errors.append(f"{prefix} must define all_terms or any_terms")
            unknown = set(component.get("semantic_profiles", [])) - profile_ids
            if unknown:
                errors.append(f"components[{i}] references unknown semantic profiles: {', '.join(sorted(unknown))}")
    missing = sorted(required_components - component_ids)
    if missing:
        errors.append(f"missing required component ids: {', '.join(missing)}")
    skill_root = os.path.dirname(os.path.dirname(json_dir))
    source_path = os.path.join(json_dir, "component-specifications.json")
    output_path = os.path.join(json_dir, "component-specifications.md")
    generator_path = os.path.join(skill_root, "scripts", "generate-component-specifications.py")
    if not os.path.isfile(output_path):
        errors.append("generated component-specifications.md is missing")
    elif not os.path.isfile(generator_path):
        errors.append("generate-component-specifications.py is missing")
    else:
        try:
            spec = importlib.util.spec_from_file_location("component_spec_generator", generator_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            source_bytes = open(source_path, "rb").read()
            expected = module.render(data, source_bytes)
            actual = open(output_path, "r", encoding="utf-8").read()
            if actual != expected:
                errors.append("component-specifications.md is stale or manually modified")
        except Exception as exc:
            errors.append(f"cannot validate generated component specification view: {exc}")
    return errors, warnings

def check_table_template_schema(data, json_dir):
    """Validator for 04_templates/table-templates/schemas/*.schema.json"""
    errors, warnings = [], []

    tid = data.get("template_id", "")
    if not tid:
        errors.append("template_id is missing or empty")

    cols = data.get("columns", [])
    if not isinstance(cols, list) or not cols:
        errors.append("columns is missing or empty")
    else:
        for j, c in enumerate(cols):
            cp = f"columns[{j}]"
            if not isinstance(c, dict):
                errors.append(f"{cp} is not an object"); continue
            if not c.get("name"): errors.append(f"{cp}.name is missing or empty")
            rq = c.get("required")
            if not isinstance(rq, bool): errors.append(f"{cp}.required is missing or not boolean")
            if not c.get("description"): errors.append(f"{cp}.description is missing or empty")
            for opt in ["allowed_values", "notes"]:
                val = c.get(opt)
                if val is not None and not isinstance(val, list):
                    errors.append(f"{cp}.{opt} is present but not a list")

    col_names = {c["name"] for c in cols if isinstance(c, dict) and c.get("name")}
    for key in ["required_columns", "optional_columns"]:
        subl = data.get(key)
        if subl is not None:
            if not isinstance(subl, list):
                errors.append(f"{key} is not a list")
            else:
                for cn in subl:
                    if cn not in col_names:
                        errors.append(f"{key} references '{cn}' which is not in columns")

    ur = data.get("usage_rules")
    if ur is not None and not isinstance(ur, list):
        warnings.append("usage_rules is present but not a list")
    apr = data.get("anti_patterns_ref")
    if apr is not None and not isinstance(apr, str):
        warnings.append("anti_patterns_ref is present but not a string")

    return errors, warnings


def check_run_log_schema(data, json_dir):
    errors, warnings = [], []
    manifest_ref = data.get("workflow_manifest")
    if not manifest_ref:
        errors.append("workflow_manifest is missing")
    else:
        skill_root = os.path.dirname(json_dir)
        manifest_path = os.path.join(skill_root, manifest_ref)
        if not os.path.isfile(manifest_path):
            errors.append(f"workflow_manifest cannot be resolved: {manifest_ref}")

    for key in ["root_causes", "severity_values", "trigger_levels"]:
        values = data.get(key)
        if not isinstance(values, list) or not values:
            errors.append(f"{key} is missing or not a non-empty list")
        elif len(values) != len(set(values)):
            errors.append(f"{key} contains duplicates")

    thresholds = data.get("trigger_level_thresholds")
    if not isinstance(thresholds, list) or not thresholds:
        errors.append("trigger_level_thresholds is missing or not a non-empty list")
    else:
        seen_counts = set()
        known_levels = set(data.get("trigger_levels", []))
        for index, item in enumerate(thresholds):
            if not isinstance(item, dict):
                errors.append(f"trigger_level_thresholds[{index}] is not an object")
                continue
            count = item.get("min_count")
            level = item.get("level")
            if not isinstance(count, int) or count < 1:
                errors.append(f"trigger_level_thresholds[{index}].min_count must be a positive integer")
            elif count in seen_counts:
                errors.append(f"trigger_level_thresholds min_count {count} is duplicated")
            seen_counts.add(count)
            if level not in known_levels:
                errors.append(f"trigger_level_thresholds[{index}].level {level!r} is unknown")

    seen_headings = set()
    for key in ["required_sections", "optional_sections"]:
        sections = data.get(key)
        if not isinstance(sections, list):
            errors.append(f"{key} is missing or not a list")
            continue
        if key == "required_sections" and not sections:
            errors.append("required_sections must not be empty")
        for index, section in enumerate(sections):
            prefix = f"{key}[{index}]"
            if not isinstance(section, dict):
                errors.append(f"{prefix} is not an object")
                continue
            heading = section.get("heading")
            columns = section.get("columns")
            if not heading:
                errors.append(f"{prefix}.heading is missing or empty")
            elif heading in seen_headings:
                errors.append(f"section heading {heading!r} is duplicated")
            else:
                seen_headings.add(heading)
            if not isinstance(columns, list) or not columns:
                errors.append(f"{prefix}.columns is missing or not a non-empty list")
            elif len(columns) != len(set(columns)):
                errors.append(f"{prefix}.columns contains duplicates")
            for alias in section.get("aliases", []):
                if alias in seen_headings:
                    errors.append(f"section alias {alias!r} collides with another heading or alias")
                seen_headings.add(alias)
    return errors, warnings


def check_workflow_manifest(data, json_dir):
    errors, warnings = [], []
    sequence = data.get("node_sequence")
    nodes = data.get("nodes")
    if not isinstance(sequence, list) or not sequence:
        errors.append("node_sequence is missing or not a non-empty list")
        sequence = []
    if len(sequence) != len(set(sequence)):
        errors.append("node_sequence contains duplicates")
    if not isinstance(nodes, list) or not nodes:
        errors.append("nodes is missing or not a non-empty list")
        nodes = []

    node_ids = []
    skill_root = os.path.dirname(json_dir)
    for index, node in enumerate(nodes):
        prefix = f"nodes[{index}]"
        if not isinstance(node, dict):
            errors.append(f"{prefix} is not an object")
            continue
        node_id = node.get("id")
        if not node_id:
            errors.append(f"{prefix}.id is missing")
        else:
            node_ids.append(node_id)
        for key in ["name", "inputs", "load_files", "outputs", "completion_conditions"]:
            value = node.get(key)
            if key == "name":
                if not value:
                    errors.append(f"{prefix}.name is missing or empty")
            elif not isinstance(value, list):
                errors.append(f"{prefix}.{key} is missing or not a list")
            elif key in {"inputs", "completion_conditions"} and not value:
                errors.append(f"{prefix}.{key} must not be empty")
        for ref in node.get("load_files", []):
            if not os.path.isfile(os.path.join(skill_root, ref)):
                errors.append(f"{prefix}.load_files cannot resolve {ref!r}")
        confirmation = node.get("human_confirmation")
        if not isinstance(confirmation, dict) or not isinstance(confirmation.get("required"), bool):
            errors.append(f"{prefix}.human_confirmation.required must be boolean")
        elif not str(confirmation.get("condition", "")).strip():
            errors.append(f"{prefix}.human_confirmation.condition is missing")
        run_log = node.get("run_log")
        if not isinstance(run_log, dict) or not all(
            isinstance(run_log.get(key), bool)
            for key in ["timeline_required", "completion_record_required"]
        ):
            errors.append(f"{prefix}.run_log must define boolean timeline_required and completion_record_required")

    if node_ids != sequence:
        errors.append(f"nodes order {node_ids!r} does not match node_sequence {sequence!r}")
    required = data.get("required_completion_nodes")
    if not isinstance(required, list) or not required:
        errors.append("required_completion_nodes is missing or empty")
    elif set(required) - set(sequence):
        errors.append("required_completion_nodes contains unknown nodes")

    conditional = data.get("conditional_outputs")
    if not isinstance(conditional, list):
        errors.append("conditional_outputs is missing or not a list")
        conditional = []

    artifacts = {
        output
        for node in nodes if isinstance(node, dict)
        for output in node.get("outputs", [])
    }
    artifacts.update(
        output.get("path") for output in conditional
        if isinstance(output, dict) and output.get("path")
    )
    aliases = data.get("retired_artifact_aliases")
    if not isinstance(aliases, dict):
        errors.append("retired_artifact_aliases is missing or not an object")
        aliases = {}
    for retired, canonical in aliases.items():
        if canonical not in artifacts:
            errors.append(f"retired alias {retired!r} points to undeclared artifact {canonical!r}")
        if retired in artifacts:
            errors.append(f"retired alias {retired!r} is still declared as an artifact")

    references = data.get("governed_reference_files")
    if not isinstance(references, list) or not references:
        errors.append("governed_reference_files is missing or not a non-empty list")
        references = []
    for ref in references:
        path = os.path.join(skill_root, ref)
        if not os.path.isfile(path):
            errors.append(f"governed_reference_files cannot resolve {ref!r}")
            continue
        text = open(path, "r", encoding="utf-8").read()
        for retired in aliases:
            if retired in text:
                errors.append(f"governed reference {ref!r} still uses retired artifact alias {retired!r}")
    return errors, warnings


def check_consistency_sweep_rules(data, json_dir):
    errors, warnings = [], []
    dimensions = data.get("dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        return ["dimensions is missing or not a non-empty list"], warnings
    dimension_ids = []
    for index, dimension in enumerate(dimensions):
        if not isinstance(dimension, dict) or not dimension.get("id") or not dimension.get("name"):
            errors.append(f"dimensions[{index}] must define id and name")
            continue
        dimension_ids.append(dimension["id"])
        if not isinstance(dimension.get("cross_cutting"), bool):
            errors.append(f"dimensions[{index}].cross_cutting must be boolean")
    if len(dimension_ids) != len(set(dimension_ids)):
        errors.append("dimension ids contain duplicates")

    route_ids = set()
    covered = set()
    routes = data.get("change_routes")
    if not isinstance(routes, list) or not routes:
        errors.append("change_routes is missing or not a non-empty list")
    else:
        for index, route in enumerate(routes):
            prefix = f"change_routes[{index}]"
            route_id = route.get("id") if isinstance(route, dict) else None
            if not route_id or not route.get("name"):
                errors.append(f"{prefix} must define id and name")
                continue
            if route_id in route_ids:
                errors.append(f"change route id {route_id!r} is duplicated")
            route_ids.add(route_id)
            required = route.get("required_dimensions")
            if not isinstance(required, list) or not required:
                errors.append(f"{prefix}.required_dimensions is missing or empty")
                continue
            unknown = set(required) - set(dimension_ids)
            if unknown:
                errors.append(f"{prefix} references unknown dimensions: {', '.join(sorted(unknown))}")
            covered.update(required)
    uncovered = set(dimension_ids) - covered
    if uncovered:
        errors.append(f"dimensions have no change route: {', '.join(sorted(uncovered))}")

    boundaries = data.get("repair_boundaries")
    if not isinstance(boundaries, dict):
        errors.append("repair_boundaries is missing or not an object")
    else:
        for key in ["auto_fix", "pm_confirmation", "forbidden"]:
            if not isinstance(boundaries.get(key), list) or not boundaries[key]:
                errors.append(f"repair_boundaries.{key} is missing or empty")
    if not isinstance(data.get("evidence_priority"), list) or not data["evidence_priority"]:
        errors.append("evidence_priority is missing or empty")
    return errors, warnings


def check_ledger_feature_contract(data, json_dir):
    errors, warnings = [], []
    skill_root = os.path.dirname(os.path.dirname(json_dir))
    index_path = os.path.join(skill_root, "04_templates", "table-templates", "table-template-index.json")
    try:
        contract_ids = {
            route["id"] for route in json.load(open(index_path, "r", encoding="utf-8"))["template_routes"]
        }
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        return [f"cannot load table contract index: {exc}"], warnings

    sections = data.get("required_sections")
    if not isinstance(sections, list) or not sections:
        errors.append("required_sections is missing or empty")
    else:
        suffixes = []
        for index, section in enumerate(sections):
            suffix = section.get("suffix") if isinstance(section, dict) else None
            if not suffix:
                errors.append(f"required_sections[{index}].suffix is missing")
                continue
            suffixes.append(suffix)
            contract = section.get("table_contract")
            if contract and contract not in contract_ids:
                errors.append(f"required_sections[{index}] references unknown contract {contract!r}")
        if len(suffixes) != len(set(suffixes)):
            errors.append("required section suffixes contain duplicates")

    order = data.get("canonical_operation_order")
    if not isinstance(order, list) or not order:
        errors.append("canonical_operation_order is missing or empty")
    elif len(order) != len(set(order)):
        errors.append("canonical_operation_order contains duplicates")
    flow = data.get("operation_flow")
    if not isinstance(flow, dict):
        errors.append("operation_flow is missing or not an object")
    else:
        for key in ["branch_contract", "decision_contract"]:
            if flow.get(key) not in contract_ids:
                errors.append(f"operation_flow.{key} references an unknown contract")
    batch = data.get("batch_import")
    if not isinstance(batch, dict):
        errors.append("batch_import is missing or not an object")
    else:
        for key in ["required_evidence", "atomicity_values", "failure_carrier_values"]:
            if not isinstance(batch.get(key), list) or not batch[key]:
                errors.append(f"batch_import.{key} is missing or empty")
        feedback = batch.get("feedback_evidence")
        if not isinstance(feedback, dict):
            errors.append("batch_import.feedback_evidence is missing or not an object")
        else:
            for key in ["all_terms", "action_terms"]:
                if not isinstance(feedback.get(key), list) or not feedback[key]:
                    errors.append(f"batch_import.feedback_evidence.{key} is missing or empty")
    return errors, warnings


def check_regression_suite(data, json_dir):
    errors, warnings = [], []
    skill_root = os.path.dirname(json_dir)
    tests = data.get("tests")
    if not isinstance(tests, list) or not tests:
        return ["tests is missing or not a non-empty list"], warnings

    ids = []
    mapped = []
    for index, test in enumerate(tests):
        prefix = f"tests[{index}]"
        if not isinstance(test, dict):
            errors.append(f"{prefix} is not an object")
            continue
        test_id = test.get("id")
        if not test_id:
            errors.append(f"{prefix}.id is missing")
        else:
            ids.append(test_id)
        command = test.get("command")
        if not isinstance(command, list) or len(command) < 2 or command[0] != "${PYTHON}":
            errors.append(f"{prefix}.command must start with ${{PYTHON}} and name a script")
        elif not os.path.isfile(os.path.join(skill_root, command[1])):
            errors.append(f"{prefix}.command cannot resolve {command[1]!r}")
        covered = test.get("covers_eval_files")
        if not isinstance(covered, list):
            errors.append(f"{prefix}.covers_eval_files must be a list")
        else:
            mapped.extend(covered)
    if len(ids) != len(set(ids)):
        errors.append("test ids contain duplicates")

    eval_files = {
        "evals/" + name for name in os.listdir(json_dir)
        if name.endswith(".json") and name != "regression-suite.json"
    }
    missing = eval_files - set(mapped)
    unknown = set(mapped) - eval_files
    duplicates = {item for item in mapped if mapped.count(item) > 1}
    if missing:
        errors.append(f"eval files have no regression mapping: {', '.join(sorted(missing))}")
    if unknown:
        errors.append(f"regression mapping references unknown eval files: {', '.join(sorted(unknown))}")
    if duplicates:
        errors.append(f"eval files are mapped more than once: {', '.join(sorted(duplicates))}")
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
    "01_workflow/workflow-manifest.json",
    "01_workflow/consistency-sweep-rules.json",
    "04_templates/run-log.schema.json",
    "04_templates/table-templates/table-template-index.json",
    "05_context/writing-standards/component-specifications.json",
    "05_context/writing-standards/ledger-feature-contract.json",
    "05_context/prd-standards/checklist-v3.3.json",
    "05_context/optimization-standards/retrospect-trigger-rules.json",
    "evals/regression-suite.json",
}

# Files under schemas/ are also execution layer
def _is_execution_layer(rel_path):
    return rel_path in EXECUTION_LAYER_PATHS or "/schemas/" in rel_path

SPECIAL_VALIDATORS = {
    "workflow-manifest.json": check_workflow_manifest,
    "consistency-sweep-rules.json": check_consistency_sweep_rules,
    "run-log.schema.json": check_run_log_schema,
    "table-template-index.json": check_template_index,
    "component-specifications.json": check_component_specifications,
    "ledger-feature-contract.json": check_ledger_feature_contract,
    "checklist-v3.3.json": check_checklist,
    "retrospect-trigger-rules.json": check_trigger_rules,
    "regression-suite.json": check_regression_suite,
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
        is_exec = _is_execution_layer(rel)
        ge, gw = check_generic(path, data, skill_root, is_exec)

        # 3. specialized checks
        se, sw = [], []
        validator = SPECIAL_VALIDATORS.get(fname)
        if not validator and fname.endswith(".schema.json"):
            validator = check_table_template_schema
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
