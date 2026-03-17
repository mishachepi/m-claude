# Lead Plugin

> workmux setup, configuration, and usage guide for parallel AI agent work.

## Prerequisites

```bash
brew install raine/tap/workmux
workmux setup --skills
```

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `workmux-setup` | Installation, configuration, and skills usage guide |
| Reference | `workmux-config.yaml` | Example workmux config |
| Reference | `workmux-skills-guide.md` | How to use /coordinator, /worktree, /merge, etc. |

## How It Works

Run `/workmux-setup` to install and configure workmux. After setup, use workmux skills directly:

| Task | Skill |
|------|-------|
| Single task in worktree | `/worktree` |
| Multiple parallel tasks | `/coordinator` |
| Merge agent's work | `/merge` |
| Create PR | `/open-pr` |

See `references/workmux-skills-guide.md` for detailed usage.
