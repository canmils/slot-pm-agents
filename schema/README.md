# Data schema

Four tables. Each is a CSV file with one JSON Schema describing one row.

| Table | One row is | Key |
|---|---|---|
| [`games`](games.schema.json) | a game | `game_id` |
| [`costs`](costs.schema.json) | one discipline of one game | `game_id` + `discipline` |
| [`milestones`](milestones.schema.json) | one milestone of one game | `game_id` + `milestone` |
| [`daily_performance`](daily_performance.schema.json) | one game on one day | `game_id` + `date` |

## Why daily performance

Games launch at different dates. To compare them fairly you need performance **by days since launch**. Monthly totals or a single "total GGR" make old games look better than new ones. Daily rows (or at least weekly) let you compute GGR at 30, 90 and 180 days for every game.

## Milestone order

`kick_off`, `initial_prototype`, `client_prototype`, `alpha`, `beta`, `gold`, `master`, `certification`, `production`, `activation`.

Rename them to match your studio. Keep the order.

## Money

All money in EUR. GGR is bets minus wins. Studio revenue is GGR multiplied by the studio's revenue share, which is set in `examples/portfolio_review/config.json`, not in the data.
