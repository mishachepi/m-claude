# Learn — scion agent mode (`$SCION_AGENT` is set)

A scion agent's persistent memory is its **template** — the directory it was spawned from
(`.scion/templates/<template>/`): system prompt `agents.md`, `lessons.md`, and whatever else the
template carries. The template survives `scion delete` + respawn; the agent home does not.

Never park durable knowledge in the home (`~/.claude/**`, auto-memory `MEMORY.md`, scratch files
under `~`) — it dies with the instance. Don't create home-memory files at all.

## Find your template

1. `scion whoami --full` → the `Template:` field.
2. A real directory under `.scion/templates/` → that's it. `custom` or no match → look for
   `.scion/templates/<your-agent-name>/`.
3. Still ambiguous → ask the user. **Never guess a template and never write into another agent's
   template.**

## Where it lives

| Type | Destination |
|---|---|
| Rule / Gotcha / role lesson — what your successor after respawn must know | append to `<template>/lessons.md` |
| Identity / boundary change — who you are, what you own | edit `<template>/agents.md` — show the exact diff, only with explicit user confirmation |
| Beyond your role — a rule or schema affecting other agents | route to its owner per the project protocol (task / message); never edit foreign templates |
| Domain knowledge — a fact about the world | the project's knowledge base, not the template |
| Work-in-progress state | nowhere — it belongs in the task tracker |

## lessons.md format

Append-only, one line per lesson, ≤ ~200 chars: date, the point, evidence in parens.

```markdown
- 2026-09-09: `oq` WHERE with a nonexistent field is silently empty, not an error — check the field against the schema. (would refute: non-empty result; 2 cases)
```

Hypotheses carry `(hypothesis, 1 case)`. File missing → create it with
`# Lessons — <template>` and `> append-only; loaded at boot; cleanup only in a template revision wave.`

- **Never edit or delete existing lines** — promotion into the system prompt and cleanup happen in
  template revision, not ad hoc.
- **Make sure it's loaded at boot:** `agents.md` (or the template's context script) must reference
  `lessons.md`; if it doesn't, add one reference line — otherwise the lessons are never read.
