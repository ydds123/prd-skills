# JSONization Backlog

> Belongs to: `05_context/optimization-standards/`
> Purpose: Track candidate Markdown files that may be split into machine-readable JSON execution layers.
> Version: v1.0.0

---

## Core Principle

```text
Markdown 负责解释：为什么这样设计、边界是什么、例子是什么、反例是什么。
JSON 负责执行：路由、匹配、过滤、校验、默认值读取、触发判断、统计。
```

Do not replace Markdown with JSON wholesale. Split JSON only when the content needs stable machine reading, routing, matching, validation, statistics, or trigger judgment.

---

## P0: Completed JSON Execution Layer

| JSON File | Source Markdown | Status | Role |
|---|---|---|---|
| `04_templates/table-templates/table-template-index.json` | `04_templates/table-templates/table-template-index.md` | Completed | Machine-readable routing from checklist `suggested_format` to table templates or rendering formats |
| `05_context/writing-standards/global-component-conventions.json` | `05_context/writing-standards/global-component-conventions.md` | Completed | Machine-readable default-value layer for field length, input handling, selection control, list display, and action behavior |
| `05_context/optimization-standards/retrospect-trigger-rules.json` | `05_context/optimization-standards/retrospect-trigger-rules.md` | Completed | Machine-readable trigger, escalation, root-cause, and human-confirm boundary configuration |

---

## P1: Next JSONization Candidates

| Source Markdown | Suggested JSON | Purpose | Why JSON-worthy | Boundary |
|---|---|---|---|---|
| `01_workflow/content-consistency-sweep.md` | `01_workflow/content-consistency-sweep.rules.json` | Machine-readable consistency sweep rules | Contains blast-radius mapping, consistency dimensions, enumeration completeness rules, and auto-fix boundaries | Keep Markdown for method explanation, examples, and sweep rationale |
| `05_context/writing-standards/table-format-conventions.md` | `05_context/writing-standards/table-format-schemas.json` | Machine-readable table column schemas | Contains fixed column sets for query, list, form, business-rule, and feature-inventory tables | Keep Markdown for rationale, anti-patterns, and examples |
| `04_templates/table-templates/*.md` | `04_templates/table-templates/schemas/*.schema.json` | Machine-readable schemas for each table template | Each template contains stable columns, column meanings, required fields, and example values | Keep Markdown for examples, bad-writing explanations, and usage guidance |
| `04_templates/run-log.md` | `04_templates/run-log.schema.json` | Machine-readable run-log writing structure | Contains fixed sections and write timing for timeline, revision records, pain points, user corrections, node completion, and retrospect trigger status | Do not convert task instance `09-run-log.md` to JSON |
| `03_gates/gates-and-retrospective.md` | `03_gates/gate-rules.json` | Machine-readable gate and confirmation rules | Contains blocking levels, patch categories, auto-fix / PM-confirm / forbidden boundaries | Keep Markdown for behavior explanation and human-confirm loop |

---

## P2: Later Candidates

| Source Markdown | Suggested JSON | Purpose | Boundary |
|---|---|---|---|
| `01_workflow/task-and-draft-rules.md` | `01_workflow/task-artifact-manifest.json` | Machine-readable task artifact list and create timing | Do not change task artifact filenames or user-facing Markdown outputs |
| `04_templates/output-contracts.md` | `04_templates/output-artifact-schemas.json` | Machine-readable output artifact structures and selected table schemas | Do not convert the Full PRD template body to JSON |
| `01_workflow/workflow-protocol.md` | `01_workflow/workflow-node-manifest.json` | Machine-readable node sequence, load files, and gate points | Do not replace workflow protocol Markdown |
| `05_context/prd-standards/prd-quality-standard.md` | `05_context/prd-standards/quality-severity-rules.json` | Optional machine-readable severity and blocking rules | Do not convert quality philosophy or PRD definition into JSON |

---

## Files That Should Stay Markdown

| File | Reason |
|---|---|
| `SKILL.md` | Entry, routing, and human-agent collaboration instructions must remain readable |
| `01_workflow/workflow-protocol.md` | Workflow protocol needs explanation, context, and judgment boundaries |
| `05_context/prd-standards/prd-quality-standard.md` | Quality philosophy and judgment model are not pure configuration |
| `04_templates/output-contracts.md` Full PRD body | PRD expression structure is better maintained in Markdown |
| Task artifacts such as `04-PRD草案v0.md`, `05-完整PRDv1.md`, `09-run-log.md` | User-facing and review-facing artifacts should remain human-readable |

---

## JSONization Criteria

A Markdown file is a JSON candidate only when the target content is:

| Criterion | Meaning |
|---|---|
| Machine-readable | Agent or script needs to read it reliably |
| Routable | It maps keywords or types to files, templates, actions, or rules |
| Schema-like | It defines stable columns, fields, enums, required properties |
| Filterable | Agent needs to filter by condition, complexity, priority, or trigger |
| Countable | Agent needs to count repeats, severity levels, or escalation states |
| Actionable | Agent needs to decide what to do next based on the data |

Do not JSONize content that mainly explains rationale, boundary, examples, anti-patterns, or product philosophy.

---

## Execution Boundary

This backlog records future candidates only.

Before creating any P1 or P2 JSON file, the Agent must:

1. Confirm the source Markdown still contains stable structured rules.
2. Propose the JSON schema first.
3. Explain which parts remain in Markdown.
4. Get user confirmation before writing.
5. Avoid creating duplicate truth sources.
6. Run `scripts/validate-json-execution-layer.py` before and after to ensure the existing JSON execution layer remains valid.
