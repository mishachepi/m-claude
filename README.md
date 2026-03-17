# m-claude

> Plugin framework for Claude Code — self-learning AI manager with determinism, delegation, and evolution.

## Plugins

| Plugin | Purpose |
|--------|---------|
| [core](./plugins/core/) | Self-learning workflow — init, learn, prompt-optimize |
| [lead](./plugins/lead/) | workmux setup and usage guide for parallel AI agent work |
| [docs](./plugins/docs/) | Keep documentation in sync with code changes |
| [research](./plugins/research/) | Multi-agent research and brainstorming |

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
| plugin-dev | core | Claude Code marketplace |
| workmux | lead | `brew install raine/tap/workmux && workmux setup --skills` |
| tmux | lead | `brew install tmux` |

## Quick Start

```bash
# Install from marketplace
claude mcp add-from-marketplace m-claude-plugins

# Or install individual plugins
claude plugin add ./plugins/core
claude plugin add ./plugins/lead
claude plugin add ./plugins/docs
claude plugin add ./plugins/research

# Initialize in your project
/init local
```

## Structure

```
m-claude/
├── plugins/
│   ├── core/          # Commands, agents, skills for self-learning
│   ├── lead/          # workmux setup and parallel agent orchestration
│   ├── docs/          # Documentation sync from code changes
│   └── research/      # Multi-agent research + brainstorming
├── docs/              # Framework documentation
│   ├── plugin-core.md
│   ├── plugin-lead.md
│   ├── plugin-docs.md
│   └── plugin-research.md
└── CLAUDE.md          # Project instructions
```

## Documentation

See [`docs/`](./docs/) for detailed plugin documentation.
