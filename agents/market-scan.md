---
name: market-scan
layer: 1
status: draft
---

# Market scan

**Job:** track competitor releases and turn them into a weekly list of trends and options.

## Inputs
- Public release lists, provider news pages, game demo pages.
- The studio's own portfolio (`schema/games.schema.json`) to spot gaps.

## Outputs
- Table of new releases: provider, title, theme, mechanic, grid, volatility, max win, date, source link.
- Short list of trends (mechanics or themes appearing often) with counts.
- 3 to 5 options: "we have no game with X, competitors released N in 90 days".

## Human decision point
- Head of Games picks which options become bets.

## Must not
- Estimate competitor revenue.
- Copy competitor art, names or unique features.

## Quality checks
- Every row has a source link.
- Volatility and max win only filled when the provider published them.
