# Interaction Logic Writing

> Belongs to: `05_context/writing-standards/`  
> Governed by: `../prd-standards/prd-quality-standard.md` §5.3 "不留猜疑"  
> Evidence: first PRD run — v1.0 lacked interaction logic for all features; 6 features needed retroactive addition in v1.1  
> Version: v1.1.0 — added cross-reference to rule-table.md for business-rule-heavy features

---

Every core feature that involves user action must include an interaction logic table. "Core feature" means any function that appears in the feature inventory and involves user input, navigation, or state change. Read-only static content pages are exempt.

**When the feature involves complex business rules**, use [rule-table.md](../../04_templates/table-templates/rule-table.md) alongside this table. The interaction logic table covers "what happens when user does X"; the rule table covers "under what conditions does Y happen."

## Table Structure

```
步骤 | 触发起点 | 用户动作 | 系统响应 | 业务规则
```

| Column | Content |
|--------|---------|
| 步骤 | Sequential number starting from 1 |
| 触发起点 | Where the user is when this step begins (e.g. "Web 端进入模板管理页面", "需要查找模板") |
| 用户动作 | What the user does (e.g. "打开页面", "输入查询条件后点击查询", "点击停用并确认") |
| 系统响应 | What the system does in response (e.g. "打开新增分组弹窗", "模板状态变为停用", "刷新列表") |
| 业务规则 | The rule that governs this step — what is allowed, what is blocked, what is validated |

## Coverage Rules

1. **Main path first**: the primary flow from entry to completion.
2. **Then branches**: secondary paths (e.g. "批量删除分组" when the main path is single delete).
3. **Not every click**: do not enumerate every field the user fills. Group related fields into one step ("填写分组信息" not "输入分组名称 → 选择所属模块 → 勾选关联模板 → 输入关键字").
4. **State changes must appear in 系统响应**: if a step changes a visible state (enabled/disabled, selected/deselected, visible/hidden), the 系统响应 column must say so.

## Key Decision: Include or Skip

| Include as a step | Skip (too detailed) |
|-------------------|---------------------|
| "点击保存" — triggers validation and persistence | "输入分组名称" — one field among many |
| "确认二次弹窗" — a gate decision | "按 Tab 键切换到下一个字段" — implementation detail |
| "从处理入口跳转到作业票详情" — changes context | "滚动列表到第 3 页" — UX detail, not product rule |

## Multi-endpoint Rules

If a feature exists on both Web and App:
- Write one interaction logic table per endpoint if the flows differ materially.
- If they are identical, write one table and state "Web/App 端" in the 触发起点 column.
- If they are almost identical but differ on one step, write one table and annotate the divergent step.

## Anti-patterns

| Don't | Why | Do instead |
|-------|-----|------------|
| Skip the interaction table entirely | R&D must infer the flow from prose scattered across sections — guaranteed to miss branches | Write the table; if the flow is trivial (one step), state that explicitly |
| Write the table without 业务规则 | The flow looks correct but the constraints are missing — R&D implements what they see, not what was intended | Every row that has a constraint must state it in 业务规则 |
| Use the table to describe visual layout | "按钮在表单右下角" is a design decision, not a product decision | Describe the action, not the pixel position |
| Merge steps to avoid writing a long table | A 10-step table is fine if the flow has 10 distinct steps. A 3-step table that collapses 10 steps is misleading. | Match the table length to the actual flow complexity |
