---
task: "{TASK_NAME}"
date: "{YYYY-MM-DD}"
duration: "{DURATION}"
status: "recorded"
tags: []
---

# Learning: {TASK_NAME}

> {One sentence description of what was accomplished}

## Overview

**Goal:** {What we wanted to achieve}

**Outcome:** {What we actually achieved}

**Complexity:** {simple | medium | complex}

**Reusability:** {high | medium | low} — {why}

---

## Prerequisites

Before starting this task:

- [ ] {Prerequisite 1}
- [ ] {Prerequisite 2}
- [ ] {Required tool/access}

---

## Concrete Version

> Specific to THIS task — exact files, commands, values.

### Steps

#### Step 1: {Step Name}

**Action:** {Tool} — {What was done}

```{language}
{Exact command or code used}
```

**Result:** {What happened}

**Files affected:** `{path/to/file}`

---

#### Step 2: {Step Name}

**Action:** {Tool} — {What was done}

```{language}
{Exact command or code used}
```

**Result:** {What happened}

---

{Continue for all steps...}

### Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `{path}` | created/modified | {why} |

---

## Abstract Version

> Generalized pattern — placeholders, reusable logic.

### Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{PROJECT_NAME}` | {description} | {example} |
| `{TARGET_PATH}` | {description} | {example} |

### Steps (Generalized)

#### Step 1: {Generic Step Name}

**Purpose:** {Why this step is needed}

**Action:** {Tool}

```{language}
{Command/code with {PLACEHOLDERS}}
```

**Expected result:** {What should happen}

**Error handling:** {What to do if it fails}

---

#### Step 2: {Generic Step Name}

**Purpose:** {Why this step is needed}

**Action:** {Tool}

```{language}
{Command/code with {PLACEHOLDERS}}
```

**Conditional:** {If applicable — when to do this step}

---

{Continue for all generalized steps...}

### Flow Diagram

```
{TRIGGER}
    │
    ▼
[Step 1] ──► {outcome}
    │
    ▼
[Step 2] ──► {outcome}
    │
    ▼
{RESULT}
```

---

## Decision Points

Choices made during execution that could vary:

### Decision 1: {What was decided}

**Options considered:**
1. {Option A} — {pros/cons}
2. {Option B} — {pros/cons}

**Chosen:** {Option X}

**Reasoning:** {Why this choice}

**For playbook:** {How to handle in automated version — ask user? default? conditional?}

---

## Mistakes & Learnings

Issues encountered and filtered from the workflow:

### Mistake 1: {What went wrong}

**What happened:** {Description}

**Cause:** {Root cause}

**Solution:** {How it was fixed}

**Prevention:** {How to avoid in playbook}

---

## Edge Cases

Scenarios to consider for a robust playbook:

- [ ] {Edge case 1} — {how to handle}
- [ ] {Edge case 2} — {how to handle}

---

## Success Criteria

The task is complete when:

- [ ] {Criterion 1}
- [ ] {Criterion 2}
- [ ] {Verification step}

---

## Playbook Recommendation

Based on this learning:

**Recommended format:** {command | skill | script}

**Reasoning:** {Why this format fits best}

**Suggested name:** `{name}`

**Triggers:** {When should this playbook be used}

---

## Raw Notes

{Any additional notes, observations, or context captured during recording}
