# PRD Workflow Skill 仓库设计文档

> 建议文件名：`prd-workflow-skill-repository-design.md`  
> 建议仓库名：`prd-workflow-skill`  
> 版本：v0.1.0  
> 定位：面向 B 端产品经理的 PRD 工作流 Skill 仓库设计稿

---

## 1. 核心结论

本仓库不应被设计成一个“PRD 生成器”，而应被设计成一个 **PRD 工作流 Skill Stack**。

它的目标不是让 AI 在收到一句模糊需求后直接生成一份完整 PRD，而是让需求经过一条受控流程：

```text
需求输入
→ 写前对齐
→ 决策账本
→ PRD 两阶段生成
→ PRD 质量审核
→ PRD 修订
→ Skill 复盘沉淀
```

最终产出一份满足以下四个核心标准的 PRD：

| 核心标准 | 含义 |
|---|---|
| 边界清晰 | 本期做什么、不做什么、后续做什么写清楚 |
| 判断显性 | 关键规则、异常、依赖、取舍、默认值写清楚 |
| 不留猜疑 | 不让研发、测试、设计、运营、未来的 PM 依赖脑补 |
| 信息准确 | 事实、假设、估算、待确认项、数据口径分开写 |

一句话定义：

```text
好的 PRD 不是章节多，而是读的人不需要再回来确认。
```

本仓库的中心不是模板，而是质量标准；不是生成能力，而是阶段门禁；不是一次写得漂亮，而是每次返工后能把错误沉淀成下一次的规则。

---

## 2. 仓库定位

### 2.1 仓库名称

推荐名称：

```text
prd-workflow-skill
```

### 2.2 一句话定位

```text
一个面向 B 端产品经理的 PRD 工作流 Skill 仓库，用于将需求输入转化为边界清晰、判断显性、不留猜疑、信息准确的 PRD，并通过审核门禁和复盘机制持续优化 Skill。
```

### 2.3 本仓库要做什么

| 能力 | 说明 |
|---|---|
| 写前对齐 | 不让 AI 在需求未澄清前直接写 PRD |
| 决策显性化 | 将隐含决策转成决策账本 |
| 分阶段写作 | 先生成主体，再补充细节 |
| 质量门禁 | 基于 PRD 质量标准审核输出 |
| 修订闭环 | 根据审核问题和 PM 确认意见修订 PRD |
| 经验回写 | 将高频错误转成 Skill / Context / Template / Gate 的优化建议 |

### 2.4 本仓库不做什么

| 不做 | 原因 |
|---|---|
| 不做一句话直接生成完整 PRD | 容易生成看似完整但判断不稳的文档 |
| 不让写作角色自审通过 | 写审必须分离 |
| 不把未确认假设写成确定事实 | 保证信息准确 |
| 不在第一版自动修改 Skill | 防止自优化失控 |
| 不把所有需求都写成重型 PRD | 小需求需要轻量输出 |

---

## 3. 设计原则

### 3.1 质量标准优先

所有流程、目录、文件、子 Skill 都应服务于同一个目标：

```text
产出边界清晰、判断显性、不留猜疑、信息准确的 PRD。
```

### 3.2 先判断，后生成

需求没有达到可写状态前，不允许进入 PRD 正文生成。

### 3.3 写作和审核分离

`prd-writer` 负责写，`prd-reviewer` 负责审。  
写作角色不能完成最终质量门禁。

### 3.4 AI 给建议，人做拍板

AI 可以给推荐方案、备选方案、风险提示，但关键方向和取舍必须由人确认。

### 3.5 错误要能回写

一次 PRD 写偏，不只修这一次文档，还要判断问题属于：

| 问题类型 | 回写位置 |
|---|---|
| 缺知识 | Context |
| 缺方法 | Skill |
| 缺模板 | Template |
| 缺门禁 | Gate |
| 缺案例 | Example |

### 3.6 第一版不追求全自动

第一版目标是跑通“写前对齐、生成、审核、复盘”的人工可控闭环，不做自动更新 Skill。

---

## 4. 完整目录结构

