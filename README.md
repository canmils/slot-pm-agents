# Slot PM Agents

Practical review workflows and a domain library for **product management in a slot game studio**.

This is not an agent framework. There are many good ones already. This repo answers a different question:

> What should an agent actually do in a slot studio, what data does it need, and where must a person decide?

## Use as a studio assistant

Open this checkout in Codex or Claude Code. The same evidence contract supports three guided reviews:

- [Brief and signposting](workflows/brief-review.md): contradictions, missing rules and acceptance criteria.
- [Release evidence](workflows/release-review.md): exact builds, markets, QA and certification dependencies.
- [Portfolio decision](workflows/portfolio-decision.md): costs, capacity and qualified historical comparisons.

[Setup and example prompts](docs/assistant-setup.md) · [Fictional evaluation cases](examples/workflow_reviews/README.md) · [Upstream audit](docs/upstream-audit.md).
These are assistant-executed reviews, not autonomous agents. Existing Python examples run independently. Native client/model quality has not yet been benchmarked.

## See it before you install anything

| What | Agent | Made by | Open |
| --- | --- | --- | --- |
| Portfolio report: 30 fictional games compared at the same age | Performance review | Code | [report.md](examples/portfolio_review/report.md) |
| The agent's written review of that report | Performance review | Claude Opus 5.5, unedited | [agent_output.md](examples/portfolio_review/agent_output.md) |
| Range of past results for a new game idea, with its own warnings | Comparables | Code | [comparables.md](examples/comparables/comparables.md) |

The agent draft passes a numeric presence check. This can catch invented numbers, but cannot verify that a number is assigned to the correct game or supports the conclusion. You can run the same check on any draft.

## What is in the repo

| Folder | What it is |
|---|---|
| [`docs/framework.md`](docs/framework.md) | The 7 layers of product management, adapted to slot games |
| [`agents/`](agents/) | One card per agent: inputs, outputs, human decision point, limits. 2 of 10 have a runnable example |
| [`schema/`](schema/) | A data model for slot projects: games, milestones, costs, daily performance |
| [`data/synthetic/`](data/synthetic/) | Fictional data that follows the schema |
| [`examples/`](examples/) | [Portfolio review](examples/portfolio_review/) and [Comparables](examples/comparables/), end to end |

**Who it is for:** developers who can build agents but do not know how a slot studio works, and producers or product people who want a clear map before they automate anything.

## Run it: no model key needed

Requires Git and Python 3.11 or 3.12.

Windows PowerShell:

```powershell
git clone https://github.com/canmils/slot-pm-agents.git
cd slot-pm-agents
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe examples/portfolio_review/analyze.py --output-dir output/portfolio-review
.\.venv\Scripts\python.exe examples/comparables/find_comparables.py --output-dir output/comparables
```

macOS/Linux:

```sh
git clone https://github.com/canmils/slot-pm-agents.git
cd slot-pm-agents
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python examples/portfolio_review/analyze.py --output-dir output/portfolio-review
.venv/bin/python examples/comparables/find_comparables.py --output-dir output/comparables
```

You get the same reports as the committed ones, in `output/`. Then:

- **Check an agent draft's numbers** (free) and **run the agent yourself** (optional, your own OpenAI key, one call): see [portfolio review step 4](examples/portfolio_review/README.md#4-see-what-the-agent-writes-and-check-it).
- **Try your own game idea:** edit [`examples/comparables/option.json`](examples/comparables/option.json).
- **Use your own data:** see [portfolio review step 5](examples/portfolio_review/README.md#5-custom-configdata-and-safe-reruns). Keep it in `data/private/`, which is git-ignored.

## The main idea

Agents do the groundwork. People make the calls.

In a slot studio this matters more than in most software products, because:

1. **Game math is regulated.** RTP, volatility and max win must be simulated and signed off by a math engineer. An agent can draft, never approve.
2. **Builds are certified.** Labs (for example BMM, GLI, DGE) test a frozen build. "Agents ship code into players' hands" does not happen here.
3. **Revenue of a new game is very hard to predict.** A few games make most of the money. An agent can show comparable games and ranges. It should not give a single number.
4. **Cost and schedule are easier to measure than revenue.** That makes them the safest place to start, as long as the data is checked first.

Read [`docs/limits.md`](docs/limits.md) before you build anything.

## Where to start

Do not build all 7 layers. Start with the layers that are low risk and data heavy:

1. **Measure** (layer 6): post-launch performance at the same age. [Example](examples/portfolio_review/).
2. **Business case** (layer 3): revenue ranges from comparable games, plus cost and weeks. [Example](examples/comparables/).
3. **Strategy** (layer 1): competitor release tracking from public sources. Card only.

Leave Define, Build and Run until the first three are trusted.

## What runs, what does not

| Part | What it does |
| --- | --- |
| `analyze.py`, `find_comparables.py` | Deterministic reports from the CSVs. No model |
| `check_agent_output.py` | Flags numbers in a draft that are not in the data. No model |
| `prepare_agent_input.py` | Builds the model messages locally. Sends nothing |
| `run_agent.py` | Optional. One OpenAI call with your key, then the number check |
| Agent cards | Domain contracts, not running agents |
| Approval | Always a person. Nothing is published, sent or scheduled |

It does not forecast revenue, certify anything or prove time savings.

## Tests

```sh
python -m unittest discover -s tests -v
```

Offline, no key. [CI](https://github.com/canmils/slot-pm-agents/actions/workflows/onboarding.yml) runs them on Ubuntu and Windows. See [ONBOARDING_CHECKS.md](ONBOARDING_CHECKS.md) for what has been checked.

## A note on the data

All data in this repo is **fictional**, generated by `scripts/generate_synthetic_data.py`. Any match with a real game or company is by chance. Do not contribute real commercial data.

## Contributing

Useful: corrections to the framework from people in studios, operators or labs; new agent cards that follow [the template](agents/_TEMPLATE.md); examples in other frameworks that use the same schema. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [`LICENSE`](LICENSE).
