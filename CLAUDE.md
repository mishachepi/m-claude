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

**Any change to a plugin = bump its `version`** in `plugin.json`, `marketplace.json` and the SKILL.md frontmatter. Installed plugins are cached per version; an unbumped change never reaches machines. Run `scripts/preflight.sh .` before every push: manifest validation, `${CLAUDE_PLUGIN_ROOT}` paths, name consistency, secret scan of the outgoing diff, version bumps.

| Plugin | Purpose |
|--------|---------|
| **learn** | Capture session learnings; `/learn:bootstrap`; `updater` agent |
| **prompt-optimize** | Prompt engineering guide + CLAUDE.md optimization |
| **docs-init** | Set up a project's documentation structure |
| **docs-update** | Documentation sync from code changes |
| **brainstorm** | Structured brainstorming → spec document |
| **lead-research** | Multi-agent research |
| **worktree-flow** | Parallel Claude Code agents on native git worktrees |
| **mcp-installer** | Find and install MCP servers, harness-agnostic, always confirm before install |
| **arc** | Arc browser MCP server via `uvx` (macOS only), read-only |

## Documentation

Project documentation lives in `docs/`. Load relevant files when working on related topics.

| File | Triggers | Purpose |
|------|----------|---------|
| `docs/plugin-learn.md` | learn, self-learning, bootstrap | Learn plugin components |
| `docs/plugin-prompt-optimize.md` | prompt-optimize, prompt engineering | Prompt Optimize plugin components |
| `docs/plugin-docs-init.md` | docs-init, init docs, documentation setup | Docs Init plugin components |
| `docs/plugin-docs-update.md` | docs-update, update docs | Docs Update plugin components |
| `docs/plugin-brainstorm.md` | brainstorm, spec | Brainstorm plugin components |
| `docs/plugin-lead-research.md` | research, lead-research | Lead Research plugin components |
| `docs/plugin-worktree-flow.md` | worktree, parallel agents, merge, tmux | Worktree Flow plugin components |
| `docs/plugin-mcp-installer.md` | mcp-installer, install MCP, find MCP server | MCP Installer plugin components |
| `docs/plugin-arc.md` | arc, arc-mcp, browser tabs | Arc plugin components |
| `docs/troubleshooting.md` | error, fails, broken, corrupted | Known gotchas and fixes |

## Prerequisites

| Tool | Plugin | Install |
|------|--------|---------|
| plugin-dev | learn (updater agent) | Claude Code marketplace |
| tmux | worktree-flow | `brew install tmux` |
| uv | arc | `brew install uv` |

Don't forget to update README.md after changes.
