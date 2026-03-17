Development of Claude Code plugins m-claude

You already use these plugins and continue to develop them.

## Remember Core Beliefs
1. **Context is power** — answer quality = context quality
2. **Determinism > improvisation** — playbook exists → use it; no → create & save
3. **Delegation > execution** — route to the right tool/agent
4. **Evolution is mandatory** — learnings → system improvements
5. **Human in the loop** — critical actions require confirmation

## Flow

```
Request → Playbook exists? → Execute
               ↓ no
          Solve → Save as playbook
```

**Playbooks** = commands, skills, agents — prepared solutions.

## Plugins

| Plugin | Purpose |
|--------|---------|
| **core** | Self-learning workflow: init, learn, prompt-optimize |
| **lead** | Parallel implementation via workmux worktrees |
| **docs** | Documentation sync from code changes |
| **research** | Multi-agent research + brainstorming |

## Documentation

Project documentation lives in `docs/`. Load relevant files when working on related topics.

| File | Triggers | Purpose |
|------|----------|---------|
| `docs/plugin-core.md` | core, init, learn, prompt-optimize | Core plugin components |
| `docs/plugin-lead.md` | lead, workmux, worktree, parallel | Lead plugin + workmux integration |
| `docs/plugin-docs.md` | docs, documentation, update docs | Docs plugin components |
| `docs/plugin-research.md` | research, brainstorm, spec | Research plugin components |

## Prerequisites

| Tool | Plugin | Install |
|------|--------|---------|
| plugin-dev | core | Claude Code marketplace |
| workmux + skills | lead | `brew install raine/tap/workmux && workmux setup --skills` |

Don't forget to update README.md after changes.
