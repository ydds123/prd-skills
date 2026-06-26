# Task and Draft Rules

Use this reference when a PRD workflow run creates or updates a PRD artifact.

## Task-Based Working Rule

Every PRD run should have a task folder. The folder is the durable workspace for drafts, context, decisions, review reports, and later revisions.

Naming:

```text
YYYY-MM-DD-{PRD名称}
```

Examples:

```text
2026-06-19-查询表格菜单
2026-06-19-站内信模板管理
```

Default location:

```text
PRD tasks/YYYY-MM-DD-{PRD名称}/
```

If the project already has a task or run root, use the local convention and state the chosen path.

## Folder Structure

```text
YYYY-MM-DD-{PRD名称}/
├─ 任务说明.md
├─ 00-上下文证据.md
├─ 01-背景理解卡.md
├─ 02-决策账本.md
├─ 03-可写状态判断.md
├─ 04-PRD草案v0.md
├─ 05-完整PRDv1.md
├─ 06-审核报告.md
├─ 07-修订记录.md
├─ 08-复盘建议.md
├─ 09-run-log.md
└─ assets/
```

| Path | Purpose | Create when |
|---|---|---|
| `任务说明.md` | Task goal, source links, status, next action | Always |
| `00-上下文证据.md` | Source materials, code/page evidence, assumptions, unresolved source gaps | Always |
| `01-背景理解卡.md` | Background understanding card | After thinking |
| `02-决策账本.md` | Confirmed, recommended, pending, and risk-accepted decisions | After thinking |
| `03-可写状态判断.md` | Writable-state judgment and blocking questions | Before draft |
| `04-PRD草案v0.md` | First PRD draft Markdown | When writing a draft |
| `05-完整PRDv1.md` | Full PRD expanded from accepted draft frame | After draft frame is accepted |
| `06-审核报告.md` | Independent review report | After review |
| `07-修订记录.md` | Revision summary, unresolved items, accepted risks | After revision |
| `08-复盘建议.md` | Skill retrospective patch proposals | After retrospect |
| `09-run-log.md` | Cross-node running timeline, decision append, revision root causes, pain point log | Always — created at Boot from `04_templates/run-log.md` template |
| `assets/` | Screenshots, exported diagrams, source images | Only when assets exist |

Do not create empty stage files just to look complete. A task folder should show the true workflow state. **Exception**: `09-run-log.md` is always created at Boot because it is written to throughout all subsequent nodes.

Task artifacts are user-facing files, so use Chinese filenames by default. Keep English filenames mainly for machine-facing skill package files such as `SKILL.md`, `manifest.json`, `agents/interface.yaml`, `evals/*.json`, and code scripts.

## Content Principles

Every file follows two principles:

- Pyramid principle: conclusion first, then grouped reasons, then evidence.
- MECE principle: sibling sections do not overlap and do not leave obvious gaps for the current layer.

Use section names that reveal the layer of thinking. Do not mix strategic why, scope what, interaction how, technical how, and acceptance proof in the same block.

## Function Type Classification

In the scope layer, classify the feature before expanding PRD content. The classification affects what the full PRD should emphasize later.

Primary types:

| Type | Meaning | Later PRD emphasis |
|---|---|---|
| 台账型功能 | Maintains records, lists, details, create/edit/delete, search, and configuration. | Object definition, list fields, CRUD boundary, lifecycle, ownership, and basic operations. |
| 业务型功能 | Drives a business process, decision, approval, collaboration, or state transition. | Roles, business rules, process branches, state changes, exceptions, and responsibility. |
| 统计型功能 | Presents metrics, aggregates, rankings, dashboards, or analysis views. | Metric definition, statistical口径, time range, dimensions, freshness, and interpretation. |

Scope tables should group capabilities by feature characteristics. Preferred grouping:

1. list-page capabilities
2. regular CRUD / ledger-layer capabilities
3. business-layer capabilities
4. statistics-layer capabilities when metrics are present

For mixed features, mark the dominant type first and identify secondary capabilities as separate rows. Do not flatten all capabilities into one undifferentiated list.

## Draft v0 Boundary

Draft v0 is a sketch. It is the product equivalent of drawing the frame before drawing the details.

Use the user experience five elements as a layer guard:

- include strategy layer: user, problem, value, success signal
- include scope layer: in scope, out of scope, key roles/scenarios, open decisions
- include only a coarse main-flow skeleton when it helps explain the scope
- exclude structure-layer details unless needed to make scope intelligible
- exclude skeleton-layer and surface-layer detail

Draft v0 must not include these by default:

- exception flows
- empty states and fallback handling
- permission or responsibility matrix
- data口径, API, database, or implementation detail
- acceptance criteria
- development self-test cases
- detailed field-level behavior

Those belong in full PRD mode after the draft frame is accepted.

## Draft v0 Output Shape

```md
# {PRD名称} PRD 草案 v0

## 1. 结论先行

## 2. 战略层

### 2.1 用户与问题
### 2.2 目标与成功信号

## 3. 范围层

### 3.1 功能类型判断
### 3.2 本期范围
按列表页能力、常规 CRUD / 台账层能力、业务层能力、统计层能力分组。
### 3.3 本期不做
### 3.4 关键角色与场景

## 4. 主流程骨架

## 5. 待确认决策
```

Keep it short. If the draft starts to contain review, testing, permissions, exception handling, or data口径, it has already crossed into full PRD mode.
