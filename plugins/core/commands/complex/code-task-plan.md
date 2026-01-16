---
description: Code analysis via subprocess (read-only, no edits)
argument-hint: <code question or analysis task>
allowed-tools: Bash, Read, AskUserQuestion
context: fork
---

# Code Task

Delegate code analysis/solution to separate ClaudeCode instance (read-only, no file edits).

**Arguments:** `$ARGUMENTS` — code question or analysis task

## When to Use

- Need code analysis without changing files
- Complex debugging investigation
- Architecture review or code explanation
- "How would you implement X?"

## Steps

### 1. Prepare Task

Task: `$ARGUMENTS`

If empty, ask: "What code task to analyze?"

### 2. Create Output File

```bash
mkdir -p ./.claude/task-results
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT_FILE="./.claude/task-results/${TIMESTAMP}-code.md"
```

### 3. Build Prompt

```
CODE TASK: {task description}

INSTRUCTIONS:
1. Analyze the codebase as needed (READ ONLY)
2. DO NOT edit any files
3. Provide complete analysis in your response
4. End response with exactly: ## Status: COMPLETED
```

### 4. Launch ClaudeCode Subprocess

```bash
claude -p "{prompt}" \
  --allowed-tools "Read,Glob,Grep,Bash(ls:*,cat:*,find:*)" \
  --permission-mode default \
  --output-format text \
  > "$OUTPUT_FILE" 2>&1 &
```

**Flags:**
- `--allowed-tools` — only read-only tools (no Write/Edit)
- `--permission-mode default` — require confirmation for any action
- `--output-format text` — plain text output

### 5. Launch Validator (background)

Spawn `complex-validator` agent in background:
- `OUTPUT_FILE` = path to output file
- `TASK_NAME` = code task description

### 6. Report to User

```
Code analysis delegated to subprocess.
Output will be at: {OUTPUT_FILE}

Validator running in background — you'll be notified when complete.
```

When validator reports back:
- Show analysis summary from output file
