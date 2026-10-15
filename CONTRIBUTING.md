# Contributing

Read README.md, docs/limits.md and the worked portfolio example first. Useful changes include
corrected domain assumptions, clearer agent contracts, fictional fixtures and verified calculations.

1. Fork/clone your fork and add upstream:
   `git remote add upstream https://github.com/canmils/slot-pm-agents.git`.
2. Create a focused branch: `git switch -c improve-portfolio-review`.
3. Install using the README's virtual-environment commands.
4. Run `python -m unittest discover -s tests -v` with that interpreter.
5. Run the analysis and message-preparation commands into a new ignored output directory.
   Analytical changes need independently checked expected values, not only snapshot updates.
6. If changing the fictional example intentionally, regenerate committed report.md/summary.json
   using `analyze.py --overwrite` and review the numerical differences.
7. Inspect `git diff` / `git status`, commit intended files, push your branch and open a PR to main.
   Describe the problem, behavior, verification and limitations. Maintainers review before merging.

Report issues at https://github.com/canmils/slot-pm-agents/issues with OS/Python version, commit,
exact command, fictional input and expected/actual output. Feature proposals should explain the
user problem, required data and human approval point. Major new workflows need a scoped design.

Do not contribute real company financials, player data, API keys or private commercial material.
Keep actual business data/configs/outputs in ignored directories or outside the checkout. Preserve
MIT attribution and upstream rights. Distinguish generated synthetic patterns from real evidence.
No model-generated revenue forecast, mathematical approval or certification sign-off should be
presented as validated. An agent card is a contract/guide, not an implemented autonomous agent.
