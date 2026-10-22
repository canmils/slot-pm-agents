"""Offline release evidence review. Supplied records never constitute release approval."""
import argparse
from datetime import date
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def day(value, field):
    try:
        if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
            raise ValueError
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError(f'{field}: expected YYYY-MM-DD') from None


def text(value):
    return isinstance(value, str) and bool(value.strip())


def review(data, as_of):
    """Validate a supplied snapshot and return stable, source-linked findings."""
    today = day(as_of, 'as_of')
    if not isinstance(data, dict):
        raise ValueError('input must be an object')
    for field in ('project', 'build', 'policy_source'):
        if not text(data.get(field)):
            raise ValueError(f'{field}: non-empty text required')
    release = day(data.get('release_date'), 'release_date')
    required = data.get('required_check_ids')
    if (not isinstance(required, list) or not required or
            not all(text(x) for x in required) or len(set(required)) != len(required)):
        raise ValueError('required_check_ids: unique, non-empty list required')
    rows = data.get('checks')
    if not isinstance(rows, list):
        raise ValueError('checks: list required')
    checks = {}
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or not text(row.get('id')):
            raise ValueError(f'checks[{i}]: id required')
        key = row['id']
        if key in checks:
            raise ValueError(f'duplicate check id: {key}')
        if row.get('status') not in ('pending', 'complete'):
            raise ValueError(f'{key}: status must be pending or complete')
        if not text(row.get('name')):
            raise ValueError(f'{key}: name required')
        day(row.get('due_date'), f'{key}.due_date')
        deps = row.get('depends_on')
        if (not isinstance(deps, list) or not all(text(x) for x in deps)
                or len(set(deps)) != len(deps)):
            raise ValueError(f'{key}: depends_on must be a unique list')
        if row.get('completed_on') is not None:
            completed = day(row['completed_on'], f'{key}.completed_on')
            if completed > today:
                raise ValueError(f'{key}: completion is after as_of')
        checks[key] = row
    visiting, visited = set(), set()

    def visit(key):
        if key in visiting:
            raise ValueError(f'dependency cycle at {key}')
        if key in visited:
            return
        visiting.add(key)
        for dep in checks[key]['depends_on']:
            if dep not in checks:
                raise ValueError(f'{key}: unknown dependency {dep}')
            visit(dep)
        visiting.remove(key)
        visited.add(key)

    for key in checks:
        visit(key)
    needed = set()

    def require(key):
        if key in needed:
            return
        needed.add(key)
        if key in checks:
            for dep in checks[key]['depends_on']:
                require(dep)

    for key in required:
        require(key)
    findings = []

    def add(key, code, detail):
        findings.append({'check_id': key, 'code': code,
                         'severity': 'blocker' if key in needed else 'warning',
                         'owner': checks.get(key, {}).get('owner') or 'Unassigned',
                         'source': f'checks[{key}]' if key in checks else 'required_check_ids',
                         'detail': detail})

    for key in sorted(needed - checks.keys()):
        add(key, 'missing_check', 'Required check has no record. Supply its status and evidence.')
    credible = {}
    for key, row in sorted(checks.items()):
        valid = row['status'] == 'complete'
        if not text(row.get('owner')):
            add(key, 'missing_owner', 'Assign an accountable owner.')
            valid = False
        if day(row['due_date'], f'{key}.due_date') > release:
            add(key, 'after_release', f"Due {row['due_date']}, after target {data['release_date']}.")
            valid = False
        if row['status'] == 'pending':
            overdue = day(row['due_date'], f'{key}.due_date') < today
            add(key, 'overdue' if overdue else 'pending',
                f"Incomplete; due {row['due_date']}." + (' Overdue.' if overdue else ''))
        else:
            for field in ('completed_on', 'evidence', 'reviewer'):
                if not text(row.get(field)):
                    add(key, 'missing_' + field, f'Complete status lacks {field}.')
                    valid = False
            if row.get('evidence_build') != data['build']:
                add(key, 'build_mismatch', f"Evidence must identify candidate build {data['build']}.")
                valid = False
        credible[key] = valid
    dependency_ok = {}

    def supported(key):
        if key not in dependency_ok:
            dependency_ok[key] = credible[key] and all(supported(d) for d in checks[key]['depends_on'])
        return dependency_ok[key]

    for key, row in sorted(checks.items()):
        for dep in row['depends_on']:
            if not supported(dep):
                add(key, 'dependency_unresolved', f'Dependency {dep} has incomplete or unsupported evidence.')
    blockers = sum(f['severity'] == 'blocker' for f in findings)
    warnings = len(findings) - blockers
    return {'project': data['project'], 'build': data['build'], 'as_of': as_of,
            'release_date': data['release_date'], 'policy_source': data['policy_source'],
            'status': 'BLOCKED' if blockers else 'NO BLOCKERS FOUND IN SUPPLIED RECORDS',
            'blockers': blockers, 'warnings': warnings, 'findings': findings,
            'limitation': 'Human release decision required. Evidence references are not opened or verified; policy completeness, authenticity and regulatory compliance are not assessed.'}


def cell(value):
    return str(value).replace('|', '\\|').replace('\r', ' ').replace('\n', ' ')


def markdown(result):
    lines = ['# Release readiness review', '',
             f"Project: {cell(result['project'])} · Build: {cell(result['build'])}",
             f"As of: {result['as_of']} · Target: {result['release_date']}",
             f"Policy supplied: {cell(result['policy_source'])}", '',
             f"**{result['status']}** — {result['blockers']} blockers; {result['warnings']} warnings.", '',
             '| Severity | Check | Owner | Finding | Source |',
             '| --- | --- | --- | --- | --- |']
    for f in result['findings']:
        lines.append('| ' + ' | '.join(cell(f[k]) for k in ('severity', 'check_id', 'owner', 'detail', 'source')) + ' |')
    lines += ['', result['limitation'], '']
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=HERE / 'fictional-release.json')
    parser.add_argument('--as-of', required=True, help='Explicit review date, YYYY-MM-DD')
    parser.add_argument('--output-dir', type=Path, help='New directory; existing directories are never overwritten')
    parser.add_argument('--fail-on-blockers', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = review(json.loads(args.input.read_text(encoding='utf-8')), args.as_of)
        report = markdown(result)
        if args.output_dir:
            args.output_dir.mkdir(parents=True, exist_ok=False)
            (args.output_dir / 'report.md').write_text(report, encoding='utf-8')
            (args.output_dir / 'report.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(report)
        return 1 if args.fail_on_blockers and result['blockers'] else 0
    except (OSError, ValueError, TypeError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    sys.exit(main())
