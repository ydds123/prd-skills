# prd-workflow-skill

面向 B 端产品经理和 AI Agent 的 PRD 工作流入口文档。

它不是“一句话生成完整 PRD”的提示词，也不是把所有 PRD 规则堆在 README 里；它是一套带写前对齐、决策账本、分阶段写作、独立评审、内容门禁、修订回扫和复盘沉淀的受控工作流。

它的核心目标是：

```text
不是把 PRD 写得更长，
而是把需求里必须被固定的判断逐层锁住，
让研发、测试、业务和后续 AI 都不需要靠猜来理解。
```

## 1. 这份 README 给谁看

| 读者 | 主要用途 |
|---|---|
| 产品经理 / 需求负责人 | 判断什么时候该使用本 Skill、会产出哪些文件、哪些节点需要人工确认 |
| AI Agent / Codex / Claude | 明确触发边界、渐进读取路径、执行顺序、质量门禁和禁止事项 |
| Skill 维护者 | 快速定位唯一事实源、验证脚本、Hook 安装方式和可维护边界 |

README 只做入口说明和导航，不作为运行规则的唯一来源。正式执行以 `SKILL.md`、`01_workflow/workflow-manifest.json`、各类 JSON 契约和模板文件为准。

## 2. 这个 Skill 解决什么问题

很多 PRD 失败不是因为内容太少，而是因为关键判断没有被固定：

```text
用户给出需求材料
→ AI 或 PM 直接写完整 PRD
→ 文档看起来完整
→ 但范围、角色、规则、异常、字段、权限、状态、验收没有闭环
→ 研发和测试仍然需要反复确认
```

`prd-workflow-skill` 把 PRD 从一次性写作变成可追踪的工作流：

```text
需求输入
→ 任务初始化
→ 写前对齐
→ 决策账本
→ PRD 框架草案
→ 完整 PRD 细化
→ 独立内容审查
→ 修订与一致性回扫
→ 内容质量门禁
→ 最终输出
→ 条件复盘沉淀
```

从第一性原理看，PRD 的根任务不是“表达”，而是“约束协作中的不确定性”。本 Skill 的所有节点、表格、脚本和门禁都围绕这个根任务设计。

## 3. 核心质量标准

本 Skill 判断 PRD 好坏，只看一个根标准：

```text
读的人是否还需要回来找 PM 确认。
```

围绕这个根标准，输出至少要满足四类质量要求：

| 质量要求 | 含义 |
|---|---|
| 边界清晰 | 本期做什么、不做什么、谁能做、什么时候能做，都要写清楚 |
| 判断显性 | 规则、异常、依赖、默认值、验收口径不能藏在语感里 |
| 不留猜疑 | 同一概念只有一个说法，研发和测试不需要自行补全 |
| 信息准确 | 不把假设写成事实，不虚构系统能力，不把未来规划混入本期 |

## 4. 什么时候适合用

适合：

- B 端后台管理系统、运营系统、HSE、ERP、审批、台账、配置类需求。
- 涉及多角色、多端、多状态、多异常、多字段规则的需求。
- 需要从“想法 / 原型 / 会议材料 / 需求口述”推进到“研发可执行 PRD”的场景。
- 需要分阶段确认范围、主流程、字段规则、异常、验收和自测的场景。
- 需要对已有 PRD 做质量门禁、修订闭环和复盘沉淀的场景。

典型触发语：

```text
使用 prd-workflow-skill，把这个需求走一遍 PRD 工作流。
先做写前对齐和决策账本，不要直接写完整 PRD。
基于这些材料产出完整 PRD，并做内容质量门禁。
对这份 PRD 进行独立审查，输出最小修改集。
这次 PRD 写作出现重复问题，读取 run-log 后做 Skill 复盘建议。
```

## 5. 什么时候不适合用

不适合：

- 只想要一版快速 PRD 初稿。
- 只需要润色一段产品说明。
- 只问产品方法论概念。
- 只做单次 PRD Review，且不需要完整工作流。
- 需求很小，不需要写前对齐、独立评审、门禁和复盘。

如果只是一次性初稿，应使用轻量 PRD 写作方式；如果只是单独评审，应使用独立 PRD 审查方式。`prd-workflow-skill` 的优势不在快，而在可控、可验证、可追溯。

