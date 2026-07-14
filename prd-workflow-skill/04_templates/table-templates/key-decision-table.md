# 关键决策点表

> Contract: `key_decision_table`
> Authority: `schemas/key-decision-table.schema.json`
> 本文件仅提供填写示例和边界说明，固定列以 Schema 为准。

| 关键决策点 | 前置条件 | 判断结果 |
|---|---|---|
| 当前对象是否允许继续处理 | 已完成业务前置校验 | 是：继续主路径；否：进入对应分支 |

普通必填、格式校验和纯技术错误不属于关键决策点；没有真实分流时不创建空表。
