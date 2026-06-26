import json, re

with open('C:/Users/rd001/.claude/skills/prd-skills/prd-workflow-skill/05_context/prd-standards/checklist-v3.3.json','r',encoding='utf-8') as f:
    data = json.load(f)

# Clean all template_ref to be semantic labels only (not file paths or Excel coords)
# Routing is handled by suggested_format + table-template-index.md
excel_count = 0
path_count = 0

for item in data['items']:
    tr = item.get('template_ref', '')
    if not tr:
        continue

    cleaned = []
    for part in tr.split(' | '):
        part = part.strip()
        # Strip Excel coordinates: "07_表格模板示例!A94｜异常规则表模板" -> "异常规则表模板"
        if '!' in part:
            if '｜' in part:
                part = part.split('｜')[-1].strip()
            else:
                part = part.split('!')[-1].strip()
            excel_count += 1
        # Strip file paths: "04_templates/table-templates/rule-table.md" -> "rule-table"
        if part.startswith('04_templates'):
            part = part.replace('04_templates/table-templates/', '').replace('.md', '')
            path_count += 1
        # Strip "｜模板" suffix if present as duplicative
        if '｜' in part:
            # Keep just the unique label part
            pass  # already handled above
        cleaned.append(part)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for c in cleaned:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    item['template_ref'] = ' | '.join(unique) if unique else ''

with open('C:/Users/rd001/.claude/skills/prd-skills/prd-workflow-skill/05_context/prd-standards/checklist-v3.3.json','w',encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Verify
sample_with_ref = [(i['id'], i['template_ref']) for i in data['items'] if i.get('template_ref')][:8]
print(f'Cleaned {excel_count} Excel coord refs, {path_count} path refs')
print('Sample remaining template_ref values (semantic labels):')
for item_id, tr in sample_with_ref:
    print(f'  {item_id}: {tr}')
print('\nRouting is now: suggested_format -> table-template-index.md -> .md file')
