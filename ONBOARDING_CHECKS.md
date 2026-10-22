# Verification record

## 15 October 2026

Fresh Python 3.12 virtual environment installed from requirements on Linux.
Six offline unittest checks cover:

- Bundled 30-game result, cutoff 2026-09-30, one young game excluded and local agent-message handoff.
- Independent summation of one game's first 90 daily rows against the structured output.
- Missing/duplicate daily data rejected, rather than silently treated as complete.
- Unknown game references and invalid window configuration rejected.
- A portfolio without reskins preserves unavailable variation rather than emitting invalid JSON.
- CLI runs into temporary output, refuses overwrite and prepares local model messages.

The source example was regenerated after changing caveats and source labels. No OpenAI or other
model provider was called. Message preparation is a local JSON handoff, not a tested model adapter.

## 15 October 2026, second pass

13 more offline tests (19 in total, all passing):

- The committed agent draft (`agent_output.md`) passes the number check; invented figures such as
  `950k` and `71%` are caught. Two weaknesses were found and fixed while writing these tests:
  percentages matched unrelated values (for example a 0.714-week slip read as 71%), so percentages now
  match only share-type fields.
- `run_agent.py` with a mocked model: no key sends nothing, an existing output is not overwritten, a
  clean draft is saved with a provenance line, a draft with an invented number returns exit code 2.
- Comparables: the committed report matches a fresh run, the least important criterion is dropped
  first, young games are never counted as zero, unknown criteria are rejected, output is not overwritten.

`agent_output.md` was written by Claude Opus 5.5 from `prompt.md` and the committed `summary.json`.
`run_agent.py` has not been run against the live OpenAI API.

[GitHub Actions](https://github.com/canmils/slot-pm-agents/actions/workflows/onboarding.yml)
runs the same tests and the analysis/handoff CLI on Ubuntu and Windows. Inspect the run for your
commit; configuring a workflow alone is not evidence it passed.

## Limits

No live AI quality, private dataset, every schema rule, native macOS execution, time savings or
buyer demand has been validated. Integrity checks are targeted and the example expects complete
daily observations/completed projects. Age alignment does not control exposure, distribution,
seasonality or causality. Revenue share is an assumption, and calculated cost recovery is not net
profit. Fictional source patterns do not establish an industry-wide business conclusion.

## Release readiness companion — 22 October 2026

- Added an offline, standard-library checker with explicit review dates, required-check coverage, transitive dependencies, candidate-build evidence matching and source-linked findings.
- Fictional report independently expected to contain four findings: missing activation record, overdue cert review, old-build QA evidence and unresolved QA dependency.
- Local Python 3.12: all 30 unit tests passed, including 11 new readiness tests. Cases cover clean records, incomplete/unsupported evidence, deadlines, dependency cycles, unknown/duplicate IDs, malformed input, output preservation and CLI exit codes.
- Committed Markdown/JSON report reproduced exactly by the tests. No provider calls or commercial records used.
- Windows execution is covered by the GitHub Actions matrix; inspect the current PR run before claiming that platform passed.
- No real studio workflow, evidence-reference retrieval, regulatory validation or time-saving study was performed.

- Initial Windows CI caught locale-dependent decoding in the new report fixture test. Test inputs now explicitly use UTF-8, matching the checker output.
