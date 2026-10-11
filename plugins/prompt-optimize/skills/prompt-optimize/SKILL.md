---
name: Prompt Optimize
description: This skill should be used when the user asks to "optimize CLAUDE.md", "check my prompts", "improve prompt", "prompt engineering", "оптимизируй", "проверь CLAUDE.md", "prompt best practices", "fix my prompt", or needs to write, improve, or audit prompts and CLAUDE.md files.
version: 1.0.1
user-invocable: true
allowed-tools: Read, Edit, Glob, AskUserQuestion
---

# Prompt Optimize

Audit a CLAUDE.md file or a prompt, or help write one, following Anthropic best practices.

## Blocking checks — always first, both modes

Two defects make an instruction set unexecutable however well it is formatted. They need actual
reading, not counting, and they decide the verdict:

1. **Contradictions** — two instructions that cannot both be obeyed ("always use tabs" vs "never
   use tabs"; "write notes to MIGRATION.md" vs "create no new files"). Report both quotes with line
   numbers **and which one to keep** — never a contradiction without a resolution.
2. **Vagueness** — no observable criterion ("be smart", "handle errors properly", "reasonably
   fast", "where appropriate"). Propose the concrete rule that was probably meant.

Either found → the verdict can't be `GOOD`, whatever else passes.

## Mode 1 — audit a CLAUDE.md

Scope: `local` → `./CLAUDE.local.md`; `global` → `~/.claude/CLAUDE.md`; `all`/nothing → both;
an explicit path → only that file.

After the blocking checks, the mechanical ones (a script could do these):

| Check | Threshold | Why |
|---|---|---|
| Size | < 100 lines | loaded every session — every line costs context |
| Sections | 3–7, unique headers | too few = incomplete, too many = cluttered |
| Required sections (global only) | Workflow, Principles | core structure |
| Unfinished | no TODO / FIXME / XXX | unfinished instructions get followed literally |
| Line length | < 120 chars | readability |

```
CLAUDE.md Analysis — {filename}
Contradictions: {OK | "{A}" (L{n}) vs "{B}" (L{m}) → keep {which}}
Vagueness:      {OK | "{quote}" (L{n}) → "{concrete rule}"}
Size / Sections / Required / Unfinished / Long lines: {OK | WARNING: detail}
Suggestions: …
Overall: {GOOD | NEEDS ATTENTION}
```

Offer fixes: delete the losing rule of a contradiction (never keep both), replace vague lines with
the concrete rule, split an oversized file, add missing sections, resolve TODOs.

## Mode 2 — write or review a prompt

After the blocking checks, apply the principles:

1. **Explicit** — say exactly what's wanted. "Create an analytics dashboard" → "…with filtering,
   charts, and export. Go beyond basics."
2. **Context (WHY)** — Claude generalizes from reasons. "NEVER use ellipses" → "Output is read by
   a TTS engine, which can't pronounce ellipses."
3. **Positive framing** — "Don't use markdown" → "Write flowing prose paragraphs."
4. **Structure** — XML tags (`<context>`, `<instructions>`, `<output_format>`, `<examples>`);
   the prompt's own format shapes the response's format.
5. **Examples** — 2–3 showing the desired behavior; Claude 4.x follows them closely.
6. **Each instruction once, no shouting** — redundancy and "CRITICAL/MUST" everywhere dilute
   the instructions that matter.

Claude 4.x defaults worth stating when wanted: act rather than suggest; call independent tools in
parallel; change only what was asked; read relevant files before proposing edits.

```
Prompt Analysis
Contradictions: {OK | "{A}" vs "{B}" → keep {which}}
Vagueness:      {OK | "{quote}" → "{criterion}"}
Principles:     {OK | which fail}
Overall: {GOOD | NEEDS ATTENTION | BLOCKED}
```

`BLOCKED` = a contradiction or unresolvable vagueness — not executable as written. Cosmetic flaws
only → at worst `NEEDS ATTENTION`. A sound prompt is `GOOD`: say so and stop — rewriting a prompt
that already has explicit scope, paths and done-criteria manufactures work.

## References

- `${CLAUDE_PLUGIN_ROOT}/skills/prompt-optimize/references/prompt-engineering.md` — full guide
- `${CLAUDE_PLUGIN_ROOT}/skills/prompt-optimize/references/context-engineering.md` — context engineering
- `${CLAUDE_PLUGIN_ROOT}/skills/prompt-optimize/references/patterns.md` — command, agent, skill, output-style formats
