---
description: Update or improve existing command
argument-hint: [command-name]
allowed-tools: Read, Write, Edit, Glob, AskUserQuestion
context: fork
agent: playbook-creator
hooks:
  PreToolUse:
    - matcher: "Edit"
      hooks:
        - type: command
          command: "bash plugins/core/hooks/scripts/dot-claude-commit.sh"
          once: true
---

# Update Command

Update or improve existing command.

**Arguments:** `$ARGUMENTS` — command name or description of what to update

## Steps

### 1. Show Command Locations

```
Commands are stored in:

Local (project):
- ./.claude/commands/

Global (user):
- ~/.claude/commands/

Plugin commands (read-only):
- Check installed plugins
```

### 2. Find Command

If `$ARGUMENTS` provided, search for it.

Otherwise, list available commands:
```bash
ls ./.claude/commands/ 2>/dev/null
ls ~/.claude/commands/ 2>/dev/null
```

Ask: "Which command to update?"

### 3. Read Current Command

Read the command file, show current content to user.

### 4. Ask What to Change

Ask user:
- "What should be changed?"
- "Add steps? Remove steps? Fix something?"
- "Change tools or behavior?"

### 5. Plan Changes

Show diff preview:
```
Changes to {command}:

Current:
  {old text}

Proposed:
  {new text}

Apply?
```

### 6. Apply Changes

Edit the command file with proposed changes.

### 7. Report

```
Updated: {command}
Location: {path}

Test by running the command.
```

## Notes

- Plugin commands should not be edited directly
- Local commands override global with same name
- Use version control to track changes
