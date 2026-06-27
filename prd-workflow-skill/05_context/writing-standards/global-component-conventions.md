# Global Component and Field Conventions

> Belongs to: `05_context/writing-standards/`
> Purpose: PRD 产品行为默认值库 — 为 PRD 中反复出现的字段、控件、列表、操作、状态、异常提供可复用的默认产品行为规则
> Governed by: `../../01_workflow/workflow-protocol.md` (load in Node 3) and `../../03_gates/gates-and-retrospective.md` (per-patch confirm→write)
> Version: v1.1.0
> Machine-readable defaults: `global-component-conventions.json` — Agent loads JSON first for field-length/input/selection/list/action defaults, then reads this Markdown file for evolution rules, promotion criteria, patch-proposal format, and boundary explanation.

---

This file defines reusable product-behavior defaults for PRD writing. It is not a UI design system, frontend component library, or technical implementation guide.

## Scope and Non-goals

**Scope** — this file covers:

- Field length, input handling, and numeric input defaults.
- Selection, date-time, query, list, and detail display defaults.
- Action, batch, and state transition defaults.
- Permission, failure, conflict, historical-data, notification, and audit defaults.

**Non-goals** — this file does NOT cover:

- Visual design parameters (color, font size, pixel, spacing, border-radius).
- Frontend component implementation or API details.
- Specific business rules that belong to a single PRD domain.
- Existing external-system, regulatory, invoice, or legacy-system constraints.
- One-time user preferences that lack repeated evidence.

Core principle:

```text
同类字段不漂移；同类控件不重写；同类操作不猜测；同类异常不漏写。
```

---

## Evolution Rule

`global-component-conventions.md` is appendable but not casually editable.

A convention enters this file through this chain:

```text
PRD run exposes repeated ambiguity or inconsistent defaults
  → evidence recorded in 09-run-log.md (user correction / revision / pain point)
  → classified as reusable product-behavior gap
  → enters 08-复盘建议.md as a convention patch proposal
  → per-patch user confirmation
  → written to this file
  → subsequent PRD writing applies the new default
```

The agent must not directly rewrite this file from a single preference. Each convention patch requires per-patch user confirmation before writing, governed by `03_gates/gates-and-retrospective.md`.

---

## Convention Promotion Criteria

Only content that satisfies ALL of the following qualifies for this file:

| Criterion | Threshold |
|---|---|
| High-frequency | Likely to recur across multiple PRD runs |
| Generic | Not bound to a single business domain |
| Default-able | Can serve as a baseline that business exceptions override |
| Misinterpretation-prone | Leaving it implicit causes drift across roles (R&D, QA, design, ops) |
| Non-visual | Does not involve color, font, pixel, spacing, or border-radius |
| Non-implementation | Does not involve API, database, code, or frontend library internals |
| Evidence-backed | Comes from user correction, PRD revision, review finding, sweep finding, or repeated pain points in `09-run-log.md` |

One-sentence rule:

```text
高频、通用、可默认、会误解，就沉淀。
低频、业务专属、实现细节、视觉参数，就不要沉淀。
```

---

## Four-layer Convention Map

| Layer | Categories | Current status |
|---|---|---|
| 1. 字段与输入层 | Field Length / Input Handling / Numeric Input | Field Length + Input Handling: v1.0; Numeric Input: reserved |
| 2. 控件与页面层 | Selection / Date-Time / Query-Filter / List-Detail | Selection + List Display: v1.0; Date-Time + Query-Filter: reserved |
| 3. 操作与流程层 | Action / Batch Operation / State Transition | Action: v1.0; Batch + State Transition: reserved |
| 4. 异常权限系统层 | Permission-Failure-Conflict / History-Notification-Audit | All reserved |

Reserved headings are listed below as the expansion target. They carry NO content until real PRD evidence activates them.

---

## Layer 1: 字段与输入层

### Field Length Defaults

| 字段类型 | 默认长度 | 适用场景 | 例外说明 |
|---|---:|---|---|
| 名称类字段 | 1～32 字符 | 模板名称、分组名称、规则名称、配置名称 | 若历史系统或外部系统已有长度限制，以业务来源为准，并在字段说明中写明 |
| 标题类字段 | 1～64 字符 | 消息标题、公告标题、任务标题 | 标题承载更多语义，可长于名称 |
| 摘要类字段 | 0～100 字符 | 消息摘要、列表摘要、说明摘要 | 可为空时写 0～100 |
| 编码类字段 | 1～32 字符 | 编号、编码、外部系统标识 | 若来源系统已有规则，以来源系统为准 |
| 标签名称 | 1～16 字符 | 标签、分类短名 | 避免列表和卡片展示拥挤 |
| 短说明字段 | 0～200 字符 | 备注、原因、说明 | 用于轻量补充 |
| 多行备注字段 | 0～500 字符 | 审批意见、驳回原因、处理备注 | B 端常见人工输入 |
| 长文本字段 | 1～1000 字符 | 消息正文、规则描述、处理说明 | 超过 1000 字符需单独说明必要性 |

若 PRD 未特别说明，名称类字段统一使用 1～32 字符。

### Input Handling Defaults

| 规则项 | 默认规范 |
|---|---|
| 首尾空格 | 保存时自动去除首尾空格 |
| 中间连续空格 | 默认保留，除非字段为编码类 |
| 空字符串 | 去除首尾空格后为空，按未填写处理 |
| 换行 | 单行文本不允许换行；多行文本允许换行 |
| 特殊符号 | 默认允许中文、英文、数字和常见符号；高风险业务字段需单独限制 |
| 重复校验 | 名称类字段如用于配置对象，默认同一业务域内不允许重复 |
| 大小写 | 中文业务字段不区分；编码类字段是否区分大小写需显式说明 |
| 失败保留 | 保存失败或校验失败时，默认保留用户已输入内容 |

