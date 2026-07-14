# 表格契约索引

> Generated from: `04_templates/table-templates/table-template-index.json`
> Version: `2.0.0`
> Source SHA256: `0e293d8dca4fe25071fda3ea139fe4b7d6e7815e988cf46476689bbeb1df1029`
> 本文件由脚本生成，请勿直接编辑。固定列以各路由的 `schema_file` 为准。

## 使用规则

- Match each table purpose to exactly one template_routes entry; schema_file is the fixed-column authority.
- For operation flows, write a numbered main path, then use exception_handling_table and key_decision_table only when applicable.
- The legacy five-column interaction table is forbidden.
- When checklist suggested_format matches non_template_formats → follow the rendering guidance in that entry.
- When suggested_format matches both template_routes and non_template_formats → apply both.
- table-template-index.md is generated from this JSON and must not be edited manually.

## 表格契约

| Contract ID | 匹配关键词 | 模板 | Schema | 适用场景 |
|---|---|---|---|---|
| query_filter_table | 查询条件表、筛选条件表、查询字段 | [query-filter-table.md](query-filter-table.md) | `schemas/query-filter-table.schema.json` | 列表页或搜索区域的查询条件 |
| list_display_table | 列表字段表、展示字段表、列表字段总览 | [list-display-table.md](list-display-table.md) | `schemas/list-display-table.schema.json` | 列表页展示字段及其来源、展示和空值规则 |
| form_modal_field_table | 表单字段表、新增表单、编辑表单、弹窗字段表 | [form-modal-field-table.md](form-modal-field-table.md) | `schemas/form-modal-field-table.schema.json` | 新增、编辑或弹窗表单字段 |
| business_rule_table | 规则表、业务规则表、默认值表、操作控制表、反馈规则表、二次确认规则表、弹窗行为规则表、排序规则表、查询规则表、筛选规则表、分页规则表、展示规则表、图表展示规则表、控件规则表、初始化规则表、空态规则表、失败态规则表、重复处理表、冲突处理表、权限异常表、数量规则表、上传规则表、交互状态表、加载状态表 | [rule-table.md](rule-table.md) | `schemas/rule-table.schema.json` | 功能的原子化业务规则 |
| field_rule_table | 字段规则表、字段总表、时间控件、日期、时间相关字段 | [field-rule-table.md](field-rule-table.md) | `schemas/field-rule-table.schema.json` | 表单字段、列表字段、详情字段的定义 |
| validation_rule_table | 校验规则表、必填校验、重复校验、格式校验 | [validation-rule-table.md](validation-rule-table.md) | `schemas/validation-rule-table.schema.json` | 保存/提交/审批前的校验规则 |
| data_caliber_table | 数据口径表、数据来源表、统计口径表、指标定义、单位精度表 | [data-caliber-table.md](data-caliber-table.md) | `schemas/data-caliber-table.schema.json` | 数据来源、计算口径、更新频率、单位精度 |
| exception_handling_table | 分支与异常表、异常规则表、异常兜底、空态处理、失败态处理、冲突处理、权限不足处理 | [exception-handling-writing.md](exception-handling-writing.md) | `schemas/exception-handling.schema.json` | 操作主路径中业务可达的分支与异常 |
| key_decision_table | 关键决策点表、业务决策表 | [key-decision-table.md](key-decision-table.md) | `schemas/key-decision-table.schema.json` | 会导向不同业务结果的关键判断 |
| acceptance_criteria_table | 验收标准表 | [acceptance-criteria-table.md](acceptance-criteria-table.md) | `schemas/acceptance-criteria-table.schema.json` | 需求完成判定、测试验收、业务验收 |
| self_test_case_table | 自测用例表 | [self-test-case-table.md](self-test-case-table.md) | `schemas/self-test-case-table.schema.json` | 研发交付前最小冒烟用例 |
| risk_acceptance_table | 风险接受表、待确认事项表 | [risk-acceptance-table.md](risk-acceptance-table.md) | `schemas/risk-acceptance-table.schema.json` | P1 风险接受记录、待确认项不阻塞记录 |
| scope_feature_inventory_table | 范围表、功能清单表、范围与功能清单表 | [scope-feature-inventory-table.md](scope-feature-inventory-table.md) | `schemas/scope-feature-inventory-table.schema.json` | 跨模块或多端的本期功能范围 |

## 非表格呈现方式

| ID | 建议形式 | 含义 | 落地方式 |
|---|---|---|---|
| scqa_problem_definition | SCQA说明 / 问题定义表 | 用 SCQA 叙事定义问题 | PRD 背景章节的引导性写作 |
| goal_table | 目标表 / 成功标准表 | 本期目标与可验证成功标准 | 用 Markdown 表格呈现 |
| role_table | 角色职责表 | 角色名称、职责、参与环节 | 用 Markdown 表格呈现，参考 rule-table 的条件→动作模式 |
| permission_matrix | 权限矩阵 | 角色 × 页面 × 操作 × 数据范围 | 用 Markdown 表格呈现，参考 rule-table 的条件→动作模式 |
| flowchart | 流程图 / 状态机图 / 关系图 / 页面流转图 | 图形化表达 | Mermaid |
| step_table | 步骤表 / 流程步骤 | 流程的步骤化描述 | 使用连续编号主路径；分支与异常、关键决策点分别使用对应 contract |
| pyramid_structure | 金字塔结构 | 结论先行的章节顺序 | 写作风格指导，非表格 |
| glossary | 术语表 | 核心术语与缩写统一 | 用 Markdown 表格呈现 |
| review_conclusion | 评审结论卡 | P0/P1 统计 + 是否可进入评审 | 审核报告的汇总表格 |
| overreach_check | 越界检查表 | PRD 是否写了不该写的技术/设计细节 | 审核检查清单，不输出到 PRD |
| capability_boundary | 能力边界表 | 本期已支持 vs 暂不支持 vs 未来规划 | 用 Markdown 表格呈现 |
| changelog | 变更记录表 | 版本号、变更点、原因、确认人 | PRD 文档头部元信息表格 |
| impact_table | 影响范围表 / 上下游影响 / 存量影响 / 历史数据处理 | 本功能变更对上下游和历史数据的影响 | 用 Markdown 表格呈现，参考 rule-table |
| example_table | 示例表 / 正反例 | 复杂规则的正例和反例 | 嵌入对应规则表下方 |
| tip_text_table | 提示文案表 | 各类提示的文案和展示位置 | 用 Markdown 表格呈现 |
| chart_animation | 图表动效说明 | 动效的业务含义 | 仅当动效承载业务状态时写，否则不进入 PRD |
| chart_default_query | 图表默认查询规则 | 图表首次打开时的默认查询范围 | 用 rule-table 呈现 |