```text
prd-workflow-skill/
├─ SKILL.md
├─ README.md
├─ VERSION
├─ CHANGELOG.md
│
├─ 00_meta/
│  ├─ project-positioning.md
│  ├─ design-principles.md
│  ├─ source-map.md
│  ├─ terminology.md
│  └─ scope-boundary.md
│
├─ 01_workflow/
│  ├─ run-protocol.md
│  ├─ workflow-state-machine.md
│  ├─ stage-transition-rules.md
│  ├─ human-ai-boundary.md
│  ├─ interaction-contract.md
│  └─ stop-confirm-rules.md
│
├─ 02_skills/
│  ├─ prd-thinking/
│  │  ├─ SKILL.md
│  │  ├─ role.md
│  │  ├─ input-contract.md
│  │  ├─ output-contract.md
│  │  ├─ context-retrieval-rules.md
│  │  ├─ writable-state-rules.md
│  │  ├─ decision-ledger-rules.md
│  │  └─ anti-patterns.md
│  │
│  ├─ prd-writer/
│  │  ├─ SKILL.md
│  │  ├─ role.md
│  │  ├─ input-contract.md
│  │  ├─ output-contract.md
│  │  ├─ complexity-routing.md
│  │  ├─ phase-1-writing-rules.md
│  │  ├─ phase-2-writing-rules.md
│  │  ├─ revision-mode-rules.md
│  │  ├─ no-go-rules.md
│  │  └─ anti-patterns.md
│  │
│  ├─ prd-reviewer/
│  │  ├─ SKILL.md
│  │  ├─ role.md
│  │  ├─ input-contract.md
│  │  ├─ output-contract.md
│  │  ├─ review-dimensions.md
│  │  ├─ subtraction-review-rules.md
│  │  ├─ severity-rubric.md
│  │  ├─ blocking-rules.md
│  │  └─ anti-patterns.md
│  │
│  └─ skill-retrospector/
│     ├─ SKILL.md
│     ├─ role.md
│     ├─ input-contract.md
│     ├─ output-contract.md
│     ├─ failure-classification.md
│     ├─ skill-patch-rules.md
│     ├─ context-patch-rules.md
│     ├─ adoption-gate.md
│     └─ anti-patterns.md
│
├─ 03_gates/
│  ├─ 01_writable-state-gate.md
│  ├─ 02_decision-confirmation-gate.md
│  ├─ 03_phase-1-prd-gate.md
│  ├─ 04_phase-2-prd-gate.md
│  ├─ 05_good-prd-output-gate.md
│  ├─ 06_review-blocking-gate.md
│  ├─ 07_final-output-gate.md
│  └─ 08_skill-update-gate.md
│
├─ 04_templates/
│  ├─ thinking/
│  │  ├─ background-understanding-card.md
│  │  ├─ context-reading-list.md
│  │  ├─ decision-ledger.md
│  │  ├─ open-questions.md
│  │  └─ writable-state-report.md
│  │
│  ├─ prd/
│  │  ├─ prd-l1-change-note.md
│  │  ├─ prd-l2-standard.md
│  │  ├─ prd-l3-complete.md
│  │  ├─ prd-l4-cross-system.md
│  │  ├─ prd-message-notification.md
│  │  ├─ prd-workflow-feature.md
│  │  ├─ prd-data-dashboard.md
│  │  └─ prd-ai-feature.md
│  │
│  ├─ review/
│  │  ├─ prd-review-report.md
│  │  ├─ severity-report.md
│  │  ├─ subtraction-review-report.md
│  │  ├─ blocking-issues-report.md
│  │  └─ minimum-fix-plan.md
│  │
│  └─ retrospective/
│     ├─ skill-iteration-log.md
│     ├─ failure-analysis.md
│     ├─ skill-patch-proposal.md
│     ├─ context-patch-proposal.md
│     └─ patch-adoption-record.md
│
├─ 05_context/
│  ├─ prd-standards/
│  │  ├─ prd-definition-quality-standard.md
│  │  ├─ good-prd-definition.md
│  │  ├─ prd-output-quality-rubric.md
│  │  ├─ prd-blocking-issue-standard.md
│  │  ├─ prd-ai-implementation-readiness.md
│  │  └─ prd-common-mistakes.md
│  │
│  ├─ product-principles/
│  │  ├─ user-problem-vs-user-solution.md
│  │  ├─ b-end-product-thinking.md
│  │  ├─ requirement-boundary-principles.md
│  │  ├─ scope-control-principles.md
│  │  └─ ai-feature-product-principles.md
│  │
│  ├─ writing-standards/
│  │  ├─ prd-section-definition.md
│  │  ├─ functional-requirement-writing.md
│  │  ├─ exception-and-empty-state-writing.md
│  │  ├─ acceptance-criteria-writing.md
│  │  ├─ dev-self-test-case-writing.md
│  │  └─ no-technical-implementation-rule.md
│  │
│  ├─ review-standards/
│  │  ├─ review-severity-definition.md
│  │  ├─ review-dimension-library.md
│  │  ├─ subtraction-review-standard.md
│  │  ├─ over-design-signals.md
│  │  └─ information-accuracy-standard.md
│  │
│  └─ optimization-standards/
│     ├─ knowledge-vs-method.md
│     ├─ failure-type-taxonomy.md
│     ├─ bounded-edit-rules.md
│     ├─ patch-validation-standard.md
│     └─ rejected-patch-standard.md
│
├─ 06_examples/
│  ├─ help-center-search/
│  │  ├─ 00_input.md
│  │  ├─ 01_background-card.md
│  │  ├─ 02_decision-ledger.md
│  │  ├─ 03_prd-phase-1.md
│  │  ├─ 04_prd-phase-2.md
│  │  ├─ 05_review-report.md
│  │  ├─ 06_revised-prd.md
│  │  └─ 07_skill-iteration-log.md
│  │
│  ├─ station-message-template/
│  │  ├─ 00_input.md
│  │  ├─ 01_background-card.md
│  │  ├─ 02_decision-ledger.md
│  │  ├─ 03_prd-phase-1.md
│  │  ├─ 04_prd-phase-2.md
│  │  ├─ 05_review-report.md
│  │  ├─ 06_revised-prd.md
│  │  └─ 07_skill-iteration-log.md
│  │
│  ├─ jsa-template-library/
│  │  ├─ 00_input.md
│  │  ├─ 01_background-card.md
│  │  ├─ 02_decision-ledger.md
│  │  ├─ 03_prd-phase-1.md
│  │  ├─ 04_prd-phase-2.md
│  │  ├─ 05_review-report.md
│  │  ├─ 06_revised-prd.md
│  │  └─ 07_skill-iteration-log.md
│  │
│  └─ ai-risk-analysis/
│     ├─ 00_input.md
│     ├─ 01_background-card.md
│     ├─ 02_decision-ledger.md
│     ├─ 03_prd-phase-1.md
│     ├─ 04_prd-phase-2.md
│     ├─ 05_review-report.md
│     ├─ 06_revised-prd.md
│     └─ 07_skill-iteration-log.md
│
├─ 07_runs/
│  ├─ README.md
│  ├─ run-index.md
│  └─ sample-run/
│     ├─ input.md
│     ├─ state.json
│     ├─ background-card.md
│     ├─ decision-ledger.md
│     ├─ prd-phase-1.md
│     ├─ prd-phase-2.md
│     ├─ review-report.md
│     ├─ revised-prd.md
│     └─ skill-iteration-log.md
│
├─ 08_quality/
│  ├─ golden-cases/
│  │  ├─ help-center-search.expected.md
│  │  ├─ station-message-template.expected.md
│  │  └─ jsa-template-library.expected.md
│  │
│  ├─ bad-cases/
│  │  ├─ missing-boundary.md
│  │  ├─ hidden-decision.md
│  │  ├─ ambiguous-requirement.md
│  │  ├─ inaccurate-information.md
│  │  ├─ over-technical-prd.md
│  │  ├─ no-exception-handling.md
│  │  └─ over-designed-feature.md
│  │
│  ├─ scorecards/
│  │  ├─ thinking-scorecard.md
│  │  ├─ writing-scorecard.md
│  │  ├─ review-scorecard.md
│  │  ├─ retrospective-scorecard.md
│  │  └─ good-prd-scorecard.md
│  │
│  └─ regression/
│     ├─ regression-checklist.md
│     ├─ known-failures.md
│     └─ fixed-failures.md
│
└─ 09_references/
   ├─ pm-ai-course/
   │  ├─ flow-map.md
   │  ├─ prd-quality-standard-extraction.md
   │  ├─ prd-workflow-extraction.md
   │  ├─ thinking-rules-extraction.md
   │  ├─ writing-rules-extraction.md
   │  └─ review-rules-extraction.md
   │
   ├─ create-prd-skill/
   │  ├─ adaptation-notes.md
   │  ├─ reusable-writing-rules.md
   │  ├─ prd-section-mapping.md
   │  └─ rejected-rules.md
   │
   ├─ check-prd-skill/
   │  ├─ adaptation-notes.md
   │  ├─ reusable-review-rules.md
   │  ├─ review-dimension-mapping.md
   │  └─ rejected-rules.md
   │
   └─ skillopt/
      ├─ adaptation-notes.md
      ├─ optimization-loop.md
      ├─ bounded-edit-mapping.md
      ├─ validation-gate-mapping.md
      └─ rejected-ideas.md
```

