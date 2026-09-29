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

One skill = one plugin: each installs, enables, and disables independently.

| Plugin | Purpose |
|--------|---------|
| **learn** | Capture session learnings; `/init` bootstrap; `updater` agent |
| **prompt-optimize** | Prompt engineering guide + CLAUDE.md optimization |
| **init** | Set up a project's documentation structure |
| **update** | Documentation sync from code changes |
| **brainstorm** | Structured brainstorming → spec document |
| **lead-research** | Multi-agent research |
| **worktree-flow** | Parallel Claude Code agents on native git worktrees |
| **tg-report** | Agents report finished turns to Telegram — summary + attached full answer |

## Documentation

Project documentation lives in `docs/`. Load relevant files when working on related topics.

| File | Triggers | Purpose |
|------|----------|---------|
| `docs/plugin-learn.md` | learn, init, self-learning, bootstrap | Learn plugin components |
| `docs/plugin-prompt-optimize.md` | prompt-optimize, prompt engineering | Prompt Optimize plugin components |
| `docs/plugin-init.md` | init docs, documentation setup | Init plugin components |
| `docs/plugin-update.md` | update docs | Update plugin components |
| `docs/plugin-brainstorm.md` | brainstorm, spec | Brainstorm plugin components |
| `docs/plugin-lead-research.md` | research, lead-research | Lead Research plugin components |
| `docs/plugin-worktree-flow.md` | worktree, parallel agents, merge, tmux | Worktree Flow plugin components |
| `docs/plugin-tg-report.md` | telegram, report, stop hook, notify | TG Report plugin components |
| `docs/troubleshooting.md` | error, fails, broken, corrupted | Known gotchas and fixes |

## Prerequisites

| Tool | Plugin | Install |
|------|--------|---------|
| plugin-dev | learn (updater agent) | Claude Code marketplace |
| tmux | worktree-flow | `brew install tmux` |

Don't forget to update README.md after changes.
