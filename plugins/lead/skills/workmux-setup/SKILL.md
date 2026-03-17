---
name: workmux Setup
description: This skill should be used when the user asks to "setup workmux", "install workmux", "configure workmux", "настрой workmux", "workmux help", or needs help with workmux installation, configuration, and usage guide.
user-invocable: true
---

# workmux — Setup & Reference

workmux orchestrates git worktrees + tmux windows for parallel AI agent work.

## Setup

```bash
# 1. Install
brew install raine/tap/workmux

# 2. Setup skills + hooks for Claude Code
workmux setup --skills

# 3. Apply config (optional — uses example from this plugin)
workmux setup references/workmux-config.yaml
```

After setup, workmux installs these Claude Code skills:

| Skill | Purpose |
|-------|---------|
| `/worktree` | Fire-and-forget — delegate task to worktree agent |
| `/coordinator` | Full lifecycle — spawn, monitor, merge multiple agents |
| `/merge` | Commit + rebase + merge + cleanup |
| `/rebase` | Smart rebase with conflict resolution |
| `/workmux` | Reference — teaches agents about workmux CLI |
| `/open-pr` | Write PR description and open in browser |

And hooks for agent status tracking in tmux window names.

## When to Use What

| Situation | Use |
|-----------|-----|
| Quick single task | `/worktree Implement X` |
| Multiple parallel tasks | `/coordinator` |
| Agent finished, merge | `/merge` or `workmux send <name> /merge` |
| Rebase on main | `/rebase` |

## CLI Quick Reference

### Create

```bash
workmux add <name>                    # worktree + window + Claude
workmux add <name> -b -P prompt.md    # background + prompt file
workmux add <name> -A "task desc"     # create + send immediately
```

### Monitor

```bash
workmux dashboard          # TUI overview
workmux status             # table of all agents
workmux status <name>      # specific agent
workmux capture <name>     # agent terminal output
workmux wait <name>        # block until done
```

### Communicate

```bash
workmux send <name> "message"     # send instruction
workmux send <name> /merge        # tell agent to merge
workmux run <name> -- npm test    # run command in worktree
```

### Complete

```bash
workmux send <name> /merge    # agent merges its own branch
workmux remove <name>         # discard without merging
```

## Status Icons

| Icon | Status | Meaning |
|------|--------|---------|
| 🤖 | `working` | Agent using tools |
| 💬 | `waiting` | Needs input |
| ✅ | `done` | Finished |

## Example Config

See `references/workmux-config.yaml` for recommended settings.

Key settings:
- `mode: window` — each worktree = tmux window
- `agent: claude` — auto-starts Claude Code
- `merge_strategy: squash` — clean merge history
- `panes` — agent (focused) + shell (for tests/git)

## What's Next?

After installation, see `references/workmux-skills-guide.md` for detailed usage of each workmux skill.

## Docs

https://workmux.raine.dev/
