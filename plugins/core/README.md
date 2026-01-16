# Core Plugin

> Self-learning workflow plugin — determinism, delegation, evolution.

- **Determinism** — Use existing playbooks before improvising
    **Determinism > improvisation** — Ready solutions first
- **Delegation** — Fork context to specialized agents
    **Delegate** — Fork context for complex tasks
- **Evolution** — Capture learnings, implement improvements
    **Evolve** — Save successful patterns

## Dependencies

**plugin-dev** — needed for evolution
It is default plugin. Activate this plugin:  
[github](https://github.com/anthropics/claude-plugins-official)

Used skills:
- `command-development` — creating new commands
- `skill-development` — evolving commands into skills
- `agent-creator` — creating specialized agents

## Installation

```
/system:init global   # Install globally (~/.claude/)
/system:init local    # Install locally (./.claude/)
/system:init          # Interactive — asks where to install
```

## Plugin

### Commands

| Command | Description |
|---------|-------------|
| `/system:init` | Initialize context system (local or global) |
| `/flow:play` | Find playbook or solve with user |
| `/flow:learn` | Capture session learnings |
| `/flow:research` | Research topic (context → web) |
| `/core:evolve` | Implement improvements from learnings |
| `/core:create-command` | Create reusable command |
| `/core:update-command` | Update existing command |
| `/core:create-context` | Create context file via interview |
| `/complex:task` | Delegate complex task to subprocess |
| `/complex:code-task` | Code analysis via subprocess (read-only) |
| `/complex:code-task-dev` | Code task with edit permissions |

### Agents

| Agent | Description | Model |
|-------|-------------|-------|
| `playbook-executor` | Execute commands step by step | sonnet |
| `playbook-creator` | Create command/skill from task | sonnet |
| `complex-validator` | Monitor subprocess completion | haiku |

### Skills

| Skill | Description |
|-------|-------------|
| `record-session` | Record session for playbook creation |
| `prompt-engineering` | Prompt engineering patterns |

### Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| `load_context_map.py` | SessionStart | Load context triggers |
| `dot-claude-commit.sh` | PreToolUse (Edit/Write) | Git snapshot before changes |


## Structure

```
plugins/
├── core/                    # Main m-claude plugin
│   ├── commands/            # Slash commands
│   │   ├── system/          # System commands (/system:*)
│   │   ├── flow/            # Workflow commands (/flow:*)
│   │   ├── core/            # Core commands (/core:*)
│   │   └── complex/         # Subprocess delegation (/complex:*)
│   ├── agents/              # Subagent definitions
│   ├── skills/              # Complex skills
│   ├── hooks/               # Hook scripts
│   ├── output-styles/       # Response formatting
│   └── templates/           # File templates
└── plugin-dev/              # Anthropic plugin dev toolkit
```

## User Context Structure

After `/system:init`:

```
~/.claude/
├── CLAUDE.md                # Workflow instructions
├── context_map.md           # Context triggers
├── context/                 # Context files
│   └── about-me.md
├── learnings/               # Session learnings
├── commands/                # User commands
└── skills/                  # User skills
```

## Workflow

```
Task → Find playbook → Execute → Done
            ↓ not found
       Solve with user → Offer to save as playbook
```

