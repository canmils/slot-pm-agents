import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "examples/portfolio_review"
COMPARABLES = ROOT / "examples/comparables"


def module(folder: Path, name: str):
    sys.path.insert(0, str(folder))
    spec = importlib.util.spec_from_file_location(name, folder / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


check = module(PORTFOLIO, "check_agent_output")
run_agent = module(PORTFOLIO, "run_agent")
comparables = module(COMPARABLES, "find_comparables")
SUMMARY = json.loads((PORTFOLIO / "summary.json").read_text(encoding="utf-8"))


class TraceabilityTest(unittest.TestCase):
    def test_committed_agent_draft_traces_to_summary(self):
        draft = (PORTFOLIO / "agent_output.md").read_text(encoding="utf-8")
        self.assertEqual(check.untraceable_numbers(draft, SUMMARY), [])

    def test_invented_numbers_are_caught(self):
        problems = check.untraceable_numbers("Ember Fang median is 950k and share is 71%.", SUMMARY)
        self.assertEqual(len(problems), 2)

    def test_window_number_does_not_authorize_percentage(self):
        summary = {"ggr_90d": 1000, "share": 0.57}
        self.assertEqual(check.untraceable_numbers("Share 90%.", summary), ["line 1: 90%"])
        self.assertEqual(check.untraceable_numbers("Share 57%.", summary), [])
        self.assertEqual(check.untraceable_numbers("Top 20%.", {"top_20pct": {"share": 0.57}}), [])

    def test_formats_and_ignored_parts(self):
        text = ("> Written on 15 October 2026 by a model 5.5\n"
                "1. Data up to 2026-09-30, G030 is young.\n"
                "Median 909k, range 1,379k, 57% share, 14 milestones, 2.6 weeks, 90 days.")
        self.assertEqual(check.untraceable_numbers(text, SUMMARY), [])

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.md"
            bad.write_text("Revenue will be 999k.", encoding="utf-8")
            self.assertEqual(check.main(["--summary", str(PORTFOLIO / "summary.json"), "--draft", str(bad)]), 1)
            self.assertEqual(check.main(["--summary", str(PORTFOLIO / "summary.json"),
                                         "--draft", str(PORTFOLIO / "agent_output.md")]), 0)


class RunAgentTest(unittest.TestCase):
    def args(self, out):
        return ["--summary", str(PORTFOLIO / "summary.json"), "--output", str(out), "--yes"]

    def test_no_key_sends_nothing(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {}, clear=True):
            calls = []
            code = run_agent.main(self.args(Path(tmp) / "d.md"), model_call=lambda m, mod: calls.append(m))
            self.assertEqual(code, 1)
            self.assertEqual(calls, [])

    def test_good_draft_saved_and_checked(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"OPENAI_API_KEY": "test"}):
            out = Path(tmp) / "d.md"
            code = run_agent.main(self.args(out), model_call=lambda m, mod: "Ember Fang median 909k.")
            self.assertEqual(code, 0)
            self.assertTrue(out.read_text(encoding="utf-8").startswith("> Agent output from"))

    def test_invented_number_returns_2(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"OPENAI_API_KEY": "test"}):
            code = run_agent.main(self.args(Path(tmp) / "d.md"), model_call=lambda m, mod: "Next game: 2,500k.")
            self.assertEqual(code, 2)

    def test_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"OPENAI_API_KEY": "test"}):
            out = Path(tmp) / "d.md"
            out.write_text("keep", encoding="utf-8")
            calls = []
            self.assertEqual(run_agent.main(self.args(out), model_call=lambda m, mod: calls.append(m)), 1)
            self.assertEqual(out.read_text(encoding="utf-8"), "keep")
            self.assertEqual(calls, [])


class ComparablesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.games, cls.summary = comparables.load_games(PORTFOLIO / "config.json")

    def test_committed_example_is_current(self):
        md, result = comparables.run(COMPARABLES / "option.json", PORTFOLIO / "config.json")
        self.assertEqual(md, (COMPARABLES / "comparables.md").read_text(encoding="utf-8"))
        self.assertEqual(len(result["comparables"]), 3)
        self.assertIn("All comparables are from one family", md)
        self.assertIn("Treat these rows as anecdotes", md)
        self.assertIn("not yet", md)

    def test_drops_least_important_criterion_first(self):
        criteria = [("mechanic", "cluster"), ("volatility", "high"), ("type", "original")]
        matches, dropped = comparables.find(self.games, criteria)
        self.assertEqual(dropped[0], "type")
        self.assertGreaterEqual(len(matches), 3)
        self.assertTrue(all(g["mechanic"] == "cluster" for g in matches))

    def test_strict_cohort_does_not_relax_exclusivity(self):
        games = [{"mechanic": "cluster", "exclusive": False}] + [
            {"mechanic": "cluster", "exclusive": True} for _ in range(3)]
        criteria = [("mechanic", "cluster"), ("exclusive", False)]
        matches, dropped = comparables.find(games, criteria, strict=True)
        self.assertEqual(len(matches), 1)
        self.assertEqual(dropped, [])
        relaxed, dropped = comparables.find(games, criteria)
        self.assertEqual(len(relaxed), 4)
        self.assertEqual(dropped, ["exclusive"])

    def test_strict_cli_preserves_all_supplied_criteria(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(comparables.main(["--strict", "--output-dir", tmp]), 0)
            result = json.loads((Path(tmp) / "comparables.json").read_text())
            self.assertEqual(result["dropped_criteria"], [])
            selected = [g for g in self.games if g["game_id"] in result["comparables"]]
            self.assertTrue(all(g["mechanic"] == "hold_and_win" and
                                g["volatility"] == "high" and g["exclusive"] is False for g in selected))

    def test_strict_no_matches_stays_empty(self):
        matches, dropped = comparables.find([{"seasonal": True}], [("seasonal", False)], strict=True)
        self.assertEqual((matches, dropped), ([], []))

    def test_young_games_never_counted_as_zero(self):
        young = [g for g in self.games if g["ggr_90d"] is None]
        self.assertTrue(young)
        row = [r for r in comparables.ranges(young) if r.get("window_days") == 90][0]
        self.assertEqual(row["games"], 0)
        self.assertIsNone(row["median"])

    def test_unknown_criterion_rejected(self):
        with self.assertRaises(ValueError):
            comparables.validate_option({"criteria": {"rtp": 0.96}})
        with self.assertRaises(ValueError):
            comparables.validate_option({"criteria": {}})

    def test_cli_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(comparables.main(["--output-dir", tmp]), 0)
            with self.assertRaises(SystemExit):
                comparables.main(["--output-dir", tmp])


if __name__ == "__main__":
    unittest.main()
