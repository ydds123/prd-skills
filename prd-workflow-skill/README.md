# prd-workflow-skill

面向 B 端产品经理的 PRD 工作流 Skill。

它不是一个“一句话生成完整 PRD”的提示词，也不是单点 PRD 写作器，而是一条带门禁、带评审、带修订、带复盘沉淀的受控 PRD 工作流。

它的核心目标是：

```text
不是让 PRD 看起来很完整，
而是让读的人不需要再回来找 PM 确认。
```

---

## 1. 这个 Skill 解决什么问题

很多 AI 写 PRD 的方式是：

```text
用户给一句需求
→ AI 直接输出一份完整 PRD
→ 文档看起来很饱满
→ 但边界、规则、异常、权限、状态、验收并没有真正固定下来
```

这类 PRD 最大的问题不是“内容少”，而是“判断没有被锁住”。

`prd-workflow-skill` 的设计目标是把 PRD 从一次性写作，变成一条可追踪的工作流：

```text
需求输入
→ 写前对齐
→ 决策账本
→ PRD 草案骨架
→ 完整 PRD 填充
→ 独立质量评审
→ 修订与一致性回扫
→ 条件触发复盘沉淀
```

它更像一条带质检门的 PRD 生产线，而不是一个文档代笔工具。

---

## 2. 核心质量标准

本 Skill 判断 PRD 好坏，只看一个根标准：

```text
读的人是否还需要回来找 PM 确认。
```

围绕这个根标准，所有输出都按四项指标检查：

| 指标   | 含义                        |
| ---- | ------------------------- |
| 边界清晰 | 本期做什么、不做什么、谁能做、什么时候能做，都写死 |
| 判断显性 | 规则、异常、依赖、风险、默认值、验收标准都明确   |
| 不留猜疑 | 同一概念只有一个说法，研发和测试不需要猜      |
| 信息准确 | 不把假设写成事实，不虚构系统能力，不混入未来规划  |

---

## 3. 什么时候适合用

适合：

* B 端后台管理系统
* 审批流、状态流转、配置类需求
* 表单、列表、详情、弹窗、权限、字段规则复杂的需求
* 多角色、多端、多状态、多异常的业务需求
* 需要把需求从“想法”推进到“研发可执行文档”的场景
* 需要对已有 PRD 做质量评审、修订闭环和复盘沉淀的场景

典型触发语：

```text
帮我把这个需求走一遍 PRD 工作流
先别直接写，先判断这个需求能不能写 PRD
把这些材料整理成决策账本，再生成 PRD
按质量门禁审一下这份 PRD，并给出最小修改集
这次 PRD 写偏了，帮我复盘应该改 skill、template、context 还是 gate
```

---

## 4. 什么时候不适合用

不适合：

* 只想快速拿一版 PRD 初稿
* 只需要普通功能说明
* 只问产品方法论概念
* 只要改一段文案或润色表达
* 需求极小，不需要完整流程、评审和复盘

如果只是“一句话快速生成初稿”，应该使用更轻量的 PRD writer。
如果只是“单独审一份 PRD”，应该使用更轻量的 PRD reviewer。

`prd-workflow-skill` 的优势不在快，而在可控。

---

## 5. 工作流概览

本 Skill 使用 5 个核心节点，加一个任务文件夹启动步骤和一个条件复盘阶段。

```text
input_received
→ [boot] task_folder
→ [1] alignment
→ [2] draft_body
→ [3] fill_details
→ [4] review
→ [4.5] content_consistency_sweep
→ [retrospect] conditional
```

### Boot：任务文件夹

每次 PRD 工作流都会创建或复用一个任务文件夹。

所有关键输出都落盘，避免只存在对话里。

默认会创建：

```text
09-run-log.md
```

`09-run-log.md` 是跨节点证据容器，记录运行时间线、修订根因、用户指正、复盘触发状态和复盘消费记录。

---

### Node 1：写前对齐

目标：先把需求判断对齐，再写 PRD。

这一阶段会产出：

* 背景理解卡
* 真实问题判断
* 范围与非范围
* 上下游依赖
* 决策账本
* 可写状态判断

关键规则：

