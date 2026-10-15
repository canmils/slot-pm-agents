# Worked example: portfolio review and agent handoff

**Code computes. An optional model drafts. Code checks the draft's numbers. A person decides.**
Steps 1 to 4 are free. Only the optional `run_agent.py` calls a paid provider. Nothing schedules
agents, sends a report or changes a roadmap.

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

## 4. See what the agent writes, and check it

**Free:** [agent_output.md](agent_output.md) is a real agent draft. Claude Opus 5.5 wrote it on
15 October 2026, following [prompt.md](prompt.md) with the committed `summary.json` as the only
input. Nobody edited it afterwards.

**Check any draft's numbers with code** (no key needed):

```sh
python examples/portfolio_review/check_agent_output.py --summary examples/portfolio_review/summary.json --draft examples/portfolio_review/agent_output.md
```

Every number in the draft must exist in `summary.json` (as written, in thousands like `909k`, or as
a percentage). Anything else is listed and the script exits with code 1. It catches invented figures;
it does not judge wording or reasoning. Limit: a small number such as `3.1` can match an unrelated
value by chance, so a pass is strong evidence, not proof.

**Optional, paid:** run the agent yourself with your own OpenAI key. One API call, and it asks first.

```sh
python -m pip install openai
python examples/portfolio_review/run_agent.py --summary output/portfolio-review/summary.json --output output/portfolio-review/agent-draft.md
```

It saves the draft with a provenance line, then runs the number check automatically. Exit code 2
means the model wrote numbers that are not in the data. Default model `gpt-4.1-mini`; set
`OPENAI_MODEL` to change it. A ChatGPT subscription does not include API credits.

Also check by hand:

- Every comparison names its window and eligible count.
- Young games remain unknown; small groups keep their warnings.
- Schedule comparisons are observations, not proof of vendor quality.
- The draft ends with questions for the Product Lead, not actions.

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

## 6. Troubleshooting

| Problem | Action |
| --- | --- |
| Python/Git not found | Install the prerequisite and reopen the terminal |
| Missing pandas or openai | Install with the same `.venv` interpreter that runs the script |
| Output already exists | Choose a new `--output-dir`, or deliberately use `--overwrite` after backup |
| Missing CSV/column | Check `data_dir`, file names and schema; do not substitute zeros |
| Coverage or duplicate error | Repair upstream daily data; weekly data is not supported |
| Main window/config error | Include 30 and the main window in `windows_days`; use a share in (0, 1] |
