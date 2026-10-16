# Use with Codex or Claude Code

Clone this repository and open the checkout as the project in either coding assistant. Codex uses the root AGENTS.md; Claude Code uses CLAUDE.md, which points to the same contract. These are project instructions and Markdown workflows, not an installed MCP server, global plugin or autonomous multi-agent runtime. No REA installation is required.

Start with a fictional case:

> Read AGENTS.md and review examples/workflow_reviews/brief.md using the brief review workflow. Cite the supplied sections and separate missing evidence from confirmed defects.

Or replace the input and choose `release-review.md` or `portfolio-decision.md`. Store real inputs under ignored data/private/ and output under ignored output/. Only use data approved for your assistant environment.

For portfolio calculations use the existing Python setup in README.md; neither assistant subscription supplies an API key for the optional run_agent.py script. To keep cohort criteria fixed:

```sh
python examples/comparables/find_comparables.py --strict --output-dir output/strict-comparables
```

For manual acceptance checks see `examples/workflow_reviews/README.md`. File routing has been inspected; no claim is made that native Codex and Claude Code sessions or model quality were benchmarked. No duplicated skill installation is needed.
