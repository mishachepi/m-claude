---
description: Solve difficult code task with ClaudeCode subprocess (with edits)
argument-hint: <coding task description>
allowed-tools: Bash, Read, AskUserQuestion
context: fork
---

# Code Task Dev

Execute complex coding task in isolated ClaudeCode subprocess with full edit permissions.

**Arguments:** `$ARGUMENTS` — coding task description

## When to Use

- Task requires deep focus on a single code problem
- Need isolation from main conversation context
- Complex refactoring, debugging, or implementation
- Difference from `/complex:task`: focused on code, uses appropriate model

## Steps

### 1. Define Task

Get task description from `$ARGUMENTS` or ask user: "What coding task to solve?"

### 2. Prepare Output File

```bash
mkdir -p ./.claude/task-results
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT_FILE="./.claude/task-results/${TIMESTAMP}-code-dev.md"
```

### 3. Build Prompt

```
CODE TASK: {task description}

INSTRUCTIONS:
1. Analyze the problem and plan solution
2. Implement changes step by step
3. Test if possible
4. Document what was done
5. End response with: ## Status: COMPLETED
   Or if failed: ## Status: FAILED: {reason}
```

### 4. Launch ClaudeCode Subprocess

```bash
claude -p "{prompt}" \
  --permission-mode acceptEdits \
  --output-format text \
  > "$OUTPUT_FILE" 2>&1 &
```

**Flags:**
- `--permission-mode acceptEdits` — auto-accept file edits
- `--output-format text` — plain text output

### 5. Launch Validator (background)

Spawn `complex-validator` agent in background:
- `OUTPUT_FILE` = path to output file
- `TASK_NAME` = coding task description

### 6. Report to User

```
Coding task delegated to subprocess.
Output will be at: {OUTPUT_FILE}

Validator running in background — you'll be notified when complete.
```

When validator reports back:
- Show result summary
- If completed: "Save as command? → /core:create-command"