## 6. 工作流概览

当前版本的权威节点来自 `01_workflow/workflow-manifest.json`：

```text
Boot
→ Node 1 写前对齐
→ Node 2 PRD 框架草案
→ Node 3 细化完整 PRD
→ Node 4 独立内容审查
→ Node 4.5 修订与一致性回扫
→ Node 5 最终输出
```

| 节点 | 目标 | 主要产物 | 是否需要人工确认 |
|---|---|---|---|
| Boot | 创建或复用任务目录，登记上下文证据 | `任务说明.md`、`00-上下文证据.md`、`09-run-log.md` | 否 |
| Node 1 | 写前对齐，确认真实问题、范围和关键决策 | `01-背景理解卡.md`、`02-决策账本.md`、`03-可写状态判断.md` | 是 |
| Node 2 | 只形成 PRD 框架，不提前堆细节 | `04-PRD草案v0.md` | 是 |
| Node 3 | 按适用清单补齐完整 PRD | `05-完整PRDv1.md` | 条件触发 |
| Node 4 | 切换为独立审查视角，找出阻断项和最小修改集 | `06-审核报告.md`、`06-内容质量审查.json` | 是 |
| Node 4.5 | 应用确认后的修订，回扫一致性并执行内容门禁 | `07-修订记录.md`、`06-content-gate.json`、`10-内容质量门禁测试结论.md` | 条件触发 |
| Node 5 | 只在门禁、契约和 Run Log 通过后最终交付 | 最终交付说明 | 否 |

人工确认不是礼貌动作，而是防止 AI 把未确认判断写成事实的协作闸门。

## 7. AI 执行方式

AI 使用本 Skill 时，应先读入口，再按节点渐进加载，不要一次性把所有标准、模板和 schema 全部塞入上下文。

| 时机 | 必读内容 | 读取目的 |
|---|---|---|
| 触发后 | `SKILL.md` | 获取最小执行骨架、路由、强制门禁 |
| 全程 | `01_workflow/workflow-manifest.json` | 确认节点顺序、输入输出、人工确认和完成条件 |
| Boot / Node 1 | `01_workflow/task-and-draft-rules.md`、`01_workflow/workflow-protocol.md`、`05_context/prd-standards/prd-quality-standard.md` | 判断需求是否可写，创建任务证据链 |
| Node 2 | `04_templates/output-contracts.md` | 按契约输出 PRD 框架草案 |
| Node 3 | `05_context/prd-standards/checklist-v3.3.json`、`04_templates/table-templates/table-template-index.json`、`05_context/writing-standards/component-specifications.json` | 按复杂度和功能类型细化 PRD |
| 台账型功能 | `05_context/writing-standards/ledger-feature-contract.json`、`05_context/writing-standards/ledger-feature-writing.md` | 写出查询、列表、新增/编辑、导入、导出、删除等台账型功能规则 |
| Node 4 / 4.5 | `05_context/prd-standards/content-quality-gate.md`、`01_workflow/consistency-sweep-rules.json`、相关验证脚本 | 独立审查、修订回扫、输出门禁结论 |
| Retrospect | `03_gates/gates-and-retrospective.md`、`05_context/optimization-standards/retrospect-trigger-rules.json`、本次 `09-run-log.md` | 判断问题是否应沉淀为可复用规则 |

AI 必须遵守：

- 不能从模糊需求直接生成完整 PRD。
- 不能跳过 Node 1、Node 2、Node 4 的人工确认。
- 不能把假设、推测、未来规划写成已确认事实。
- 不能用写作者自检替代独立内容审查。
- 不能在内容门禁缺失、过期、阻断或未完成时进入最终输出。
- 不能因为 Hook 已安装就省略内联门禁。

## 8. 台账型 PRD 写作规则

台账型功能是本 Skill 的重点场景之一，例如岗位危害因素配置、劳保用品管理、月度应发/实发记录等。

台账型功能不再使用泛化的“通用五列交互表”作为主要结构，而应按业务操作顺序展开：

```text
功能定位
→ 查询条件
→ 列表展示
→ 新增/编辑表单
→ 新增/编辑主路径
→ 分支与异常表
→ 关键决策点表
→ 批量导入
→ 查询/查看
→ 启用/停用
→ 导出
→ 删除
→ 验收标准
→ 自测用例
```

