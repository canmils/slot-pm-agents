# Superpowers setup

Reviewed 2026-11-17 against obra/superpowers v7.0.2 (MIT).
Sources: [README](https://github.com/obra/superpowers/tree/v7.0.2),
[OpenCode installation](https://github.com/obra/superpowers/blob/v7.0.2/.opencode/INSTALL.md).
This is a coding workflow, not an agent team, product dependency or running service.

## Install separately in each coding tool

Claude Code: run `/plugin install superpowers@claude-plugins-official` and
choose project scope for this checkout (or user scope for all repositories).
Preserve existing hooks and permission settings.

Codex App: Plugins → Superpowers → Install. Codex CLI: `/plugins`, search
Superpowers, then Install Plugin. Repository instructions cannot install a
user-level Codex plugin.

OpenCode: check `opencode --version`. In OpenCode V2 (2.0.4+), merge this into
the effective project or user configuration, preserving other settings:

```json
{"plugins":["superpowers@git+https://github.com/obra/superpowers.git#v7.0.2"]}
```

OpenCode V1 uses `plugin` (singular) instead of `plugins`. Do not add both
keys blindly. Existing repository configurations remain V1-compatible where
they use the V1 schema. For shared global agents, install in the user configuration
too: a project configuration affects only that project. Restart the tool.
Do not overwrite personal configuration or copy machine-specific absolute paths.

Pi: upstream documents `pi install git:github.com/obra/superpowers`.
Restart and verify independently; installing in one tool does not install in another.

## Verify in a fresh session

1. List native skills; confirm `using-superpowers`, `brainstorming`,
   `writing-plans`, `systematic-debugging` and
   `verification-before-completion` are present.
2. Ask the agent to load `using-superpowers` and report the loaded skill name.
3. Ask for a small feature plan without implementation; check that it uses the
   relevant planning skill and includes acceptance checks.
4. When fixing a reproducible bug, require a failing test, the fix and a passing run.
5. Confirm existing permission hooks still apply. A skill does not grant tools,
   filesystem access, delegation, merging or deployment permission.

A configuration entry is not proof of a successful runtime load. Record the tool
version, plugin version, skills discovered and actual check results. If the
plugin is missing, report that explicitly. These repository changes were checked
statically; interactive tool installation and skill activation require a local session.

## Updates and rollback

OpenCode is pinned to v7.0.2 where configured. Review upstream changes before
updating the pin. Marketplace versions follow their own update mechanism.
To roll back, revert the workflow commit and remove only the Superpowers plugin
entry; preserve existing hooks, agents, instructions and permissions.
