# PRD Quality Standard

Use this reference whenever the workflow writes, reviews, revises, or retrospectively improves a PRD.

## Root Definition

A PRD fixes product judgment into a shared answer that a team can execute, verify, and trace.

The only final quality standard:

```text
Readers should not need to come back to the PM for confirmation.
```

Readers include engineering, QA, design, operations, business owners, and the future PM who revisits the decision months later.

## Foundational Thinking Model

Use this model as the baseline for all PRD-related thinking. It defines how input becomes product judgment, and how product judgment becomes a readable PRD.

### Input Stage: Improve Signal Quality

Goal: reduce noise, widen the field of view, and expose blind spots before writing.

Use these tools:

| Tool | Purpose | PRD usage |
|---|---|---|
| 5W1H | Ensure the input covers who, what, when, where, why, and how. | Check whether the requirement has enough context to enter the writable-state gate. |
| Feynman technique | Test whether the agent can explain the requirement in simple language. | If the requirement cannot be explained plainly, the understanding is probably shallow. |
| First principles | Decompose the requirement into atomic facts and necessary assumptions. | Separate real facts from inherited solution language, habits, and surface assumptions. |
| Johari Window | Calibrate knowns, blind spots, hidden assumptions, and unknowns. | Ask for external feedback to reduce blind spots; make hidden assumptions explicit when they affect product judgment. |

Johari Window is a meta-tool across the whole workflow. In the input stage, it helps distinguish:

- open area: known to the user and visible to the agent
- blind area: visible in source material or external feedback, but not yet noticed by the user
- hidden area: known by the user or agent but not yet made explicit
- unknown area: not yet discovered by either side

### Processing Stage: Convert Input into Insight

Goal: turn scattered material into structured product judgment without losing creative emergence.

Use these tools:

| Tool | Purpose | PRD usage |
|---|---|---|
| MECE | Ensure categories are mutually exclusive and collectively exhaustive. | Decompose problem space, feature scope, scenario groups, and risk categories. |
| Pyramid principle, bottom-up | Group facts into supporting modules before writing the top-level conclusion. | Turn evidence, examples, and user feedback into clear arguments. |
| SCQA | Build a situational narrative before the answer. | Clarify situation, complication, question, and answer for background sections. |
| Issue Tree | Break a vague problem into answerable branches. | Structure open questions, scope choices, and decision ledger entries. |
| Systems thinking and causal loops | Reveal nonlinear relationships and feedback effects. | Identify dependencies, downstream impact, operational loops, and second-order risks. |
| Johari Window extension | Reflect on hidden knowledge and blind spots during synthesis. | Decide what must be made explicit before the PRD can be considered writable. |

In this stage, MECE is core. It prevents duplicated scope, missing scenarios, and overlapping classifications. Pyramid principle is used first as bottom-up induction, then later as top-down expression.

### Output Stage: Deliver Value Clearly

Goal: make product judgment immediately understandable, executable, and reviewable.

Use these tools:

| Tool | Purpose | PRD usage |
|---|---|---|
| Pyramid principle, top-down | Put the core answer first, then support it layer by layer. | Make every PRD section lead with the conclusion or decision before details. |
| MECE | Keep output complete and non-redundant. | Maintain clean sectioning for scope, flows, rules, exceptions, and acceptance. |
| PREP or STAR | Improve narrative fluency when explanation is needed. | Use PREP for principles and recommendations; use STAR for scenario-based evidence. |
| Audience orientation | Adjust information density by reader role. | Use Johari Window awareness to avoid overexposing hidden context or ignoring reader blind spots. |

Gold rule: Pyramid principle and MECE are the output foundation, but output quality depends on input quality. Do not use polished structure to hide weak input.

## Four Core Criteria

| Criterion | Meaning | Common failure |
|---|---|---|
| Clear boundary | This release's scope, non-goals, roles, scenarios, data, version, and responsibility are explicit. | Scope creep, "does this belong to this phase?" |
| Explicit judgment | Rules, defaults, exceptions, dependencies, owners, and tradeoffs are visible. | Each team invents its own interpretation. |
| No guessing | Triggers, entries, inputs, outputs, states, feedback, acceptance, and self-tests are executable. | Readers ask "is this what you meant?" |
| Accurate information | Facts, assumptions, estimates, pending items, data sources, and system capability boundaries are separated. | Unconfirmed content becomes implementation truth. |

## Must-Writes

Every PRD must include:

- real problem and affected user or role
- this release's goal
- in-scope items
- out-of-scope items
- main flow
- core rules and defaults
- exceptions and empty states
- role and permission rules for B-end needs
- acceptance criteria
- pending items
- known assumptions

## Do Not Write

Do not put these into a PRD unless the user explicitly asks for a technical or visual design document:

- database tables
- API field details
- code logic
- colors, pixels, font sizes, or exact component styling
- unverified external data
- future plans mixed into current scope
- vague phrases such as "optimize", "friendly", "reasonable", or "intelligent" without measurable criteria

## Complexity Levels

| Level | Need type | PRD requirement |
|---|---|---|
| L1 | Copy, field, config, or small rule change | Change note with change point, impact scope, rule, and acceptance. |
| L2 | Single page or single flow | Standard PRD covering background, scope, flow, rules, exceptions, and acceptance. |
| L3 | Multi-role, multi-state, or multi-exception feature | Complete PRD covering roles, permissions, states, exceptions, upstream/downstream, and self-test. |
| L4 | Cross-system, permission, data, or AI capability | Complete PRD plus risk review and AI implementation readiness check. |

Complexity can shorten or lengthen the document, but it cannot lower the standard for product judgment.

## Blocking Severity

| Severity | Meaning | Gate behavior |
|---|---|---|
| P0 | Fatal issue: real problem unclear, scope unclear, core flow not executable, key decision missing, unconfirmed fact treated as fact, context conflict, or serious product/tech/design boundary violation. | Must block final output. |
| P1 | High risk: missing non-goals, exception handling, permissions, state changes, acceptance, upstream/downstream impact, or data source. | Blocks by default unless PM explicitly accepts risk. |
| P2 | Quality issue: local ambiguity, weak example, coarse acceptance, poor organization, or minor terminology drift. | Does not block but should be fixed before review when possible. |
| P3 | Optimization suggestion: readability, order, example, or format improvement. | Never blocks. |

## AI Implementation Readiness

If the PRD may be used by AI to implement or prototype, check:

- no hidden default values
- no unmarked assumptions
- input, processing, and output are clear for each core feature
- empty, failure, conflict, permission, low-confidence, and wrong-result handling are defined
- acceptance criteria can become tests or self-check cases
