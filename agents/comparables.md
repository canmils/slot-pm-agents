---
name: comparables
layer: 3
status: example available
---

# Comparables

**Job:** find past games similar to a new option and show their performance as a range.

## Inputs
- `games.csv` and `daily_performance.csv`.
- The option: family, mechanic, volatility, exclusive or not, season.

## Outputs
- List of comparable games with GGR at 30, 90 and 180 days.
- Range (low, median, high) and break-even day for each.
- Plain statement of uncertainty.

## Human decision point
- Product Lead decides if the range justifies the cost.

## Must not
- Give one forecast number.
- Compare games at different ages.

## Quality checks
- At least 3 comparables, or a clear warning.
- Uses the same normalisation as `examples/portfolio_review`.

See [`examples/comparables`](../examples/comparables/).
