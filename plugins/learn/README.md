# Learn Plugin

> Capture session learnings as reusable rules, skills, and commands. Determinism + evolution loop.

## Commands

| Command | Description |
|---------|-------------|
| `/init` | Initialize context system (local `CLAUDE.local.md` or global `~/.claude/CLAUDE.md`) |

## Skills

| Skill | Description |
|-------|-------------|
| `learn` | Capture session learnings → rules, skills, or `CLAUDE.local.md` updates; install a missing MCP server (confirm-first, via `mcp-installer`); ship a cross-project workflow as a new m-claude plugin or fix m-claude itself (clone → branch → PR, never `main`) |

## Agents

| Agent | Color | Description |
|-------|-------|-------------|
| `updater` | blue | Create a command or skill from a completed task |

## Dependencies

- **qmd**, **obsidian** (auto-installed) — vault search used by the learn/context loop
- **plugin-dev** — needed by `updater` when creating commands/skills ([marketplace](https://github.com/anthropics/claude-plugins-official))

## Context Structure

After `/init local`:

```
./
├── CLAUDE.local.md          # Local context
└── .claude/
    ├── rules/               # Behavioral rules
    ├── commands/            # Project commands
    └── skills/              # Project skills
```
