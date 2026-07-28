# Worktree Flow Plugin

> Parallel Claude Code agents on native git worktrees — spawn, run, merge.

## Philosophy

- **Native only** — `claude -w` + git + tmux, no external orchestrator binary
- **One task = one worktree = one tmux window** — isolation is the unit of parallelism
- **The agent commits, the coordinator merges** — squash-merge, one commit per task
- **Discover state, never assume it** — `git worktree list --porcelain`, `tmux list-windows`

## Skills

| Skill | Description |
|-------|-------------|
| `worktree-flow` | Spawn, monitor, merge and discard parallel worktree agents |

## Usage

```
"spawn a worktree agent for <task>"
"run these three tasks in parallel worktrees"
"merge the worktree <name>"
"параллельные агенты в worktree"
```

## Flow

```
split request → spawn (tmux window + claude -w) → monitor panes
              → agent commits on worktree-<name>
              → squash-merge → unlock → remove worktree → drop branch
```

## Gotchas (verified on Claude Code 2.1.220)

| Behaviour | Consequence |
|-----------|-------------|
| Branch `worktree-<name>` is cut from `origin/main`, not from current HEAD | Unpushed local commits are invisible to the agent — push or rebase the worktree |
| Worktree stays `locked` after the session exits | `locked` is not a liveness signal; removal needs `git worktree unlock` (or `remove -f -f`) |
| Worktrees land in `<repo>/.claude/worktrees/` | The parent repo must gitignore `.claude/worktrees/` |

## Requirements

| Tool | Install |
|------|---------|
| Claude Code ≥ 2.1 (`-w/--worktree`) | https://claude.ai/code |
| git ≥ 2.30 (`git worktree`) | system |
| tmux | `brew install tmux` |
