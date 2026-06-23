# Gates and Retrospective

## Writable-State Gate

Pass only when:

- background is understandable
- real user or role problem is clear
- in-scope and out-of-scope items are explicit enough
- key upstream/downstream dependencies are identified
- key decisions are confirmed or marked as pending
- there is no question that could overturn the main PRD direction

Fail action:

- stop PRD writing
- ask at most 3 priority questions
- explain which output each answer unlocks

## Decision-Confirmation Gate

Pass only when:

- important tradeoffs are confirmed by user material, or
- AI recommendations are labeled as recommended defaults, not facts

Fail action:

- produce decision ledger
- mark pending decisions
- do not hide pending decisions in prose

## Phase-1 Confirmation Gate

Pass only when:

- scope is stable
- main flow is stable
- affected roles are stable

Fail action:

- output phase 1 only
- ask for confirmation before phase 2

## Review-Blocking Gate

P0 always blocks final output.

P1 blocks by default unless the PM explicitly accepts risk and the PRD records:

- accepted risk
- reason
- owner
- follow-up condition

P2 and P3 do not block final output.

## Final-Output Gate

Before saying "final PRD", check:

- no unmarked assumptions
- no unverified data presented as fact
- no invented system capability
- no future plan mixed into current scope
- no technical implementation detail unless requested
- no visual design parameter unless requested
- no unresolved P0
- no unresolved unaccepted P1

## Skill-Update Gate

Retrospective can propose changes to reusable assets, but cannot apply them without human confirmation.

Valid patch categories:

| Failure type | Patch target |
|---|---|
| Missing business knowledge | Context |
| Missing method rule | Skill |
| Missing output slot | Template |
| Missing blocker | Gate |
| Missing comparable case | Example |
| One-off issue | Run history only |

Patch proposal must include:

- observed failure
- evidence from the run
- why existing rules missed it
- proposed target file or category
- bounded change
- regression risk
- adoption recommendation

Rejected patch signals:

- it turns one-off preference into a universal rule
- it expands PRD scope instead of fixing clarity
- it duplicates an existing rule
- it makes the entry skill heavier without improving reliability
- it changes rules without evidence