---

## 5. 目录 MECE 边界

| 目录 | 只负责 | 不负责 |
|---|---|---|
| `00_meta/` | 定义项目身份、范围、来源、术语 | 不定义执行流程 |
| `01_workflow/` | 定义流程如何流转 | 不定义具体写作模板 |
| `02_skills/` | 定义四个角色如何执行 | 不保存公共质量标准 |
| `03_gates/` | 定义能不能进入下一步 | 不生成内容 |
| `04_templates/` | 定义输出长什么样 | 不解释为什么这样写 |
| `05_context/` | 定义标准、原则、知识 | 不记录某次运行结果 |
| `06_examples/` | 提供标准流程样例 | 不记录真实运行过程 |
| `07_runs/` | 记录真实运行过程 | 不沉淀长期规则 |
| `08_quality/` | 做回归测试和质量对照 | 不参与日常输出 |
| `09_references/` | 记录外部来源如何被吸收 | 不直接作为执行规则 |

文件放置判断规则：

```text
如果它是原则，放 05_context。
如果它是流程，放 01_workflow。
如果它是角色动作，放 02_skills。
如果它是阻断条件，放 03_gates。
如果它是输出格式，放 04_templates。
如果它是案例，放 06_examples。
如果它是某次真实结果，放 07_runs。
如果它是质量测试样本，放 08_quality。
如果它是外部材料吸收记录，放 09_references。
```

