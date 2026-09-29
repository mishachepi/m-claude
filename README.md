# m-claude

> Plugin framework for Claude Code — self-learning AI manager with determinism, delegation, and evolution.

## Plugins

| Plugin | Purpose |
|--------|---------|
| [learn](./plugins/learn/) | Capture session learnings; `/init` bootstrap; `updater` agent |
| [prompt-optimize](./plugins/prompt-optimize/) | Prompt engineering guide + CLAUDE.md optimization |
| [init](./plugins/init/) | Set up a project's documentation structure |
| [update](./plugins/update/) | Keep documentation in sync with code changes |
| [brainstorm](./plugins/brainstorm/) | Structured brainstorming → spec document |
| [lead-research](./plugins/lead-research/) | Multi-agent research |
| [worktree-flow](./plugins/worktree-flow/) | Parallel Claude Code agents on native git worktrees |
| [tg-report](./plugins/tg-report/) | Agents report finished turns to Telegram |

One skill = one plugin: each installs, enables, and disables independently.

## Core Beliefs

1. **Context is power** — answer quality = context quality
2. **Determinism > improvisation** — playbook exists → use it; no → create & save
3. **Delegation > execution** — route to the right tool/agent
4. **Evolution is mandatory** — learnings → system improvements

## Workflow

```
Request → Playbook exists? → Execute
               ↓ no
          Solve → /learn → Save as playbook
```

## Prerequisites

| Tool | Required by | Install |
|------|------------|---------|
| Claude Code | all | https://claude.ai/code |
| plugin-dev | learn (updater agent) | Claude Code marketplace |
| tmux | worktree-flow | `brew install tmux` |

## Quick Start

```bash
# Register this marketplace
claude plugin marketplace add mishachepi/m-claude

# Install the plugins you want
claude plugin install learn@m-claude-plugins
claude plugin install prompt-optimize@m-claude-plugins
claude plugin install init@m-claude-plugins
claude plugin install update@m-claude-plugins
claude plugin install brainstorm@m-claude-plugins
claude plugin install lead-research@m-claude-plugins
claude plugin install worktree-flow@m-claude-plugins
claude plugin install tg-report@m-claude-plugins

# Initialize in your project
/init local
```

## Structure

```
m-claude/
├── plugins/
│   ├── learn/           # Skill learn, /init command, updater agent
│   ├── prompt-optimize/ # Prompt engineering skill
│   ├── init/             # Docs-structure bootstrap skill
│   ├── update/           # Docs-sync skill
│   ├── brainstorm/       # Brainstorming skill
│   ├── lead-research/    # Research skill + 3 agents
│   ├── worktree-flow/    # Parallel agents on native git worktrees
│   └── tg-report/        # Telegram reporting on turn completion
├── docs/              # Framework documentation
│   ├── plugin-learn.md
│   ├── plugin-prompt-optimize.md
│   ├── plugin-init.md
│   ├── plugin-update.md
│   ├── plugin-brainstorm.md
│   ├── plugin-lead-research.md
│   ├── plugin-worktree-flow.md
│   └── plugin-tg-report.md
└── CLAUDE.md          # Project instructions
```

## Documentation

See [`docs/`](./docs/) for detailed plugin documentation.