```text
不能从一个模糊需求直接生成完整 PRD。
```

如果输入不足，Agent 最多问 3 个高价值问题。

---

### Node 2：PRD 草案骨架

目标：只确认框架，不提前堆细节。

这一阶段只写：

* 战略层
* 范围层
* 主流程骨架

不会展开：

* 异常
* 权限
* 状态
* 数据口径
* 验收标准
* 自测用例

这些会等用户确认主框架后，在 Node 3 再填。

---

### Node 3：完整 PRD 填充

目标：把确认后的 PRD 框架补成完整可执行文档。

这一阶段会加载 V3.3 操作完整性清单，根据需求复杂度和适用条件筛选检查项。

重点补齐：

* 角色与场景
* 菜单、列表、筛选、表格、表单
* 字段规则
* 业务规则
* 状态流转
* 权限规则
* 异常、空态、失败态、冲突态
* 数据口径
* 上下游影响
* 验收标准
* 自测用例
* 待确认事项
* 风险接受表

原则：

```text
字不如表，表不如图。
```

能用表说清楚的，不拆成重复段落。
能用图表达状态和流程的，不强行堆文字。

---

### Node 4：独立质量评审

目标：让另一个角色挑刺，而不是让写作者自我通过。

评审时 Agent 必须切换成独立 reviewer：

```text
我不再是 PRD writer。
我只忠于质量标准和完整性清单。
每个看似顺滑的判断都需要被验证。
```

评审重点：

* 是否边界清晰
* 是否判断显性
* 是否不留猜疑
* 是否信息准确
* 是否有 P0 / P1 阻塞项
* 是否有过度设计
* 是否有缺失的异常、权限、状态、验收、自测
* 是否有不该进入当前范围的未来规划

阻塞规则：

| 等级      | 处理                   |
| ------- | -------------------- |
| P0      | 永远阻塞最终输出             |
| P1      | 默认阻塞，除非 PM 明确接受风险并记录 |
| P2 / P3 | 不默认阻塞，但需要记录          |

---

### Node 4.5：内容一致性回扫

目标：修复之后再检查一次，避免“修 A 坏 B”。

触发条件：

```text
只要应用了内容修复，就应执行一致性回扫。
```

但如果只是错别字、格式、标题编号，不影响引用和规则，可以不跑。

回扫重点：

* 范围一致性
* 角色一致性
* 权限一致性
* 流程一致性
* 状态一致性
* 规则一致性
* 数据一致性
* 异常一致性
* 验收一致性
* 术语一致性

边界：

| 类型                    | 是否可自动修   |
| --------------------- | -------- |
| 术语统一、编号修正、旧说法替换       | 可以自动修    |
| 涉及范围、权限、状态、默认值、数据口径   | 需要 PM 确认 |
| 未确认事实、未确认系统能力、P0 风险接受 | 禁止自动修    |

---

### Retrospect：条件复盘沉淀

复盘不是必经阶段，而是条件触发阶段。

触发条件包括：

* 用户明确要求复盘
* 同类质量问题重复出现
* T3 Retrospect Trigger 命中
* P0 门禁失效
* 内容一致性回扫发现系统性缺陷

复盘不会自动修改 Skill 文件。

它只会先生成 patch 建议，用户逐条确认后，才允许写入对应文件。

---

## 6. Retrospect Trigger Detector

本 Skill 内置复盘触发器，用于捕捉“这次问题是否值得沉淀”。

触发器会在以下时机运行：

* 用户指正后
* 每个 Node 完成后
* PRD 修订完成后
* 内容一致性回扫完成后

它会判断：

```text
这是当前 PRD 的局部问题，
还是 Skill 的可复用规则、模板、门禁、案例缺陷？
```

### T0-T3 分级

| 等级 | 含义       | 处理                                       |
| -- | -------- | ---------------------------------------- |
| T0 | 不进入复盘    | 普通润色、一次性偏好、当前 PRD 局部修正                   |
| T1 | 观察       | 写入 run-log，记录用户指正或 AI 自检发现               |
| T2 | 复盘候选     | 标记 `needs_retrospect_candidate`，后续询问是否复盘 |
| T3 | 强制生成复盘建议 | 生成 `08-Skill复盘沉淀建议.md`，但不自动应用 patch      |

