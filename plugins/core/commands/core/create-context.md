---
description: Create context file through guided interview
argument-hint: [topic]
allowed-tools: Read, Write, Edit, Bash(mkdir:*), AskUserQuestion
context: fork
---

# Create Context

Create context file through interview. Saves to local `./.claude/` if exists, otherwise global `~/.claude/`.

## Steps

### 1. Determine Location

Check if `./.claude/context/` exists (local project context).

- **Local exists:** `CONTEXT_DIR = ./.claude`
- **No local:** `CONTEXT_DIR = ~/.claude`

### 2. Define Topic

Ask: "What context topic?"

Examples: preferences, tech stack, project details

### 3. Define Filename

Suggest: `{kebab-case}.md`

Ask: "Filename? (suggestion: {filename})"

### 4. Interview

```
I'll ask about "{TOPIC}". Answer naturally, say "done" when finished.
```

Questions:
1. "Main purpose of this context?"
2. "Key information to include?"
3. "Any patterns, rules, conventions?"
4. "Anything else?"

### 5. Structure Content

Template:
```markdown
# {Topic}

{Why this context matters}

## Key Facts

| Item | Value |
|------|-------|
| ... | ... |

## Preferences

- Do X because Y
```

Keep under 500 tokens. If larger, ask about splitting.

### 6. Save

```bash
mkdir -p {CONTEXT_DIR}
```

Write to `{CONTEXT_DIR}/context/{FILENAME}.md`

### 7. Update context_map.md

Read `{CONTEXT_DIR}/context_map.md`, add row:
```
| `context/{FILENAME}.md` | {TRIGGERS} | {PURPOSE} |
```

### 8. Report

```
Context saved: {TOPIC}
Location: {CONTEXT_DIR}/context/{FILENAME}.md

{local ? "Project-specific context" : "Global context"}
```
