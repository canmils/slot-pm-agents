---
name: performance-review
layer: 6
status: example available
---

# Performance review

**Job:** report what each released game did, compared fairly, and feed the result back to strategy and business cases.

## Inputs
- `games.csv`, `costs.csv`, `milestones.csv`, `daily_performance.csv`.

## Outputs
- GGR at 30, 90 and 180 days per game (only when the game is old enough).
- Break-even day per game.
- Patterns by family, type, exclusive, vendor.
- Schedule slip by vendor and by reason.

## Human decision point
- Product Lead reviews and decides what changes in the next roadmap.

## Must not
- Rank games on total GGR when they have different ages.
- Draw conclusions from groups smaller than 3 games without a warning.

## Quality checks
- Every figure can be traced to the data.
- Games too young for a window are shown as "not yet", not as zero.

See [`examples/portfolio_review`](../examples/portfolio_review/).
