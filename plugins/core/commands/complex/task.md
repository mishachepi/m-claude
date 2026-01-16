---
description: Handle complex tasks (4+ steps) via subprocess
argument-hint: <task description>
allowed-tools: Bash, Read, AskUserQuestion
context: fork
---

# Complex Task

Delegate complex task to separate ClaudeCode instance, monitor completion.

**Arguments:** `$ARGUMENTS` — task description

## When to Use

- Task requires 4+ steps
- Task needs deep focus without context pollution
- Examples: "implement feature X", "refactor module Y", "set up CI/CD"

## Steps

### 1. Prepare Task

Task: `$ARGUMENTS`

If empty, ask: "What complex task to solve?"

### 2. Create Output File

```bash
mkdir -p ./.claude/task-results
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT_FILE="./.claude/task-results/${TIMESTAMP}-task.md"
```

### 3. Build Prompt

```
TASK: {task description}

INSTRUCTIONS:
1. Plan the solution first
2. Execute step by step
3. Document what was done in your response
4. End response with exactly: ## Status: COMPLETED
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
- `TASK_NAME` = task description

Agent will monitor and report when subprocess completes.

### 6. Report to User

```
Task delegated to subprocess.
Output will be at: {OUTPUT_FILE}

Validator running in background — you'll be notified when complete.
```

When validator reports back:
- Show status and summary
- If completed: "Save as command? → /core:create-command"
