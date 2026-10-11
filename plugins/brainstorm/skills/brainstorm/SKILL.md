---
name: Brainstorm
description: This skill should be used when the user has an idea but needs to think it through — says "brainstorm", "let's think about", "spec out", "help me plan", "давай подумаем". Turns a vague idea into a written spec through a structured interview.
version: 1.0.1
user-invocable: true
allowed-tools: Read, Write, Edit, AskUserQuestion
---

# Brainstorm

Turn a vague idea into a spec through a structured interview. For: an idea with unexamined
details, tradeoffs to explore, a spec/PRD before implementation.

## Requires a live human

The interview is the whole value, and it runs on `AskUserQuestion` — absent in headless runs
(`claude -p`, spawned agents, CI) and possibly denied by permissions. **Check before Step 1.**
Unavailable → stop; don't invent answers (a spec built on guessed answers looks authoritative and
is worthless). Report "brainstorm needs an interactive session; `AskUserQuestion` is unavailable
here" and offer an **assumptions document** instead: the questions you'd have asked, each with a
proposed default and the risk if it's wrong, labelled unvalidated.

## 1. Capture the idea

"Tell me about your idea in 1–2 sentences. What problem does it solve?" Keep a short name, the
problem, and the user's first description verbatim.

## 2. Interview — at least 5 rounds, via AskUserQuestion

| Round | Cover |
|---|---|
| Problem | who has it, how painful (1–10), how it's solved today, what's wrong with that |
| Vision | what success looks like, the core interaction, minimum vs dream version |
| Technical | stack, main components, data, integrations |
| Risks | what breaks, hardest parts, assumptions, what would make it fail |
| Scope | v1 vs later, must-have vs nice-to-have, what to cut at half the time, the one thing that must work |

Technique — this is where the value is:
- **Non-obvious questions:** "What happens when X fails?", "How would a power user abuse this?",
  "What's the embarrassing version?", "Without [technology], what would you do?"
- **Go deep on vague answers:** "Give me an example", "Walk me through the user flow".
- **Challenge assumptions:** "Why that instead of X?", "Requirement or preference?"
- **Watch for contradictions** between answers — they mark unclear thinking; surface them.
- Capture quotes, not just summaries. Ten good questions beat thirty shallow ones.
- The user can say "skip" (move on) or "go deeper" (more on this topic). Long session → save
  interim notes.

## 3. Write the spec

Read `${CLAUDE_PLUGIN_ROOT}/skills/brainstorm/TEMPLATE.md` and fill it from the interview — that
file is the structure; don't improvise or trim sections that feel covered. Sections the interview
didn't reach stay, marked `{unknown — not covered in interview}`, so the gap is visible.

Ask where to save; suggest `./SPEC.md` or `./docs/specs/<name>.md`.

## 4. Review

Present the spec with its 3 key points: "Does this capture your vision? What would you change?"
Iterate, then report: `Brainstorm complete: <name> — spec saved to <path>, <n> interview rounds.`