台账型 PRD 的核心不是“页面上有什么”，而是“每个操作如何改变数据、哪些判断会阻断、用户看到提示后下一步能做什么”。字段、组件、校验、提示语和导入模板都应优先从唯一事实源读取。

## 9. 内容质量门禁

内容质量门禁用于回答三个问题：

```text
这份 PRD 能不能继续交付？
用户还需要判断什么？
工作流已经直接修了什么？
```

门禁由 Node 4.5 执行，至少包括：

- `06-内容质量审查.json`：机器可读审查结果。
- `06-content-gate.json`：内容门禁凭证。
- `10-内容质量门禁测试结论.md`：人类可读测试结论。

测试结论要先给结论，再用大白话说明风险和需人工判断事项。它不是工程测试日志，也不是给脚本看的内部报告。

## 10. Run Log 机制

`09-run-log.md` 是整个 PRD 工作流的证据中枢。

它记录：

- 运行时间线。
- 修订记录。
- 痛点日志。
- Node 完成记录。
- 用户指正记录。
- 复盘触发状态。
- 复盘消费记录。

时间精度统一到 `YYYY-MM-DD HH:mm:ss`。当需要复盘 Skill 时，AI 必须优先读取本次任务的 `09-run-log.md`，不要靠聊天记忆回忆问题。

权威结构以 `04_templates/run-log.schema.json` 为准，人工说明以 `04_templates/run-log.md` 为准。

## 11. Hook 机制

Hook 是可选增强，不是工作流本体。

它的作用是提高两类事情的稳定性：

- 捕捉用户指正和复盘信号，写入当前任务的 `09-run-log.md`。
- 在 Claude Stop 阶段检查 Node 5 前的内容门禁状态。

当前 Hook 相关脚本：

```text
hooks/claude_hook.py
hooks/retrospect_trigger.py
hooks/append_retrospect_event.py
scripts/manage-hooks.py
scripts/manage-current-task.py
```

Hook 不负责：

- 自动写 PRD。
- 自动修 PRD。
- 自动修改 Skill。
- 自动接受 P1 风险。
- 替代 Node 4 / Node 4.5 的内联门禁。

常用命令：

```text
python scripts/manage-hooks.py install --scope user --dry-run
python scripts/manage-hooks.py install --scope user
python scripts/manage-hooks.py check --scope user
python scripts/manage-hooks.py uninstall --scope user --dry-run
python scripts/manage-current-task.py show
python scripts/manage-current-task.py activate --task-folder <任务目录> --node Boot
python scripts/manage-current-task.py deactivate
```

## 12. 文件结构

文件结构不是为了“看起来完整”，而是为了让人和 AI 能快速判断：某个问题该读哪里、该改哪里、该用哪个脚本验证。

```text
prd-workflow-skill/
├─ SKILL.md
├─ README.md
├─ VERSION
├─ manifest.json
├─ agents/
│  ├─ interface.yaml
│  └─ openai.yaml
├─ adapters/
│  ├─ claude/adapter.json
│  └─ codex/adapter.json
├─ skill-ir/
│  ├─ schema.json
│  └─ examples/prd-workflow.json
├─ 01_workflow/
│  ├─ workflow-manifest.json
│  ├─ workflow-protocol.md
│  ├─ task-and-draft-rules.md
│  ├─ consistency-sweep-rules.json
│  └─ content-consistency-sweep.md
├─ 03_gates/
│  └─ gates-and-retrospective.md
├─ 04_templates/
│  ├─ output-contracts.md
│  ├─ run-log.md
│  ├─ run-log.schema.json
│  ├─ content-gate-test-conclusion.md
│  └─ table-templates/
├─ 05_context/
│  ├─ prd-standards/
│  ├─ writing-standards/
│  └─ optimization-standards/
├─ hooks/
├─ scripts/
├─ evals/
└─ tests/
```

### 12.1 顶层文件

