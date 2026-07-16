# Prototype Context Intake

Use this reference when a PRD task has UI prototypes, screenshots, wireframes, or a folder named like `原型文件`.

## First Principle

Prototype files are evidence for what users can see and operate. They are not decoration. If a PRD writes query conditions, list columns, form fields, buttons, tabs, or page-level operation names, and a prototype exists, the writer must inspect the prototype before treating those items as facts.

## Boot Intake

During task folder initialization:

1. Record the prototype source path in `00-上下文证据.md`.
2. List readable prototype files and unreadable or unsupported files separately.
3. Map prototype pages to PRD function domains when possible.
4. Extract visible UI facts only: query conditions, list fields, detail fields, form fields, operation buttons, tabs, filters, import/export entry names, and obvious empty/error states.
5. Mark cropped, blurry, hidden, dynamic, or ambiguous areas as `待原型核对`; do not infer them from component templates.

Recommended evidence table:

| 功能域/页面 | 原型文件 | 读取状态 | 查询条件 | 列表字段 | 表单/详情字段 | 操作入口 | 不清晰区域 | 写作处理 |
|---|---|---|---|---|---|---|---|---|
| 示例 | `原型文件/...` | 已读取/不可读/需放大 | 只写可见项 | 只写可见项 | 只写可见项 | 只写可见项 | 截图遮挡/未展示 | 写入正文/待原型核对 |

## Writing Rules

- Prototype-visible UI fields outrank generic component defaults.
- Existing PRD decisions, user confirmations, and source-system rules can explain behavior behind a visible field, but should not silently add fields that the prototype does not show.
- Component specifications can guide how to describe an input control, but cannot create business rules, lengths, requiredness, status values, or defaults without project evidence.
- If source materials and prototype conflict, record the conflict in the decision ledger or pending-review list before finalizing the PRD text.

## Quality Gate Signal

A review should flag a finding when:

- a page-level field list was written while prototype files were available but not inspected;
- prototype-visible fields differ from the PRD without an explicit decision;
- component templates were used to fill requiredness, length, option values, or defaults as settled rules without project evidence;
- unclear prototype areas were converted into confident PRD wording instead of `待原型核对`.
