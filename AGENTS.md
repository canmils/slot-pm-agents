# Slot PM Agents

A domain library for building AI agents for product management in a slot game
studio: what an agent should do, what data it needs and where a person must
decide. Not an agent framework. All data is synthetic.

## Commands

- Install: `python -m venv .venv && .venv/bin/python -m pip install -r requirements.txt`
- Tests: `.venv/bin/python -m unittest discover -s tests -v`
- Examples: `examples/comparables/find_comparables.py`, `examples/portfolio_review/analyze.py`, `examples/release_readiness/check.py`
- Synthetic data: `scripts/generate_synthetic_data.py`

## Layout

- `agents/`: agent specs. `schema/`: data contracts. `data/`: synthetic data.
- `examples/`, `docs/`, `tests/`.

## Rules

- Synthetic data only. Never add data from a real employer or real studio.
- Every agent spec names where a human decides.

## Coding discipline (Karpathy guidelines)

Before writing, reviewing or refactoring code, load the `karpathy-guidelines` skill
(source: github.com/multica-ai/andrej-karpathy-skills, MIT). The short version:

1. **Read first.** Read the code, docs and tests you will touch before you change anything. Investigate; do not guess.
2. **Think before coding.** State your assumptions. If there is more than one reading of the task, name them. If something is unclear, stop and ask.
3. **Simplicity first.** Write the minimum code for the request. No speculative features, no early abstractions, no new dependency without a stated reason.
4. **Surgical changes.** Touch only what the task needs and match the existing style. Mention unrelated problems; do not fix them silently.
5. **Define success before building.** Turn the task into a check, for example a test that fails first and then passes.
6. **Test the behaviour and fix the root cause.** A green build is not enough. Do not patch symptoms.
7. **Explain what changed and why.** Files touched, the reason, and the checks you actually ran.

## Superpowers coding workflow

For software implementation, debugging, refactoring and code review, load
`using-superpowers` and the relevant installed Superpowers skills before acting.
See [setup and verification](docs/SUPERPOWERS.md). If the skills are unavailable,
report the missing installation; do not claim that reading this file loads them.

- Clarify the goal and acceptance criteria with `brainstorming`; reuse an already
  approved brief and existing authorization instead of restarting approval.
- Use `writing-plans` for multi-step work, with small tasks and explicit checks.
- Use `using-git-worktrees` when isolation is needed. Preserve existing clean
  isolated checkouts and project-specific worktree restrictions.
- Follow `executing-plans`, or `subagent-driven-development` when delegation is
  authorized and available. Parallel work requires independent scopes and file ownership.
- For behavior changes use `test-driven-development`; for failures use
  `systematic-debugging`. Documentation/configuration-only changes need relevant
  validation, not artificial behavior tests.
- Use `requesting-code-review` / `receiving-code-review` and
  `verification-before-completion`; report commands actually run and remaining gaps.
- Finish with `finishing-a-development-branch`. Opening a PR does not authorize
  merging, deployment, deletion, paid services or changing permissions.

These are development-tool instructions, not a runtime dependency or a replacement
for domain agents. Existing safety rules, domain gates, ownership, permissions and
explicit user instructions remain in force. Do not apply coding rituals to ordinary
research, coaching or writing. Keep the existing simplicity guidelines.
