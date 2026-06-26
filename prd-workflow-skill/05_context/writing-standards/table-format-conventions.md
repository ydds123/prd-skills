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
| 组件类型 | Input component: 单行文本输入框 / 下拉单选 / 下拉多选 / 日期范围选择 / 标签页 / 级联选择 — and any special behaviors (e.g. "超过 7 项支持模糊搜索") |

**控件有内部层级结构时，说明列必须写清层级关系、默认展开状态和搜索范围。**

| 控件特征 | 说明列必须覆盖 |
|---------|-------------|
| 有父子层级（如"模块→消息类型"、"部门→人员"、"省→市→区"） | 层级关系：共几级，每级的取值来源 |
| 默认折叠 | 默认展开到第几级，或默认全部折叠 |
| 支持模糊搜索 | 搜索范围：仅最末级 / 所有层级 |
| 树形选择 | 是否支持勾选父级（勾选父级=全选子级 / 父级仅作分类不可选） |

级联选择不是独立组件类型——它是下拉单选/下拉多选的**结构变体**。组件类型写"下拉单选（级联）"或"下拉多选（级联）"，内部结构全部落在说明列。
| 查询精度 | Match mode: 精确匹配 / 模糊匹配 / 范围匹配 |
| 说明 | Constraints: character limits, whitespace trimming rules, default value, option source ("写死选项" / "引用系统模块字段"), empty handling |

Do not merge 组件类型 and 说明 into a single column. Component choice and business constraints are different decisions.

## List / Display Tables

For any list page or data table:

```
字段 | 字段含义 | 数据来源 | 展示规则 | 空值展示 | 备注
```

| Column | Content |
|--------|---------|
| 字段 | Column name as shown in the list header |
| 字段含义 | What business information this column conveys |
| 数据来源 | Where the data comes from: which system/table/API field, or computed (with formula). Use dotted notation to trace the source chain (e.g. "作业票基础信息.作业票类型名称"). If static/system-generated, say so. |
| 展示规则 | Format, truncation threshold, merge rules, special rendering (e.g. "超过 20 字符截断并追加…，hover 展示全文"), sorting capability. If the column supports click navigation, state the target. |
| 空值展示 | What to show when the source data is empty/null/missing. Not the same as format — this is the fallback display. |
| 备注 | Any constraints, linkage rules, or special notes |

**Why this replaces the old `字段 | 说明` two-column format**: the old format collapsed source, format, truncation, and empty state into one prose cell. R&D had to parse the description to extract what they needed. The new format makes each dimension explicit — a blank cell is a visible gap, not a buried omission.

If the list has action buttons, add an `操作` column at the end.

### Example

| 字段 | 字段含义 | 数据来源 | 展示规则 | 空值展示 | 备注 |
|------|---------|---------|---------|---------|------|
| 消息类型 | 该模板对应的消息触发类型 | 系统内置消息类型枚举，取 display_name | 格式："模块名称 > 消息类型名称"（如"特殊作业 > 提交审批"） | — | 模块名称为第一级分类 |
| 启用状态 | 模板当前是否启用 | 系统内置模板配置.启用状态 | 启用展示绿色"已启用"，停用展示灰色"已停用" | — | 停用后不触发消息 |
| 最近更新时间 | 模板或分组最近一次维护时间 | 取模板维护记录.操作时间 或 分组维护记录.操作时间（取最新） | YYYY-MM-DD HH:mm | -- | 保存后自动更新 |

## Form / Modal Field Tables

For any create or edit form:

```
字段名称 | 字段类型 | 是否必填 | 引导文案 | 字段说明
```

| Column | Content |
|--------|---------|
| 字段名称 | Field label |
| 字段类型 | Component: 单行文本输入框 / 下拉单选 / 下拉多选 / 多选列表 / 日期选择器 — and any special behaviors |
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
| Write "下拉选择" without specifying 单选 or 多选 | R&D cannot implement "a dropdown" — they need to know whether the user can pick one option or many. Multi-select requires checkboxes, single-select does not. | Always write "下拉单选" or "下拉多选" — never the bare "下拉选择" |
| Use "下拉单选" for a cascading tree of options without explaining the structure | R&D knows it's a dropdown but doesn't know there are two levels (e.g. 模块→消息类型), whether it's collapsed by default, or whether searching hits both levels. | Write "下拉单选（级联）" in 组件类型; put hierarchy, expansion state, and search scope in 说明 |
