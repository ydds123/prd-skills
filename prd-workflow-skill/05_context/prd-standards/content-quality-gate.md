# PRD Content Quality Gate

## Purpose

The gate answers one narrow question: **is there sufficient, current evidence that the final PRD completed the required content review and satisfies the blocking formula?**

It does not ask a script to understand business semantics. Semantic judgments remain the independent reviewer's responsibility.

## First-Principles Model

The final output can be trusted only when all four statements are true:

1. **Coverage**: every checklist item has an explicit disposition; no item disappears silently.
2. **Evidence**: every passed item points to a concrete PRD location and explains why it passes.
3. **Decision**: findings follow the P0/P1/P2/P3 rules, including complete P1 risk acceptance and the prohibition on accepting P0 risk.
4. **Freshness**: the PRD, machine-readable review, human-readable report, and checklist are the same files that were sealed.

The mechanism therefore uses two artifacts:

- `06-内容质量审查.json`: semantic review record, maintained by the independent reviewer.
- `06-content-gate.json`: generated receipt containing hashes, counts, and the recomputed gate conclusion.

## Mandatory Flow

### 1. Initialize the review record

```powershell
python scripts/prd-content-gate.py init `
  --prd "{task-folder}/05-完整PRDv1.md" `
  --review-report "{task-folder}/06-审核报告.md" `
  --out "{task-folder}/06-内容质量审查.json" `
  --complexity L3 `
  --writer-ref "writer-context-id" `
  --reviewer-ref "reviewer-context-id"
```

The command creates one pending disposition for every item in the current checklist. It must not overwrite an existing review record unless `--force` is explicitly used.

### 2. Perform semantic review

The independent reviewer must resolve every item:

| Situation | `applicability` | `result` | Required evidence |
|---|---|---|---|
| Applies and passes | `applicable` | `pass` | At least one `location + summary` evidence object |
| Applies and fails | `applicable` | `fail` | At least one linked active finding |
| Does not apply | `not_applicable` | `not_applicable` | A concrete reason |
| Cannot yet be checked | `pending` | `pending_check` | The reason it cannot be checked |
| Needs source material | `pending` | `pending_supplement` | The missing material or decision |

Finding rules:

- Severity cannot be lower than the linked checklist item's `priority`; escalation is allowed.
- P0 must be fixed and cannot be risk accepted.
- P1 is blocking unless `risk_accepted` records accepted-by, time, reason, owner, follow-up, and deadline.
- Fixed findings must include resolution evidence.
- Open P2/P3 findings are recorded but do not block final output.
- `review_revision` starts at `1`. When the PRD or checklist changes after a prior seal, the reviewer must recheck the affected content, update evidence, and increment this number before resealing. The seal command rejects an unchanged or non-incremented review record.

`writer_ref != reviewer_ref` is a process attestation, not cryptographic identity proof. A platform with separate agents or sessions should use their real IDs; a single-agent platform must at least use separately initialized writer and reviewer contexts.

### 3. Seal the reviewed output

Run after confirmed fixes and the content consistency sweep:

```powershell
python scripts/prd-content-gate.py seal `
  --review "{task-folder}/06-内容质量审查.json" `
  --out "{task-folder}/06-content-gate.json"
```

The command validates the review contract, recalculates the V3.3 blocking formula, and seals SHA-256 hashes for the PRD, review JSON, review report, and checklist. It returns a non-zero exit code for `block` or `incomplete` conclusions.

### 4. Validate before final output

```powershell
python scripts/prd-content-gate.py validate `
  --gate "{task-folder}/06-content-gate.json"
```

The final PRD must not be delivered when this command returns non-zero. Any content change after sealing invalidates the receipt and requires review of the change's impact, an updated consistency sweep when applicable, incrementing `review_revision`, and resealing.

### 5. Produce the plain-language decision sheet

After validation, generate a Markdown decision sheet using `04_templates/content-gate-test-conclusion.md`. It is the primary file for human review; the review JSON and gate receipt remain supporting evidence that users do not need to understand.

The conclusion must:

- map the machine result to exactly one plain status: 可以继续 / 可以继续，但有已接受风险 / 暂时不能继续 / 还不能判断;
- lead with the business conclusion and immediate next action;
- show only genuine business decisions that require user confirmation, one decision per item;
- give each decision a recommendation, reason, alternative, impact, and copyable reply format;
- distinguish fixes the workflow will apply directly;
- explain what happens after the reply and when the work is complete;
- keep severity labels, checklist counts, hashes, commands, exit codes, and revision identifiers out of the main sections; link technical evidence only in the optional final section.

Validate the result with:

```powershell
python scripts/validate-test-conclusion.py --file "{test-conclusion-path}"
```

A structurally incomplete conclusion or a machine-only summary means the reporting stage is incomplete even when the underlying gate receipt is valid.

## Hook Integration

Hooks are defense in depth, not the primary guarantee. The mandatory inline validation above remains authoritative because skill folders cannot guarantee that every host platform loads external hook configuration.

For hook execution, `.prd-workflow/current-task.json` must contain:

```json
{
  "task_folder": "absolute task folder",
  "run_log_path": "absolute path to 09-run-log.md",
  "content_gate_path": "06-content-gate.json"
}
```

Then run:

```powershell
python scripts/prd-content-gate.py validate --current-task
```

## Trust Boundary

The gate can prove completeness of the review record, evidence shape, blocking-rule application, and file freshness. It cannot prove that a reviewer interpreted the business correctly or wrote truthful evidence. That residual risk is controlled by independent review context, human sign-off for risk acceptance, and targeted forward tests.