| 文件 | 作用 | 维护方式 |
|---|---|---|
| `SKILL.md` | AI 运行时入口，定义触发边界、强制流程、渐进读取和不可绕过的门禁 | 只保留运行时必须加载的骨架，不写长规则 |
| `README.md` | 面向使用者、AI 和维护者的入口说明，解释如何理解和使用本 Skill | 只做导航和说明，不承载正式规则 |
| `VERSION` | 当前 Skill 版本号 | 版本发布或验收后更新 |
| `manifest.json` | 包级元数据，说明版本、状态、目标平台、质量门禁和主要资产 | 维护治理信息和发布边界 |

### 12.2 跨平台与元数据

| 文件/目录 | 作用 | 维护方式 |
|---|---|---|
| `agents/interface.yaml` | 面向 Agent 的通用展示元数据，如名称、简介、默认提示和兼容性说明 | 人工维护，需与 `SKILL.md` 触发边界一致 |
| `agents/openai.yaml` | OpenAI / Codex 侧展示元数据 | 由适配脚本校验，避免与通用接口漂移 |
| `adapters/claude/adapter.json` | Claude 目标的轻量适配描述 | 由共享 IR 派生或校验 |
| `adapters/codex/adapter.json` | Codex 目标的轻量适配描述 | 由共享 IR 派生或校验 |
| `skill-ir/schema.json` | Skill IR 的结构约束 | 约束跨平台共享描述的形态 |
| `skill-ir/examples/prd-workflow.json` | 当前 PRD Workflow 的共享 IR 示例，也是双目标一致性检查的核心输入 | 作为跨平台契约，不写平台私有规则 |

### 12.3 工作流层

| 文件 | 作用 | 维护方式 |
|---|---|---|
| `01_workflow/workflow-manifest.json` | 工作流唯一事实源，定义 Boot、Node 1-5、Node 4.5 的输入、输出、确认点和完成条件 | 修改节点必须先改这里，再跑回归 |
| `01_workflow/workflow-protocol.md` | 解释工作流执行原则、节点协作方式和人工确认边界 | 只解释，不重复定义节点表 |
| `01_workflow/task-and-draft-rules.md` | 说明任务初始化、草案阶段和可写状态判断规则 | 给 Boot / Node 1 使用 |
| `01_workflow/consistency-sweep-rules.json` | 一致性回扫唯一事实源，定义受控维度、影响范围和自动修订边界 | 由门禁脚本消费 |
| `01_workflow/content-consistency-sweep.md` | 一致性回扫的人类解释版，说明为什么要回扫、怎么判断影响范围 | 只解释 JSON 规则，不另建规则 |

### 12.4 门禁与复盘层

| 文件 | 作用 | 维护方式 |
|---|---|---|
| `03_gates/gates-and-retrospective.md` | 说明最终门禁、风险接受、复盘触发和 Skill 优化建议的处理方式 | Node 5 和 Retrospect 使用 |

### 12.5 输出模板层

| 文件/目录 | 作用 | 维护方式 |
|---|---|---|
| `04_templates/output-contracts.md` | 定义 PRD 各阶段产物的输出契约和文档边界 | 引用权威源，不复制固定表头 |
| `04_templates/run-log.md` | `09-run-log.md` 的人工可读模板 | 需与 `run-log.schema.json` 保持一致 |
| `04_templates/run-log.schema.json` | Run Log 唯一事实源，定义必需章节、表头、时间格式和枚举 | 校验器直接读取 |
| `04_templates/content-gate-test-conclusion.md` | 人类可读门禁测试结论模板 | 用于把技术校验结果转成可审核结论 |
| `04_templates/table-templates/` | 表格模板、表格路由和 schema 集合 | 表格规则统一从这里路由和校验 |
| `04_templates/table-templates/table-template-index.json` | 表格路由唯一事实源，按用途匹配一套表格契约 | 脚本和 checklist 引用它 |
| `04_templates/table-templates/table-template-index.md` | 表格路由的人类可读说明 | 与 JSON 保持一致 |
| `04_templates/table-templates/*.md` | 各类表格模板的人类说明，如查询条件、列表字段、表单字段、分支与异常、关键决策点 | 只解释列含义和使用原则 |
| `04_templates/table-templates/schemas/*.schema.json` | 各类表格的机器校验 schema | 由回归测试检查是否与路由一致 |

### 12.6 上下文与写作标准层

