# Workflow Protocol

> `01_workflow/workflow-manifest.json` is the authoritative source for node order, inputs, loaded files, outputs, human-confirmation conditions, completion conditions, and Run Log requirements. This document explains execution methods and must not override the manifest.

This protocol keeps PRD work from jumping directly from vague input to polished but unreliable output.

## Human–AI Division

This is not advisory. It is the line that keeps judgment human and execution automated.

| Node | Human guards | AI handles |
|---|---|---|
| Write-before Alignment | Problem definition: whose real problem, is it worth solving; confirming the decision ledger | Retrieving materials, producing background card and decision ledger with recommendations |
| Draft Body | Confirming the scope and main-flow frame is correct before details are filled | Writing strategy layer, scope layer, and main-flow skeleton only — no exceptions, permissions, or data yet |
| Fill Details | Only needed if draft scope is being overridden; normally the agent runs without human intervention | Expanding the accepted frame: exceptions, error states, permissions, state transitions, data sources, acceptance criteria, self-test cases |
| Independent Review | Deciding which P0/P1 fixes to apply, whether to accept a risk, and whether to cut a feature | Spotting errors by checklist: inconsistency, gaps, conflicts, over-design, missing items; subtracting first, then classifying |
| Retrospect (conditional) | Confirming which patch proposals should modify reusable rules | Classifying failure types and proposing bounded patches |

The four things only humans can hold: problem definition, direction, tradeoffs, and quality sign-off. The rest is volume work with clear right answers — AI territory.

## State Machine

```text
input_received
→ [boot] task_folder
→ [1] alignment → human confirms direction
→ [2] draft_body → human confirms scope & main flow
→ [3] fill_details
→ [4] review → human decides fixes
→ [retrospect] conditional — user request, repeated quality issues, or T3 trigger
```

## Cross-node Correction and Decision Intake

When a user correction, review finding, full-PRD discovery, or sweep finding changes product judgment:

1. Append the decision to `02-决策账本.md` with a new decision ID.
2. If the correction changes a prior decision, mark the old entry `superseded` and reference the new ID.
3. Record the event in `09-run-log.md` 运行时间线.
4. If triggered by user correction, also record in 用户指正记录 with the decision ID.
5. If triggered by review, revision, or sweep, record in 修订记录 with the decision ID.
6. Do not duplicate full decision content in `09-run-log.md`.

Decision changes go to `02-决策账本.md`.
Process evidence goes to `09-run-log.md`.

All `09-run-log.md` time fields use the task timezone and the exact format `YYYY-MM-DD HH:mm:ss`. Automated writers use the runtime local timezone. Never degrade run evidence to date-only or minute-only values.

Before any node is marked complete, run `python <skill-root>/scripts/validate-run-log.py <task-folder>/09-run-log.md`. Validation failure blocks node completion. Existing logs created before this contract may use `--allow-legacy-date` only when the file contains an explicit migration note; new tasks must run in strict mode.

## Node Rules

### 0. Task Folder (Boot)

Goal: make each PRD run file-backed and reviewable.

Required actions:

- create or reuse a task folder before drafting
- name it by date and PRD name
- write every material output into a Markdown or JSON file inside the task folder
- keep chat output as a summary or preview when files are being created

See [Task and Draft Rules](task-and-draft-rules.md).

### 1. Write-before Alignment

Goal: align background, scope, and key decisions before any PRD body is written.

Required actions:

- read all named files and user-provided context
- **problem drilling**: identify whether the user gave a problem, a proposed solution, or mixed material. Users almost always present solutions ("add an export button"), not problems ("I spend two hours every Friday copying data into my weekly report by hand"). A solution is a symptom; the real problem is underneath. Drill through the proposed solution to find the underlying problem before judging whether the requirement is writable. If the user only gave a solution, ask: "what does that person actually need to get done that they can't do today?"
- use 5W1H, Feynman technique, first principles, and Johari Window to improve input quality before synthesis
- use MECE, bottom-up pyramid grouping, SCQA, Issue Tree, and systems thinking to turn scattered input into product judgment
- produce a background understanding card
- produce a decision ledger
- list at most 3 blocking questions when needed
- output a writable-state judgment

**Decision ledger rigid rule**: Every decision point must carry a recommendation and rationale. A decision entry that only rephrases the question — listing options without a recommendation — is invalid. The agent must always state the direction it would take and why. If the agent cannot form a recommendation, the requirement is not writable. A good decision entry reads like "I recommend A, because X and Y; alternative B exists but costs Z more" — the PM's job shifts from "answer ten questions" to "veto one or two recommendations."

