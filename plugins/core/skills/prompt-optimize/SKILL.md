---
name: Prompt Optimize
description: This skill should be used when the user asks to "optimize CLAUDE.md", "check my prompts", "improve prompt", "prompt engineering", "оптимизируй", "проверь CLAUDE.md", "prompt best practices", "fix my prompt", or needs to write, improve, or audit prompts and CLAUDE.md files.
version: 2.0.0
user-invocable: true
allowed-tools: Read, Edit, Glob, AskUserQuestion
---

# Prompt Optimize

Write effective prompts and optimize CLAUDE.md files following Anthropic best practices.

## Two Modes

### Mode 1: Optimize CLAUDE.md

Triggered by: "optimize", "check CLAUDE.md", "audit prompts"

Analyze CLAUDE.md files and suggest improvements.

#### Scope

- `local` → `./CLAUDE.local.md`
- `global` → `~/.claude/CLAUDE.md`
- `all` or no input → both
- an explicit file path → that file, and only that file (scope keywords are ignored)

#### Checklist

| Rule | Threshold | Why |
|------|-----------|-----|
| File size | < 100 lines | Smaller = faster load, easier maintain |
| Section count | 3-7 | Too few = incomplete, too many = cluttered |
| Line length | < 120 chars | Readability |
| No duplicate sections | unique headers | Avoid confusion |
| Has required sections | Workflow, Principles | Core structure |
| No TODO/FIXME | 0 | Unfinished work |
| No contradicting instructions | 0 | Two rules that cannot both be obeyed make the file unusable |
| No unresolvable vagueness | 0 | "be smart", "handle properly" carry no decision procedure |

#### Analysis Steps

1. **Size** — count lines, warn if > 100
2. **Structure** — count sections, warn if < 3 or > 7
3. **Required sections** — check for Workflow, Principles (global only)
4. **Duplicates** — find duplicate headers
5. **Unfinished** — search TODO, FIXME, XXX
6. **Long lines** — count lines > 120 chars
7. **Contradictions** — read the instructions and pair up any two that cannot both be followed
   (e.g. "always use tabs" vs "never use tabs", "ask before editing" vs "never ask"). Steps 1-6
   are mechanical and a script can do them; this step and step 8 need actual reading, and they
   are the ones that decide whether the file is usable at all. Report each pair with both line
   numbers and say which one to keep — never report a contradiction without a resolution.
8. **Vagueness** — flag instructions that state no observable criterion ("be smart about it",
   "handle errors properly"). For each, propose the concrete rule that was probably meant.

#### Report

```
CLAUDE.md Analysis
==================

{filename}:
Size: {lines} lines {OK | WARNING}
Sections: {count} {OK | WARNING}
Required: {OK | MISSING: list}
Duplicates: {OK | FOUND: list}
Unfinished: {OK | FOUND: count}
Contradictions: {OK | FOUND: "{rule A}" (L{n}) vs "{rule B}" (L{m}) → keep {which}}
Vagueness: {OK | FOUND: "{quote}" (L{n}) → suggest "{concrete rule}"}

Suggestions:
- {suggestion 1}
- {suggestion 2}

Overall: {GOOD | NEEDS ATTENTION}
```

A file that passes every mechanical check but contradicts itself is NOT `GOOD` — contradictions
and vagueness outrank size and formatting in the overall verdict.

#### Fix Offers

- File too large → offer to split
- TODOs found → offer to review
- Missing sections → offer to add
- Contradiction found → offer to delete the losing rule (never keep both)
- Vague instruction → offer to replace it with the concrete rule

### Mode 2: Prompt Engineering Guide

Triggered by: "write a prompt", "improve prompt", "prompt engineering"

Use these principles when writing or reviewing prompts.

#### Core Principles

**1. Be Explicit** — say it directly, no ambiguity
```
Bad:  Create an analytics dashboard
Good: Create an analytics dashboard with filtering, charts, and export. Go beyond basics.
```

**2. Add Context (WHY)** — Claude generalizes from explanations
```
Bad:  NEVER use ellipses
Good: Response will be read by TTS engine, so avoid ellipses since TTS can't pronounce them.
```

**3. Positive Instructions** — say what TO DO
```
Bad:  Do not use markdown
Good: Compose smoothly flowing prose paragraphs.
```

**4. XML Tags** — organize structure
```xml
<context>...</context>
<instructions>...</instructions>
<output_format>...</output_format>
```

**5. Examples** — show desired behavior (Claude 4.x pays close attention)

**6. Style Matching** — prompt format influences response format

#### Claude 4.x Tips

- **Action-first:** "Implement changes rather than only suggesting them"
- **Parallel tools:** "Call independent tools in parallel"
- **Keep simple:** "Only make changes directly requested"
- **Investigate first:** "Read relevant files before proposing edits"

#### Anti-Patterns

1. Over-engineering: no need for "CRITICAL", "MUST" everywhere
2. Negative instructions: "Don't X" → "Do Y instead"
3. Vague modifiers: "be good" → "include X, Y, Z"
4. Redundant sections: each instruction once
5. Missing context: always explain WHY

#### Prompt Template

```xml
<identity>[Role]</identity>
<context>[Background]</context>
<instructions>[Steps]</instructions>
<decision_flow>[When to do what]</decision_flow>
<output_format>[Response structure]</output_format>
<examples>[2-3 correct behavior examples]</examples>
<constraints>[Limits, positive framing]</constraints>
```

#### Checklist

- [ ] Explicit instructions (no ambiguity)
- [ ] Context explains WHY
- [ ] Positive framing (do X, not don't Y)
- [ ] XML tags for structure
- [ ] Examples match desired behavior
- [ ] No redundant sections

## References

- `references/prompt-engineering.md` — full detailed prompt engineering guide
- `references/context-engineering.md` — context engineering principles
- `references/patterns.md` — command, agent, skill, output style formats
