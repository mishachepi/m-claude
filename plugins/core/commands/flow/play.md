---
description: Find playbook or solve task with user
argument-hint: <task description>
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, AskUserQuestion, Skill
---

# Play

Find existing playbook or solve task together with user.

**Arguments:** `$ARGUMENTS` — task description

## Steps

### 1. Parse Task

Task: `$ARGUMENTS`

If empty, ask: "What task?"

### 2. Find Playbook

Search for matching command, skill, or agent:
- Check available skills and commands
- Think: does anything fit this task?

### 3. Execute or Solve

**Playbook found:**
- If command/skill: execute via `playbook-executor` agent or directly
- Report result, done.

**Not found:** Solve with user step by step:
1. Clarify requirements
2. Break into steps
3. Execute each step
4. Track: tools used, what worked, edge cases

### 4. Reflection (after solving)

After completing task (especially if no playbook was found), offer:

```
**Context gap?** → /core:create-context
**Repeatable?** → /core:create-command
**Improve existing?** → /core:update-command
**Capture learnings?** → /flow:learn
```

If user wants to save as command → delegate to `playbook-creator` agent.