**Writable-state check** (inline, not separate gate): The requirement is writable only when: background is understandable, real problem and affected role are clear, in-scope and out-of-scope items are explicit, key upstream/downstream dependencies are identified, key decisions have a status (confirmed or pending), and no pending question could overturn the main PRD direction. If not writable, stop and ask at most 3 priority questions, explaining which output each answer unlocks.

**Decision check** (inline): Key tradeoffs are confirmed by user material, or AI recommendations are labeled as recommended defaults. Unconfirmed decisions are marked as pending — never hidden in prose.

Forbidden during alignment:

- do not write PRD body
- do not ask generic questions that are not grounded in the material
- do not let uncertainty disappear into prose
- do not use pyramid-style polished output to cover weak input, missing evidence, or unexamined assumptions

→ Human confirms direction. No PRD body before this point.

### 2. Draft Body

Goal: sketch the frame before filling the muscles.

Required actions:

- write strategy layer: why this matters, for whom, and what success means
- write scope layer: in-scope items, out-of-scope items, role/scenario boundary, and open decisions
- write main-flow skeleton: the normal path at a coarse level

Do not include exception flows, empty-state handling, permission matrices, data specs, acceptance criteria, self-test cases, API details, or implementation-like content unless the user explicitly asks.

**Constraint-structure marking (when applicable):** If the draft involves state reversal, flow rollback, permission exception, field unlock, void-then-restore, or re-submission after completion, the draft skeleton must flag which system constraint boundaries are touched — even if full rule analysis is deferred to Node 3. The draft does not need to resolve whether the constraint holds, but it must not present such rules as harmless main-flow steps without noting the constraint boundary they cross.

**Draft check** (inline, not separate gate): If strategy, scope, or main flow are uncertain, pause for confirmation. If they are already confirmed in source material, continue and state the basis.

→ Human confirms scope and main flow are correct. Do not expand to full PRD before this confirmation.

### 3. Fill Details

Goal: expand the accepted frame into a complete PRD body.

**Before writing:**

