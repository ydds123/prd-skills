# Output Contracts

Use these contracts to keep outputs stable and reviewable.

## Universal Content Principles

Every generated file must follow:

- Pyramid principle: conclusion first, then key arguments, then supporting detail.
- MECE principle: sibling sections should be mutually exclusive and collectively exhaustive for the current layer.
- Layer discipline: do not mix strategy, scope, structure, interaction detail, technical detail, and acceptance detail in the same section.
- Draft restraint: a draft should sketch the frame before filling the muscles.
- Feature-type clarity: the scope layer must classify whether the feature is mainly 台账型, 业务型, 统计型, or a mixed feature.

For PRD draft v0, only write strategy layer, scope layer, and main-flow skeleton. Keep exception flows, empty states, permissions, data口径, acceptance criteria, and self-test cases for full PRD mode.

## PRD Task Folder

```text
YYYY-MM-DD-{prd-name}/
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

Minimum first-run files:

- `任务说明.md`: task goal, source links, current status, next action
- `00-上下文证据.md`: source materials and evidence notes
- `09-run-log.md`: created from `04_templates/run-log.md` template at Boot — running timeline, decision append, revision root causes, pain point log
- `04-PRD草案v0.md`: the draft Markdown file (created at Node 2)

Use additional files only when that stage has actually happened.

## Background Understanding Card

```md
## 背景理解卡

| 项 | 内容 |
|---|---|
| 需求一句话 |  |
| 真实问题 |  |
| 目标用户 / 角色 |  |
| 当前场景 |  |
| 本期目标 |  |
| 初步范围 |  |
| 明确不做 |  |
| 上下游影响 |  |
| 关键风险 |  |
| 信息缺口 |  |
```

## Context Reading List

```md
## 上下文读取清单

| 材料 | 读取目的 | 使用结论 | 仍不确定 |
|---|---|---|---|
|  |  |  |  |
```

## Decision Ledger

```md
## 决策账本

| 决策项 | 推荐结论 | 备选方案 | 依据 | 状态 | 确认人 |
|---|---|---|---|---|---|
|  |  |  |  | confirmed / recommended / pending / risk accepted |  |
```

## Writable-State Report

```md
## 可写状态判断

结论：可写 / 暂不可写 / 可写但需标记待确认

| 检查项 | 结论 | 依据 | 缺口 |
|---|---|---|---|
| 背景 |  |  |  |
| 真实问题 |  |  |  |
| 范围与非目标 |  |  |  |
| 上下游影响 |  |  |  |
| 关键决策 |  |  |  |
| 阻塞问题 |  |  |  |

优先追问：
1. 
2. 
3. 
```

## PRD Draft v0

```md
# {需求名称} PRD 草案 v0

## 1. 结论先行
## 2. 战略层
### 2.1 用户与问题
### 2.2 目标与成功信号
## 3. 范围层
### 3.1 功能类型判断
### 3.2 本期范围
### 3.3 本期不做
### 3.4 关键角色与场景
## 4. 主流程骨架
## 5. 待确认决策
```

Do not include:

- exception flows or empty-state兜底
- permission and responsibility matrices
- data口径 or technical data details
- acceptance criteria
- development self-test cases

## Full PRD

Full PRD uses a 总分总 structure:

1. **Top summary**: document information, core conclusion, background, scope, users, main flow, and function list.
2. **Domain details**: organize detailed requirements by functional domain / business object, not by horizontal content type.
3. **Final closure**: non-functional requirements, acceptance criteria, self-test checklist, business review items, and version boundary.

````md
# {需求名称} PRD v{版本号}

## 1. 文档信息

| 项 | 内容 |
|---|---|
| 需求名称 |  |
| 版本 |  |
| 日期 |  |
| 状态 | 草案 / 待评审 / 已修订 / 可进入评审 |
| 适用端 | Web 端 / App 端 / 系统侧 / 其他 |
| 需求类型 | 台账型 / 业务型 / 统计型 / 混合型 |

## 2. 结论先行

用 1-2 段先说明本期到底建设什么、不是建设什么。

核心结论：

1. 
2. 
3. 

## 3. 背景与问题

说明为什么做、解决谁的问题、当前没有它会产生什么影响。

| 问题 | 影响 |
|---|---|
|  |  |

## 4. 需求范围

### 4.1 需求目标

| 目标 | 成功标准 |
|---|---|
|  |  |

### 4.2 本期不做

| 非目标 | 说明 |
|---|---|
|  |  |

## 5. 用户与场景

| 用户 / 角色 | 典型场景 | 需要的能力 |
|---|---|---|
|  |  |  |

## 6. 主流程

优先使用 Mermaid 图或流程表说明主流程。

```mermaid
flowchart TD
  A[开始] --> B[处理]
  B --> C[结束]
