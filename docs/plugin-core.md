# Core Plugin

Self-learning workflow — determinism, delegation, evolution loop.

## Components

| Type | Name | Color | Purpose |
|------|------|-------|---------|
| Command | `/init` | — | Initialize context system (local/global) |
| Agent | `updater` | blue | Create command/skill from completed task |
| Skill | `learn` | — | Capture session learnings → rules, skills, CLAUDE.local.md |
| Skill | `prompt-optimize` | — | Prompt engineering guide + CLAUDE.md audit |

## Dependency

Requires **plugin-dev** for creating commands/skills.

## Workflow

```
Task → Playbook exists? → Execute
            ↓ no
       Solve → /learn → Save as playbook
```
