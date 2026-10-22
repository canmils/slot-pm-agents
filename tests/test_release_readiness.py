import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'examples/release_readiness'
spec = importlib.util.spec_from_file_location('readiness', FOLDER / 'check.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
FIXTURE = json.loads((FOLDER / 'fictional-release.json').read_text(encoding='utf-8'))


class ReadinessTest(unittest.TestCase):
    def review(self, data):
        return checker.review(data, '2026-10-22')

    def clean(self):
        data = copy.deepcopy(FIXTURE)
        data['checks'][1]['evidence_build'] = data['build']
        data['checks'][2].update(status='complete', completed_on='2026-10-21',
                                 evidence='fictional://cert/review', reviewer='Pat', evidence_build=data['build'])
        data['checks'].append(dict(id='activation', name='Activation review', owner='Chris',
                                  status='complete', due_date='2026-10-22', completed_on='2026-10-22',
                                  evidence='fictional://activation/review', reviewer='Robin',
                                  evidence_build=data['build'], depends_on=['cert']))
        return data

    def test_fixture_specific_findings(self):
        result = self.review(FIXTURE)
        self.assertEqual(result['blockers'], 4)
        self.assertEqual({(x['check_id'], x['code']) for x in result['findings']},
                         {('activation','missing_check'), ('qa','build_mismatch'),
                          ('cert','overdue'), ('cert','dependency_unresolved')})
        self.assertIn('not opened or verified', result['limitation'])

    def test_clean_is_never_approval(self):
        result = self.review(self.clean())
        self.assertEqual(result['blockers'], 0)
        self.assertEqual(result['status'], 'NO BLOCKERS FOUND IN SUPPLIED RECORDS')
        self.assertIn('Human release decision required', result['limitation'])

    def test_complete_without_evidence_reviewer_or_date_blocks(self):
        for field in ('evidence', 'reviewer', 'completed_on'):
            with self.subTest(field=field):
                data = self.clean()
                del data['checks'][0][field]
                result = self.review(data)
                self.assertTrue(any(f['code'] == 'missing_' + field for f in result['findings']))
                self.assertEqual(result['status'], 'BLOCKED')

    def test_unowned_and_due_after_release_block(self):
        data = self.clean()
        data['checks'][0].update(owner='', due_date='2026-10-30')
        codes = {f['code'] for f in self.review(data)['findings']}
        self.assertTrue({'missing_owner', 'after_release'} <= codes)

    def test_not_due_yet_still_incomplete(self):
        data = self.clean()
        data['checks'][3].update(status='pending', due_date='2026-10-29')
        result = self.review(data)
        self.assertEqual(result['blockers'], 1)
        self.assertEqual(result['findings'][0]['code'], 'pending')

    def test_optional_dependency_is_required_transitively(self):
        data = self.clean()
        data['required_check_ids'] = ['activation']
        data['checks'][0]['status'] = 'pending'
        result = self.review(data)
        self.assertTrue(all(f['severity'] == 'blocker' for f in result['findings']))
        self.assertTrue(any(f['check_id']=='activation' and f['code']=='dependency_unresolved'
                            for f in result['findings']))

    def test_unrelated_pending_check_is_warning(self):
        data = self.clean()
        data['checks'].append(dict(id='nice', name='Optional polish', owner='Lee', status='pending',
                                  due_date='2026-10-25', depends_on=[]))
        result = self.review(data)
        self.assertEqual((result['blockers'], result['warnings']), (0, 1))

    def test_invalid_dates_status_duplicates_and_graph(self):
        changes = [lambda d: d['checks'][0].update(status='approved'),
                   lambda d: d.update(release_date='2026-02-30'),
                   lambda d: d['checks'][0].update(completed_on='2026-10-23'),
                   lambda d: d['checks'].append(copy.deepcopy(d['checks'][0])),
                   lambda d: d['checks'][0].update(depends_on=['unknown']),
                   lambda d: d['checks'][0].update(depends_on=['activation']),
                   lambda d: d.update(required_check_ids=[]),
                   lambda d: d.update(required_check_ids=['qa', 'qa'])]
        for change in changes:
            data = self.clean()
            change(data)
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.review(data)

    def test_report_escapes_table_content(self):
        data = self.clean()
        data['checks'][0].update(owner='Alex|Pat\nTeam', status='pending')
        report = checker.markdown(self.review(data))
        self.assertIn('Alex\\|Pat Team', report)

    def test_cli_exit_codes_and_no_overwrite(self):
        cmd = [sys.executable, str(FOLDER / 'check.py'), '--as-of', '2026-10-22']
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'report'
            first = subprocess.run(cmd + ['--output-dir',str(out)], capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            original = (out/'report.json').read_bytes()
            again = subprocess.run(cmd + ['--output-dir',str(out)], capture_output=True, text=True)
            self.assertEqual(again.returncode, 2)
            self.assertEqual((out/'report.json').read_bytes(), original)
            self.assertEqual(subprocess.run(cmd + ['--fail-on-blockers'], capture_output=True).returncode, 1)
            bad = Path(tmp)/'bad.json'
            bad.write_text('{broken', encoding='utf-8')
            self.assertEqual(subprocess.run(cmd + ['--input',str(bad)], capture_output=True).returncode, 2)

    def test_committed_report_reproducible(self):
        expected = self.review(FIXTURE)
        self.assertEqual(json.loads((FOLDER/'report.json').read_text(encoding='utf-8')), expected)
        self.assertEqual((FOLDER/'report.md').read_text(encoding='utf-8'), checker.markdown(expected))


if __name__ == '__main__':
    unittest.main()
