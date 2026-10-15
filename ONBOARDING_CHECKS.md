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

[GitHub Actions](https://github.com/canmils/slot-pm-agents/actions/workflows/onboarding.yml)
runs the same tests and the analysis/handoff CLI on Ubuntu and Windows. Inspect the run for your
commit; configuring a workflow alone is not evidence it passed.

## Limits

No live AI quality, private dataset, every schema rule, native macOS execution, time savings or
buyer demand has been validated. Integrity checks are targeted and the example expects complete
daily observations/completed projects. Age alignment does not control exposure, distribution,
seasonality or causality. Revenue share is an assumption, and calculated cost recovery is not net
profit. Fictional source patterns do not establish an industry-wide business conclusion.
