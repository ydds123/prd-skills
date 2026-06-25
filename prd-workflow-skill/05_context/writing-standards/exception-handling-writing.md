# Exception Handling Writing

> Belongs to: `05_context/writing-standards/`  
> Governed by: `prd-definition-quality-standard.md` §6.2 "异常情况"  
> Evidence: first PRD run — v1.0 lacked exception handling for all features; 6 features needed retroactive addition in v1.1  
> Version: v1.0.0

---

Every core feature must include an exception handling table. If the feature genuinely has no possible exception states, state "本功能无特殊异常" — do not omit the table. Silence is indistinguishable from an omission.

## Table Structure

```
触发条件 | 处理逻辑 | 引导提示 | 恢复机制
```

| Column | Content |
|--------|---------|
| 触发条件 | The specific scenario that triggers the exception (e.g. "分组名称为空", "网络异常", "查询无结果") |
| 处理逻辑 | What the system does (e.g. "阻断保存", "保留页面并提供重试入口", "展示空列表状态") |
| 引导提示 | The exact message shown to the user (e.g. "请输入分组名称", "消息加载失败，请重试") |
| 恢复机制 | What the user can do to recover (e.g. "用户补充分组名称后重新保存", "用户点击重试或刷新") |

## Coverage Dimensions

For each core feature, check these dimensions:

| Dimension | Trigger examples | Must cover? |
|-----------|-----------------|-------------|
| 空态 (empty) | No data, no results, blank field | Always |
| 失败态 (failure) | Submit fails, load fails, save fails | Always (if the feature has a submit/load/save) |
| 校验失败 (validation) | Required field empty, format invalid, duplicate name | Always (if the feature has input) |
| 网络异常 (network) | Request timeout, no response, partial failure | Always |
| 权限不足 (permission) | User lacks view/edit/delete permission | If the feature has role-based access |
| 并发冲突 (concurrency) | Data modified by another user, state already changed | If the feature edits shared data |
| 依赖缺失 (dependency) | Required config not set, upstream data unavailable | If the feature has dependencies |
| 数据边界 (boundary) | Over-length text, max items exceeded, numeric overflow | If the feature has input with constraints |

## Coverage Rule

**Do not pad.** If a dimension does not apply to this feature, skip it. But check all eight before concluding. The most common error is skipping 网络异常 because "the system will always be online" — no system is always online.

## User-Facing vs System-Only Exceptions

| Exception type | 引导提示 shows? | 恢复机制 shows? |
|---------------|----------------|----------------|
| User-correctable (empty field, duplicate name) | Yes — tell the user what to fix | Yes — tell the user how to proceed |
| System-only (config sync failed, background job timeout) | No frontend prompt | Log and notify admin/ops; user retries are automatic on next action |
| Silent (template disabled, no matching template) | No frontend prompt | Log for troubleshooting; user experience is unaffected |

## Anti-patterns

| Don't | Why | Do instead |
|-------|-----|------------|
| Omit the exception table entirely | R&D implements only the happy path, QA discovers gaps in production | Write the table; if truly no exceptions, write "本功能无特殊异常" |
| Use vague prompts | "操作失败" tells the user nothing — they don't know if they should retry, change input, or contact support | Write the exact prompt: "分组名称已存在，请修改后保存" |
| Skip the 恢复机制 column | The user knows something went wrong but has no path forward | Every exception row must answer: "and then what?" |
| Treat network errors as "won't happen" | WiFi drops, VPN disconnects, load balancer fails — these are normal, not exceptional | Cover network exceptions for every feature that makes a request |
