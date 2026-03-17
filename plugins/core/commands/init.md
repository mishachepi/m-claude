---
description: 
argument-hint: [local | global]
allowed-tools: Bash, Write, Read, Edit, AskUserQuestion
---

# Init

Initialize CLAUDE.md with workflow and principles.

## Arguments

- `local` — create `./CLAUDE.local.md` in current project
- `global` — create `~/.claude/CLAUDE.md` (system-wide)
- No argument — ask user

## Step 1: Determine Scope

**If argument provided:** Use it directly.

**If no argument:** Use AskUserQuestion:
- Question: "Where to initialize?"
- Header: "Scope"
- Options:
  1. `Local (./CLAUDE.local.md)` (Recommended) — Project-specific
  2. `Global (~/.claude/)` — Works everywhere

Store choice as `SCOPE`.

---

## GLOBAL Installation

### Step G1: Create Structure

```bash
mkdir -p ~/.claude/commands
mkdir -p ~/.claude/skills
```

### Step G2: Create ~/.claude/CLAUDE.md

Check if `~/.claude/CLAUDE.md` exists:
- **Not exists:** Copy from `plugins/core/templates/CLAUDE.md`
- **Exists:** Ask user: "CLAUDE.md exists. Overwrite or skip?"

### Step G3: Report

```
Global initialized: ~/.claude/

Structure:
~/.claude/
├── CLAUDE.md        # Workflow + Principles
├── commands/        # Custom commands
└── skills/          # Custom skills

Next: /init local in your projects
```

---

## LOCAL Installation

### Step L1: Create Structure

```bash
mkdir -p ./.claude/rules
mkdir -p ./.claude/commands
mkdir -p ./.claude/skills
```

### Step L2: Collect Project Info

Use AskUserQuestion:

**Question 1:** "Project name?"
- Header: "Name"
- Free text

**Question 2:** "Primary tech stack?"
- Header: "Stack"
- Options: TypeScript/Node, Python, Go, Rust, Other

**Question 3:** "Brief project description?"
- Header: "About"
- Free text

### Step L3: Create ./CLAUDE.local.md

Check if `./CLAUDE.local.md` exists:
- **Not exists:** Copy from `plugins/core/templates/CLAUDE.local.md`
- **Exists:** Ask user: "CLAUDE.local.md exists. Overwrite or skip?"

Replace placeholders:
- `{PROJECT_NAME}` → project name
- `{TECH_STACK}` → tech stack
- `{PROJECT_DESCRIPTION}` → description

### Step L4: Report

```
Local initialized: ./CLAUDE.local.md

Structure:
./
├── CLAUDE.local.md  # Project config
└── .claude/
    ├── rules/       # Behavioral rules
    ├── commands/    # Custom commands
    └── skills/      # Custom skills

Priority: local > global
Use /learn to capture session learnings
```