````

## 7. 功能清单

功能清单按功能域 / 业务对象纵向组织，`所属端` 只标记该功能涉及的端，不作为一级分组依据。

| 所属端 | 模块 / 功能域 | 功能点 | 功能说明 |
| --- | -------- | --- | ---- |
|     |          |     |      |

## 8. 详细需求

详细需求必须按功能域 / 业务对象组织。每个功能域内部再写字段、规则、状态、交互、异常、数据和权限。不要把异常、权限、数据全部拆成独立大章节，除非它们确实是跨功能域的公共规则。

### 8.1 {功能域一}

#### 8.1.1 功能说明

说明该功能域管理什么、解决什么问题、与其他功能域的关系。

| 内容 | 说明 |
| -- | -- |
|    |    |

#### 8.1.2 查询条件

仅适用于存在查询区的功能域。不适用时删除本节。

| 查询字段 | 组件类型        | 查询精度 | 说明 |
| ---- | ----------- | ---- | -- |
|      | 精准筛选 / 模糊筛选 |      |    |

#### 8.1.3 列表字段

仅适用于存在列表的功能域。不适用时删除本节。

| 字段 | 字段含义 | 数据来源 | 展示规则 | 空值展示 | 备注 |
| -- | ---- | ---- | ---- | ---- | -- |
|    |      |      |      |      |    |

#### 8.1.4 表单 / 详情字段

根据功能形态选择“表单字段”或“详情字段”。不适用时删除本节。

| 字段名称 | 字段含义 | 数据来源 | 字段状态             | 备注 |
| ---- | ---- | ---- | ---------------- | -- |
|      |      |      | 只读 / 可编辑 / 用户可配置 |    |

#### 8.1.5 业务规则

| 规则编号 | 规则对象 | 触发条件 | 规则说明 | 系统处理 | 处理后结果 | 异常处理 | 适用角色 | 备注 |
| ---- | ---- | ---- | ---- | ---- | ----- | ---- | ---- | -- |
| R001 |      |      |      |      |       |      |      |    |

#### 8.1.6 状态流转

仅适用于有状态变化的功能域。不适用时删除本节。

| 当前状态 | 触发动作 | 目标状态 | 条件 |
| ---- | ---- | ---- | -- |
|      |      |      |    |

#### 8.1.7 数据与口径

仅适用于有字段来源、变量、统计口径、快照、状态数据的功能域。不适用时删除本节。

| 数据 / 变量 / 口径 | 数据来源 | 使用位置 | 缺失处理 |
| ------------ | ---- | ---- | ---- |
|              |      |      |      |

#### 8.1.8 交互逻辑

| 步骤 | 触发起点 | 用户动作 | 系统响应 | 业务规则 |
| -- | ---- | ---- | ---- | ---- |
| 1  |      |      |      |      |

#### 8.1.9 异常处理

| 触发条件 | 处理逻辑 | 引导提示 | 恢复机制 |
| ---- | ---- | ---- | ---- |
|      |      |      |      |

### 8.2 {功能域二}

按 8.1 的结构继续展开。只保留适用于该功能域的小节，不机械填满。

## 9. 非功能需求

仅写与本期产品判断相关的非功能约束，不写具体技术实现。

| 约束项 | 规则 |
| --- | -- |
|     |    |

## 10. 验收标准

验收标准按功能域或主流程编号组织，优先覆盖主流程，再覆盖分支、边界和异常。

### 10.1 {功能域一}

| 编号 | 验收项 | 预期结果 |
| -- | --- | ---- |
| A1 |     |      |

### 10.2 {功能域二}

| 编号 | 验收项 | 预期结果 |
| -- | --- | ---- |
| B1 |     |      |

## 11. 研发自测清单

自测清单与验收标准编号层级对齐，自上而下覆盖主流程、分支、边界和异常。

| 编号 | 自测点 |
| -- | --- |
| D1 |     |

## 12. 待业务复核项

不阻塞进入研发评审、但建议业务方在评审会上确认的内容放在这里。每个复核项应包含推荐方案、备选方案和拍板人。

| 复核项 | 推荐方案 | 备选方案 | 影响 | 建议拍板人 |
| --- | ---- | ---- | -- | ----- |
|     |      |      |    |       |

