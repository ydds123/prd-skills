# Workflow Protocol

This protocol keeps PRD work from jumping directly from vague input to polished but unreliable output.

## State Machine

```text
input_received
→ task_folder
→ thinking
→ writable_state_gate
→ decision_confirmation_gate
→ draft_v0
→ draft_confirmation_gate
→ full_prd
→ review
→ review_blocking_gate
→ revision_mode
→ final_output_gate
→ retrospective
```

## Stage Rules

### 1. Task Folder

Goal: make each PRD run file-backed and reviewable.

Required actions:

- create or reuse a task folder before drafting
- name it by date and PRD name
- write every material output into a Markdown or JSON file inside the task folder
- keep chat output as a summary or preview when files are being created

See [Task and Draft Rules](task-and-draft-rules.md).

### 2. Thinking

Goal: decide whether the requirement is writable.

Required actions:

- read all named files and user-provided context
- identify whether the user gave a problem, a proposed solution, or mixed material
- use 5W1H, Feynman technique, first principles, and Johari Window to improve input quality before synthesis
- use MECE, bottom-up pyramid grouping, SCQA, Issue Tree, and systems thinking to turn scattered input into product judgment
- infer product type only when useful
- produce a background understanding card
- produce a decision ledger
- list at most 3 blocking questions when needed

Forbidden:

- do not write PRD body
- do not ask generic questions that are not grounded in the material
- do not let uncertainty disappear into prose
- do not use pyramid-style polished output to cover weak input, missing evidence, or unexamined assumptions

### 3. Writable-State Gate

The requirement is writable only when these are clear enough:

- why this is being done
- who has the problem
- what this release covers
- what this release excludes
- what upstream and downstream systems or teams are affected
- which key choices are confirmed or explicitly pending

If not writable, stop and ask the smallest set of high-leverage questions.

### 4. Decision Confirmation

Use a decision ledger before PRD writing.

Each decision should include:

- decision topic
- recommended option
- alternatives
- rationale
- owner or confirmer
- status: confirmed, recommended default, pending, or risk accepted

AI may recommend defaults. Humans confirm key tradeoffs.

### 5. Draft v0

Draft v0 is a sketch, not a full PRD.

It should only establish:

- strategy layer: why this matters, for whom, and what success means
- scope layer: this release's in-scope items, out-of-scope items, role/scenario boundary, and open decisions
- main-flow skeleton: the normal path at a coarse level

Do not include exception flows, empty-state handling, permission matrices, data口径, acceptance criteria, self-test cases, API details, or implementation-like content in draft v0 unless the user explicitly asks.

### 6. Draft Confirmation Gate

If strategy, scope, or main flow are uncertain, pause for confirmation.

If they are already confirmed in source material, continue and state the basis.

### 7. Full PRD

Write the PRD body that fixes the main direction:

- background and real problem
- goals and success criteria
- scope and non-goals
- users and scenarios
- main flow
- core functions and rules

- exception handling
- empty, failure, conflict, duplicate, irreversible, and permission cases
- state changes
- data sources, fields by business meaning, and data cadence
- upstream/downstream impact
- acceptance criteria
- development self-test cases
- pending items and accepted risks

### 8. Independent Review

Review is not writing. The reviewer should:

- check clear boundary, explicit judgment, no guessing, and accurate information
- classify findings as P0/P1/P2/P3
- produce minimum fix set
- say whether the PRD can enter review or final output

### 9. Revision Mode

Revision uses confirmed review feedback.

Required outputs:

- revised PRD or patch-style section updates
- revision summary
- unresolved items
- accepted risks
- whether the document can proceed

### 10. Retrospective

Run retrospective when a repeated quality problem appears or the user asks to improve the workflow.

Classify the failure:

- missing knowledge: update Context
- missing method: update Skill
- missing format: update Template
- missing gate: update Gate
- missing example: update Example
- one-off issue: record in run history only

Do not apply patches without human confirmation.
