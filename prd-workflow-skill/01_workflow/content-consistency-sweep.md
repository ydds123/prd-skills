# 修订后内容一致性回扫

> 所属节点：Node 4.5
> 权威规则：`01_workflow/consistency-sweep-rules.json`

## 目的

在应用已确认的修订后，检查变更是否造成跨章节矛盾、旧口径残留或关联内容未同步。它是按变更影响范围执行的定向回扫，不是重新执行整份 Checklist。

本文件只解释执行方法。受控维度、变更类型到维度的映射、自动修复边界、需确认边界、禁止事项、证据优先级和可跳过的变更类型，均以权威 JSON 为准；不得在 Markdown 中另维护一份列表。

## 执行步骤

1. 列出本轮实际内容变更，并为每类变更选择 JSON 中存在的 `change_routes.id`。
2. 读取每个变更类型的 `required_dimensions`，取并集作为本轮最小必查维度。
3. 按必查维度检索 PRD 的受影响章节和交叉引用，记录可定位的 `location + summary` 证据。
4. 按 JSON 中的 `repair_boundaries` 判断：可直接修、需要产品经理确认或禁止修改。
5. 直接修复有现成证据且不引入新产品事实的问题；需要确认的问题每轮最多集中展示 3 项。
6. 修订完成后重新回扫，并将最终结果写入 `06-内容质量审查.json` 的 `consistency_sweep`。
7. 执行内容门禁；未知变更类型、未知维度、必查维度覆盖不足或缺少证据时必须阻断。

## 审查记录

内容有实质变更时：

```json
{
  "consistency_sweep": {
    "status": "complete",
    "change_types": ["<change_routes.id>"],
    "dimensions_checked": ["<dimensions.id>"],
    "evidence": [
      {"location": "<章节或文件位置>", "summary": "<检查结果>"}
    ]
  }
}
```

只有变更类型属于 JSON 的 `not_required_change_types` 时，才允许：

```json
{
  "consistency_sweep": {
    "status": "not_required",
    "change_types": ["<not_required_change_types 中的值>"],
    "dimensions_checked": [],
    "evidence": []
  }
}
```

## 人类可读输出

| 变更类型 | 必查维度 | 已检查维度 | 证据位置 | 发现与处理 | 结论 |
|---|---|---|---|---|---|
| 读取权威 JSON | 读取权威 JSON | 实际执行结果 | 文件/章节 | 已修复、待确认或禁止修改 | 通过或阻断 |

输出中使用 JSON 的 ID 或当前名称即可，不复制维护完整映射表。若 JSON 与任何说明文档冲突，以 JSON 为准，并将说明文档漂移作为 Skill 缺陷记录。
