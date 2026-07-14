---
name: prd-workflow
description: Orchestrate an end-to-end B-end PRD workflow with write-before alignment, decision ledger, two-phase PRD writing, independent quality review, deterministic content-gate validation, revision, and retrospective improvement proposals. Use when the user asks to write, review, revise, or systematize PRDs through a controlled workflow, especially when they mention PRD 工作流, 写前对齐, 决策账本, 质量门禁, 修订闭环, or skill 复盘. Do not use for a simple one-shot PRD draft only; use a dedicated PRD writer if available. Do not use for a standalone PRD review only; use a dedicated PRD reviewer if available.
---

# PRD Workflow

把需求判断固化为可执行、可验证、可追溯的 B 端 PRD。不要从模糊请求直接生成完整 PRD，也不要把未确认假设写成事实。

## 路由

- 模糊新需求：先执行写前对齐。
- 已有充分上下文并要求完整推进：执行全部节点。
- 已有 PRD 仅要求审查：改用独立 PRD 审查 Skill。
- 仅要求一次性初稿：改用轻量 PRD 写作 Skill。
- 要求复盘或优化工作流：读取本次 `09-run-log.md` 后提出补丁；未经逐项确认不得修改复用规则。

## 强制流程

1. 读取 `01_workflow/workflow-manifest.json`，以其中节点、输入、输出、人工确认和完成条件为准。
2. Boot：创建或复用可写任务目录，登记上下文证据，并按 `04_templates/run-log.md` 创建 `09-run-log.md`。不可写则停止。
3. 依次执行 Node 1 至 Node 5。Node 1、Node 2、Node 4 的人工确认不可跳过；Node 3 或 Node 4.5 出现会改变主方向且无证据的判断时暂停确认。
4. Node 3 写作时按 PRD 复杂度筛选 `05_context/prd-standards/checklist-v3.3.json`；表格只从 `04_templates/table-templates/table-template-index.json` 路由；表单字段先匹配 `05_context/writing-standards/component-specifications.json`；台账型功能同时读取 `05_context/writing-standards/ledger-feature-contract.json`。
5. Node 4 必须由不同于写作者的审查上下文完成。先初始化 `06-内容质量审查.json`，逐项处置 Checklist，再由用户决定修正和 P1 风险接受。
6. Node 4.5 按 `01_workflow/consistency-sweep-rules.json` 回扫，执行内容门禁 `seal` 和 `validate`，并输出大白话测试结论。门禁缺失、过期、阻断或未完成时不得进入最终输出。
7. 每个节点完成前执行 `scripts/validate-run-log.py`；Node 5 同时要求最终 PRD 契约、内容门禁和 Run Log 全部通过。

Hook 只提供额外防护，未安装或平台不支持时仍必须内联执行全部门禁。激活任务指针用 `scripts/manage-current-task.py`；Claude Hook 生命周期用 `scripts/manage-hooks.py`。

## 渐进读取

| 时机 | 读取 |
|---|---|
| 全程 | `01_workflow/workflow-manifest.json`、当前任务产物 |
| Boot/Node 1 | `01_workflow/task-and-draft-rules.md`、`01_workflow/workflow-protocol.md`、PRD 质量标准 |
| Node 2 | `04_templates/output-contracts.md` |
| Node 3 | 仅加载适用 Checklist、组件、台账和表格契约 |
| Node 4/4.5 | 内容质量门禁、一致性回扫规则及对应脚本 |
| Retrospect | `03_gates/gates-and-retrospective.md`、优化规则和本次 Run Log |

最终交付必须语言准确、边界明确、无隐藏假设，并给出“能否继续、用户要判断什么、工作流会直接修什么”。
