---
name: Scion Learn
description: This skill should be used when a scion agent wants to remember something durable — the user says "learn", "запомни", "remember this", OR the agent itself just hit a tool gotcha, had an assumption refuted, or was corrected. Routes the lesson into the agent's scion template (its only persistent memory); never into the ephemeral agent home.
version: 0.1.0
user-invocable: true
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion
---

# Scion Learn — the template is the memory

A scion agent's persistent memory is its **template**: the directory it was spawned from
(`.scion/templates/<template>/` in the project workspace) — system prompt (`agents.md`),
`lessons.md`, and whatever else the template carries. The template survives `scion delete` +
respawn; the agent's home does not. Therefore:

- **Never park durable knowledge in the agent home** (`~/.claude/**`, auto-memory `MEMORY.md`,
  scratch files under `~`). It dies with the agent instance. Do not create home-memory files at all.
- A lesson left only in the transcript dies with the session. This skill is the one ritual that
  moves it into the layer that survives.

## Step 0 — quality gate (mandatory)

Before writing anything, check:

1. **A lesson counts only if its check could have failed.** "Looks like", one truncated run, a
   command that didn't error while silently eating a parameter — not lessons.
2. **One case is a case, not a class.** No second confirmation → record it marked `(1 case)`, not
   as a rule.
3. **A lesson must name what would refute it.** Can't name it → it's an opinion, not a lesson.

Fails the gate → don't record it, or record it explicitly marked as a hypothesis.

## Step 1 — find your template

1. `scion whoami` → your agent name; `scion whoami --full` → `Template:` field.
2. If the Template field names a real directory under `.scion/templates/`, that's it. If it says
   `custom` or doesn't match, look for `.scion/templates/<your-agent-name>/`.
3. Still ambiguous → ask the user. **Never guess a template directory and never write into
   another agent's template.**

## Step 2 — classify: where does it live

| Type | Signal | Destination |
|---|---|---|
| **Role lesson** | durable: a tool gotcha, a boundary, an error pattern — what your successor after respawn must know | append to `<template>/lessons.md` |
| **Identity / boundary change** | who you are, what you own, how you must behave | edit `<template>/agents.md` — only with explicit user confirmation |
| **Beyond your role** | a rule, schema, or convention affecting other agents | route to its owner per the project's protocol (task / message); do not edit foreign templates |
| **Domain knowledge** | a fact about the world, not about agent behavior | the project's knowledge base, not the template |
| **Work-in-progress state** | current task status, temporary workarounds | nowhere — it belongs in the task/tracker, not in memory |

## Step 3 — write

### lessons.md — strict format

Append-only, one line per lesson, at the bottom:

```markdown
- 2026-09-09: `oq` WHERE with a nonexistent field is silently empty, not an error — always check the field against the schema. (would refute: non-empty result; 2 cases)
```

- ≤ ~200 chars: date, the point, evidence in parens — what would refute it / how many cases.
- Hypothesis → explicit `(hypothesis, 1 case)` marker.
- File missing → create it:

```markdown
# Lessons — <template>

> append-only; loaded at boot; cleanup happens only during a template revision wave.
```

- **Never edit or delete existing lines** — promotion of a lesson into the system prompt and
  cleanup happen during template revision, not ad hoc.
- **Ensure the file is loaded at boot**: `agents.md` (or the template's context script) must
  reference `lessons.md`. If it doesn't, add one reference line to `agents.md` — otherwise the
  lessons exist but are never read.

### agents.md — identity edits

Show the exact diff to the user and wait for confirmation. The system prompt is the agent's
constitution; it changes deliberately, not as a side effect of one session.

## Step 4 — confirm

Interactive: present the classification and the draft line **before** writing; wait.
Headless (no user available): write immediately, but the result (path + line) must be visible in
the final output of the turn.

## What is NOT a lesson

- Session play-by-play ("did X, then Y") — that's the transcript, it already exists.
- Someone else's lesson from a received message — its author records it.
- An unresolved problem — that's a task, not a lesson.
- A number/metric — that belongs in tracked data with a source, not in lessons.
