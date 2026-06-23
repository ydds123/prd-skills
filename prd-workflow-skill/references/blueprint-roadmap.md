# Blueprint Roadmap

This roadmap maps the original PRD workflow repository blueprint into staged implementation work.

## Current Position

Current package status: MVP / Phase 1 partial.

Already implemented:

- total-control `SKILL.md`
- quality standard reference
- workflow protocol reference
- output contract reference
- task-folder and draft-v0 rules
- trigger evals
- manifest and agent interface metadata
- one real PRD task folder example

Not yet implemented:

- full `00_meta` directory
- full `01_workflow` directory
- independent `02_skills` sub-skill packages
- independent `03_gates` files
- full `04_templates` library
- expanded `05_context` standards
- `06_examples` golden cases
- `07_runs` run index and state files
- `08_quality` regression samples
- `09_references` source absorption records

## Staged Plan

| Phase | Goal | Add when | Main outputs |
|---|---|---|---|
| Phase 1 | Stabilize MVP workflow | Now | `SKILL.md`, references, trigger evals, task folders |
| Phase 2 | Add writing templates and complexity routing | After 2-3 PRD tasks expose repeated draft/full-PRD needs | `04_templates/prd/`, L1-L4 templates, stronger draft/full PRD contracts |
| Phase 3 | Add review gates | After at least one full PRD review run | `03_gates/`, review severity files, P0/P1 gate files |
| Phase 4 | Add retrospective and improvement governance | After repeated failures appear across tasks | failure taxonomy, patch proposal templates, adoption gates |
| Phase 5 | Add examples and regression quality | After 2-3 completed PRD task folders exist | `06_examples/`, `08_quality/`, golden/bad cases |
| Phase 6 | Add semi-automated run state | After manual task folders become repetitive | `07_runs/`, `state.json`, `run-index.md`, gate-result schema |

## Expansion Rule

Do not create blueprint directories merely because the blueprint lists them. Create a directory when one of these is true:

- at least two task runs need the same reusable structure
- a current reference file becomes too broad and needs separation
- a gate needs independent review or regression
- a template is reused across PRD tasks
- a real example can prevent a repeated mistake

## Near-Term Next Moves

1. Keep using task folders for real PRD runs.
2. Collect 2-3 draft v0 and full PRD examples.
3. Promote repeated draft structures into `04_templates`.
4. Promote repeated review failures into `03_gates`.
5. Promote representative completed tasks into `06_examples`.