---

## 6. 总控 SKILL.md 设计稿

### 6.1 总控定位

总控 `SKILL.md` 是整个仓库的调度器。  
它不负责写完整 PRD，也不负责保存模板全集，而是负责：

| 职责 | 说明 |
|---|---|
| 识别任务类型 | 判断用户是要写、审、修、复盘，还是问方法 |
| 调度子 Skill | 决定进入 `prd-thinking`、`prd-writer`、`prd-reviewer`、`skill-retrospector` |
| 执行全局门禁 | 不允许跳过可写状态、主体确认、审核阻塞 |
| 维护人机边界 | AI 给建议，人拍板 |
| 引用质量标准 | 所有产出都要对齐 PRD 定义与质量标准 |
| 控制输出节奏 | 分阶段输出，不一口气吞掉全流程 |

### 6.2 总控 SKILL.md 建议结构

```md
# PRD Workflow Skill

## 1. Role

## 2. When to Use

## 3. Core Quality Standard

## 4. Global Workflow

## 5. Task Routing

## 6. Global Gates

## 7. Human-AI Boundary

## 8. Output Protocol

## 9. Forbidden Behaviors

## 10. Sub-skill Index
```

---

### 6.3 Role

```md
# Role

You are a PRD workflow orchestrator for B-end product managers.

Your job is not to directly generate a PRD from a vague request.

Your job is to guide the requirement through a controlled workflow:

1. clarify whether the requirement is writable;
2. expose hidden decisions;
3. generate PRD in two phases;
4. review PRD against quality gates;
5. convert recurring failures into Skill or Context improvement proposals.

A good PRD must satisfy four core standards:

1. clear boundary;
2. explicit judgment;
3. no guessing;
4. accurate information.
```

中文版：

```md
# 角色定位

你是一个面向 B 端产品经理的 PRD 工作流调度器。

你的任务不是在收到模糊需求后直接生成 PRD，而是把需求推进一条受控流程：

1. 先判断是否达到可写状态；
2. 再暴露隐含决策；
3. 再分两阶段生成 PRD；
4. 再按质量门禁独立审核；
5. 最后把高频问题沉淀为 Skill 或 Context 的优化建议。

一份合格 PRD 必须满足四个核心标准：

1. 边界清晰；
2. 判断显性；
3. 不留猜疑；
4. 信息准确。
```

---

### 6.4 When to Use

| 用户意图 | 是否触发 | 路由 |
|---|---|---|
| 帮我写 PRD | 是 | `prd-thinking` |
| 根据这些内容生成需求文档 | 是 | `prd-thinking` |
| 检查这份 PRD | 是 | `prd-reviewer` |
| 这个需求怎么写 | 是 | `prd-thinking` |
| 帮我梳理需求范围 | 是 | `prd-thinking` |
| 按审核意见修订 PRD | 是 | `prd-writer/revision mode` |
| 把这次问题沉淀到 Skill | 是 | `skill-retrospector` |
| 优化普通文案 | 否 | 普通回答 |
| 画页面原型 | 否 | 除非明确要写 PRD |
| 解释某个产品概念 | 否 | 普通回答 |

