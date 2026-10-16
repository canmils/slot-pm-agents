# Worked example: Comparables

**Job of the agent:** find past games similar to a new option and show how they performed, as a range. Never one forecast number. See the [agent card](../../agents/comparables.md).

No model key needed. It reuses the portfolio data and the same rule: GGR is compared at the same age after launch.

## Run

From the repository root, with your `.venv` interpreter:

```sh
python examples/comparables/find_comparables.py --output-dir output/comparables
```

Result: `comparables.md` (for people) and `comparables.json` (for other agents). The committed [comparables.md](comparables.md) is the output for the bundled [option.json](option.json).

## Describe your option

Edit `option.json`. Put the **most important criterion first**:

```json
{
  "name": "New high-volatility Hold and Win",
  "criteria": { "mechanic": "hold_and_win", "volatility": "high", "exclusive": false }
}
```

Allowed criteria: `family`, `mechanic`, `volatility`, `theme`, `type`, `vendor`, `exclusive`, `seasonal`. Values must match the data exactly (for example `hold_and_win`, `Vendor North`).

## What the report does for you

- Matches on all criteria. If fewer than 3 games match, it drops the **last** criterion and tries again, and says which ones it dropped.
- Shows low, median and high for GGR at 30, 90 and 180 days, actual cost and weeks to launch.
- Marks windows where fewer than 3 games are old enough. Young games show "not yet", never zero.
- Warns when all comparables come from one family, because the range may then reflect that family and not your criteria.

The bundled example shows the last two warnings on purpose: 3 games match, only 2 are older than 90 days, and all 3 are Ember Fang.

## Limits

Matching on a few attributes is crude. It does not control for theme quality, distribution, operators, season or marketing. The data is fictional. The Product Lead decides; this report does not recommend.

### Keep a cohort fixed

Add `--strict` to keep every criterion in option.json, even if fewer than three games match. The default retains the original relaxation behavior; inspect dropped criteria before interpreting its ranges. Strict matching does not adjust for missing operator/market exposure.
