---
description: Initialize context system (local or global)
argument-hint: [local | global]
allowed-tools: Bash, Write, Read, Edit, AskUserQuestion
---

# Init

Initialize personal context system.

## Arguments

- `local` — install in `./.claude/` (current project)
- `global` — install in `~/.claude/` (system-wide)
- No argument — ask user

## Step 0: Determine Installation Scope

**If argument provided:** Use it directly.

**If no argument:** Use AskUserQuestion:
- Question: "Where to initialize?"
- Header: "Scope"
- Options:
  1. `Global (~/.claude/)` (Recommended) — Works everywhere
  2. `Local (./.claude/)` — Current project only

Store choice as `SCOPE` (local/global).

## Step 1: Set Paths

```
If SCOPE == "global":
    CONTEXT_DIR = ~/.claude
    CLAUDE_MD = ~/.claude/CLAUDE.md

If SCOPE == "local":
    CONTEXT_DIR = ./.claude
    CLAUDE_MD = ./.claude/CLAUDE.md
```

## Step 2: Create Structure

```bash
mkdir -p "$CONTEXT_DIR/context"
mkdir -p "$CONTEXT_DIR/learnings"
```

If global, also create:
```bash
mkdir -p ~/.claude/commands
mkdir -p ~/.claude/skills
```

## Step 3: Create context_map.md

Write to `$CONTEXT_DIR/context_map.md`:

```markdown
# Context MAP

Load context files when triggered:

| File | Triggers | Purpose |
|------|----------|---------|
```

## Step 4: Update CLAUDE.md

Check if `$CLAUDE_MD` exists:
- If not exists: create it
- If exists: read first, then append (don't overwrite)

Read template from `plugins/core/templates/CLAUDE.md` and append to `$CLAUDE_MD` (only sections not already present).

## Step 5: Collect Initial Context

Use AskUserQuestion to gather context:

**Question 1:** "What's your primary tech stack?"
- Header: "Tech Stack"
- Options: TypeScript/Node, Python, Go, Rust, Other

**Question 2:** "Brief description about yourself (role, preferences)?"
- Header: "About You"
- Free text (user selects "Other")

**If local installation, also ask:**

**Question 3:** "Brief project description?"
- Header: "Project"
- Free text (user selects "Other")

**Question 4:** "Anything else to add to context?"
- Header: "Extra"
- Options: No, that's all; Yes, I want to add more
- If yes — prompt for additional info

## Step 6: Create Context Files

Based on answers, create context files in `$CONTEXT_DIR/context/`:

**about-me.md** (if provided):
```markdown
# About Me

{user's description}

## Tech Stack
- Primary: {tech stack}
```

**project.md** (if local and provided):
```markdown
# Project

{project description}
```

Update context_map.md with created files:
```markdown
| `context/about-me.md` | me, preferences, stack | Personal info |
| `context/project.md` | project, code | Project info |
```

## Step 7: Report

```
Initialized at: $CONTEXT_DIR

Structure:
$CONTEXT_DIR/
├── context_map.md   # Context triggers
├── context/         # Context files
└── learnings/       # Session learnings

CLAUDE.md updated with Workflow.

Next steps:
- Use /core:create-context to add more context
- Use /flow:learn to capture learnings
```
