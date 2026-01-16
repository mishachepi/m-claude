---
description: Create reusable command from description
argument-hint: <what the command should do>
allowed-tools: Read, Write, Edit, Bash(mkdir:*), AskUserQuestion
context: fork
agent: playbook-creator
hooks:
  PreToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "bash plugins/core/hooks/scripts/dot-claude-commit.sh"
          once: true
---

# Create Command

Create a reusable command (playbook) based on description.

**Arguments:** `$ARGUMENTS` — what the command should do

## When to Use

- User knows what command they need
- Converting known workflow into playbook
- User says "create command for X"

## Steps

### 1. Parse Description

Description: `$ARGUMENTS`

If empty, ask: "What should this command do?"

### 2. Clarify Details

Ask questions to understand the command:
- What's the goal?
- What tools/steps are needed?
- Any edge cases to handle?
- Suggested name?

### 3. Draft Command

Create command structure:

```markdown
---
description: {one-line description}
allowed-tools: {tools needed}
---

# {Title}

{Purpose - one sentence}

## Steps

### 1. {First Step}
{Instructions}

### 2. {Second Step}
{Instructions}

## Notes
- {Edge cases, tips}
```

### 4. Review with User

Show draft, ask: "Look good? Any changes?"

Iterate until user approves.

### 5. Save

```bash
mkdir -p ./.claude/commands
```

Write to `./.claude/commands/{name}.md`

### 6. Report

```
Command created: {name}
Location: ./.claude/commands/{name}.md

Use: /{name}
```
