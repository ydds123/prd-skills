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
└─ assets/
```

Minimum first-run files:

- `任务说明.md`: task goal, source links, current status, next action
- `00-上下文证据.md`: source materials and evidence notes
- `04-PRD草案v0.md`: the draft Markdown file

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

```md
# {需求名称} PRD - 完整版

## 1. 背景与真实问题
## 2. 本期目标与成功标准
## 3. 范围与非目标
## 4. 用户 / 角色 / 场景
## 5. 主流程与状态变化
## 6. 功能规则与关键决策
## 7. 异常、空态与兜底
## 8. 权限与责任边界
## 9. 数据说明与口径
## 10. 上下游影响
## 11. 验收标准
## 12. 研发自测用例
## 13. 待确认事项与已接受风险
```

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

## Retrospective Patch Proposal

```md
## Skill 复盘沉淀建议

| 发现的问题 | 归因 | 建议回写位置 | 建议动作 | 是否需要用户确认 |
|---|---|---|---|---|
|  | 缺知识 / 缺方法 / 缺模板 / 缺门禁 / 缺案例 / 偶发 | Context / Skill / Template / Gate / Example / Run history |  | 是 |

不自动修改规则。等待用户确认后再执行。
```
