# m-claude

> Plugin framework for Claude Code — self-learning AI manager with determinism, delegation, and evolution.

## Plugins

| Plugin | Purpose |
|--------|---------|
| [core](./plugins/core/) | Self-learning workflow — init, learn, prompt-optimize |
| [docs](./plugins/docs/) | Keep documentation in sync with code changes |
| [research](./plugins/research/) | Multi-agent research and brainstorming |
| [worktree-flow](./plugins/worktree-flow/) | Parallel Claude Code agents on native git worktrees |

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
| tmux | worktree-flow | `brew install tmux` |

## Quick Start

```bash
# Install from marketplace
claude mcp add-from-marketplace m-claude-plugins

# Or install individual plugins
claude plugin add ./plugins/core
claude plugin add ./plugins/docs
claude plugin add ./plugins/research
claude plugin add ./plugins/worktree-flow

# Initialize in your project
/init local
```

## Structure

```
m-claude/
├── plugins/
│   ├── core/          # Commands, agents, skills for self-learning
│   ├── docs/          # Documentation sync from code changes
│   ├── research/      # Multi-agent research + brainstorming
│   └── worktree-flow/ # Parallel agents on native git worktrees
├── docs/              # Framework documentation
│   ├── plugin-core.md
│   ├── plugin-docs.md
│   ├── plugin-research.md
│   └── plugin-worktree-flow.md
└── CLAUDE.md          # Project instructions
```

## Documentation

See [`docs/`](./docs/) for detailed plugin documentation.
