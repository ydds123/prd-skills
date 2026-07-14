#!/usr/bin/env python3
"""Validate a prd-workflow 09-run-log.md output contract."""

import argparse
import re
import sys
from pathlib import Path

FULL_TIMESTAMP = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')
LEGACY_DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
SEPARATOR_CELL = re.compile(r'^:?-{3,}:?$')
LEVEL_RANK = {'T0': 0, 'T1': 1, 'T2': 2, 'T3': 3}


def split_row(line):
    value = line.strip()
    if value.startswith('|'):
        value = value[1:]
    if value.endswith('|'):
        value = value[:-1]
    return [cell.strip() for cell in re.split(r'(?<!\\)\|', value)]


def is_separator(line):
    cells = split_row(line)
    return bool(cells) and all(SEPARATOR_CELL.fullmatch(cell) for cell in cells)


def parse_tables(lines):
    heading = ''
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith('## '):
            heading = stripped[3:].strip()
        if (
            stripped.startswith('|')
            and index + 1 < len(lines)
            and is_separator(lines[index + 1])
        ):
            headers = split_row(lines[index])
            rows = []
            row_index = index + 2
            while row_index < len(lines) and lines[row_index].strip().startswith('|'):
                rows.append((row_index + 1, split_row(lines[row_index])))
                row_index += 1
            yield heading, index + 1, headers, rows
            index = row_index
            continue
        index += 1


def required_level_for_count(count):
    if count >= 3:
        return 'T3'
    if count >= 2:
        return 'T2'
    return 'T1'


def validate(path, allow_legacy_date=False):
    lines = path.read_text(encoding='utf-8').splitlines()
    errors = []
    warnings = []
    table_count = 0
    trigger_ids = set()
    legacy_lines = []

    for heading, header_line, headers, rows in parse_tables(lines):
        table_count += 1
        for line_number, cells in rows:
            if len(cells) != len(headers):
                errors.append(
                    f'line {line_number}: table {heading!r} has {len(cells)} cells; expected {len(headers)}')
                continue

            for column in ('时间', '开始时间', '完成时间'):
                if column not in headers:
                    continue
                value = cells[headers.index(column)]
                if not value or value == '—':
                    continue
                if FULL_TIMESTAMP.fullmatch(value):
                    continue
                if allow_legacy_date and LEGACY_DATE.fullmatch(value):
                    legacy_lines.append(line_number)
                    continue
                errors.append(
                    f'line {line_number}: {column} must use YYYY-MM-DD HH:mm:ss, got {value!r}')

            if heading == '复盘触发状态' and '触发编号' in headers:
                trigger_id = cells[headers.index('触发编号')]
                if trigger_id in trigger_ids:
                    errors.append(f'line {line_number}: duplicate trigger ID {trigger_id!r}')
                trigger_ids.add(trigger_id)

                try:
                    count = int(cells[headers.index('出现次数')])
                except (ValueError, IndexError):
                    errors.append(f'line {line_number}: 出现次数 must be a positive integer')
                    continue
                if count < 1:
                    errors.append(f'line {line_number}: 出现次数 must be at least 1')
                    continue

                level = cells[headers.index('当前等级')]
                required = required_level_for_count(count)
                if level not in LEVEL_RANK:
                    errors.append(f'line {line_number}: unknown trigger level {level!r}')
                elif LEVEL_RANK[level] < LEVEL_RANK[required]:
                    errors.append(
                        f'line {line_number}: count {count} requires at least {required}, got {level}')

    if legacy_lines:
        sample = ', '.join(str(line) for line in legacy_lines[:5])
        suffix = '...' if len(legacy_lines) > 5 else ''
        warnings.append(
            f'{len(legacy_lines)} legacy date-only values allowed for migration; lines {sample}{suffix}')
    if table_count == 0:
        errors.append('no Markdown tables found')
    return errors, warnings, table_count


def main():
    parser = argparse.ArgumentParser(description='Validate 09-run-log.md structure and evidence rules')
    parser.add_argument('run_log', help='Path to 09-run-log.md')
    parser.add_argument(
        '--allow-legacy-date',
        action='store_true',
        help='Allow pre-migration YYYY-MM-DD values as warnings; new tasks must not use this flag.',
    )
    args = parser.parse_args()

    path = Path(args.run_log)
    if not path.exists():
        print(f'[ERROR] run log not found: {path}')
        return 1

    errors, warnings, table_count = validate(path, args.allow_legacy_date)
    print(f'Run log validation: {path}')
    print(f'Tables: {table_count}  Errors: {len(errors)}  Warnings: {len(warnings)}')
    for warning in warnings:
        print(f'[WARN] {warning}')
    for error in errors:
        print(f'[ERROR] {error}')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())