单行文本默认保存时去除首尾空格；去空格后为空，视为未填写。

### Numeric Input Defaults

> Reserved — no conventions yet. Activate when PRD evidence exposes repeated numeric-input ambiguity.

---

## Layer 2: 控件与页面层

### Selection Control Defaults

| 控件类型 | 默认规范 |
|---|---|
| 下拉单选 | 默认支持清空，除非字段必选；选项超过 7 项默认支持模糊搜索 |
| 下拉多选 | 默认支持多选标签回显，选项超过 7 项默认支持模糊搜索；是否支持全选需单独说明 |
| 级联选择 | 必须说明层级、取值来源、默认展开层级、搜索范围 |
| 树形选择 | 必须说明父级是否可选，勾选父级是否等于全选子级 |
| 远程搜索 | 必须说明搜索字段、最小触发字符数、无结果反馈 |
| 枚举选项 | 必须说明选项来源：系统内置 / 字典配置 / 接口返回 / 当前业务对象 |
| 失效选项 | 历史已选但当前失效的选项，详情和列表中仍展示原值；编辑时是否允许保留，必须显式说明 |

不得只写"下拉选择"，必须明确是"下拉单选"还是"下拉多选"。

### Date and Time Defaults

> Reserved — no conventions yet. Activate when PRD evidence exposes repeated date-time ambiguity.

### Query and Filter Defaults

> Reserved — no conventions yet. Activate when PRD evidence exposes repeated query-filter ambiguity.

### List Display Defaults

| 项目 | 默认规范 |
|---|---|
| 空值展示 | 默认展示 `--` |
| 长文本截断 | 列表长文本默认超过 20 字符截断；是否 hover / 点击展示全文需显式说明 |
| 默认排序 | 默认按最近更新时间倒序；新数据在上，旧数据在下。若业务对象有优先级，以业务优先级规则为准 |
| 分页 | 默认分页展示；具体每页条数不作为 PRD 全局硬规则，除非业务要求 |
| 列表刷新 | 新增 / 编辑 / 删除 / 启停成功后，默认刷新当前列表 |
| 状态字段 | 必须说明状态枚举、展示文案、是否可筛选 |
| 操作列 | 必须说明按钮显示、禁用、隐藏条件 |
| 删除后列表定位 | 删除当前页最后一条后如何展示，需显式说明 |

列表字段必须说明数据来源、展示规则、空值展示；不能只写字段名和说明。

---

## Layer 3: 操作与流程层

### Action Defaults

| 操作类型 | 默认规范 |
|---|---|
| 新增 | 保存成功后返回列表还是停留当前页，需显式说明 |
| 编辑 | 保存前校验必填、唯一性、格式；成功后刷新来源页面 |
| 删除 | 默认二次确认；删除影响范围必须说明 |
| 启用 / 停用 | 默认不删除历史数据，只改变后续是否生效 |
| 取消 | 默认不保存当前变更；有未保存内容时是否二次确认需说明 |
| 批量操作 | 必须说明可选范围、是否跨页生效、部分失败处理 |
| 一键操作 | 必须说明是否可撤销、是否二次确认 |
| 高风险操作 | 必须说明确认文案、影响范围、是否可恢复 |

凡是不可逆、影响多人、影响历史数据、影响流程状态的操作，必须有二次确认。

### Batch Operation Defaults

> Reserved — no conventions yet. Activate when PRD evidence exposes repeated batch-operation ambiguity.

### State Transition Defaults

> Reserved — no conventions yet. Activate when PRD evidence exposes repeated state-transition ambiguity.

---

## Layer 4: 异常、权限与系统边界层

### Permission, Failure, and Conflict Defaults

> Reserved — no conventions yet. Activate when PRD evidence exposes repeated permission/failure/conflict ambiguity.

### Historical Data, Notification, and Audit Defaults

> Reserved — no conventions yet. Activate when PRD evidence exposes repeated history/notification/audit ambiguity.

---

## Exception Override Rule

Global defaults are the baseline, not the law.

A PRD can override any default when:

- An external system imposes a different constraint.
- A regulatory or legal requirement demands a specific rule.
- A historical or legacy system has an incompatible existing behavior.
- The business domain genuinely requires a different default.

When overriding, the PRD must state:
1. Which global default is being overridden.
2. The reason for the override.
3. The domain-specific value or rule replacing it.

Do not silently diverge from a global default — the override must be visible in the field or rule description.

---

## Patch Proposal Format

Every convention addition or change must be proposed as a patch before writing:

```md
## Convention Patch Proposal

| 字段 | 内容 |
|---|---|
| 规范编号 | GCC-xxx |
| 所属层级 | Layer 1-4 |
| 所属类别 | e.g. Field Length Defaults |
| 触发证据 | 来自 09-run-log.md 的用户指正 / 修订记录 / 痛点日志 |
| 当前问题 | 描述反复出现的口径漂移或歧义 |
| 建议规则 | 具体的默认规范文字 |
| 适用范围 | 适用场景和字段类型 |
| 例外条件 | 哪些情况可以覆盖此默认值 |
| 回归风险 | 是否与已有 PRD 或规范冲突 |
| 是否建议写入 | 是 / 否 |
```

The agent must not write convention content into this file without per-patch user confirmation.