### 沉淀位置

触发器本身不是记录器。
它的输出最终沉淀到当前任务文件夹的：

```text
09-run-log.md
```

其中：

| 内容                 | 写入位置                  |
| ------------------ | --------------------- |
| 用户指出 AI 理解错、结构错、漏了 | 用户指正记录                |
| T1 / T2 / T3 触发状态  | 复盘触发状态                |
| T3 patch 建议        | 08-Skill复盘沉淀建议.md     |
| 已采纳 patch          | 目标 Skill 文件，并回写复盘消费记录 |

---

## 7. Hooks 机制

本 Skill 提供轻量 hooks 增强。

它不是 OS 级高频 hook，也不会每次工具调用都扫描。
它只是一个可选的触发增强层，用来提高“用户指正被捕捉”的稳定性。

核心脚本：

```text
hooks/retrospect_trigger.py
```

职责：

* 识别用户指正
* 识别沉淀意图
* 识别 P0 / P1 / 门禁失效
* 输出结构化 JSON
* 不写文件
* 不修改 PRD
* 不修改 Skill

示例配置：

```text
hooks/hook_config.example.json
```

这个配置只作为参考，不是运行强依赖。

---

## 8. Run Log 机制

`09-run-log.md` 是整个 workflow 的证据中枢。

它记录：

* 运行时间线
* 决策追加
* 修订记录
* 痛点日志
* Node 完成记录
* 用户指正记录
* 复盘触发状态
* 复盘消费记录

它解决的问题是：

```text
不要让复盘依赖对话记忆。
```

当 Skill 需要复盘时，Agent 必须优先读取 `09-run-log.md`，而不是凭聊天上下文回忆。

---

## 9. 包结构

核心结构如下：

```text
prd-workflow-skill/
├─ SKILL.md
├─ README.md
├─ VERSION
├─ manifest.json
├─ agents/
│  └─ interface.yaml
├─ hooks/
│  ├─ retrospect_trigger.py
│  ├─ append_retrospect_event.py
│  └─ hook_config.example.json
├─ scripts/
│  ├─ build_checklist.py
│  ├─ clean_template_refs.py
│  └─ fill_template_refs.py
├─ evals/
│  └─ trigger-evals.json
├─ 00_meta/
│  └─ blueprint-roadmap.md
├─ 01_workflow/
│  ├─ workflow-protocol.md
│  ├─ task-and-draft-rules.md
│  └─ content-consistency-sweep.md
├─ 03_gates/
│  └─ gates-and-retrospective.md
├─ 04_templates/
│  ├─ output-contracts.md
│  ├─ run-log.md
│  └─ table-templates/
│     ├─ table-template-index.md
│     ├─ rule-table.md
│     ├─ field-rule-table.md
│     ├─ validation-rule-table.md
│     ├─ data-caliber-table.md
│     ├─ exception-handling-writing.md
│     ├─ acceptance-criteria-table.md
│     ├─ self-test-case-table.md
│     └─ risk-acceptance-table.md
└─ 05_context/
   ├─ prd-standards/
   │  ├─ prd-quality-standard.md
   │  └─ operational-completeness-checklist.json
   ├─ writing-standards/
   │  ├─ table-format-conventions.md
   │  └─ interaction-logic-writing.md
   └─ optimization-standards/
      └─ retrospect-trigger-rules.md
```

---

## 10. 文件与目录职责

