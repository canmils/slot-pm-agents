# Review a slot portfolio decision

Read `docs/assistant-contract.md`. Start with `examples/portfolio_review/README.md`, `examples/comparables/README.md` and the generated report/JSON when provided.

Inputs: options (original/sequel/reskin), rationale, costs, available capacity by discipline, milestones/dependencies, distribution/market assumptions, historical game data and decision horizon. The current schema supports original/reskin; label a sequel proposal explicitly and do not silently encode it as a measured historical category.

1. Verify data provenance, date, currency, completeness, game ages and GGR versus provider revenue. Describe revenue share and cost coverage; break-even is not net profit.
2. Compare at the same launch age, then examine distribution exposure, exclusive periods, season, markets, family concentration, RTP variants and missing observations. Same-age GGR alone does not normalize operator reach. Never infer causal mechanic superiority from it.
3. Inspect matching criteria and dropped criteria in the JSON. Run strict cohorts first: pass `--strict` to the comparables CLI. Report too few matches honestly. The legacy default can relax criteria: explicitly disclose any relaxation before using it, particularly exclusivity or seasonality. Show eligible sample size for each window, not only total matched games.
4. Present past low/median/high as descriptive observations, never a forecast interval or probability of success. Do not invent player retention, competitor revenue or uplift. The number checker verifies numeric presence, not the truth of a claim or its association with a game.
5. Compare option costs, capacity constraints, delivery/certification lead times, reuse uncertainty, portfolio overlap and evidence needed. Keep cannibalization as an unvalidated hypothesis unless measured. Prefer a conditional recommendation or defer decision when evidence cannot separate options.

Use the shared output contract plus an options table: strategic fit | cost evidence | constrained discipline | historical cohort | uncertainty | next validation. Product Lead decides investment; no autonomous green light.
