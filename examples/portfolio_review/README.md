# Example: portfolio review (layer 6, Measure)

This is the one example in the repo that runs end to end. It shows the split this library is built on:

- **Code does the numbers.** `analyze.py` is deterministic. Same data, same result.
- **The agent does the writing and the questions.** It reads `summary.json`, follows the rules in [`prompt.md`](prompt.md), and drafts a review.
- **A person decides.** The Product Lead reads the draft and decides what changes in the roadmap.

Do not let a language model do the arithmetic. Give it the numbers.

## Run

```bash
pip install pandas
python examples/portfolio_review/analyze.py
```

Output:

- [`report.md`](report.md): readable review.
- `summary.json`: structured facts for an agent.

Change settings (revenue share, windows, minimum group size) in [`config.json`](config.json). Point `data_dir` to your own data to use it for real. Keep real data out of git.

## Connect it to an agent

Any framework works. The pattern:

1. Register `analyze.py` (or its `build()` function) as a tool.
2. Give the agent `prompt.md` as its instructions.
3. Pass `summary.json` as the tool result.
4. Send the draft to a person, not to a channel.

## What the fictional data shows

The synthetic data is built to show the traps a real portfolio review falls into:

1. **Ranking on total GGR is wrong.** Old games look better only because they had more time. See "Why age matters" in the report.
2. **Cost is predictable, revenue is not.** Reskin costs vary a few percent. Revenue varies a lot. This is why the Cost estimator agent is easy and a revenue "forecast" agent is not.
3. **A few games make most of the money.** Use ranges, not averages.
