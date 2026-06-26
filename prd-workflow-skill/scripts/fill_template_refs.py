import json

with open('C:/Users/rd001/.claude/skills/prd-skills/prd-workflow-skill/05_context/prd-standards/checklist-v3.3.json','r',encoding='utf-8') as f:
    data = json.load(f)

TEMPLATE_MAP = {
    '规则表': 'rule-table.md', '业务规则表': 'rule-table.md', '默认值表': 'rule-table.md',
    '操作控制表': 'rule-table.md', '反馈规则表': 'rule-table.md', '二次确认规则表': 'rule-table.md',
    '弹窗行为规则表': 'rule-table.md', '排序规则表': 'rule-table.md', '查询规则表': 'rule-table.md',
    '筛选规则表': 'rule-table.md', '分页规则表': 'rule-table.md', '展示规则表': 'rule-table.md',
    '图表展示规则表': 'rule-table.md', '控件规则表': 'rule-table.md', '初始化规则表': 'rule-table.md',
    '空态规则表': 'rule-table.md', '失败态规则表': 'rule-table.md', '重复处理表': 'rule-table.md',
    '冲突处理表': 'rule-table.md', '权限异常表': 'rule-table.md', '数量规则表': 'rule-table.md',
    '上传规则表': 'rule-table.md', '交互状态表': 'rule-table.md', '加载状态表': 'rule-table.md',
    '字段规则表': 'field-rule-table.md', '字段总表': 'field-rule-table.md', '表格字段总览': 'field-rule-table.md',
    '校验规则表': 'validation-rule-table.md',
    '数据口径表': 'data-caliber-table.md', '数据来源表': 'data-caliber-table.md',
    '统计口径表': 'data-caliber-table.md', '单位精度表': 'data-caliber-table.md',
    '异常规则表': 'exception-handling-writing.md',
    '验收标准表': 'acceptance-criteria-table.md',
    '自测用例表': 'self-test-case-table.md',
    '风险接受表': 'risk-acceptance-table.md', '待确认事项表': 'risk-acceptance-table.md',
}

filled = 0
for item in data['items']:
    if item.get('template_ref'):
        continue
    sf = item.get('suggested_format', '')
    if not sf:
        continue
    parts = [p.strip() for p in sf.replace(' / ', '/').split('/')]
    matched = []
    for part in parts:
        part = part.strip()
        if part in TEMPLATE_MAP:
            matched.append(TEMPLATE_MAP[part])
    if matched:
        seen = set()
        unique = []
        for m in matched:
            if m not in seen:
                seen.add(m)
                unique.append(m)
        base = '04_templates/table-templates'
        refs = [f'{base}/{m}' for m in unique]
        item['template_ref'] = ' | '.join(refs)
        filled += 1
        print(f"{item['id']} {item['item']} -> {item['template_ref']}")

with open('C:/Users/rd001/.claude/skills/prd-skills/prd-workflow-skill/05_context/prd-standards/checklist-v3.3.json','w',encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nDone: {filled} items filled")
