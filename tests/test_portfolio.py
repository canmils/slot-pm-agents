import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'examples/portfolio_review'
def module(name):
    spec = importlib.util.spec_from_file_location(name, EXAMPLE / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result
analyze = module('analyze')
agent = module('prepare_agent_input')
CFG = json.loads((EXAMPLE / 'config.json').read_text())

class PortfolioTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = analyze.load(CFG)

    def test_bundled_example_and_agent_handoff(self):
        report, summary = analyze.build(CFG)
        self.assertEqual(len(summary['games']), 30)
        self.assertEqual(summary['data_date'], '2026-09-30')
        self.assertEqual(len(summary['facts']['games_too_young']), 1)
        self.assertIn('fictional', report)
        payload = agent.prepare(summary)
        self.assertEqual(len(payload['messages']), 2)
        self.assertIn('Do not calculate new figures', payload['messages'][0]['content'])
        json.dumps(payload, allow_nan=False)
        # Independently calculate a game window from CSV rows, not lifetime GGR.
        row = summary['games'][0]
        launch = self.tables['games'].set_index('game_id').loc[row['game_id'], 'launch_date']
        p = self.tables['daily_performance']
        days = (p['date'] - launch).dt.days
        expected = p.loc[(p['game_id'] == row['game_id']) & days.between(0, 89), 'ggr_eur'].sum()
        self.assertAlmostEqual(row['ggr_90d'], expected, places=5)
        young = next(g for g in summary['games'] if g['game_id'] in summary['facts']['games_too_young'])
        self.assertIsNone(young['ggr_90d'])

    def test_missing_and_duplicate_daily_rows_are_rejected(self):
        t = copy.deepcopy(self.tables)
        t['daily_performance'] = t['daily_performance'].iloc[1:]
        with self.assertRaisesRegex(ValueError, 'coverage'):
            analyze.validate_tables(t)
        t = copy.deepcopy(self.tables)
        import pandas as pd
        t['daily_performance'] = pd.concat([t['daily_performance'], t['daily_performance'].iloc[:1]])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            analyze.validate_tables(t)

    def test_unknown_game_rejected(self):
        t = copy.deepcopy(self.tables)
        t['daily_performance'].iloc[0, t['daily_performance'].columns.get_loc('game_id')] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'unknown game_id'):
            analyze.validate_tables(t)

    def test_invalid_window_rejected(self):
        with self.assertRaisesRegex(ValueError, 'main_window_days'):
            analyze.validate_config({**CFG, 'main_window_days': 365})

    def test_portfolio_without_reskins_preserves_unknown_variation(self):
        from unittest.mock import patch
        t = {name: table.loc[table['game_id'] == 'G001'].copy() for name, table in self.tables.items()}
        with patch.object(analyze, 'load', return_value=t):
            report, summary = analyze.build(CFG)
        self.assertIsNone(summary['facts']['cost_variation_reskin'])
        self.assertIn('not available', report)
        json.dumps(summary, allow_nan=False)

    def test_cli_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            cmd = [sys.executable, str(EXAMPLE / 'analyze.py'), '--output-dir', directory]
            subprocess.run(cmd, check=True, capture_output=True)
            target = Path(directory) / 'report.md'
            target.write_text('My reviewed report', encoding='utf-8')
            second = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn('Output already exists', second.stderr)
            self.assertEqual(target.read_text(), 'My reviewed report')
            payload = Path(directory) / 'agent-input.json'
            subprocess.run([sys.executable, str(EXAMPLE / 'prepare_agent_input.py'), '--summary', str(Path(directory)/'summary.json'), '--output', str(payload)], check=True, capture_output=True)
            self.assertEqual(json.loads(payload.read_text())['messages'][0]['role'], 'system')

if __name__ == '__main__':
    unittest.main()