---

### 6.5 Core Quality Standard

```md
# Core Quality Standard

All PRD-related outputs must follow:

`05_context/prd-standards/prd-definition-quality-standard.md`

The core definition is:

A good PRD is not a long document.  
A good PRD fixes product judgment into a shared answer that the team can execute, verify, and trace.

The minimum quality standard is:

Readers should not need to come back to the PM for confirmation.

This is operationalized into four criteria:

| Criterion | Meaning |
|---|---|
| Clear boundary | What is in scope and out of scope is explicit |
| Explicit judgment | Rules, exceptions, dependencies, and decisions are visible |
| No guessing | No hidden default, vague phrase, or missing condition requires interpretation |
| Accurate information | Facts, assumptions, estimates, and pending confirmations are separated |
```

---

### 6.6 Global Workflow

```text
input_received
→ thinking
→ writable_state_gate
→ decision_confirmation_gate
→ writing_phase_1
→ phase_1_confirmation_gate
→ writing_phase_2
→ review
→ review_blocking_gate
→ revision_mode
→ final_output_gate
→ retrospective
```

| 阶段 | 子 Skill | 输出 |
|---|---|---|
| `thinking` | `prd-thinking` | 背景理解卡、决策账本、可写状态判断 |
| `writing_phase_1` | `prd-writer` | PRD 主体版 |
| `writing_phase_2` | `prd-writer` | PRD 完整版 |
| `review` | `prd-reviewer` | PRD 审核报告 |
| `revision_mode` | `prd-writer` | PRD 修订版 |
| `retrospective` | `skill-retrospector` | Skill 迭代清单 |

---

### 6.7 Task Routing

| 用户请求 | 路由 | 处理规则 |
|---|---|---|
| 新需求写 PRD | `prd-thinking` | 不直接写 |
| 已有背景充分，且用户说“可以直接写” | 快速跑 writable gate | 通过后进入 writer |
| 用户提供 PRD 要检查 | `prd-reviewer` | 不重写，先审 |
| 用户要求按审核意见修改 | `prd-writer/revision mode` | 根据确认意见修订 |
| 用户要求沉淀经验 | `skill-retrospector` | 输出 patch 建议 |
| 用户要求解释方法论 | 普通回答 | 不进入完整流程 |

---

### 6.8 Global Gates

| 门禁 | 通过条件 | 未通过动作 |
|---|---|---|
| 可写状态门禁 | 背景、上下游、关键决策、范围、阻塞问题完成检查 | 停止，不写正文 |
| 决策确认门禁 | 关键决策已确认，或有默认建议并明确标注 | 停止，列最多 3 个优先问题 |
| 主体确认门禁 | PM 确认范围和主流程 | 不补细节 |
| 质量审核门禁 | 无 P0，P1 已处理或被 PM 接受风险 | 不输出最终版 |
| 最终输出门禁 | 无未标记假设，无伪装成事实的待确认项 | 标记待确认，不得冒充确定 |
| Skill 更新门禁 | 只有建议，不自动改 Skill | 等用户确认 |

---

### 6.9 Human-AI Boundary

| 环节 | AI 负责 | 人负责 |
|---|---|---|
| 写前对齐 | 读取材料、指出缺口、给推荐问题 | 判断问题是否值得做 |
| 决策账本 | 暴露隐含决策、给推荐方案和备选方案 | 拍板关键决策 |
| PRD 写作 | 展开结构、规则、异常、验收 | 确认范围和核心流程 |
| PRD 审核 | 发现问题、分级、给最小修改集 | 决定是否接受风险 |
| 修订 | 按确认意见修订 | 决定哪些审核意见采纳 |
| 复盘 | 给 Skill / Context patch 建议 | 确认是否沉淀 |

---

### 6.10 Forbidden Behaviors

```md
# Forbidden Behaviors

1. Never directly generate a full PRD from a vague one-line request.
2. Never skip writable-state checking.
3. Never treat an unconfirmed assumption as a fact.
4. Never write technical implementation details into PRD unless the user explicitly asks for a technical design document.
5. Never write design parameters such as color values, pixel sizes, or exact component styling into PRD.
6. Never let the writer review its own PRD as the final quality gate.
7. Never output a “final PRD” when P0 issues exist.
8. Never automatically update Skill rules without human confirmation.
```

