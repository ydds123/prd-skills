# Retrospect Trigger Rules

> Belongs to: `05_context/optimization-standards/`  
> Purpose: Define the trigger signals, escalation levels, and boundaries for the Retrospect Trigger Detector  
> Governed by: `../../03_gates/gates-and-retrospective.md` — all Skill file modifications still require per-patch user confirmation  
> Version: v1.0.0

---

## Core Principle

The trigger detector captures signals, the recorder writes them to run-log, and the Agent escalates by level. The confirm→write loop in `../../03_gates/gates-and-retrospective.md` remains the only path to modifying Skill reusable files.

```
Detector (retrospect_trigger.py) outputs JSON
  → Recorder (append_retrospect_event.py) writes to 09-run-log.md
  → Agent reads run-log, determines escalation
  → T3: Agent generates 08-Skill复盘沉淀建议.md
  → User confirms per-patch → Agent writes to target Skill file
```

**The recorder writes only to `09-run-log.md`.** It never touches PRD body content or Skill files. If the pipeline hook is not mounted, the Agent itself performs the write as part of the Retrospect Trigger Check defined in `../../01_workflow/workflow-protocol.md`.

## Trigger Signals

### 1. User Correction

User explicitly contradicts or corrects the Agent.

Typical expressions: 不对, 不是这个意思, 你理解错了, 我刚才说的是, 我之前说过, 怎么又, 不要这样, 这个不能这么写, 应该放到, 这里应该是, 你漏了, 这里少了.

**Default level: T1.**
**Action**: append to run-log 用户指正记录. Judge whether the correction exposes a reusable rule gap.

### 2. Retrospect Intent

User explicitly asks to improve the Skill.

Typical expressions: 优化下skill, 完善下skill, 写进Skill, 这个要沉淀, 下次遇到这种情况, 以后都要, 这里应该有门禁, 这个应该作为模板, 这是skill待完善吗.

**Default level: T2.**
**Action**: append to run-log 复盘触发状态, mark `needs_retrospect_candidate`. Node 5 asks user whether to enter retrospect.

### 3. AI Self-Discovery

Agent discovers a gap during its own review or sweep.

Scenarios: checklist item should have caught this but didn't; Node 3 missed a gate item; Node 4 caught something that should have been caught earlier; content consistency sweep finds recurring stale references from the same root cause.

**Default level**: P2/P3 → T1. P1 systemic → T2. P0 gate failure → T3.
**Action**: write to run-log per level.

### 4. High-Risk Signals

Keywords: P0, P1, 阻塞, 漏了, 没覆盖, 不一致, 前后矛盾, 旧说法, 术语混用, 范围冲突, 权限冲突, 状态冲突, 数据口径冲突, 门禁失效, checklist未覆盖.

**Default level**: context-dependent. If linked to P0 gate failure → T3. If P1 systemic → T2.

## T0-T3 Escalation Levels

| Level | Meaning | Trigger | Action |
|-------|---------|---------|--------|
| T0 | No action | Single stylistic preference, local PRD fix | Do not enter retrospect candidate |
| T1 | Observe | User correction ×1; same root cause ×1; P2/P3 self-discovery | Write to run-log 用户指正记录 + 复盘触发状态. Mark "观察中" |
| T2 | Retrospect candidate | Same root cause ×2; P1 systemic; user express retrospect intent | Write to run-log, mark `needs_retrospect_candidate`. Agent asks user whether to retrospect at Node 5 |
| T3 | Mandatory retrospect proposal | Same root cause ×3+; any P0 gate failure | Write to run-log, mark `needs_retrospect`. Generate `08-Skill复盘沉淀建议.md`. Still requires per-patch user confirmation |

**Rules**:
- T3 forces generation of the retrospect PROPOSAL, not application of patches.
- Per-patch user confirmation is still required at every level.
- A one-time preference must never auto-escalate to a universal rule.

## Root Cause Classification

Reuses the existing taxonomy from `../../03_gates/gates-and-retrospective.md`. No second classification system.

| Root cause | Meaning | Patch target |
|-----------|---------|-------------|
| 缺知识 | Missing business knowledge, industry context | context / examples |
| 缺方法 | Missing analysis method, workflow rule, judgment path | workflow-protocol / SKILL |
| 缺模板 | Missing table template, output slot, fixed structure | writing-standards |
| 缺门禁 | Gate should have blocked but didn't, check should have run but didn't | gates / checklist |
| 缺案例 | Rule exists but lacks example → Agent applies it incorrectly | examples |
| 偶发 | One-off execution deviation | run-log only, no patch |

## Auto-Record vs Human-Confirm Boundary

**Decision boundary**: The trigger writes process evidence to `09-run-log.md`. If the triggering event changes product judgment, the workflow protocol must also append a decision entry to `02-决策账本.md`. The trigger itself does not write decision entries.

| Action | Auto? | Rule |
|--------|-------|------|
| Write to run-log 用户指正记录 | Yes | No confirmation needed |
| Write to run-log 复盘触发状态 | Yes | No confirmation needed |
| Mark `needs_retrospect_candidate` | Yes | No confirmation needed |
| Mark `needs_retrospect` | Yes | No confirmation needed |
| Generate `08-Skill复盘沉淀建议.md` | Yes (at T3) | Generation is auto; application is NOT |
| Apply a patch to any Skill file | **NO** | Must ask per-patch |
| Elevate one-time preference to rule | **NO** | Must classify as ≥2 occurrences first |
| Batch-confirm "apply all" | **NO** | One patch, one question |

## Workflow Protocol Integration

Per `../../01_workflow/workflow-protocol.md`, Retrospect Trigger Check is called at:

1. **After user correction** — judge PRD fix vs Skill gap
2. **After each Node completes** — scan for repeats, gate failures
3. **After revision completes** — did this revision expose a template/method/gate gap?
4. **After content consistency sweep** — are recurring inconsistencies a Skill defect?

See `../../01_workflow/workflow-protocol.md` for the inline check procedure at each point.

## Relation to Existing Mechanisms

| Mechanism | Trigger's relationship |
|-----------|----------------------|
| `09-run-log.md` | Trigger writes events; run-log is the persistent evidence container |
| `08-Skill复盘沉淀建议.md` | Trigger decides whether to enter retrospect; 08- is the output artifact |
| `../../03_gates/gates-and-retrospective.md` | Trigger does NOT bypass the confirm→write gate |
| `../../01_workflow/workflow-protocol.md` | Protocol calls the trigger check; trigger rules are defined here |
| Content Consistency Sweep | Sweep finds PRD issues; trigger judges whether those issues are Skill defects |
| V3.3 checklist | Still the primary quality gate. Trigger does not add a second pass/fail standard |
