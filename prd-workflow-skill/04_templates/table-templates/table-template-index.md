# 表格模板索引

> Belongs to: `04_templates/table-templates/`  
> Source: PRD 需求自查清单 V3.3 · Sheet 07  
> Version: v1.0.0
> Machine-readable routing: `table-template-index.json` — Agent loads JSON first for keyword→template matching, then reads this Markdown file for routing logic and maintenance rules.

当 checklist 的 `suggested_format` 字段指向一个表格模板时，Agent 通过本索引定位到正确的 .md 文件。本索引是唯一真相来源——JSON 的 `template_ref` 字段仅作提示。

---

## 主模板

| suggested_format 关键词 | 模板文件 | 适用场景 |
|------------------------|---------|---------|
| 规则表 / 业务规则表 / 默认值表 / 操作控制表 / 反馈规则表 / 二次确认规则表 / 弹窗行为规则表 / 排序规则表 / 查询规则表 / 筛选规则表 / 分页规则表 / 展示规则表 / 图表展示规则表 / 控件规则表 / 初始化规则表 / 空态规则表 / 失败态规则表 / 重复处理表 / 冲突处理表 / 权限异常表 / 数量规则表 / 上传规则表 / 交互状态表 / 加载状态表 | [rule-table.md](rule-table.md) | 任何"条件 → 动作 → 结果"模式的规则描述 |
| 字段规则表 / 字段总表 / 列表字段总览 / 时间控件/日期/时间相关字段 | [field-rule-table.md](field-rule-table.md) | 表单字段、列表字段、详情字段的定义 |
| 校验规则表 / 必填校验 / 重复校验 / 格式校验 | [validation-rule-table.md](validation-rule-table.md) | 保存/提交/审批前的校验规则 |
| 数据口径表 / 数据来源表 / 统计口径表 / 指标定义 / 单位精度表 | [data-caliber-table.md](data-caliber-table.md) | 数据来源、计算口径、更新频率、单位精度 |
| 异常规则表 / 异常兜底 / 空态处理 / 失败态处理 / 冲突处理 / 权限不足处理 | [exception-handling-writing.md](exception-handling-writing.md) | 异常场景的系统处理、用户提示、恢复机制 |
| 验收标准表 | [acceptance-criteria-table.md](acceptance-criteria-table.md) | 需求完成判定、测试验收、业务验收 |
| 自测用例表 | [self-test-case-table.md](self-test-case-table.md) | 研发交付前最小冒烟用例 |
| 风险接受表 / 待确认事项表 | [risk-acceptance-table.md](risk-acceptance-table.md) | P1 风险接受记录、待确认项不阻塞记录 |

## 非模板呈现方式

以下 `suggested_format` 值不映射到表格模板——它们是表现形式建议：

| suggested_format | 含义 | 落地方式 |
|-----------------|------|---------|
| SCQA说明 / 问题定义表 | 用 SCQA 叙事定义问题 | PRD 背景章节的引导性写作 |
| 范围表 / 非目标表 | 本期范围与排除项 | 用 Markdown 表格呈现，参考 field-rule-table 的表结构思路 |
| 目标表 / 成功标准表 | 本期目标与可验证成功标准 | 用 Markdown 表格呈现 |
| 角色职责表 | 角色名称、职责、参与环节 | 用 Markdown 表格呈现，参考 rule-table 的表结构思路 |
| 权限矩阵 | 角色 × 页面 × 操作 × 数据范围 | 用 Markdown 表格呈现，参考 rule-table 的条件→动作模式 |
| 流程图 / 状态机图 / 关系图 / 页面流转图 | 图形化表达 | 用 Mermaid 语法绘制 |
| 步骤表 / 流程步骤 | 流程的步骤化描述 | 用 Markdown 表格，参考 interaction-logic-writing.md |
| 金字塔结构 | 结论先行的章节顺序 | 写作风格指导，非表格 |
| 术语表 | 核心术语与缩写统一 | 用 Markdown 表格呈现 |
| 评审结论卡 | P0/P1 统计 + 是否可进入评审 | 审核报告的汇总表格 |
| 越界检查表 | PRD 是否写了不该写的技术/设计细节 | 审核检查清单，不输出到 PRD |
| 能力边界表 | 本期已支持 vs 暂不支持 vs 未来规划 | 用 Markdown 表格呈现 |
| 变更记录表 | 版本号、变更点、原因、确认人 | PRD 文档头部元信息表格 |
| 影响范围表 / 上下游影响 / 存量影响 / 历史数据处理 | 本功能变更对上下游和历史数据的影响 | 用 Markdown 表格呈现，参考 rule-table |
| 示例表 / 正反例 | 复杂规则的正例和反例 | 嵌入对应规则表下方 |
| 提示文案表 | 各类提示的文案和展示位置 | 用 Markdown 表格呈现 |
| 图表动效说明 | 动效的业务含义 | 仅当动效承载业务状态时写，否则不进入 PRD |
| 图表默认查询规则 | 图表首次打开时的默认查询范围 | 用 rule-table 呈现 |

## Agent 使用规则

1. 当 checklist 的 `suggested_format` 命中"主模板"表的关键词时 → 打开对应 .md 文件，按空白模板填写。
2. 当命中"非模板呈现方式"时 → 按"落地方式"列的指引处理，不要强行映射到表格模板。
3. 如果 `suggested_format` 同时命中主模板和非模板（如"流程图 + 规则表"），两个都要落地。
