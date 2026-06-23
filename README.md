# PRD Skills Workspace

This repository is a working context package for PRD-related agent skills.

Current status: framework-first, not complete.

The main active skill is `prd-workflow-skill`, which defines a gated PRD workflow for:

- write-before alignment
- task folder creation
- background understanding
- decision ledger
- writable-state checking
- draft v0
- full PRD v1
- independent review
- revision and retrospective improvement

The surrounding files are kept as external context for future enrichment. They are intended to help refine `prd-workflow-skill` over time rather than represent a finished production skill set.

## Key Files

| Path | Purpose |
|---|---|
| `prd-workflow-skill/` | Current PRD workflow skill package |
| `prd-definition-quality-standard.md` | Source material for PRD quality standards |
| `prd-workflow-skill-repository-design.md` | Source material for the skill repository design |
| `create-prd-skill/` | Earlier PRD creation skill reference |
| `check-prd-skill/` | Earlier PRD review/checking skill reference |
| `SkillOpt/` | External reference material for skill optimization ideas |

## Boundary

This repository is public by design, but it should not contain private project PRDs, credentials, customer data, or internal implementation details.

