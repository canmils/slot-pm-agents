# Release readiness checker

A small offline tool for a producer preparing a release review. It compares a supplied checklist snapshot against the team's supplied required-check list and candidate build. No model, key, installation or network request is needed beyond Python 3.11/3.12.

**[See the fictional report](report.md)** · [Machine-readable output](report.json) · [Input](fictional-release.json)

The example has four blockers: missing activation record, overdue certification review, QA evidence for an older build, and certification depending on that unsupported QA evidence. These are four findings, not four independent root causes.

## Run from the repository root

```sh
python examples/release_readiness/check.py --as-of 2026-10-22
```

On macOS/Linux use `python3` if that is your Python command. This prints a report without creating files. Run from any working directory by giving the script's absolute path; the default fixture is resolved relative to the script.

To export Markdown and JSON into a **new** directory:

```sh
python examples/release_readiness/check.py --as-of 2026-10-22 --output-dir output/release-readiness
```

Existing output directories are refused. Choose a new directory for another run. For a local input:

```sh
python examples/release_readiness/check.py --input data/private/release.json --as-of 2026-10-22
```

The review date is explicit for reproducibility. Completion dates after that date are rejected; inputs should represent the snapshot known on that date. There is no history reconstruction.

Exit codes: **0** report generated, **1** blockers found when `--fail-on-blockers` is supplied, **2** invalid input or file/output error. A zero exit code never means release approval. No CI deploy gate is installed.

## Input contract

| Field | Meaning |
| --- | --- |
| `project`, `build` | Non-empty project name and exact candidate identifier |
| `release_date` | Target date in YYYY-MM-DD |
| `policy_source` | Name/version/reference of the team's supplied checklist; not fetched |
| `required_check_ids` | Non-empty unique list of required checks; missing records become blockers |
| `checks` | Records described below; IDs must be unique |

Every check has `id`, `name`, `status` (`pending` or `complete`), `due_date`, and `depends_on` (list of check IDs). Supply an `owner`; missing/blank owners are findings. Completed checks also need `completed_on`, `evidence` (non-empty reference), `reviewer` and `evidence_build` matching the candidate. The tool records claims; it does not authenticate reviewers, inspect references or prove that a person approved anything.

Required checks and all their dependencies affect blocker status. Other checks produce warnings. Unknown dependencies, duplicate IDs and dependency cycles reject the input. Incomplete required checks block even if their due date is still in the future. Overdue means due before the review date. A due date after the release target is a finding even for a completed record, because the supplied plan needs reconciliation.

Evidence for a different build is flagged for human review. This conservative example does not determine whether changes need re-testing or re-certification. Reviewers decide which checks apply to a build. It does not calculate critical paths, capacity or a feasible new release date.

## Design and decision boundary

Input JSON → validate dates/IDs/dependency graph → expand required dependencies → evaluate recorded status/evidence → emit source-linked findings. Rules are deterministic and use only the Python standard library. Existing portfolio/comparables data formats are unchanged: they do not contain build-specific evidence, so this example has a separate snapshot contract.

A future agent could summarise these findings, but a model is unnecessary for these checks. Adding one would require traceability to findings and must not turn incomplete evidence into approval. The default is an inspectable report.

**Human decision:** validate checklist coverage, inspect the actual evidence, reconcile candidate identity, resolve blockers and decide whether to release. A clean report means only **NO BLOCKERS FOUND IN SUPPLIED RECORDS**. It cannot detect omitted policy requirements, forged references, revoked evidence or every production risk.

Use fictional data for public examples. Keep permitted private inputs under ignored `data/private/` and outputs under ignored `output/`. Nothing is transmitted. Do not commit real studio records.

## Help validate usefulness

Try the fictional snapshot. Which flag would change your next action? Which is noisy? Suggest one missing check with a fictional input and expected finding. Producer feedback is needed before claiming time saved or operational value.
