---
name: Worktree Flow
description: This skill should be used when the user asks to "spawn a worktree agent", "run tasks in parallel worktrees", "merge a worktree", "worktree flow", "параллельные агенты в worktree", "смерджи worktree", or wants to run/manage/merge parallel Claude Code sessions on isolated branches. Native flow — no external binaries.
version: 2.0.1
user-invocable: true
allowed-tools: Bash, Read, Glob, Grep
---

# Worktree Flow — parallel agents on native Claude Code worktrees

Several tasks at once, each a **live** Claude session on its own worktree and branch, squash-merged
back when done. Built on `claude -w` + git + tmux only. Live is the default — attach, talk, steer;
headless is the exception.

## Mechanics (what `claude -w <name>` does)

- Creates a worktree at `<repo>/.claude/worktrees/<name>`
- Creates branch `worktree-<name>` **from `origin/main`**, not the current HEAD (it says
  `(based on origin/main)` on startup) — unpushed local commits are invisible to the agent.
- Locks the worktree for the session; the lock is **not** released on exit

Two consequences, both verified on Claude Code 2.1.220:

- **Rebase, or lose work.** Right after spawning, check `git -C .claude/worktrees/<name> log --oneline -1`.
  If it is behind the intended base, `git -C .claude/worktrees/<name> rebase main` before the agent
  gets far — otherwise the squash-merge silently reverts everything that landed after `origin/main`.
- **`locked` is not a liveness signal.** A finished session leaves the worktree locked; removing it
  needs `git worktree unlock <path>` first (or `git worktree remove -f -f`). Judge "done" by the
  tmux session/window and the agent's commit.

Discover state with `git worktree list --porcelain` — never assume paths.

## Prerequisite: workspace trust (once per repo)

Interactive `claude -w` fails with `Error creating worktree: Workspace trust not yet accepted` in a
repo whose trust dialog was never accepted — spawned from tmux, the window just dies in a second and
looks like "the agent never started". A human accepts it once: run `claude` in the repo, "Yes, I
trust this folder", exit (`projects.<repo>.hasTrustDialogAccepted` in `~/.claude.json`). Headless
`-p` skips the gate, which is why a batch run can succeed where a live one fails.

## Spawn a live agent

Own tmux **session** per agent — the closest thing to a dedicated workspace:

```bash
claude -w <name> --tmux=classic     # plain tmux; drop "=classic" for iTerm2 panes
```

This creates session `<repo>_worktree-<name>` with the agent running in the worktree. Inside it,
detach with `C-b C-b d` — the prefix is pressed twice because Claude itself uses `C-b`.

Own **window** in the current session — lighter, better when juggling many at once:

```bash
tmux new-window -n wt-<name> "claude -w <name>"
tmux new-window -d -n wt-<name> "claude -w <name> '<initial task>'"   # -d: start it without jumping to it
```

Rules:
- One task = one worktree = one session/window. Short kebab-case names.
- State the deliverable in the task AND that the agent must commit on its branch when done.
- Independent tasks only. Two agents editing the same files produce two conflicting branches.

## Attach, steer, switch

| Action | Command |
|--------|---------|
| List agent sessions | `tmux list-sessions \| grep worktree-` |
| Jump to a session | `tmux switch-client -t <repo>_worktree-<name>` |
| Jump to a window | `C-b w` (picker) or `C-b <n>` |
| Detach from an agent | `C-b C-b d` inside a Claude session |
| Peek without attaching | `tmux capture-pane -pt <target> \| tail -30` |
| Type into an agent from outside | `tmux send-keys -t <target> "<text>" Enter` |
| Did it commit yet | `git -C .claude/worktrees/<name> log --oneline -3` |

Attached, it is an ordinary Claude session: answer its questions, redirect it, interrupt it.
This is the whole point of running live — a stuck agent costs one sentence instead of a rerun.

## Headless (`-p`)

```bash
tmux new-window -d -n wt-<name> "claude -p -w <name> '<task>'; exec bash"
```

Only for work needing no supervision (a sweep, a report, a check): it prints just the final
message, can't be steered, and skills that call `AskUserQuestion` dead-end. `exec bash` keeps the
window (and output) alive after it finishes — so collect the output (`tmux capture-pane -pt
wt-<name>`, or `| tee /tmp/<name>.out`) and `tmux kill-window -t wt-<name>`; a screen of idle dead
shells reads as "something broke".

## Merge (squash) + cleanup

From the main worktree, once the agent committed:

```bash
git -C .claude/worktrees/<name> rebase main       # always — the base is origin/main, main has moved
git merge --squash worktree-<name>
git commit -m "<one-line summary of the task>"
git worktree unlock .claude/worktrees/<name>
git worktree remove .claude/worktrees/<name>
git branch -D worktree-<name>
tmux kill-session -t <repo>_worktree-<name> 2>/dev/null   # or: tmux kill-window -t wt-<name>
```

Rebase conflicts get resolved inside the worktree, where the agent's context lives — not in main.

Uncommitted work in the worktree? Commit it there first (or ask the user); never merge a dirty
worktree silently.

## Discard without merging

```bash
git worktree remove -f -f .claude/worktrees/<name>   # -f -f overrides the stale lock
git branch -D worktree-<name>
tmux kill-session -t <repo>_worktree-<name> 2>/dev/null
```

Kill the session first if the agent is still running.

## Coordinator pattern (N parallel tasks)

Split into genuinely independent tasks, spawn each live, rebase each fresh worktree (Mechanics),
rotate through sessions unblocking whoever waits, merge finished ones one at a time — re-rebasing
as main moves — and report merged / discarded / still running.

## Repo hygiene

`.claude/worktrees/` must be gitignored — otherwise every spawned agent pollutes `git status` of
the parent repo and can be committed by accident.