| 文件/目录 | 作用 | 维护方式 |
|---|---|---|
| `05_context/prd-standards/prd-quality-standard.md` | PRD 质量标准，解释 P0/P1/P2/P3、阻断风险和审查口径 | Node 1 / Node 4 使用 |
| `05_context/prd-standards/checklist-v3.3.json` | Node 3 写作和 Node 4 审查的 checklist 唯一事实源 | 门禁脚本直接读取 |
| `05_context/prd-standards/content-quality-gate.md` | 内容质量门禁的人类说明 | 解释门禁结果和人工判断边界 |
| `05_context/writing-standards/component-specifications.json` | 组件规范唯一事实源，定义组件类型、必填规则和字段描述要求 | 字段规则和最终 PRD 校验读取它 |
| `05_context/writing-standards/component-specifications.md` | 组件规范的人类可读说明 | 与 JSON 保持一致 |
| `05_context/writing-standards/ledger-feature-contract.json` | 台账型功能写作契约，定义章节、操作顺序、流程表和导入证据要求 | 台账 PRD 校验直接读取 |
| `05_context/writing-standards/ledger-feature-writing.md` | 台账型功能写法说明和正反例 | 解释契约，不另立规则 |
| `05_context/writing-standards/operation-flow-writing.md` | 主路径、分支与异常表、关键决策点表的统一写法 | 流程类内容的写作说明 |
| `05_context/writing-standards/table-format-conventions.md` | 表格格式、人类可读性和 Markdown 表格约定 | 不定义业务表头 |
| `05_context/optimization-standards/retrospect-trigger-rules.json` | 复盘触发规则的机器来源 | Hook 和复盘判断使用 |
| `05_context/optimization-standards/retrospect-trigger-rules.md` | 复盘触发规则的人类解释 | 说明什么问题应进入复盘候选 |
| `05_context/optimization-standards/jsonization-backlog.md` | 记录尚未 JSON 化或暂不适合 JSON 化的规则 | 用于后续治理，不参与运行门禁 |

### 12.7 Hook 层

| 文件 | 作用 | 维护方式 |
|---|---|---|
| `hooks/claude_hook.py` | Claude Hook 统一入口，处理 UserPromptSubmit 和 Stop 事件 | 只做触发和拦截，不写 PRD |
| `hooks/retrospect_trigger.py` | 判断用户输入是否命中复盘或指正触发规则 | 读取复盘规则 |
| `hooks/append_retrospect_event.py` | 将命中的用户指正写入当前任务 Run Log | 只追加记录，不改正文 |
| `hooks/hook_config.example.json` | Hook 配置示例 | 用于安装预览和人工理解 |

### 12.8 脚本层

| 脚本 | 作用 |
|---|---|
| `scripts/run-regression-suite.py` | 统一回归入口，串联 JSON、组件、表格、Run Log、内容门禁、PRD 契约、Hook、适配器测试 |
| `scripts/prd-content-gate.py` | 内容质量门禁脚本，执行 seal / validate 等确定性检查 |
| `scripts/validate-prd-contracts.py` | 最终 PRD 产物级契约检查，覆盖台账结构、表格、组件和导入规则 |
| `scripts/validate-run-log.py` | Run Log 结构和节点完成记录校验 |
| `scripts/validate-json-execution-layer.py` | JSON 执行层结构、引用和元信息校验 |
| `scripts/validate-test-conclusion.py` | 人类可读测试结论校验，避免输出变成技术日志 |
| `scripts/manage-hooks.py` | Hook 安装、检查和卸载管理 |
| `scripts/manage-current-task.py` | 当前 PRD 任务指针管理 |
| `scripts/generate-platform-adapters.py` | Codex / Claude 适配器一致性生成或校验 |
| `scripts/generate-component-specifications.py` | 组件规范 Markdown 视图生成或校验 |
| `scripts/generate-table-contract-index.py` | 表格模板索引 Markdown 视图生成或校验 |
| `scripts/test-*.py` | 各规则族的正反向回归测试 |

### 12.9 验证资产层

| 文件/目录 | 作用 | 维护方式 |
|---|---|---|
| `evals/*.json` | 触发、组件、表格、Run Log、内容门禁、台账 PRD 等回归用例定义 | 必须被统一 runner 或对应测试消费 |
| `tests/fixtures/` | 真实或近真实 PRD fixture 和期望结果 | 用于证明最终产物级门禁有效 |

