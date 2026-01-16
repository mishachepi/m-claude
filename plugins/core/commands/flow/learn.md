---
description: Capture session learnings manually - save proposals to learnings file
allowed-tools: Read, Write, Edit, Bash(mkdir:*)
---

# Capture Learnings

Analyze current session and save proposals to `~/.claude/learnings/YYYY-MM-DD.md`.

## When to Use

- Mid-session when you want to capture something important
- After completing a significant task
- Periodic reflection on patterns discovered

## Steps

### 1. Analyze Session

Review what happened:
- **What was accomplished?** — main tasks completed
- **Context used/missing** — what context was loaded, what should exist
- **Commands used/needed** — existing commands used, new ones needed
- **Patterns discovered** — reusable approaches

### 2. Prepare Directory

```bash
mkdir -p ~/.claude/learnings
```

### 3. Check Existing File

Read `~/.claude/learnings/{TODAY}.md` if exists (format: YYYY-MM-DD).

### 4. Append Learnings

Add new entry to the file (append to existing content if file exists):

```markdown
## {HH:MM} - Manual capture

**Task:** {what was done}

### Proposals

**Context gaps:**
- {missing context that should exist}

**Command ideas:**
- {repetitive task} → command `{name}`

**Improvements:**
- {existing command/context} → {fix}
```

Use Edit tool to append, or Write tool if file is new.

### 5. Report

```
Learnings saved to ~/.claude/learnings/{DATE}.md

To implement: /core:evolve
```

## What NOT to Capture

- General knowledge (belongs in docs)
- One-time fixes (not patterns)
- Secrets/credentials (never store)
- Verbose explanations (keep actionable)
