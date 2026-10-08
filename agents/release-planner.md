---
name: release-planner
layer: 2
status: draft
---

# Release planner

**Job:** turn approved games into a release calendar with milestone dates and capacity checks.

## Inputs
- Milestone templates and historical durations (`schema/milestones.schema.json`).
- Team and vendor capacity.
- Marketing lead times: roadmap slot, promo materials, external demo links.

## Outputs
- 2 or 3 scenarios (for example: all in-house, mix with vendor, reskin first).
- Per game: dates for each milestone, certification and activation.
- Conflicts: two games needing the same team in the same week.

## Human decision point
- Head of Product picks a scenario.

## Must not
- Use planned durations only. Always add historical slip.

## Quality checks
- Dates match the template order.
- Slip buffer is shown and explained.
