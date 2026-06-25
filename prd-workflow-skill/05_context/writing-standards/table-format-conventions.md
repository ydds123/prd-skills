# Table Format Conventions

> Belongs to: `05_context/writing-standards/`
> Governed by: `prd-definition-quality-standard.md` §5.3 "不留猜疑"
> Evidence: first PRD run — query/filter/field/form tables were reworked across 8 revision rounds due to missing format standards
> Version: v1.0.0

---

Every table in a PRD that R&D or QA depends on must use a fixed column set. Do not let the column set drift by section.

## Query / Filter Tables

For any list page or search panel that has filter controls:

```
查询字段 | 组件类型 | 查询精度 | 说明
```

| Column | Content |
|--------|---------|
| 查询字段 | The field name as shown to the user |
| 组件类型 | Input component: 单行文本输入框 / 下拉选择 / 日期范围选择 / 标签页 — and any special behaviors (e.g. "超过 7 项支持模糊搜索") |
| 查询精度 | Match mode: 精确匹配 / 模糊匹配 / 范围匹配 |
| 说明 | Constraints: character limits, whitespace trimming rules, default value, option source ("写死选项" / "引用系统模块字段"), empty handling |

Do not merge 组件类型 and 说明 into a single column. Component choice and business constraints are different decisions.

## List / Display Tables

For any list page or data table:

```
字段 | 说明
```

| Column | Content |
|--------|---------|
| 字段 | Column name as shown in the list |
| 说明 | What data this column shows, where it comes from, and any special rendering rules |

If the list has action buttons, add an 操作 column at the end with the available actions.

## Form / Modal Field Tables

For any create or edit form:

```
字段名称 | 字段类型 | 是否必填 | 引导文案 | 字段说明
```

| Column | Content |
|--------|---------|
| 字段名称 | Field label |
| 字段类型 | Component: 单行文本输入框 / 下拉选择 / 多选列表 / 日期选择器 — and any special behaviors |
| 是否必填 | 是 / 否 |
| 引导文案 | Placeholder text shown in the empty field |
| 字段说明 | Validation rules, character limits, uniqueness constraints, linkage rules, "保存时自动去除首尾空格" rules, dependency on other fields |

## Business Rule Tables

For rule sets that govern a feature's behavior:

```
规则 | 说明 | 用例
```

| Column | Content |
|--------|---------|
| 规则 | The rule expressed as a statement |
| 说明 | Why this rule exists and how it is enforced |
| 用例 | A concrete example showing the rule in action |

The 用例 column is the single most effective way to prevent ambiguity. If a rule is ambiguous without an example, the 用例 is not optional.

## Scope / Feature Inventory Tables

For feature lists that span modules and endpoints:

```
所属端 | 模块 | 功能点 | 功能说明
```

| Column | Content |
|--------|---------|
| 所属端 | Web 端 / App 端 / 系统侧 |
| 模块 | The functional domain or business object the feature belongs to |
| 功能点 | The specific feature name |
| 功能说明 | What this feature does in one sentence |

System-side capabilities (automated triggers, message generation, state computation) belong under `系统侧`, not shoehorned into a user-facing endpoint.

## Anti-patterns

| Don't | Why | Do instead |
|-------|-----|------------|
| Merge component type into 说明 as prose | Component choice and business rules get mixed together, hard to scan | Keep 组件类型 as its own column |
| Use prose paragraphs where a table would work | Prose hides missing fields — it's easy to write "supports filtering" without specifying which fields, what component, or what match mode | Use the fixed table format; a blank cell is a visible gap |
| Let the same table type have different column sets in different sections | R&D and QA build different mental models for each variation, leading to inconsistent implementation | Pick one column set per table type and use it everywhere |