## 13. 版本边界

说明本版本的适用范围、后续扩展边界、已接受风险和不进入本期的内容。

| 边界项   | 说明 |
| ----- | -- |
| 本期范围  |    |
| 后续扩展  |    |
| 已接受风险 |    |
| 不进入本期 |    |

````

Rules:

- Do not force every optional subsection to appear. Keep only sections supported by the current requirement.
- Do not scatter one functional domain across separate top-level chapters.
- Exceptions, permissions, data, and states should live inside the relevant functional domain whenever possible.
- Use top-level cross-domain chapters only when the rule truly applies across multiple functional domains.
- Keep “结论先行” as the first substantive section after document information.
- Keep acceptance criteria and self-test cases aligned by functional domain or flow.

---

## Review Report

```md
## PRD 审核报告

总体结论：可进入评审 / 需修订 / 不可进入评审
总分：__/100

### 四项核心指标

| 指标 | 评价 | 关键证据 |
|---|---|---|
| 边界清晰 |  |  |
| 判断显性 |  |  |
| 不留猜疑 |  |  |
| 信息准确 |  |  |

### 阻塞问题

| 级别 | 问题 | 位置 | 为什么阻塞 | 最小修法 |
|---|---|---|---|---|
| P0/P1 |  |  |  |  |

### P2/P3 建议

| 级别 | 问题 | 位置 | 建议 |
|---|---|---|---|

### 最小修改集
1.
2.
3.
```

---

## Checklist-driven Full PRD Writing

`output-contracts.md` defines the PRD output structure.
`05_context/prd-standards/checklist-v3.3.json` defines what must be checked, activated, and satisfied.

Full PRD writing runs on a five-file engine:

```text
01_workflow/workflow-protocol.md decides when and how the writing process runs;
05_context/prd-standards/prd-quality-standard.md defines the quality baseline and blocking logic;
05_context/prd-standards/checklist-v3.3.json decides what must be extracted;
04_templates/output-contracts.md decides where extracted content lands;
04_templates/table-templates/table-template-index.md decides which table template renders it.
```

output-contracts.md is not a standalone template. It is the landing layer
inside this engine.

Do not treat the Full PRD template as a fixed form to fill mechanically.
The template provides the 总分总 skeleton.
The checklist activates the actual content slots.

### Checklist Execution Rule

Before writing Full PRD details:

1. Determine the PRD complexity level: L1 / L2 / L3 / L4.
2. Load `05_context/prd-standards/checklist-v3.3.json`.
3. Filter checklist items by:
   - `complexity`: whether the item applies to the current PRD level.
   - `condition`: whether the current requirement triggers the item.
4. For each applicable item:
   - use `question` to identify what must be answered;
   - use `pass_criteria` to judge whether the PRD has written enough;
   - use `failure_signal` to avoid common omissions;
   - use `suggested_format` to select the output form through `04_templates/table-templates/table-template-index.md`;
   - use `priority` and `hierarchy` to determine whether omission blocks output.
5. Every applicable `hierarchy: gate` item must be addressed or explicitly marked `不适用` with a reason.
6. Do not dump checklist items into the PRD. The checklist is a silent extraction and quality guide.

### Location Resolution Rule

The `suggested_location` field in checklist-v3.3 is a semantic hint, not a hard chapter path.

When `suggested_location` conflicts with the Full PRD 总分总 structure, resolve location as follows:

| Checklist item type | Landing location in Full PRD |
|---|---|
| Real problem, goal, scope, non-goals, applicable endpoints | Top summary: sections 2-4 |
| Users, roles, scenarios | Section 5, or inside the relevant functional domain if role behavior differs by domain |
| Main flow across the whole requirement | Section 6 |
| Function list / scope decomposition | Section 7 |
| Functional rules, defaults, operations, states, data, exceptions, permissions, interactions | Section 8, inside the relevant functional domain / business object |
| Cross-domain rules shared by multiple functional domains | Section 8 shared/common subsection, or section 9 if it is non-functional |
| Acceptance criteria | Section 10, aligned by functional domain or main flow |
| Development self-test cases | Section 11, aligned with acceptance criteria |
| Pending decisions, assumptions, accepted risks | Section 12 |
| Current-version boundary and future exclusions | Section 13 |

Default principle:

```text
If a checklist item belongs to one functional domain, place it inside that functional domain.
If it applies across the whole PRD, place it in the top summary or final closure.
```

### Functional Domain Progressive Extraction

