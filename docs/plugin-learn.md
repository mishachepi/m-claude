# Learn Plugin

Capture session learnings — determinism, evolution loop.

## Components

| Type | Name | Color | Purpose |
|------|------|-------|---------|
| Command | `/init` | — | Initialize context system (local/global) |
| Agent | `updater` | blue | Create command/skill from completed task |
| Skill | `learn` | — | Capture session learnings → rules, skills, CLAUDE.local.md; MCP install (via `mcp-installer`); new m-claude plugin / framework fix (clone → PR) |

## Dependencies

- **qmd**, **obsidian** — auto-installed cross-marketplace deps, vault search for the learn loop
- **plugin-dev** — for `updater` when creating commands/skills
- **mcp-installer** (optional, same marketplace) — `learn` hands MCP-need learnings to it; without it, `learn` runs the same confirm-first flow inline

## Workflow

```
Task → Playbook exists? → Execute
            ↓ no
       Solve → /learn → Save as playbook
```
