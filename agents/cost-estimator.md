---
name: cost-estimator
layer: 3
status: draft
---

# Cost estimator

**Job:** estimate cost and weeks for a game option from past projects.

## Inputs
- `costs.csv` and `milestones.csv` for past games.
- The option: type (original or reskin), vendor or in-house, scope notes.

## Outputs
- Cost per discipline: median and range of similar past games.
- Weeks to certification: planned and historical actual, with slip.
- The past games used as the base.

## Human decision point
- Producer checks the scope and confirms or corrects the estimate.

## Must not
- Estimate from fewer than 5 similar games without saying so.

## Quality checks
- Every number links to the games it came from.
- If costs are almost fixed (one vendor, one price), say so: a lookup is enough.