中文版：

```md
# 禁止行为

1. 禁止在需求模糊时直接生成完整 PRD。
2. 禁止跳过可写状态检查。
3. 禁止把未确认假设写成确定事实。
4. 禁止在 PRD 中写具体技术实现，除非用户明确要求技术方案。
5. 禁止在 PRD 中写色号、像素、字体大小等设计参数。
6. 禁止让写作角色完成最终审核。
7. 禁止存在 P0 问题时输出“最终版 PRD”。
8. 禁止未经用户确认自动修改 Skill 规则。
```

---

## 7. 四个子 Skill 的职责边界

### 7.1 子 Skill 总览

| 子 Skill | 核心问题 | 核心输出 | 边界 |
|---|---|---|---|
| `prd-thinking` | 能不能写 | 背景卡、决策账本、可写状态判断 | 不写 PRD |
| `prd-writer` | 怎么写 | PRD 主体版、完整版、修订版 | 不审核自己 |
| `prd-reviewer` | 写得行不行 | 审核报告、阻塞项、最小修改集 | 不直接重写 |
| `skill-retrospector` | 下次怎么少错 | Skill 迭代清单、patch 建议 | 不自动改 Skill |

短定义：

```text
thinking 管能不能写。
writer 管怎么写。
reviewer 管写得行不行。
retrospector 管下次怎么少错。
```

---

## 8. `prd-thinking` 职责边界

### 8.1 定位

```text
只负责把需求推进到可写状态。
不写 PRD 正文。
```

### 8.2 输入

| 输入类型 | 示例 |
|---|---|
| 一句话需求 | “我要做站内信模板管理” |
| 业务背景 | 产品说明、用户反馈、会议纪要 |
| 截图描述 | 页面、流程、交互截图 |
| 旧 PRD | 相邻模块、历史需求 |
| Context | 产品现状、术语、规则、边界 |

### 8.3 输出

| 输出物 | 是否必须 |
|---|---|
| 背景理解卡 | 必须 |
| 上下文读取清单 | 必须 |
| 关键决策账本 | 必须 |
| 背景追问 | 条件必需 |
| 可写状态判断 | 必须 |
| 写作输入包 | 可写时必须 |

### 8.4 不做

| 禁止项 | 原因 |
|---|---|
| 不写 PRD 正文 | 防止未对齐就进入生成 |
| 不替 PM 拍板 | AI 给推荐，人做最终判断 |
| 不问泛问题 | 问题必须基于已读材料和缺口 |
| 不无限追问 | 最多列 3 个优先阻塞问题 |

### 8.5 可写状态检查

| 检查项 | 通过标准 |
|---|---|
| 背景 | 知道为什么做 |
| 问题 | 知道解决谁的什么问题 |
| 范围 | 本期做什么、不做什么有初步边界 |
| 上下游 | 知道依赖谁、影响谁 |
| 决策 | 关键选择题有推荐方案 |
| 阻塞 | 没有会推翻主体方向的问题 |

---

## 9. `prd-writer` 职责边界

### 9.1 定位

```text
负责基于已确认的写作输入包生成 PRD。
采用两阶段写作，并承担按审核意见修订的 revision mode。
```

### 9.2 输入

| 输入类型 | 来源 |
|---|---|
| 写作输入包 | `prd-thinking` |
| 决策账本 | `prd-thinking` |
| 可写状态报告 | `prd-thinking` |
| PRD 模板 | `04_templates/prd/` |
| 质量标准 | `05_context/prd-standards/` |
| 审核报告 | `prd-reviewer`，仅 revision mode 使用 |

### 9.3 输出

| 模式 | 输出 |
|---|---|
| Phase 1 | PRD 主体版：背景、目标、范围、角色、核心流程、核心功能 |
| Phase 2 | PRD 完整版：异常、边界、权限、数据、验收、自测、上下游 |
| Revision mode | 修订版 PRD、修改说明、未解决项 |

### 9.4 不做

| 禁止项 | 原因 |
|---|---|
| 不在可写状态前写 PRD | 防止伪完整 |
| 不私自新增范围 | 避免 AI 加戏 |
| 不把待确认项写成事实 | 保证信息准确 |
| 不写技术实现 | PRD 只写产品行为 |
| 不写设计参数 | 设计细节不属于 PRD |
| 不做最终审核 | 写审必须分离 |

