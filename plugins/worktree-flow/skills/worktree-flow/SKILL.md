---
name: Worktree Flow
description: This skill should be used when the user asks to "spawn a worktree agent", "run tasks in parallel worktrees", "merge a worktree", "worktree flow", "параллельные агенты в worktree", "смерджи worktree", or wants to run/manage/merge parallel Claude Code sessions on isolated branches. Native flow — no external binaries.
version: 2.0.0
user-invocable: true
allowed-tools: Bash, Read, Glob, Grep
---

# Worktree Flow — parallel agents on native Claude Code worktrees

Run several tasks at once, each as its own live Claude session on its own git worktree and
branch, then squash-merge the finished ones back. Built entirely on `claude -w` + git + tmux —
no orchestrator binary.

The default is a **live** session: attach to it, talk to it, steer it. Headless is the exception,
not the rule (see Headless).

## Mechanics (what `claude -w <name>` does)

- Creates a worktree at `<repo>/.claude/worktrees/<name>`
- Creates branch `worktree-<name>` **from `origin/main`** — the tool says so itself on startup:
  `Created worktree: …/.claude/worktrees/<name> (based on origin/main)`. Not from the current
  HEAD: local commits that are not pushed are invisible to the agent.
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

Interactive `claude -w` refuses to create a worktree in a directory whose trust dialog has never
been accepted:

```
Error creating worktree: Workspace trust not yet accepted.
```

Spawned from tmux, the error scrolls past and the window dies in a second — it reads as "the agent
never started". A human must accept it once: run `claude` in the repo, answer "Yes, I trust this
folder", exit. The flag lives at `projects.<repo>.hasTrustDialogAccepted` in `~/.claude.json`.
Headless `-p` bypasses the gate entirely, which is why a batch run can succeed where a live one fails.

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

Use only for work that genuinely needs no supervision: a mechanical sweep, a report, a check.
The trade-offs are real:

- prints only the final message — nothing can be steered mid-flight
- skills that call `AskUserQuestion` (interviews, confirmations) dead-end
- `exec bash` is required, otherwise the window closes and takes the output with it

That trailing shell is the price of keeping the output: a finished headless window looks exactly
like an idle `bash` prompt, and a screen full of them reads as "something broke". Collect the output
(`tmux capture-pane -pt wt-<name>`, or `| tee /tmp/<name>.out` in the command) and then
`tmux kill-window -t wt-<name>` — do not leave dead shells behind for the user to find.

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

1. Split the request into genuinely independent tasks; spawn each live.
2. Rebase each fresh worktree onto the intended base before it gets far.
3. Rotate through the sessions: unblock whoever is waiting, let the rest run.
4. Merge finished branches one at a time (squash), re-rebasing each one as main moves.
5. Report: merged / discarded / still running.

## Repo hygiene

`.claude/worktrees/` must be gitignored — otherwise every spawned agent pollutes `git status` of
the parent repo and can be committed by accident.
