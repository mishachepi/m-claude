# workmux Skills Guide

Quick reference for using workmux skills after installation.

## /worktree — Single Task

Fire-and-forget: launch one agent in a worktree.

```
/worktree Add user authentication to the API
/worktree Refactor database layer to use connection pool
```

Agent gets its own branch, runs independently. Use `/merge` when done.

## /coordinator — Multiple Tasks

Full lifecycle manager for parallel agents. Use when you have 2+ independent tasks.

```
/coordinator
```

The coordinator will:
1. Ask for your tasks (or accept a plan)
2. Write prompt files for each task
3. Spawn worktree agents in parallel (`workmux add -b -P`)
4. Monitor progress (`workmux status`, `workmux capture`)
5. Merge sequentially when agents finish (`workmux send <name> /merge`)

**Best practices:**
- Keep tasks independent (no shared files)
- Max 5 parallel worktrees
- Each task should be self-contained with clear success criteria

## /merge — Complete & Merge

Run from inside a worktree agent to merge its work back.

```
/merge
```

Does: commit → rebase on main → merge → cleanup worktree.

From main session, tell an agent to merge:
```bash
workmux send auth-agent /merge
```

## /rebase — Smart Rebase

Rebase current branch on main with conflict resolution.

```
/rebase
```

Handles merge conflicts automatically when possible.

## /workmux — CLI Reference

Teaches the agent about workmux CLI commands. Useful when agent needs to interact with other worktrees.

```
/workmux
```

## /open-pr — Create PR

Writes PR description from branch changes and opens in browser.

```
/open-pr
```

## Typical Workflow

```
1. Plan tasks
2. /coordinator → spawns agents
3. workmux dashboard → monitor
4. Agents finish → /merge each
5. /open-pr → create PR
```