### 9.5 复杂度路由

| 等级 | 场景 | 模板 |
|---|---|---|
| L1 | 字段、文案、配置、小规则 | `prd-l1-change-note.md` |
| L2 | 单页面、单流程功能 | `prd-l2-standard.md` |
| L3 | 多角色、多状态、多异常 | `prd-l3-complete.md` |
| L4 | 跨系统、权限、数据、AI 能力 | `prd-l4-cross-system.md` |

### 9.6 两阶段边界

| 阶段 | 写什么 | 不写什么 |
|---|---|---|
| Phase 1 | 背景、目标、范围、用户、主流程、核心功能 | 不展开全部异常和验收 |
| Phase 2 | 异常、边界、权限、状态、数据、验收、自测、上下游 | 不推翻 Phase 1 已确认范围 |

---

## 10. `prd-reviewer` 职责边界

### 10.1 定位

```text
负责独立审核 PRD 是否满足质量标准。
先做减法审查，再做完整性审查。
输出问题分级和最小修改集。
```

### 10.2 输入

| 输入类型 | 来源 |
|---|---|
| PRD 完整版 | `prd-writer` |
| 背景理解卡 | `prd-thinking` |
| 决策账本 | `prd-thinking` |
| PRD 质量标准 | `05_context/prd-standards/` |
| 审核标准 | `05_context/review-standards/` |

### 10.3 输出

| 输出物 | 是否必须 |
|---|---|
| 总体结论 | 必须 |
| 四项核心指标检查 | 必须 |
| P0/P1/P2/P3 问题清单 | 必须 |
| 减法审查结果 | 必须 |
| 最小修改集 | 必须 |
| 可选优化项 | 可选 |
| 是否可进入评审 | 必须 |

### 10.4 不做

| 禁止项 | 原因 |
|---|---|
| 不直接重写 PRD | 审核不是写作 |
| 不替 PM 推翻已确认方向 | 只能提示风险 |
| 不讨好式反馈 | 审核必须独立 |
| 不只查格式 | 先查判断，再查结构 |
| 不把 P0/P1 混成普通建议 | 阻塞项必须阻塞 |

### 10.5 审核顺序

| 顺序 | 审什么 | 对应质量标准 |
|---|---|---|
| 1 | 是否该做，是否过度设计 | 边界清晰 |
| 2 | 问题、目标、取舍是否清楚 | 判断显性 |
| 3 | 流程、规则、异常、验收是否完整 | 不留猜疑 |
| 4 | 事实、假设、数据口径是否准确 | 信息准确 |
| 5 | 是否可进入评审 | 门禁判断 |

---

## 11. `skill-retrospector` 职责边界

### 11.1 定位

```text
负责把本次 PRD 运行中的问题转化为 Skill 或 Context 的优化建议。
不直接修改 Skill。
```

### 11.2 输入

| 输入类型 | 来源 |
|---|---|
| 原始需求 | `07_runs/input.md` |
| 背景卡 | `prd-thinking` |
| 决策账本 | `prd-thinking` |
| PRD 草稿和修订版 | `prd-writer` |
| 审核报告 | `prd-reviewer` |
| 用户最终修改意见 | 用户反馈 |

### 11.3 输出

| 输出物 | 是否必须 |
|---|---|
| 问题复盘表 | 必须 |
| 缺知识 / 缺方法分类 | 必须 |
| Skill Patch 建议 | 条件必需 |
| Context Patch 建议 | 条件必需 |
| Template Patch 建议 | 条件必需 |
| Gate Patch 建议 | 条件必需 |
| 是否建议采纳 | 必须 |

### 11.4 不做

| 禁止项 | 原因 |
|---|---|
| 不自动改 Skill | 防止自我篡改 |
| 不把偶发错误都写成规则 | 防止规则膨胀 |
| 不混淆缺知识和缺方法 | 回写位置不同 |
| 不输出泛泛复盘 | 必须给具体 patch |
| 不绕过人工确认 | 用户确认后才沉淀 |

### 11.5 问题归因标准

| 问题类型 | 回写位置 | 示例 |
|---|---|---|
| 缺知识 | `05_context/` | 不知道某业务规则 |
| 缺方法 | `02_skills/` | 没要求未确认数据标待确认 |
| 缺模板 | `04_templates/` | 模板缺异常处理栏 |
| 缺门禁 | `03_gates/` | P1 问题未阻塞 |
| 缺案例 | `06_examples/` | 没有相似 B 端场景样例 |
| 偶发问题 | `07_runs/` 记录即可 | 不进入规则 |

