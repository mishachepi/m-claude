# Lead Plugin

workmux setup and usage guide — parallel AI agent orchestration with git worktrees.

## Prerequisites

workmux with skills: `brew install raine/tap/workmux && workmux setup --skills`

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `workmux-setup` | Installation, configuration, and workmux skills usage guide |
| Reference | `workmux-config.yaml` | Example workmux config |
| Reference | `workmux-skills-guide.md` | /coordinator, /worktree, /merge usage |

## Key Skills (from workmux)

| Skill | Use For |
|-------|---------|
| `/worktree` | Single task in worktree |
| `/coordinator` | Multiple parallel tasks |
| `/merge` | Merge agent's work back |
| `/open-pr` | Create PR from branch |
