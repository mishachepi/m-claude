---
description: Review and implement proposals from learnings files
allowed-tools: Read, Write, Edit, Bash(mkdir:*, mv:*), Glob, AskUserQuestion
context: fork
agent: playbook-creator
---

# Evolve

Review accumulated learnings and implement approved proposals.

## When to Use

- Dedicated evolution session (not during active work)
- After multiple sessions accumulated learnings
- Periodic improvement

## Steps

### 1. Find Learnings

Use Glob to find files: `~/.claude/learnings/*.md` (exclude archive/).

If no files found: "No learnings to process. Run /flow:learn first."

### 2. Read and Summarize

Read each learnings file using Read tool. Extract and group proposals:
- **Context gaps** — missing context files
- **Command ideas** — new commands to create
- **Improvements** — fixes to existing files

### 3. Present Proposals

Show user consolidated list:

```
Evolution Proposals

From {N} session(s):

**Context to create:**
1. context/{name}.md — {purpose}

**Commands to create:**
1. {name} — {purpose}

**Improvements:**
1. {file} — {change}

Which proposals to implement? (all / numbers like "1,3" / skip)
```

Use AskUserQuestion for selection.

### 4. Implement Approved

For each approved proposal:

**Context gaps:**
- Create `~/.claude/context/{name}.md` using Write tool
- Read `~/.claude/context_map.md`, then Edit to add row to table

**Command ideas:**
- Create `~/.claude/commands/{name}.md` using Write tool

**Improvements:**
- Read target file, then Edit as proposed

### 5. Archive Processed Files

```bash
mkdir -p ~/.claude/learnings/archive
```

Move each processed file individually:
```bash
mv ~/.claude/learnings/2025-01-15.md ~/.claude/learnings/archive/
```

Do NOT use wildcards — move only the files you actually processed.

### 6. Report

```
Evolution complete

Created:
- context/{name}.md
- ~/.claude/commands/{name}.md

Improved:
- {file}: {change}

Archived: {N} learnings files
```

## Notes

- Run in dedicated session, not during active work
- User approves each change before implementation
- Only archive files that were actually processed
