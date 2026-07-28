---
name: Worktree Flow
description: This skill should be used when the user asks to "spawn a worktree agent", "run tasks in parallel worktrees", "merge a worktree", "worktree flow", "параллельные агенты в worktree", "смерджи worktree", or wants to run/manage/merge parallel Claude Code sessions on isolated branches. Native flow — no external binaries.
version: 1.0.0
user-invocable: true
allowed-tools: Bash, Read, Glob, Grep
---

# Worktree Flow — parallel agents on native Claude Code worktrees

Run parallel tasks as isolated Claude sessions, one git worktree + tmux window each, then squash-merge back. Built entirely on `claude -w` + git + tmux.

## Mechanics (what `claude -w <name>` does)

- Creates worktree at `<repo>/.claude/worktrees/<name>`
- Creates branch `worktree-<name>` **from the remote default branch** (`origin/main`), not from the current HEAD or the checked-out branch
- Locks the worktree for the session; the lock is **not** released on exit

Two consequences, both verified on Claude Code 2.1.220:

- **Unpushed local commits are invisible to the agent.** Push first, or rebase the worktree onto the intended base right after spawning: `git -C .claude/worktrees/<name> rebase <base>`.
- **`locked` is not a liveness signal.** A finished session leaves the worktree locked; removing it needs `git worktree unlock <path>` first (or `git worktree remove -f -f`). Use the tmux window or the agent's commit as the "done" signal instead.

Discover state at any time with `git worktree list --porcelain` — never assume paths.

## Spawn

From a repo root, one tmux window per task:

```bash
tmux new-window -d -n wt-<name> 'claude -w <name> "<task text>"'
```

Interactive single task in the current terminal: `claude -w <name> --tmux` (needs `--worktree`; `--tmux=classic` for plain tmux instead of iTerm panes).

Fire-and-forget subtask inside an existing Claude session: use the Agent tool with `isolation: "worktree"` instead of spawning a full session.

Rules:
- One task = one worktree = one window. Keep names short and kebab-case.
- The task prompt must state the deliverable AND that the agent must commit its result on its branch when done.
- If the work depends on commits that are not on `origin/main` yet, say so in the prompt and rebase the worktree onto the right base before the agent starts.

## Monitor

```bash
git worktree list                          # what exists (ignore the lock flag — see Mechanics)
tmux list-windows | grep wt-               # running agent windows = what is actually alive
tmux capture-pane -pt wt-<name> | tail -30 # peek at an agent
tmux send-keys -t wt-<name> "<follow-up>" Enter   # talk to an agent
git -C .claude/worktrees/<name> log --oneline -3  # did it commit yet?
```

An agent is done when its tmux window is gone (or idle) **and** its branch carries the expected commit.

## Merge (squash) + cleanup

From the main worktree, once the agent committed:

```bash
git merge --squash worktree-<name>
git commit -m "<one-line summary of the task>"
git worktree unlock .claude/worktrees/<name>
git worktree remove .claude/worktrees/<name>
git branch -D worktree-<name>
tmux kill-window -t wt-<name> 2>/dev/null
```

If the base moved since spawn — rebase first, inside the worktree:

```bash
git -C .claude/worktrees/<name> rebase main   # resolve conflicts there, then squash-merge as above
```

Uncommitted work in the worktree? Commit it there first (or ask the user); never merge a dirty worktree silently.

## Discard without merging

```bash
git worktree remove -f -f .claude/worktrees/<name>   # -f -f overrides the stale lock
git branch -D worktree-<name>
tmux kill-window -t wt-<name> 2>/dev/null
```

Kill the tmux window **before** removing if the session is still running.

## Coordinator pattern (N parallel tasks)

1. Split the request into independent tasks; spawn each (see Spawn).
2. Poll tmux windows + peek panes; unblock agents via `send-keys` when they wait.
3. Merge finished branches one at a time (squash), re-running rebase for later ones.
4. Report: merged / discarded / still running.

## Repo hygiene

`.claude/worktrees/` must be gitignored — otherwise every spawned agent pollutes `git status` of the parent repo and can be committed by accident.