Detailed requirements are extracted progressively.
A functional domain does not need to include every possible subsection.
It only includes subsections activated by applicable checklist items and supported by current evidence.

For each functional domain:

1. Identify the dominant functional-domain type.
2. Select applicable checklist items.
3. Group selected items into requirement slots.
4. Write only the activated slots.
5. Delete non-applicable slots.
6. Mark necessary but insufficiently evidenced slots as `待确认`.

The dominant type of a functional domain determines which slots to extract
first. Do not extract all 12 slots for every domain.

| Domain type | Priority slots to extract | Typically skip |
|---|---|---|
| 列表管理型 | 查询条件、列表字段、操作规则、异常处理 | 状态流转、变量字典 |
| 表单配置型 | 表单字段、校验规则、保存规则、业务规则 | 查询条件、列表字段 |
| 流程状态型 | 主流程、状态流转、节点规则、交互逻辑、异常分支 | 列表字段、变量字典 |
| 消息通知型 | 触发事件、模板内容、变量字典、接收人解析、生成规则 | 查询条件、列表字段 |
| 数据口径型 | 指标定义、数据来源、计算规则、空值处理 | 状态流转、权限矩阵 |
| 系统联动型 | 触发条件、系统处理、上下游依赖、失败兜底 | 表单字段、列表字段 |
| 扩展边界型 | 本期边界、后续扩展点、不做内容、兼容规则 | 查询条件、列表字段、表单字段 |

A domain that mixes types (e.g. 台账型 + 业务型) should extract the union,
but still skip slots neither type activates.

### Functional Domain Slot Activation

Use applicable checklist items to activate subsections:

| Functional-domain slot | Activated by checklist examples | Typical output |
|---|---|---|
| 功能说明 | C01, C04, C11 | concise domain conclusion + explanation table |
| 查询条件 | items related to search, filter, default query, query linkage | query condition table |
| 列表字段 | list/table/card display items | field overview table |
| 表单 / 详情字段 | field state, text input, selection, date/time, validation items | field rule table / validation table |
| 业务规则 | core rules, default rules, operation control, trigger conditions | business rule table |
| 状态流转 | approval, enable/disable, publish, close, terminate, state-change items | state machine diagram / state transition table |
| 权限与责任 | role boundary, permission boundary, data permission items | role-permission matrix |
| 数据与口径 | data source, variables, statistics, calculation, snapshot, missing value items | data caliber table |
| 交互逻辑 | click before/during/after, popup behavior, page navigation, result feedback items | interaction logic table |
| 异常处理 | empty, failure, duplicate, conflict, permission-denied, irreversible cases | exception handling table |
| 验收点映射 | acceptance criteria items | acceptance table in section 10 |
| 自测点映射 | self-test items | self-test table in section 11 |

### Slot Treatment Rule

For each possible slot:

| Situation | Treatment |
|---|---|
| The current functional domain does not trigger this checklist item | Delete the slot |
| The checklist item applies and evidence is sufficient | Write the slot |
| The checklist item applies but evidence is insufficient | Keep the slot and mark `待确认` |
| The checklist item is `hierarchy: gate` but not applicable | Mark `不适用` with reason in the writing/review trace, not necessarily in the PRD body |
| The checklist item is applicable but intentionally accepted as risk | Record it in the accepted-risk / pending-decision area |

Do not add empty placeholders merely to keep the template complete.
Do not invent content to satisfy a checklist item.
Checklist-driven extraction must strengthen information accuracy, not decorate missing evidence.

### Traceability Rule

The PRD body must remain clean and readable. Checklist item IDs, gate status,
and compliance judgments belong to the writing trace, not the PRD body.

After Node 3 Fill Details completes, record checklist application evidence
in `09-run-log.md` Node 完成记录:

1. The PRD complexity level used for filtering.
2. Which checklist items were activated.
3. Every gate item addressed, with section reference.
4. Gate items marked `不适用`, with reason.
5. Items deferred as `待确认` due to insufficient evidence.
6. Accepted P1 risks.

The checklist is a silent extraction and quality guide. Its evidence lives in
run-log; its output lives in the PRD body. Never cross the streams.


```md
## Skill 复盘沉淀建议

| 发现的问题 | 归因 | 建议回写位置 | 建议动作 | 是否需要用户确认 |
|---|---|---|---|---|
|  | 缺知识 / 缺方法 / 缺模板 / 缺门禁 / 缺案例 / 偶发 | Context / Skill / Template / Gate / Example / Run history |  | 是 |

不自动修改规则。等待用户确认后再执行。
```
