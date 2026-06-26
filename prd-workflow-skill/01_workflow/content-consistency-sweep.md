# Post-Revision Content Consistency Sweep

> Belongs to: `01_workflow/`  
> Node: 4.5 — executed after Node 4 revision, before Final-output check  
> Version: v1.0.0

---

## Goal

After applying confirmed review fixes, verify that the fix did not create cross-section contradictions, stale references, or unsynchronized tables. This is NOT a re-run of the full V3.3 checklist — it is a targeted sweep focused on the fix's blast radius and its cross-references.

## Trigger

Execute when:
- Any PRD content fix was applied from Node 4 review.
- Scope, non-goals, roles, permissions, states, flows, rules, data sources, exceptions, acceptance criteria, or self-test cases were modified.
- Core objects, roles, states, fields, buttons, entry points, or modules were added, deleted, or renamed.
- A P1 risk was accepted, or pending items were added.
- User asks to "update the whole document", "check consistency", or "sync the changes".

Skip when:
- Only typos, formatting, or layout were changed — unless they affect cross-references.

## Blast Radius — Select Dimensions

Do NOT run all 10 dimensions every time. Determine the fix's blast radius and run only the affected dimensions.

| Fix touched | Sweep dimensions to run |
|------------|------------------------|
| Scope / non-goals (§2, §4) | 1.范围 + 5.状态(if scope changed states) + 7.数据(if scope changed data sources) |
| Roles (§5) | 2.角色 + 3.权限 + us9.验收(role-based test cases) |
| Permissions (§10) | 3.权限 + 8.异常(permission exception handling) + 9.验收(permission test cases) |
| States / flows (§6, §8.1.4.1, §8.1.9) | 4.流程 + 5.状态 + 8.异常(flow exceptions) |
| Rules (§8.1.4, §8.1.6, §8.1.8) | 6.规则 + 5.状态(if rules alter state) + 9.验收(rule-based criteria) |
| Data (§8.1.7, §9) | 7.数据 + 6.规则(if data drives rules) |
| Exceptions (§8.x.10, §8.x.7, §8.x.8) | 8.异常 + 9.验收(exception test cases) |
| Acceptance / self-test (§11, §12) | 9.验收 |
| Terminology / naming (anywhere) | 10.术语 |
| Full §10 rewrite (role matrix + operation control + permission exception) | 2.角色 + 3.权限 + 4.流程 + 8.异常 + 9.验收 + 10.术语 |
| Template detail table column changed (e.g. 跳转入口 renamed) | 10.术语(match against §8.3.5 reference table) + 4.流程(verify flow target consistency) |
| **Added/deleted an item in an enumerated set** (e.g. new message type, new role, new state, new exception case) | **11.枚举完备性**(re-verify the set's coverage against its domain) + 10.术语(sync all cross-references to the updated count) |

## Enumeration Completeness — Cross-Cutting Check

Not a 10-dimension check — a method that applies whenever the PRD contains an **enumerated set** that claims to cover a domain.

The V3.3 checklist checks whether each *member* of the set is written well. It cannot check whether the *set itself* is missing members. This is the blind spot: "each item is thorough, but one was never listed."

### When to apply

Trigger when:
- A new item was added to an enumerated set (the domain was incomplete before the add).
- A set claims completeness ("全部 12 类", "覆盖所有角色", "所有异常类型").
- User reports a missing notification/missing state/missing permission that "should obviously be there."

### Method

```
1. Identify the domain the set claims to cover.
   Source: business flow (§6), role table (§5), feature inventory (§7).

2. Extract the set's current members from the PRD.

3. Subtract: domain − covered members = gap.

4. Gap ≠ ∅ → the set is incomplete. Fill missing members:
   a. Derive each missing member's attributes from the domain source.
   b. Insert into the set at the structurally correct position.
   c. Sync all cross-references (counts, query options, acceptance items, self-test entries).
   d. Gap = ⊘ → set is complete.

5. No explicit domain source? → cannot auto-fix. Ask PM: "here are the 12 members I found. Should there be 13?"
```

### This applies generically to

| Set type | Domain source | Gap example |
|---------|--------------|-------------|
| Message types / notification templates | Business flow nodes needing notification | 许可审批节点到达通知 missing |
| States in a state machine | All states the business object can be in | "已过期" state never listed |
| Roles in a permission matrix | All actors defined in §5 | A role in §5 never mapped to §10 |
| Exception types per feature | All exception dimensions (empty/failure/duplicate/conflict/permission) | 并发冲突 never addressed |
| Acceptance criteria | All feature points in §7 | A feature has the "how" but no "how to verify" |
| Variables in a variable dictionary | All variables referenced in template bodies | A variable used in a body but never defined in the dict |
| Query filter options | All enumerable values of the filtered field | "许可审批待处理" missing from the dropdown list |

## 10 Consistency Dimensions

### 1. 范围一致性 (Scope Consistency)

检查：§2 结论、§4 范围/非目标、§7 功能清单、§8.4 扩展边界、§14 版本边界。

| 检查要点 | 自动修复条件 |
|---------|------------|
| §2 核心结论是否与 §4.2 非目标冲突 | §2 以 §4.2 为准自动更新 |
| §7 功能清单是否列出 §4.2 已排除的功能 | 从 §7 删除 |
| §14 版本边界是否与 §4.1 目标对齐 | 以 §4.1 为准 |

### 2. 角色一致性 (Role Consistency)

检查：§5 用户表、§8.1.6 接收人类型、§10 权限矩阵。

| 检查要点 | 自动修复条件 |
|---------|------------|
| §5 的角色名称是否在 §10 权限矩阵中出现 | 两边名称对齐——以 §5 为定义源 |
| §8.1.6 的接收人类型是否在 §5 中有对应角色 | §8.1.6 是解析角色，不需要一一对应，但名称不能冲突 |
| 权限矩阵中列出的角色是否引用 §5 中已定义的名称 | 以 §5 的名称为准 |

### 3. 权限一致性 (Permission Consistency)

检查：§10.1 权限矩阵、§10.2 操作控制表、§10.3 权限异常处理、§10.4 通用规则。

| 检查要点 | 自动修复条件 |
|---------|------------|
| 操作控制表中的角色是否在权限矩阵中存在 | 以权限矩阵为准 |
| 权限异常处理的场景是否覆盖操作控制表中每个涉及权限的操作 | 补缺的异常行——使用已有文案风格 |
| 权限矩阵中标记"可操作"的功能是否在交互逻辑表（§8.1.9等）中有对应步骤 | 无需修改交互逻辑表本身，但检查交互逻辑表步骤是否有角色条件 |

### 4. 流程一致性 (Flow Consistency)

检查：§6 主流程图、§8.1.9/§8.2.6/§8.3.7 交互逻辑表、§8.3.5 处理入口表。

| 检查要点 | 自动修复条件 |
|---------|------------|
| 交互逻辑的步骤编号是否连续 | 自动修正编号 |
| 处理入口表中的消息类型是否全部在 §8.1.5 中有定义 | 以 §8.1.5 为准 |
| 模板明细（§8.1.5.x）的"跳转入口"字段是否与 §8.3.5 的名称一致 | 以 §8.3.5 为准——模板明细是源数据，§8.3.5 是汇总 |

### 5. 状态一致性 (State Consistency)

检查：§8.1.4.1 状态流转表、§8.1.4 启停规则表、§8.1.9 交互逻辑中的状态变化、§10.2 操作控制表中按钮的显示/禁用条件。

| 检查要点 | 自动修复条件 |
|---------|------------|
| 状态流转表中的状态名称是否在启停规则表和操作控制表中一致 | 以状态流转表为准 |
| 状态流转表是否覆盖启停规则表中全部触发动作 | 补缺的状态流转行——从规则表中提取 |
| 交互逻辑中"模板状态变为停用"是否匹配状态流转表的目标状态 | 以状态流转表为准 |

### 6. 规则一致性 (Rule Consistency)

检查：§8.1.4 启停规则、§8.1.6 接收人解析规则、§8.1.8 通用生成规则、§8.2.5 分组业务规则。

| 检查要点 | 自动修复条件 |
|---------|------------|
| 同一规则是否在多处描述一致 | 以更详细的那处为准，另一处简化为引用 |
| 用例列是否与规则说明一致 | 以规则说明为准 |
| 规则引用的数据字段是否在 §8.1.7 变量字典或相关数据表中存在 | 不能自动修——标记为需确认 |

### 7. 数据一致性 (Data Consistency)

检查：§8.1.7 变量字典、§8.1.2/§8.2.2/§8.3.2 查询条件表、§8.1.3/§8.2.3/§8.3.3 列表字段、§9 非功能需求。

| 检查要点 | 自动修复条件 |
|---------|------------|
| 列表字段是否引用了不存在的变量名称 | 以变量字典为准 |
| 模板明细中的变量（特殊规则列）是否在变量字典中有定义 | 以变量字典为准——补缺或删引用，需确认 |
| 非功能需求的数据指标是否与详细需求中的定义一致 | 以详细需求为准 |

### 8. 异常一致性 (Exception Consistency)

检查：§8.1.10/§8.2.7/§8.3.8 异常处理表、§10.3 权限异常处理。

| 检查要点 | 自动修复条件 |
|---------|------------|
| 新增规则是否同步了对应的异常处理 | 从规则中提取异常条件，补充到对应异常表中 |
| 权限异常处理是否与操作控制表中存在权限限制的操作匹配 | 补缺的权限异常行 |
| 异常处理表中的恢复机制是否与交互逻辑表中的步骤一致 | 以交互逻辑表为准 |

### 9. 验收一致性 (Acceptance Consistency)

检查：§11 验收标准、§12 自测清单、§8.1.5 模板明细、§8.1.4 启停规则。

| 检查要点 | 自动修复条件 |
|---------|------------|
| 新增或修改的规则是否有对应的验收项 | 补充验收行——编号从已有最大编号+1 |
| 新增的验收项是否有对应的自测用例 | 补充自测行——覆盖主流程/校验/权限/异常 |
| 验收标准中引用的状态、角色、规则名称是否与正文一致 | 以正文为准 |

### 10. 术语一致性 (Terminology Consistency)

检查：全篇。

| 检查要点 | 自动修复条件 |
|---------|------------|
| 同一对象是否使用不同名称（如"消息模板/站内信模板/推送模板"） | 以首次定义或出现频率最高者为准，全篇统一 |
| 同一字段是否在不同表中使用不同名称 | 统一 |
| 编号、锚点、交叉引用是否有效 | 修正断裂引用 |

---

## Auto-Fix vs PM Confirmation Boundary

### 可自动修

满足以下全部条件时可以自动修复：

- 能从 PRD 已有内容中找到明确依据（后期细节 > 前期总论 > 外部源材料）。
- 不新增产品事实——只是让已有的判断在全文保持一致。
- 不改变已确认的产品判断。
- 不扩大或缩小需求范围。
- 属于：术语统一、旧说法替换、表格补齐（已有规则→验收/自测）、编号修正、引用修正、版本号同步。

后期章节（§8-12）的细节与前期章节（§2-5）的结论冲突时，**以后期细节为准**——细则是决策的落地，总论是落地后的总结。自动更新总论。

### 需 PM 确认后修

涉及以下内容时必须向 PM 确认：

- 本期做什么 / 不做什么。
- 角色是否有权限做某操作。
- 状态是否可逆。
- 默认值如何取。
- 异常后是否可恢复。
- 数据口径如何计算。
- 风险是否接受。

### 禁止自动修

以下内容绝对不能自动修：

- 未确认业务规则补成确定事实。
- 未确认系统能力补成"本期已支持"。
- 未确认外部依赖补成本地实现。
- 未确认数据来源补成具体系统/表。
- P0 问题的风险接受。
- Skill 可复用规则修改（只输出复盘沉淀建议）。

---

## Output Format

### 1. Consistency Sweep Report

| 问题编号 | 一致性类型 | 问题等级 | 冲突位置 A | 冲突位置 B | 问题描述 | 修复建议 | 可自动修 | 需PM确认 |
|---------|-----------|---------|-----------|-----------|---------|---------|---------|---------|

### 2. Auto-Fix Patches

```md
## Patch CS-001：[简短标题]

问题来源：[一致性类型]  
问题等级：P0 / P1 / P2  
修复位置：PRD §X.Y、PRD §A.B  
修复方式：[一句话说明]

【替换前】
...
【替换后】
...
```

### 3. PM Confirmation Items

最多 3 个高优先级问题。每个必须包含：
- 为什么需要确认
- 不确认影响哪部分
- AI 推荐默认值
- 推荐理由
- 确认后将修改的章节

### 4. Sweep Conclusion

| 检查项 | 结果 |
|--------|------|
| 是否存在 P0 一致性问题 | 是 / 否 |
| 是否存在未接受 P1 一致性风险 | 是 / 否 |
| 是否存在旧说法残留 | 是 / 否 |
| 是否需要重新进入 Node 4 Review | 是 / 否 |
| 是否允许进入最终输出门禁 | 是 / 否 |

---

## Real Example: PRD v1.9 Sweep

问题来源：Node 4 修复了 C07(权限矩阵)、C10(状态流转表)、C12(默认排序)、C13(操作控制表)。

Blast radius：修改了 §2、§4.1、§8.1.5.x(8个模板)、§10 全章、§14。

应跑维度：4.流程一致性(跳转入口)、10.术语一致性(版本号)、9.验收一致性。

实际发现问题 3 个，全部可自动修：

| 问题 | 类型 | 自动修 |
|------|------|--------|
| §2 #4 与 §8.3.5 双端能力描述矛盾 | 流程一致性 | 以 §8.3.5 为准更新 §2 |
| 8 个模板明细的跳转入口与 §8.3.5 名称不一致 | 术语一致性 | 逐模板对齐到 §8.3.5 |
| 标题+§14 版本号仍是 v1.8 | 术语一致性 | 统一为 v1.9 |

0 个需 PM 确认。
