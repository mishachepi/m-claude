# Core Plugin

> Self-learning workflow — determinism, delegation, evolution.

## Dependencies

**plugin-dev** — needed for creating commands/skills ([marketplace](https://github.com/anthropics/claude-plugins-official))

## Commands

| Command | Description |
|---------|-------------|
| `/init` | Initialize context system (local or global) |

## Agents

| Agent | Description |
|-------|-------------|
| `updater` | Create command/skill from completed task |

## Skills

| Skill | Description |
|-------|-------------|
| `learn` | Capture session learnings → rules, skills, CLAUDE.local.md |
| `prompt-optimize` | Prompt engineering guide + CLAUDE.md optimization |

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

After `/init global`:

```
~/.claude/
├── CLAUDE.md                # Global context
├── commands/
└── skills/
```

## Workflow

```
Task → Playbook exists? → Execute
            ↓ no
       Solve → /learn → Save as playbook
```