## 13. 唯一事实源

不要在 README 中复制复杂规则。AI 和维护者应通过下表定位事实源：

| 问题 | 唯一事实源 |
|---|---|
| 工作流节点、输入输出、人工确认、完成条件 | `01_workflow/workflow-manifest.json` |
| PRD 质量标准和 P0/P1/P2/P3 判断 | `05_context/prd-standards/prd-quality-standard.md` |
| Node 3 / Node 4 的完整性清单 | `05_context/prd-standards/checklist-v3.3.json` |
| 内容质量门禁要求 | `05_context/prd-standards/content-quality-gate.md` |
| 台账型功能写作契约 | `05_context/writing-standards/ledger-feature-contract.json` |
| 组件字段规则 | `05_context/writing-standards/component-specifications.json` |
| 表格模板路由 | `04_templates/table-templates/table-template-index.json` |
| 一致性回扫规则 | `01_workflow/consistency-sweep-rules.json` |
| Run Log 结构 | `04_templates/run-log.schema.json` |
| 跨平台 Skill IR | `skill-ir/examples/prd-workflow.json` |

## 14. 常用维护命令

在 Skill 根目录执行：

```text
python scripts/run-regression-suite.py
python scripts/generate-platform-adapters.py --check
python scripts/validate-json-execution-layer.py
python scripts/test-hook-lifecycle.py
python scripts/prd-content-gate.py --help
```

Hook 管理：

```text
python scripts/manage-hooks.py install --scope user --dry-run
python scripts/manage-hooks.py check --scope user
python scripts/manage-hooks.py uninstall --scope user --dry-run
```

任务指针管理：

```text
python scripts/manage-current-task.py show
python scripts/manage-current-task.py activate --task-folder <任务目录> --node Boot
python scripts/manage-current-task.py deactivate
```

## 15. 维护原则

### 入口要轻

`SKILL.md` 只放运行时必须知道的触发、路由、强制流程和门禁；README 只做面向人和 AI 的入口说明；复杂规则放入对应目录。

### 细则下沉

质量标准、流程协议、门禁规则、输出模板、组件规范、台账契约、表格模板和复盘规则，都应放在对应事实源中。不要把同一规则散落在多个文件里。

### JSON 执行层与 Markdown 解释层分离

JSON 负责执行：路由、匹配、过滤、校验、默认值读取、触发判断。

Markdown 负责解释：为什么这样设计、边界是什么、例子和反例是什么。

AI 应先读 JSON 获取机械答案，再按需读 Markdown 获取解释。

### 所有判断要有证据

PRD 写作、评审、修订、复盘都必须能追溯到：

- 用户输入。
- 文件材料。
- 决策账本。
- checklist。
- run-log。
- 审核报告。
- 内容质量门禁。

不要靠聊天记忆补事实。

### 自动化只能到记录和提案

系统可以自动记录、检测、提示和生成建议，但不能自动接受风险，不能把 P0 改成风险接受，不能把用户一次性偏好沉淀为全局规则，不能未经确认修改 Skill 可复用文件。

## 16. 当前版本边界

当前版本：`0.7.0`。

当前支持：

- 写前对齐。
- 决策账本。
- 两阶段 PRD 写作。
- 台账型 PRD 结构化写作。
- 组件规范唯一事实源。
- 独立内容审查。
- P0/P1 阻塞门禁。
- 内容一致性回扫。
- 内容质量门禁。
- 人类可读测试结论。
- Run Log 证据链。
- Retrospect Trigger Detector。
- 条件复盘沉淀。
- Claude 可选 Hook。
- OpenAI / Claude 适配器。
- JSON 执行层和回归测试。

当前不承诺：

- 一句话直接生成可交付 PRD。
- 自动替 PM 做最终产品判断。
- 自动接受风险。
- 自动修改 Skill 文件。
- 自动把所有用户偏好变成通用规则。
- 替代真实业务评审、研发评审和测试评审。

## 17. 一句话总结

```text
prd-workflow-skill 不是替你把 PRD 写长，
而是帮助人和 AI 把需求里的关键判断固定下来，
再用门禁和证据链确认它真的能交付。
```