---

## 12. 第一版 MVP 文件清单

完整目录可以保留，但第一版不需要一次写满。  
建议 MVP 先创建以下文件：

```text
prd-workflow-skill/
├─ SKILL.md
├─ README.md
├─ VERSION
│
├─ 00_meta/
│  ├─ project-positioning.md
│  ├─ design-principles.md
│  ├─ source-map.md
│  └─ terminology.md
│
├─ 01_workflow/
│  ├─ run-protocol.md
│  ├─ workflow-state-machine.md
│  ├─ stage-transition-rules.md
│  └─ human-ai-boundary.md
│
├─ 02_skills/
│  ├─ prd-thinking/
│  │  ├─ SKILL.md
│  │  └─ output-contract.md
│  ├─ prd-writer/
│  │  ├─ SKILL.md
│  │  └─ output-contract.md
│  ├─ prd-reviewer/
│  │  ├─ SKILL.md
│  │  └─ output-contract.md
│  └─ skill-retrospector/
│     ├─ SKILL.md
│     └─ output-contract.md
│
├─ 03_gates/
│  ├─ 01_writable-state-gate.md
│  ├─ 05_good-prd-output-gate.md
│  ├─ 06_review-blocking-gate.md
│  └─ 08_skill-update-gate.md
│
├─ 04_templates/
│  ├─ thinking/background-understanding-card.md
│  ├─ thinking/decision-ledger.md
│  ├─ prd/prd-l2-standard.md
│  ├─ prd/prd-l3-complete.md
│  ├─ review/prd-review-report.md
│  └─ retrospective/skill-iteration-log.md
│
├─ 05_context/
│  ├─ prd-standards/prd-definition-quality-standard.md
│  ├─ prd-standards/prd-output-quality-rubric.md
│  ├─ writing-standards/no-technical-implementation-rule.md
│  ├─ review-standards/review-severity-definition.md
│  └─ optimization-standards/knowledge-vs-method.md
│
└─ 06_examples/
   └─ help-center-search/
      ├─ 00_input.md
      ├─ 01_background-card.md
      ├─ 02_decision-ledger.md
      ├─ 03_prd-phase-1.md
      ├─ 04_prd-phase-2.md
      ├─ 05_review-report.md
      └─ 07_skill-iteration-log.md
```

MVP 原则：

```text
先保证流程能跑。
再保证质量能审。
再保证错误能沉淀。
最后再扩目录、补案例、做回归。
```

---

## 13. 后续建设路线

| 阶段 | 目标 | 产物 |
|---|---|---|
| Phase 1 | 建立仓库骨架和总控 Skill | `SKILL.md`、4 个子 Skill、核心门禁、核心模板 |
| Phase 2 | 接入 create-prd-skill 写作能力 | PRD 模板、复杂度路由、两阶段写作规则 |
| Phase 3 | 接入 check-prd-skill 审核能力 | 审核维度、P0/P1 门禁、最小修改集 |
| Phase 4 | 接入 SkillOpt 式复盘机制 | 失败分类、patch 建议、采纳门禁 |
| Phase 5 | 建立回归样本 | golden cases、bad cases、scorecards |
| Phase 6 | 半自动化运行 | state.json、run-index、gate-result schema |

---

## 14. 设计确认项

当前设计采用以下判断：

| 编号 | 设计判断 | 结论 |
|---|---|---|
| 1 | 仓库名 | `prd-workflow-skill` |
| 2 | 子 Skill 数量 | 4 个 |
| 3 | 是否保留独立 `prd-reviser` | 不保留，合并到 `prd-writer/revision mode` |
| 4 | 质量标准位置 | `05_context/prd-standards/prd-definition-quality-standard.md` |
| 5 | 目录深度 | 完整目录保留，MVP 先创建核心文件 |
| 6 | 自优化方式 | 第一版只输出 patch 建议，不自动改 Skill |

---

## 15. 最终收束

```text
这个仓库的中心不是 PRD 模板。
是质量标准。

这个仓库的关键不是生成能力。
是阶段门禁。

这个仓库的长期价值不是一次写得漂亮。
是每次返工之后，能把错误变成下一次的规矩。
```

四个子 Skill 的最终边界：

```text
prd-thinking 管能不能写。
prd-writer 管怎么写。
prd-reviewer 管写得行不行。
skill-retrospector 管下次怎么少错。
```
