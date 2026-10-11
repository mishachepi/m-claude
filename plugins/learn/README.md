# Learn Plugin

> Capture session learnings as reusable rules, skills, and commands. Determinism + evolution loop.

## Commands

| Command | Description |
|---------|-------------|
| `/learn:bootstrap` | Initialize context system (local `CLAUDE.local.md` or global `~/.claude/CLAUDE.md`) |

## Skills

| Skill | Description |
|-------|-------------|
| `learn` | Quality-gate a lesson, then persist it where the next session reads it: project rules/skills/`CLAUDE.local.md`, or — as a scion agent (`$SCION_AGENT` set) — the agent's template (`lessons.md`/`agents.md`; replaces the former `scion` plugin); install a missing MCP server (confirm-first, via `mcp-installer`); ship a cross-project workflow as a new m-claude plugin or fix m-claude itself (clone → branch → PR, never `main`) |

## Agents

| Agent | Color | Description |
|-------|-------|-------------|
| `updater` | blue | Create a command or skill from a completed task |

## Dependencies

- **qmd**, **obsidian** (auto-installed) — vault search used by the learn/context loop
- **plugin-dev** — needed by `updater` when creating commands/skills ([marketplace](https://github.com/anthropics/claude-plugins-official))

## Context Structure

After `/learn:bootstrap local`:

```
./
├── CLAUDE.local.md          # Local context
└── .claude/
    ├── rules/               # Behavioral rules
    ├── commands/            # Project commands
    └── skills/              # Project skills
```
