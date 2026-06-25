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
| Retrospect (on demand) | Confirming which patch proposals should modify reusable rules | Classifying failure types and proposing bounded patches |

The four things only humans can hold: problem definition, direction, tradeoffs, and quality sign-off. The rest is volume work with clear right answers — AI territory.

## State Machine

```text
input_received
→ [boot] task_folder
→ [1] alignment → human confirms direction
→ [2] draft_body → human confirms scope & main flow
→ [3] fill_details
→ [4] review → human decides fixes
→ [retrospect] on demand only
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

1. Verify `09-run-log.md` exists in the task folder. If not, create it from the template at `05_context/run-log.md`. Append a Node 3 start entry to 运行时间线.
2. Read `09-run-log.md` — particularly 痛点日志 — to avoid repeating mistakes from prior runs.
3. Load `references/operational-completeness-checklist.json`.
4. Match the PRD's feature types against `load_map.mappings` to identify which checklist modules to load.
5. For each matched module, load its `items` array filtered by `level: "blocking"`. These are the questions that R&D cannot work without answers to.
6. As each functional section is expanded, cross-reference the injected items — every blocking item must either be written into the PRD or explicitly marked "不适用" with a reason.
7. Do not dump the checklist into the PRD. Use it as a silent writing guide. The output the reader sees is the filled-out PRD, not a questionnaire.

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

1. Update `09-run-log.md` Node 完成记录 for Node 3: which checklist modules were loaded, how many blocking items were addressed vs. skipped.
2. If any content was revised in response to feedback, append to 修订记录: round number, trigger, scope, root cause classification (缺知识/缺方法/缺模板/缺门禁/缺案例/偶发), and which checklist module was involved.
3. If a revision reveals a systemic gap (something the writer "shouldn't have missed" on first pass), append to 痛点日志: what was missed, why it was missed on the first pass, which checklist module covers it, and severity.

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
- Your only loyalty is to the quality standard (`references/prd-quality-standard.md`) and the completeness checklist (`references/operational-completeness-checklist.json`).
- You were not in the room when this PRD was written. Every claim in the PRD is a claim to be verified, not a fact to be assumed correct.
- Default stance: skeptical. If the PRD makes something sound easy, ask "what breaks when this fails?"

**Review materials (load before starting):**
1. Read `09-run-log.md` in the task folder — focus on 痛点日志 and 修订记录. These tell you what the writer already knows they missed and why. Cross-check: did the writer actually fix those gaps, or just acknowledge them?
2. `references/prd-quality-standard.md` — the four criteria and blocking severity rules
3. `references/operational-completeness-checklist.json` — load the `gate_rules.node4_review` thresholds and the checklist modules matching the PRD's feature types via `load_map.mappings`

Required actions:

- **subtract first**: before checking completeness, ask of every feature: "if we skip this, what breaks?" If the answer is "the user can still manage, just less conveniently," flag it as potential over-design.
- **operational completeness sweep**: for each checklist module loaded, check every `level: "blocking"` item against the PRD. A blocking item that is neither addressed nor marked "不适用" is a P1 gap.
- check clear boundary, explicit judgment, no guessing, and accurate information
- classify findings as P0/P1/P2/P3
- produce minimum fix set
- say whether the PRD can enter review or final output

**Review gate** (inline): 
- P0 always blocks final output.
- P1 blocks by default unless the PM explicitly accepts risk and the PRD records the accepted risk, reason, owner, and follow-up condition.
- P2 and P3 do not block.
- **Checklist threshold**: ≥ `gate_rules.node4_review.blocking_threshold.per_module.max_blocking_miss` blocking items missed in a single module → mark that module P0. ≥ `gate_rules.node4_review.blocking_threshold.total.max_p1` total P1 accumulated → reject the PRD.

**Minimum output:** Even if the PRD appears flawless, the reviewer must produce at least one concrete observation per applicable checklist module — either a finding, or an explicit statement of why no finding exists for that module. A review that marks everything "pass" without evidence is a failed review.

→ Human decides which fixes to apply.

**Revision** (inline, not separate stage): Apply only confirmed review feedback. Outputs: revised PRD or patch-style section updates, revision summary, unresolved items, accepted risks, and whether the document can proceed.

**Final-output check** (inline): No unmarked assumptions, no invented system capabilities, no unverified data presented as fact, no future plans mixed into current scope, no technical or visual detail unless requested, no unresolved P0, no unaccepted P1.

**After review completes:** Update `09-run-log.md` Node 完成记录 for Node 4: checklist modules swept, blocking items found, P0/P1 counts.

### 5. Retrospect (On Demand)

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
3. Classify each failure using the taxonomy in [Gates and Retrospective](references/gates-and-retrospective.md).

Patch proposals must include observed failure, run evidence from `09-run-log.md`, why existing rules missed it, a proposed target, bounded change, regression risk, and adoption recommendation. Rejected-patch signals: turning one-off preference into a universal rule, expanding PRD scope instead of fixing clarity, duplicating an existing rule, making the entry skill heavier without improving reliability, or changing rules without evidence.

Execute the per-patch confirm→write loop defined in [Gates and Retrospective](references/gates-and-retrospective.md) §复盘确认→写入闭环.

**After retrospect completes:** Update `09-run-log.md` 复盘消费 section: which 痛点 were consumed, which patches were produced, and whether each patch was written to its target file.
