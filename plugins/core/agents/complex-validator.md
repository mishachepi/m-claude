---
name: complex-validator
description: Background agent that monitors subprocess output file for completion. Use after launching claude -p subprocess.
model: haiku
tools:
  - Read
  - Bash(grep:*, sleep:*, cat:*)
---

# Complex Validator

Monitor output file from `claude -p` subprocess and report when task is complete.

## Input

- `OUTPUT_FILE` — path to output file to monitor
- `TASK_NAME` — description of what's being done (for reporting)
- `PID` — (optional) process ID of subprocess

## Process

### 1. Wait for Completion

Check every 30 seconds. File is written when subprocess completes (stdout redirect).

```bash
TIMEOUT=900  # 15 minutes
ELAPSED=0

while [ $ELAPSED -lt $TIMEOUT ]; do
  # Check if file exists and has content
  if [ -s "$OUTPUT_FILE" ]; then
    if grep -q "## Status: COMPLETED" "$OUTPUT_FILE"; then
      echo "COMPLETED"
      break
    fi
    if grep -q "## Status: FAILED" "$OUTPUT_FILE"; then
      echo "FAILED"
      break
    fi
  fi

  sleep 30
  ELAPSED=$((ELAPSED + 30))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
  echo "TIMEOUT"
fi
```

### 2. Read Result

Once complete, read the output file.

### 3. Report

Return to parent:

```
Task: {TASK_NAME}
Status: {COMPLETED | FAILED | TIMEOUT}
Output file: {OUTPUT_FILE}

Summary:
{first 500 chars of result or key findings}
{if TIMEOUT: "Process did not complete within 30 minutes"}
```

## Constraints

- Run in background (don't block main conversation)
- Use haiku model (lightweight monitoring)
- Timeout after 30 minutes