1. Verify `09-run-log.md` exists in the task folder. If not, create it from the template at `04_templates/run-log.md`. Append a Node 3 start entry to 运行时间线.
2. Read `09-run-log.md` — particularly 痛点日志 — to avoid repeating mistakes from prior runs.
3. Load `05_context/prd-standards/checklist-v3.3.json` (V3.3).
4. Identify which checklist items apply: filter by `complexity` (L1-L4 matches the PRD's complexity level) and `condition` (domain-specific conditions like "has multi-role" or "has delete action").
5. For each applicable item, use `question`, `pass_criteria`, and `failure_signal` as the writing guide. The `suggested_format` field tells you which table contract to use. Read `table-template-index.json` first, match exactly one route, then load only its `schema_file`; load the Markdown template only for examples and boundaries. `component-specifications.json` remains authoritative for component behavior and field semantics, and `retrospect-trigger-rules.json` for trigger/escalation rules. Generated Markdown views must never be edited by hand.

**Table template lazy loading rule:**

Do not preload all table template schemas or Markdown templates. Load `table-template-index.json` first for routing. After a route is matched, load only the matched `schema_file` to get fixed columns and required fields. Load only the matched Markdown template when examples, anti-patterns, or boundary explanations are needed.

This protects the context window and prevents unrelated table schemas from influencing the current PRD output.

6. Table template reading order: (1) `table-template-index.json` for routing → (2) match route by `suggested_format` → (3) load only the matched `schema_file` → (4) use schema for fixed columns and required fields → (5) load only the matched Markdown template when examples, anti-patterns, or boundary rules are needed. Do not load unrelated schemas or templates.
7. Load `05_context/writing-standards/component-specifications.json`. For each form field: match exactly one component; match a field semantic profile when the component supports one; fill every `must_specify` item; combine component behavior and semantic defaults into the final `表单内容规则`; then apply any higher-priority evidence-based override. Run `scripts/generate-component-specifications.py --check` before relying on the Markdown view. If the domain is ledger-oriented or includes batch import/export, also load `05_context/writing-standards/ledger-feature-writing.md` and run its completion check.
8. Every gate item (`hierarchy: "gate"`) must either be addressed in the PRD or explicitly marked as not applicable with a reason.
9. Do not dump the checklist into the PRD. Use it as a silent writing guide.

Write:

- background and real problem
- goals and success criteria
- scope and non-goals
- users and scenarios
- main flow
- core functions and rules
- operation flows using a numbered main path, followed by branch/exception and key-decision tables only when applicable
- empty, failure, conflict, duplicate, irreversible, and permission cases
- state changes
- data sources, fields by business meaning, and data cadence
- upstream/downstream impact
- acceptance criteria
- development self-test cases
- pending items and accepted risks

For any rule that touches system constraint boundaries — such as state reversal, flow rollback, permission exception, field unlock, void recovery, re-submission after completion, or task reassignment that bypasses normal ownership — the PRD must explicitly address whether the system's constraint structure still holds after the rule is allowed. Refer to [PRD Quality Standard](05_context/prd-standards/prd-quality-standard.md) §Constraint Integrity for what constraint structure means. If constraint integrity cannot be confirmed, mark the rule 待确认 or record it in the risk-acceptance table. Do not use polished prose to make a constraint violation look benign.

**After Fill Details completes (or after each revision round ends):**

1. Update `09-run-log.md` Node 完成记录 for Node 3: which checklist items were applied (by complexity and condition filters), how many gate items were addressed vs. skipped.
2. If any content was revised in response to feedback, append to 修订记录: round number, trigger, scope, root cause classification (缺知识/缺方法/缺模板/缺门禁/缺案例/偶发), and which checklist module was involved.
3. If a revision reveals a systemic gap (something the writer "shouldn't have missed" on first pass), append to 痛点日志: what was missed, why it was missed on the first pass, which checklist module covers it, and severity.

**Table and flow conventions:**
- Use `table-template-index.json` as the only table routing authority; fixed columns come from the matched `schema_file`.
- For every function that needs an operation flow, use `05_context/writing-standards/operation-flow-writing.md`: numbered main path, then `exception_handling_table` and `key_decision_table` only when applicable.
- The legacy five-column interaction table is removed and must not be generated.

**Multi-endpoint consistency check** (if the PRD covers Web + App):
- For each endpoint: verify visibility, detail display, action entry, acceptance criteria, and self-test coverage.
- If endpoints diverge on a behavior, state the divergence as a deliberate decision, not an omission.

### 4. Independent Review

Goal: catch problems the writer missed, with a separate role that has no ego in the draft.

**Role switch (mandatory):** Before starting the review, explicitly switch context:
- You are no longer the PRD writer. You are an independent reviewer.
- Your only loyalty is to the quality standard (`05_context/prd-standards/prd-quality-standard.md`) and the completeness checklist (`05_context/prd-standards/checklist-v3.3.json`).
- You were not in the room when this PRD was written. Every claim in the PRD is a claim to be verified, not a fact to be assumed correct.
- Default stance: skeptical. If the PRD makes something sound easy, ask "what breaks when this fails?"

**Review materials (load before starting):**
1. Read `09-run-log.md` in the task folder — focus on 痛点日志 and 修订记录. These tell you what the writer already knows they missed and why. Cross-check: did the writer actually fix those gaps, or just acknowledge them?
2. `05_context/prd-standards/prd-quality-standard.md` — the four criteria and blocking severity rules
3. `05_context/prd-standards/checklist-v3.3.json` (V3.3) — for each checklist item, review against the PRD using `question` (what to check), `pass_criteria` (what passing looks like), and `failure_signal` (what failing looks like). Items are filtered by `hierarchy` (gate = must check, extended = applicable-by-condition, advisory = suggested). When an applicable item is missing: **the severity follows `priority`, not `hierarchy`**. A gate item with priority P1 is P1. An extended item with priority P0 is P0. Only when `priority` is empty does `hierarchy` provide the fallback: gate → P0, extended → P1, advisory → P3.

**Initialize the machine-readable review record (mandatory):**

Run `scripts/prd-content-gate.py init` before semantic review. It creates `06-内容质量审查.json` with one pending disposition for every current checklist item. The independent reviewer must resolve every item; filtering by complexity and condition decides `applicable` versus `not_applicable`, but must not remove the item from the record. See `05_context/prd-standards/content-quality-gate.md` for commands and field rules.

Required actions:

- **subtract first**: before checking completeness, ask of every feature: "if we skip this, what breaks?" If the answer is "the user can still manage, just less conveniently," flag it as potential over-design.
- **operational completeness sweep**: for each applicable checklist item (filtered by `complexity` and `condition`), check against the PRD using `question`, `pass_criteria`, and `failure_signal`. When an applicable item is missing:
  - **Severity follows `priority`**: the item's `priority` field (P0/P1/P2/P3) determines the finding severity.
  - **`hierarchy` determines obligation**: gate = must check and address (or mark 不适用); extended = check if condition is met; advisory = suggested but not required.
  - **Fallback when `priority` is empty**: gate → P0, extended → P1, advisory → P3.
  - Example: C56 (空态处理) is `hierarchy: "extended", priority: "P0"` → missing = P0 block, not P1.
- check clear boundary, explicit judgment, no guessing, and accurate information
- classify findings as P0/P1/P2/P3
- **constraint-erosion check**: for every rule, exception, reversal, unlock, recovery, or re-submission the PRD introduces, ask: "if this is allowed, do the system's existing constraints still hold?" Flag any design where local reasonableness masks systemic erosion of main rules, irreversible states, permission boundaries, flow direction, responsibility attribution, or data caliber — even if the PRD text is otherwise well-written. A finding of this type is at minimum P1; if the PRD text makes the erosion invisible through smooth wording, escalate to P0.
- produce minimum fix set
- say whether the PRD can enter review or final output

**Review gate** (V3.3 rules, see `05_context/prd-standards/checklist-v3.3.json` §gate_rules):
- **P0 always blocks** final output and review entry. Any single P0 = the PRD cannot proceed.
- **P1 blocks by default** unless the PM explicitly accepts the risk and records it in a 风险接受表 (reason, owner, follow-up action, deadline). See `04_templates/table-templates/risk-acceptance-table.md`.
- **P2 and P3 do not block.**
- **V3.3 review conclusion logic:**
  - P0阻塞 > 0 → 不可进入评审
  - P1风险 > 0 (unaccepted) → 默认不建议进入评审
  - 待检查项 > 0 → 检查未完成
  - 待补充项 > 0 → 需补充
  - All clear → 可进入评审

This replaces the per-module counting threshold from V2.0. The gate is now pass/fail based on whether ANY P0 or unaccepted P1 exists — not on how many are missing from a single module.

**Minimum output:** Produce both `06-审核报告.md` and `06-内容质量审查.json`. Even if the PRD appears flawless, every applicable checklist item in the JSON must contain at least one concrete `location + summary` evidence object. Every not-applicable or pending item must state a reason. A review that marks everything "pass" without evidence is a failed review.

→ Human decides which fixes to apply.

**Revision** (inline, not separate stage): Apply only confirmed review feedback. Outputs: revised PRD or patch-style section updates, revision summary, unresolved items, accepted risks, and whether the document can proceed.

**Content Consistency Sweep** (Node 4.5, executed after applying confirmed fixes and before Final-output check):

Goal: verify that the fix did not create cross-section contradictions, stale references, or unsynchronized sections. This is NOT a re-run of the full V3.3 checklist — it is a targeted sweep focused on the fix's blast radius.

Trigger: executed after ANY content fix, unless the only changes are typos, formatting, or layout that do not affect cross-references.

Method:

1. Determine the fix's blast radius: which sections were modified, which objects/roles/states/rules were changed.
2. Load `01_workflow/consistency-sweep-rules.json`. Map every actual change to a declared `change_routes.id`, then take the union of its `required_dimensions`. Do not infer dimension names from this prose.
3. Check every required dimension and record concrete `location + summary` evidence.
4. Classify each finding using the JSON `repair_boundaries`; do not maintain another classification list here.
5. Apply auto-fixes immediately. Do not accumulate auto-fixes into a new revision round — they are applied inline within the sweep.
6. Accumulate needs-confirm items (max 3 presented at once).
7. Output: consistency sweep report (table) + auto-fix patches applied + PM confirmation items (max 3) + sweep conclusion.

Gate: a P0 consistency issue (contradiction that would cause R&D to build the wrong thing) blocks final output. P1 issues default to auto-fix or PM confirmation. P2 (terminology drift, stale reference) auto-fix.

See `01_workflow/content-consistency-sweep.md` for the execution and recording method. The machine-readable rules remain authoritative.

**After sweep completes:** Update `09-run-log.md` 运行时间线 with sweep execution, and 修订记录 for any auto-fix patches applied.

**Executable content gate (mandatory):**

1. Update `06-内容质量审查.json` to reflect the final PRD, resolved findings, accepted P1 risks, and consistency-sweep status.
2. Run `scripts/prd-content-gate.py seal --review "{task-folder}/06-内容质量审查.json" --out "{task-folder}/06-content-gate.json"`.
3. Run `scripts/prd-content-gate.py validate --gate "{task-folder}/06-content-gate.json"`.
4. A non-zero exit code, missing receipt, stale hash, `block`, or `incomplete` conclusion blocks final output. Do not refresh a hash merely to make the gate pass; review the changed content, update evidence, and reseal.
5. Generate a plain-language decision sheet using `04_templates/content-gate-test-conclusion.md`. This is the primary artifact for user review. In order, it states whether work can continue, which business decisions require the user, which fixes will be applied directly, what happens after the reply, and when the work is complete. Severity labels, checklist counts, hashes, commands, and exit codes stay out of the main sections.
6. Run `scripts/validate-test-conclusion.py --file "{test-conclusion-path}"`. Missing sections, an invalid conclusion, technical jargon in the main sections, or a machine-only summary blocks completion of the reporting stage.

Human conclusion mapping is deterministic: `pass` with no accepted P1 → 可以继续; `pass` with accepted P1 → 可以继续，但有已接受风险; `block` → 暂时不能继续; `incomplete` or incomplete evidence → 还不能判断. Do not invent softer intermediate labels.

**Final-output check** (inline): The executable content gate returns `pass`; no unmarked assumptions, invented system capabilities, unverified data presented as fact, future plans mixed into current scope, technical or visual detail unless requested, unresolved P0, or unaccepted P1.

**After review completes:** Update `09-run-log.md` Node 完成记录 for Node 4: checklist modules swept, blocking items found, P0/P1 counts.

**Retrospect Trigger Check (inline, after every significant event):**

After user corrections, node completion, revision completion, and content consistency sweep, the agent MUST execute a Retrospect Trigger Check. This check does not replace any existing gate — it determines whether a quality issue is a one-off PRD fix or a reusable Skill gap.

See `05_context/optimization-standards/retrospect-trigger-rules.md` for the full trigger signal definitions, T0-T3 escalation levels, and root cause classification.

The check procedure:

1. For each significant event (user correction, node complete, revision applied, sweep finding), classify the event against the trigger signals in `05_context/optimization-standards/retrospect-trigger-rules.md`.
2. **Mandatory landing**: if the event triggers T1 or higher, the detection result MUST be written to `09-run-log.md` in the task folder — not just explained in the conversation. Use the `append_retrospect_event.py` recorder, or if the hook is not mounted, the Agent writes directly.
3. If user correction or high-risk signal: append to `09-run-log.md` 用户指正记录 — time, node, user quote excerpt, correction type, content involved, AI judgment (PRD-local or Skill-gap).
4. If classified as T1 or higher: append to `09-run-log.md` 复盘触发状态 — trigger ID, root cause, occurrence count, recent evidence, current level, suggested action.
5. Apply escalation rules from T0-T3:
   - T0: do not write. No action needed.
   - T2: mark `needs_retrospect_candidate`. At next Node 5 or user idle point, ask whether to enter retrospect.
   - T3: mark `needs_retrospect`. Generate `08-Skill复盘沉淀建议.md`. Each patch in the proposal STILL requires per-patch user confirmation before writing to any Skill file.
6. T3 does NOT auto-apply patches. T3 does NOT bypass `../03_gates/gates-and-retrospective.md` confirm→write loop.

**When NOT to escalate**: a one-time stylistic preference, a single PRD-local fix with no reusable pattern, or a correction that the user explicitly says is "just this once."

### 5. Retrospect (Conditional)

Triggered when a repeated quality problem appears or the user asks to improve the workflow.

**Before analysis, load evidence:**

1. Read `09-run-log.md` as primary process evidence — 修订记录, 痛点日志, 用户指正记录, 复盘触发状态. If run-log records reference decision IDs, read `02-决策账本.md` to reconstruct product-judgment changes.
2. Read the task folder's `06-审核报告.md` if it exists.
3. Do NOT rely on conversation memory as the primary evidence source. Run Log is the authoritative record.

**Analyze:**

1. Count root cause distribution from 修订记录 and 痛点日志:
   - 缺知识 → Context patch
   - 缺方法 → Skill patch  
   - 缺模板 → Template patch
   - 缺门禁 → Gate patch
   - 缺案例 → Example patch
   - 偶发 → 仅记录，不出 patch
2. **Threshold rule**: same root cause ≥ 2 occurrences → must propose a patch. ≥ 3 occurrences → patch priority is P0.
3. Classify each failure using the taxonomy in [Gates and Retrospective](03_gates/gates-and-retrospective.md).

Patch proposals must include observed failure, run evidence from `09-run-log.md`, why existing rules missed it, a proposed target, bounded change, regression risk, and adoption recommendation. Rejected-patch signals: turning one-off preference into a universal rule, expanding PRD scope instead of fixing clarity, duplicating an existing rule, making the entry skill heavier without improving reliability, or changing rules without evidence.

Execute the per-patch confirm→write loop defined in [Gates and Retrospective](03_gates/gates-and-retrospective.md) §复盘确认→写入闭环.

**After retrospect completes:** Update `09-run-log.md` 复盘消费 section: which 痛点 were consumed, which patches were produced, and whether each patch was written to its target file.

