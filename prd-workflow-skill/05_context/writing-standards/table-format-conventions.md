# PRD 表格使用规范

> Belongs to: `05_context/writing-standards/`
> Canonical routing: `../../04_templates/table-templates/table-template-index.json`
> Generated human view: `../../04_templates/table-templates/table-template-index.md`

固定表头、必填列和适用场景只在表格契约索引及其 `schema_file` 中定义。本文件解释如何选择和填写，不重复维护列结构。

## 使用顺序

1. 根据内容目的在 `table-template-index.json` 中匹配一个 contract ID。
2. 读取该路由的 `schema_file`，按固定列输出。
3. 需要示例或反例时再读取 `template_file`。
4. 无法唯一匹配时停止输出并修正路由，不自行拼接两套表头。

## 常用契约

- 查询条件：`query_filter_table`
- 列表字段：`list_display_table`
- 新增/编辑表单：`form_modal_field_table`
- 业务规则：`business_rule_table`
- 分支与异常：`exception_handling_table`
- 关键决策点：`key_decision_table`
- 范围与功能清单：`scope_feature_inventory_table`

其他验收、自测、校验、数据口径、风险接受和跨页面字段定义，按索引中的专用 contract 使用。

## 查询条件与列表字段

查询条件描述用户如何找到数据；列表字段描述系统如何展示数据。两者目的不同，不得复制同一表头。查询条件需要写清组件、匹配方式和选项来源；列表字段需要写清数据来源、展示规则和空值规则。

## 新增/编辑表单

“字段规则”描述数据来源、联动、单位、唯一性和依赖；“表单内容规则”描述允许和禁止的内容、长度或值域、格式和规范化处理。两列不得混写。

每个表单字段必须匹配 `component-specifications.json` 中的一个组件，并补齐该组件全部 `must_specify`。组件存在字段语义档位时，按业务含义选择，不用统一字符上限覆盖所有文本字段。

## 操作流程

操作流程不使用表格契约描述正常路径，也不再使用五列交互表。统一按 `operation-flow-writing.md` 输出连续编号主路径，并在对应步骤后按需使用分支与异常、关键决策点契约。

## 空单元格

固定列不等于允许无意义留空。确实不适用时写“不适用”并说明原因；缺少业务结论时标记待确认，不用空单元格掩盖遗漏。
