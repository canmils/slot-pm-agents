# Worked example: portfolio review and agent handoff

**Code computes. An optional model drafts. A person decides.** The repository includes the first
part and a local handoff helper; it does not run a provider, schedule agents or send a report.

## 1. Run the analysis

Follow the root README's installation. From the repository root, using your `.venv` interpreter:

```sh
python examples/portfolio_review/analyze.py --output-dir output/portfolio-review
```

Outputs are `report.md` for human inspection and `summary.json` containing facts for downstream use.
The committed [report.md](report.md) / [summary.json](summary.json) are reference outputs from the
fictional CSVs, not a live business portfolio. A new run uses 30 games, cutoff 2026-09-30 and
90-day comparisons; one young game is excluded. Inspect the source CSVs and small-group warnings.

## 2. Understand the calculations

| Item | Definition / limit |
| --- | --- |
| 90-day GGR | Sum of daily GGR from launch day 0 through day 89; daily GGR can be negative |
| Young game | Fewer than 90 observed calendar days at the common cutoff; its 90-day value is null |
| Group range | Observed minimum/maximum, not a forecast or confidence interval |
| Small group | Eligible count below `min_group_size`; do not draw a decision from it |
| Revenue share | Configured assumption applied to GGR, not verified contract revenue |
| Break-even day | First zero-based day cumulative GGR × share reaches recorded actual cost; 0 is launch day |
| Profit-to-date field | GGR × share minus recorded costs; omits unrecorded fees/taxes/expenses and is not net profit |
| Ranking | Aligns time since launch, not distribution, operator coverage, exposure, seasonality or causality |

Comparing lifetime GGR favors older games, but equal age alone does not make games commercially
comparable. The fictional cost/revenue patterns were generated deliberately; do not generalize them
to real studios. A first break-even crossing does not guarantee the balance remains positive later.

## 3. Prepare a concrete agent input without paying or sending data

```sh
python examples/portfolio_review/prepare_agent_input.py --summary output/portfolio-review/summary.json --output output/portfolio-review/agent-input.json
```

This produces a JSON object with `messages`: the [prompt.md](prompt.md) as a system instruction and
serialized facts as a user message. It refuses to overwrite an existing file. No SDK, model account,
network request, provider key, email or publishing is involved.

For a manual model trial, copy the prompt instructions followed by the generated summary into your
chosen permitted AI tool. For a coded integration, pass the generated message array through your
framework's model adapter. Provider authentication, model parameters, costs and response handling
belong to that separate adapter; compatibility with every framework is not claimed.

A minimal framework-neutral orchestration is:

```python
# Run in this example directory, or import these modules through your application's package layout.
from analyze import build
from prepare_agent_input import prepare

report, summary = build(config)  # config is the parsed config.json dictionary
payload = prepare(summary)
# draft = your_model_adapter(payload["messages"])  # implement and test separately
# present draft + report to a human; never automatically send or change a roadmap
```

Use fictional data for initial trials. Private financial information must not be sent to a provider
without permission. Treat model output as untrusted: it can invent facts despite instructions.

## 4. Acceptance checks for the draft

- Numbers and game/group names must match `summary.json`; no model arithmetic or new forecasts.
- Every comparison names its window and eligible count.
- Young games remain unknown; small groups retain warnings.
- No previous review was supplied: changes since last review are unknown.
- Schedule comparisons are observations, not proof of vendor quality or causes of delay.
- Output ends with decisions/questions for the Product Lead, not autonomous actions.

A human-written reference opening could be: “The fictional portfolio contains 30 games at the
2026-09-30 cutoff. One has not completed the 90-day window and is excluded from that comparison.”
This illustrates acceptable caveating; it is not a tested model response.

## 5. Custom config/data and safe reruns

Copy `config.json` to ignored `data/private/review-config.json` and edit it. `data_dir` always resolves
relative to this example directory, even when the config is elsewhere. Use `../../data/private` for
that repository location, or an absolute path. Supply all four CSVs from the schema.
Set `data_label` to reflect the source. No real data is provided or independently verified.

```sh
python examples/portfolio_review/analyze.py --config data/private/review-config.json --output-dir output/my-review
```

The analyzer expects complete **daily** data through one common cutoff and completed milestone dates.
It rejects gaps instead of treating missing performance as zero. Planned/unlaunched portfolios,
weekly aggregates and incomplete projects need a different analytical workflow. The schema files
are documentation; the current loader performs targeted checks, not every possible schema rule.
`windows_days` must include 30 and `main_window_days`; all windows must be positive integers.

Outputs refuse overwrite by default. Use a new folder for each review, or explicitly add
`--overwrite` after preserving the previous one. The generator overwrites fictional source CSVs;
never place private data in the synthetic directory.
