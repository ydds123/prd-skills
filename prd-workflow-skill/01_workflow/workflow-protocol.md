# Workflow Protocol

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

**Draft check** (inline, not separate gate): If strategy, scope, or main flow are uncertain, pause for confirmation. If they are already confirmed in source material, continue and state the basis.

→ Human confirms scope and main flow are correct. Do not expand to full PRD before this confirmation.

### 3. Fill Details

Goal: expand the accepted frame into a complete PRD body.

**Before writing:**

1. Verify `09-run-log.md` exists in the task folder. If not, create it from the template at `04_templates/run-log.md`. Append a Node 3 start entry to 运行时间线.
2. Read `09-run-log.md` — particularly 痛点日志 — to avoid repeating mistakes from prior runs.
3. Load `05_context/prd-standards/checklist-v3.3.json` (V3.3).
4. Identify which checklist items apply: filter by `complexity` (L1-L4 matches the PRD's complexity level) and `condition` (domain-specific conditions like "has multi-role" or "has delete action").
5. For each applicable item, use `question`, `pass_criteria`, and `failure_signal` as the writing guide. The `suggested_format` field tells you which table template to use (see `04_templates/table-templates/`).
6. Every gate item (`hierarchy: "gate"`) must either be addressed in the PRD or explicitly marked as not applicable with a reason.
7. Do not dump the checklist into the PRD. Use it as a silent writing guide.

Write:

- background and real problem
- goals and success criteria
- scope and non-goals
- users and scenarios
- main flow
- core functions and rules
- exception handling (use the table structure: 触发条件 | 处理逻辑 | 引导提示 | 恢复机制)
- empty, failure, conflict, duplicate, irreversible, and permission cases
- state changes
- data sources, fields by business meaning, and data cadence
- upstream/downstream impact
- acceptance criteria
- development self-test cases
- pending items and accepted risks

**After Fill Details completes (or after each revision round ends):**

1. Update `09-run-log.md` Node 完成记录 for Node 3: which checklist items were applied (by complexity and condition filters), how many gate items were addressed vs. skipped.
2. If any content was revised in response to feedback, append to 修订记录: round number, trigger, scope, root cause classification (缺知识/缺方法/缺模板/缺门禁/缺案例/偶发), and which checklist module was involved.
3. If a revision reveals a systemic gap (something the writer "shouldn't have missed" on first pass), append to 痛点日志: what was missed, why it was missed on the first pass, which checklist module covers it, and severity.

**Decision intake after corrections (inline):**

When a user correction, review finding, or sweep discovery changes product judgment:

1. Append the decision to `02-决策账本.md` with a new decision ID.
2. If the correction changes a prior decision, mark the old entry `superseded` and reference the new ID.
3. Record the event in `09-run-log.md` 运行时间线.
4. If triggered by user correction, also record in 用户指正记录 with the decision ID.
5. If triggered by review or sweep revision, record in 修订记录 with the decision ID.

Do NOT duplicate full decision content in `09-run-log.md`. Decision changes go to `02-决策账本.md`. Process evidence goes to `09-run-log.md`.

**Table format conventions** (see `05_context/writing-standards/table-format-conventions.md`):
- Query condition tables: 查询字段 | 组件类型 | 查询精度 | 说明
- Form field tables: 字段名称 | 字段类型 | 是否必填 | 引导文案 | 字段说明
- Each core function MUST include an interaction logic table (步骤 | 触发起点 | 用户动作 | 系统响应 | 业务规则) and an exception handling table (触发条件 | 处理逻辑 | 引导提示 | 恢复机制).

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

Required actions:

- **subtract first**: before checking completeness, ask of every feature: "if we skip this, what breaks?" If the answer is "the user can still manage, just less conveniently," flag it as potential over-design.
- **operational completeness sweep**: for each applicable checklist item (filtered by `complexity` and `condition`), check against the PRD using `question`, `pass_criteria`, and `failure_signal`. When an applicable item is missing:
  - **Severity follows `priority`**: the item's `priority` field (P0/P1/P2/P3) determines the finding severity.
  - **`hierarchy` determines obligation**: gate = must check and address (or mark 不适用); extended = check if condition is met; advisory = suggested but not required.
  - **Fallback when `priority` is empty**: gate → P0, extended → P1, advisory → P3.
  - Example: C56 (空态处理) is `hierarchy: "extended", priority: "P0"` → missing = P0 block, not P1.
- check clear boundary, explicit judgment, no guessing, and accurate information
- classify findings as P0/P1/P2/P3
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

**Minimum output:** Even if the PRD appears flawless, the reviewer must produce at least one concrete observation per applicable checklist module — either a finding, or an explicit statement of why no finding exists for that module. A review that marks everything "pass" without evidence is a failed review.

→ Human decides which fixes to apply.

**Revision** (inline, not separate stage): Apply only confirmed review feedback. Outputs: revised PRD or patch-style section updates, revision summary, unresolved items, accepted risks, and whether the document can proceed.

**Content Consistency Sweep** (Node 4.5, executed after applying confirmed fixes and before Final-output check):

Goal: verify that the fix did not create cross-section contradictions, stale references, or unsynchronized sections. This is NOT a re-run of the full V3.3 checklist — it is a targeted sweep focused on the fix's blast radius.

Trigger: executed after ANY content fix, unless the only changes are typos, formatting, or layout that do not affect cross-references.

Method:

1. Determine the fix's blast radius: which sections were modified, which objects/roles/states/rules were changed.
2. Use the blast-radius table in `01_workflow/content-consistency-sweep.md` to select which of the 10 consistency dimensions to sweep. Do NOT run all 10 — only those affected by the blast radius.
3. For each selected dimension, check per the dimension's criteria.
4. Classify each finding: `can-auto-fix` (PRD-internal evidence exists, no new product facts) / `needs-pm-confirm` (involves scope/permission/state/default/data decisions) / `forbidden` (would fabricate unconfirmed facts).
5. Apply auto-fixes immediately. Do not accumulate auto-fixes into a new revision round — they are applied inline within the sweep.
6. Accumulate needs-confirm items (max 3 presented at once).
7. Output: consistency sweep report (table) + auto-fix patches applied + PM confirmation items (max 3) + sweep conclusion.

Gate: a P0 consistency issue (contradiction that would cause R&D to build the wrong thing) blocks final output. P1 issues default to auto-fix or PM confirmation. P2 (terminology drift, stale reference) auto-fix.

See `01_workflow/content-consistency-sweep.md` for the full 10-dimension checklist, auto-fix boundary rules, output format, and real example.

**After sweep completes:** Update `09-run-log.md` 运行时间线 with sweep execution, and 修订记录 for any auto-fix patches applied.

**Final-output check** (inline): No unmarked assumptions, no invented system capabilities, no unverified data presented as fact, no future plans mixed into current scope, no technical or visual detail unless requested, no unresolved P0, no unaccepted P1.

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

1. Read `09-run-log.md` as primary evidence — 修订记录 (revision rounds and root causes), 痛点日志 (systemic gaps), 决策追加 (mid-stream decisions).
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