| 路径                                                   | 作用                                   | 不负责                        |
| ---------------------------------------------------- | ------------------------------------ | -------------------------- |
| `SKILL.md`                                           | 运行时入口，负责触发、任务路由、全局门禁和最小执行骨架          | 不保存完整方法论和长模板               |
| `README.md`                                          | 给人看的介绍、安装理解、使用边界和目录职责说明              | 不作为运行时必须加载的执行规则            |
| `05_context/prd-standards/prd-quality-standard.md`     | 定义 PRD 根标准、质量指标、复杂度等级和 P0-P3         | 不定义完整流程状态机                 |
| `01_workflow/workflow-protocol.md`                    | 定义工作流状态机、节点规则、评审、修订、回扫、复盘调用位置        | 不定义所有输出模板                  |
| `05_context/prd-standards/operational-completeness-checklist.json` | V3.3 操作完整性清单，用于 Node 3 填充和 Node 4 评审 | 不直接输出到 PRD 正文              |
| `03_gates/gates-and-retrospective.md`                | 定义可写状态、确认门禁、评审阻塞、最终输出和 Skill 更新门禁    | 不生成 PRD 正文                 |
| `05_context/optimization-standards/retrospect-trigger-rules.md` | 定义复盘触发信号、T0-T3、根因分类和自动记录边界           | 不保存事件，不写入文件                |
| `04_templates/run-log.md`                             | Run Log 模板，承接运行证据、用户指正和复盘触发状态        | 不定义触发规则                    |
| `04_templates/table-templates/`                       | 表格模板（规则表、字段表、校验表、异常表、验收表、自测表等）     | 不负责流程调度                    |
| `05_context/writing-standards/`                       | 表格格式规范、交互逻辑写作规范                     | 不负责表格模板本身                  |
| `hooks/`                                             | 复盘触发检测器与 run-log 记录器                  | 不改 PRD，不改 Skill            |
| `evals/`                                             | 触发与回归样例                              | 不参与日常 PRD 输出               |

---

## 11. 维护原则

### 入口要轻

`SKILL.md` 只放运行时必须知道的内容：

* 什么时候触发
* 怎么分流
* 哪些门禁不能越过
* 每个节点最小动作是什么

复杂细则放进 `01_workflow/`、`03_gates/`、`04_templates/`、`05_context/` 等对应目录。

---

### 细则下沉

质量标准、流程协议、门禁规则、输出模板、复盘规则、写作表格模板，都放进对应目录中，按需加载。

---

### 所有判断要有证据

PRD 写作、评审、修订、复盘都必须能追溯到：

* 用户输入
* 文件材料
* 决策账本
* checklist
* run-log
* 审核报告

不要靠聊天记忆补事实。

---

### 自动化只能到“记录和提案”

系统可以自动：

* 记录用户指正
* 标记复盘候选
* 生成复盘建议
* 自动修复 PRD 内部一致性问题

但不能自动：

* 接受 P1 风险
* 把 P0 变成风险接受
* 修改 Skill 可复用文件
* 把用户一次性偏好变成全局规则
* 批量采纳 patch

---

## 12. 最小使用方式

可以这样调用：

```text
请使用 prd-workflow-skill，帮我把这个需求走一遍完整 PRD 工作流。
先做写前对齐和决策账本，不要直接写完整 PRD。
```

如果材料很多，可以这样说：

```text
请先读取这些材料，判断当前是否达到可写 PRD 状态。
如果可以，输出背景理解卡和决策账本；
如果不可以，只问最多 3 个会影响主方向的问题。
```

如果要审查现有 PRD：

```text
请按 prd-workflow-skill 的 Node 4 独立评审逻辑审查这份 PRD，
用 V3.3 完整性清单、P0/P1 门禁和最小修改集输出审核结果。
```

如果要复盘 Skill：

```text
这次 PRD 过程中出现了重复问题，请读取 09-run-log.md，
判断是缺知识、缺方法、缺模板、缺门禁、缺案例还是偶发，
并输出 Skill 复盘沉淀建议。
```

---

## 13. 当前版本边界

当前版本支持：

* 写前对齐
* 决策账本
* 两阶段 PRD 写作
* V3.3 完整性清单
* 独立评审
* P0/P1 阻塞门禁
* 内容一致性回扫
* run-log 证据链
* Retrospect Trigger Detector
* 条件复盘沉淀
* 可选 hooks 检测

当前版本不承诺：

* 一句话直接生成可交付 PRD
* 自动替 PM 做最终产品判断
* 自动接受风险
* 自动修改 Skill 文件
* 自动把所有用户偏好变成通用规则
* 替代真实业务评审和研发评审

---

## 14. 一句话总结

```text
prd-workflow-skill 不是替你把 PRD 写长，
而是帮你把 PRD 中必须被固定的判断，一层一层锁住。
```
