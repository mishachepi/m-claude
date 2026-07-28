# Worktree Flow Plugin

Parallel Claude Code agents on native git worktrees — spawn, run, merge.

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `worktree-flow` | Spawn / monitor / merge / discard parallel worktree agents |

## Mechanism

Built on `claude -w <name>` only — no external orchestrator. Each task gets a git
worktree under `<repo>/.claude/worktrees/<name>` on branch `worktree-<name>`, driven
from its own tmux session (`<repo>_worktree-<name>`, via `--tmux`) or window (`wt-<name>`).
Sessions are live and attachable by default; `-p` runs an agent headless for unsupervised work.

## Flow

```
split request        → independent tasks
tmux new-window      → claude -w <name> "<task>"   (one window per task)
monitor              → tmux capture-pane / send-keys
agent commits        → on worktree-<name>
git merge --squash   → one commit per task on the base branch
unlock + remove      → worktree and branch dropped
```

## Verified behaviour (Claude Code 2.1.220)

- Branch base is `origin/main`, stated by the tool itself on startup ("based on origin/main").
  Unpushed local commits do not reach the agent — rebase the worktree before it gets far.
- The worktree stays `locked` after the session ends — `locked` cannot be used as a
  "still running" signal, and removal needs `git worktree unlock` or `remove -f -f`.
- Interactive `claude -w` fails with "Workspace trust not yet accepted" in a directory
  whose trust dialog was never answered; headless `claude -p -w` bypasses that gate.
  A tmux-spawned window dies within a second on this error, which reads as "the agent
  never started".
- `--tmux` requires `--worktree`; `--tmux=classic` uses plain tmux instead of iTerm panes.

## Repo requirement

The consuming repo must gitignore `.claude/worktrees/` — otherwise spawned agents
pollute `git status` and can be committed by accident.
