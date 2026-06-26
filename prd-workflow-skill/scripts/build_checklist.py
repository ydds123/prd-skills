import openpyxl, json

wb = openpyxl.load_workbook('C:/Users/rd001/.claude/skills/prd-skills/需求自查清单_V3.3_PRD质量门禁版_含表格模板示例.xlsx')
ws = wb['01_需求自查清单']

items = []
for row in ws.iter_rows(min_row=2, values_only=True):
    seq = row[0]
    if seq is None:
        continue
    item = {
        'id': f'C{int(seq):02d}',
        'hierarchy': 'gate' if str(row[1]).strip() == '必查门禁' else ('extended' if str(row[1]).strip() == '扩展检查' else 'advisory'),
        'domain': str(row[2]).strip() if row[2] else '',
        'module': str(row[3]).strip() if row[3] else '',
        'item': str(row[4]).strip() if row[4] else '',
        'condition': str(row[5]).strip() if row[5] else '',
        'question': str(row[6]).strip() if row[6] else '',
        'pass_criteria': str(row[7]).strip() if row[7] else '',
        'failure_signal': str(row[8]).strip() if row[8] else '',
        'suggested_location': str(row[9]).strip() if row[9] else '',
        'suggested_format': str(row[10]).strip() if row[10] else '',
        'priority': str(row[11]).strip() if row[11] else '',
        'complexity': str(row[12]).strip() if row[12] else '',
        'template_ref': str(row[21]).strip() if len(row) > 21 and row[21] else ''
    }
    items.append(item)

# Build load_map
quality_indicators = {
    'boundary': ['边界清晰检查'],
    'judgment': ['需求定义与复杂度判断', '判断显性检查'],
    'guesswork': ['不留猜疑检查', '操作交互与反馈检查'],
    'accuracy': ['信息准确检查', '阻塞问题与评审结论'],
    'page_form': ['页面、表单与数据展示检查'],
    'list_query': ['列表查询与数据展示检查'],
    'report_chart': ['报表图表与统计检查'],
    'exception_test': ['异常验收与测试检查'],
    'init_history': ['初始化历史与测试检查'],
    'expression': ['组织表达优化']
}

load_map = {}
for label, domains in quality_indicators.items():
    matched = [i for i in items if i['domain'] in domains]
    if matched:
        load_map[label] = {
            'domains': domains,
            'gate_count': sum(1 for i in matched if i['hierarchy'] == 'gate'),
            'extended_count': sum(1 for i in matched if i['hierarchy'] == 'extended'),
            'advisory_count': sum(1 for i in matched if i['hierarchy'] == 'advisory'),
            'item_ids': [i['id'] for i in matched]
        }

data = {
    'meta': {
        'version': '3.3',
        'source': 'PRD需求自查清单 V3.3',
        'governed_by': 'prd-definition-quality-standard.md',
        'total_items': len(items),
        'hierarchies': {
            'gate': sum(1 for i in items if i['hierarchy'] == 'gate'),
            'extended': sum(1 for i in items if i['hierarchy'] == 'extended'),
            'advisory': sum(1 for i in items if i['hierarchy'] == 'advisory')
        }
    },
    'items': items,
    'load_map': load_map,
    'gate_rules': {
        'review_conclusion': {
            'logic': 'V3.3 review conclusion formula',
            'rules': [
                {'condition': 'P0_block > 0', 'conclusion': '不可进入评审', 'action': 'block'},
                {'condition': 'P1_risk_unaccepted > 0', 'conclusion': '默认不建议进入评审', 'action': 'block_unless_accepted'},
                {'condition': 'pending_check > 0', 'conclusion': '检查未完成', 'action': 'warn'},
                {'condition': 'pending_supplement > 0', 'conclusion': '需补充', 'action': 'warn'},
                {'condition': 'all_clear', 'conclusion': '可进入评审', 'action': 'pass'}
            ]
        },
        'priority_rules': {
            'P0': {'severity': '致命问题', 'behavior': '必须阻塞', 'fix_rule': '必须修正，不能仅标记风险接受'},
            'P1': {'severity': '高风险问题', 'behavior': '默认阻塞', 'fix_rule': '优先修正；如PM接受风险须记录原因、责任人、后续动作'},
            'P2': {'severity': '质量问题', 'behavior': '不默认阻塞', 'fix_rule': '建议评审前修正；反复出现时进入模板/Skill迭代'},
            'P3': {'severity': '优化建议', 'behavior': '不阻塞', 'fix_rule': '不影响交付时处理'}
        }
    }
}

out_path = 'C:/Users/rd001/.claude/skills/prd-skills/prd-workflow-skill/05_context/prd-standards/operational-completeness-checklist.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Written {len(items)} items to {out_path}")
print(f"  Gate: {data['meta']['hierarchies']['gate']}")
print(f"  Extended: {data['meta']['hierarchies']['extended']}")
print(f"  Advisory: {data['meta']['hierarchies']['advisory']}")
print(f"  Load map groups: {list(load_map.keys())}")
