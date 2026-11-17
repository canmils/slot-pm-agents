@AGENTS.md

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
