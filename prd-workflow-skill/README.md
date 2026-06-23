# prd-workflow-skill

面向 B 端产品经理的 PRD 工作流调度 skill。

它不是一个“一句话生成完整 PRD”的生成器，而是一条受控流程：

```text
需求输入
→ 写前对齐
→ 决策账本
→ PRD 两阶段生成
→ PRD 质量审核
→ PRD 修订
→ Skill 复盘沉淀
```

核心质量标准：

```text
好的 PRD 不是章节多，而是读的人不需要再回来确认。
```

## 什么时候用

- `帮我把这个需求走一遍 PRD 工作流`
- `先别直接写，帮我判断这需求能不能写 PRD`
- `把这些材料整理成决策账本，再生成 PRD`
- `按质量门禁审一下这份 PRD，然后给最小修改集`
- `这次 PRD 写偏了，帮我复盘应该改 skill、context、template 还是 gate`

## 什么时候不用

- 只想快速拿一版 PRD 初稿：用独立 `create-prd` 类 skill 更合适。
- 只想单独审一份 PRD：用独立 `check-prd` 类 skill 更合适。
- 只问产品概念或普通写作建议：普通回答即可。

## 包结构

```text
prd-workflow-skill/
├─ SKILL.md
├─ README.md
├─ VERSION
├─ manifest.json
├─ agents/interface.yaml
├─ references/
│  ├─ prd-quality-standard.md
│  ├─ workflow-protocol.md
│  ├─ task-and-draft-rules.md
│  ├─ output-contracts.md
│  ├─ blueprint-roadmap.md
│  └─ gates-and-retrospective.md
└─ evals/
   └─ trigger-evals.json
```

## 文件与目录职责

| 路径 | 作用 | 不负责 |
|---|---|---|
| `SKILL.md` | 运行时入口，负责触发、任务路由、全局门禁和最小执行骨架 | 不保存完整方法论、长模板或大段目录说明 |
| `README.md` | 给人看的使用说明、设计边界和目录职责说明 | 不作为运行时必须加载的执行规则 |
| `VERSION` | 当前 skill 包版本 | 不记录变更历史 |
| `manifest.json` | 机器可读的生命周期、治理、来源、产物和质量门禁元数据 | 不放长文本执行说明 |
| `agents/interface.yaml` | Agent 兼容层元数据，描述展示名、默认提示、目标适配和信任边界 | 不放 PRD 业务规则 |
| `references/` | 按需加载的执行细则，承载质量标准、流程协议、输出契约和门禁规则 | 不负责触发路由；不替代 `SKILL.md` |
| `references/prd-quality-standard.md` | 定义好 PRD 的根标准、四项质量指标、复杂度等级、P0-P3 和 AI 实现就绪检查 | 不定义完整工作流状态机 |
| `references/workflow-protocol.md` | 定义 PRD 工作流状态机、阶段流转、写前对齐、两阶段写作、审核、修订和复盘规则 | 不定义每类输出的具体格式 |
| `references/task-and-draft-rules.md` | 定义 PRD 任务文件夹、任务文件结构、金字塔原则、MECE 原则和草案 v0 的边界 | 不替代质量审核；不写完整 PRD |
| `references/output-contracts.md` | 定义背景理解卡、上下文读取清单、决策账本、可写状态报告、PRD、审核报告和复盘建议的输出格式 | 不判断内容是否合格 |
| `references/blueprint-roadmap.md` | 把完整蓝图拆成 Phase 1-6 的建设路线，说明哪些目录何时补 | 不替代当前执行规则 |
| `references/gates-and-retrospective.md` | 定义可写状态、决策确认、阶段确认、审核阻塞、最终输出和 Skill 更新门禁 | 不生成 PRD 正文 |
| `evals/` | 保存路由和质量验证样例 | 不参与日常输出 |
| `evals/trigger-evals.json` | 记录应该触发和不应该触发 `prd-workflow` 的样例，避免和 `create-prd`、`check-prd` 混淆 | 不做完整 PRD 内容评测 |

维护原则：

- 入口要轻：只有会影响触发、分流、门禁和安全执行的内容才放进 `SKILL.md`。
- 细则下沉：质量标准、阶段协议、输出模板和复盘规则放进 `references/`。
- 元数据归位：生命周期、治理、兼容性和来源写进 `manifest.json` 或 `agents/interface.yaml`。
- 评测独立：触发样例和回归样例放进 `evals/`，不要混进 README 或入口文件。
- 任务制落盘：每次 PRD 运行默认创建 `PRD tasks/YYYY-MM-DD-{PRD名称}/`，草案作为 Markdown 文件沉淀在任务目录中。
- 草案要轻：草案 v0 只写战略层、范围层和主流程骨架；异常、权限、数据口径、验收和自测进入完整 PRD 阶段，并落到任务目录中的 `05-完整PRDv1.md`。
- 任务文件中文优先：PRD 任务产物是给人连续阅读和查找的，默认使用 `00-上下文证据.md`、`04-PRD草案v0.md` 这类中文文件名；英文主要保留给 skill 包的机器元数据和脚本。

## 设计来源

本版从两份本地材料沉淀：

- `../prd-definition-quality-standard.md`
- `../prd-workflow-skill-repository-design.md`

同时参考当前目录已有的 `create-prd-skill` 和 `check-prd-skill`：本 skill 作为总控调度器，不重复承担单点写作或单点审核能力。

## 第一版边界

第一版只保证流程能跑、质量能审、错误能沉淀。暂不创建完整 00-09 大目录，也不自动修改其他 skill。
