# System Prompt Patterns

Detailed patterns for system components.

## Command Format

Commands are structured instructions for repeatable tasks in Claude Code slash command format.

```yaml
---
description: Brief description of what this command does
allowed-tools: Bash, Read, Write, Edit
---
# Command Title

## Purpose
One sentence: what this command achieves.

## Pre-conditions
- Condition 1
- Condition 2

## Steps

### 1. First Step
Specific action with instructions.

### 2. Second Step
Specific action with instructions.

### 3. Third Step
Specific action with instructions.

## Post-actions
- What to do after completion

## Notes
- Important notes
- Edge cases
```

**Command principles:**
- Description — brief, clear purpose
- Steps — concrete, executable
- Pre-conditions — what must be true before starting

## Agent Definition Format

```yaml
---
name: research-agent
model: sonnet
description: Research and information gathering
---
# Research Agent

## When to Use
- Need research on a topic
- Gathering info from multiple sources
- Analysis before decision making

## Context to Pass
- Specific question for research
- Scope (research boundaries)
- Output format (what to return)

## Instructions
[Detailed instructions for the agent]
```

**Agent principles:**
- Clear trigger conditions in description
- Defined scope and context requirements
- Specific output expectations

## Output Style Format

```yaml
---
name: Manager Style
description: Response format for Manager Assistant
---
# Identity

You are a Manager AI Assistant. First-person voice.

## Response Format

**For Tasks:**
GOAL: [One sentence]
ACTIONS: [What done]
RESULT: [Outcome]

**Rules:**
- First-person always ("I", "my", "we")
- Concise, no fluff
- End with actionable summary
```

## Skill YAML Frontmatter

```yaml
---
name: Skill Name
description: This skill should be used when the user asks to "trigger phrase 1", "trigger phrase 2", "trigger phrase 3". Third person, specific triggers.
version: 0.1.0
---
```

**Description best practices:**

Good:
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", or mentions hook events (PreToolUse, PostToolUse, Stop).
```

Bad:
```yaml
description: Use this skill when working with hooks.  # Wrong person, vague
description: Provides hook guidance.  # No trigger phrases
```

## Hook Prompt Format

For Stop/PreToolUse/PostToolUse hooks:

```
Before ending, ask: "Save learnings from this session?"

If user declines: return {"decision": "allow"}

If user agrees, analyze session:

1. IDENTIFY what was useful:
   - Context files loaded
   - Commands executed
   - Tools/patterns discovered
   - Missing context that should exist

2. CATEGORIZE improvements:
   - Context updates (preferences, gotchas, patterns)
   - Command improvements (better steps, edge cases)
   - New commands (repetitive workflows)

3. PROPOSE specific changes:
   - Show exact edits to context/*.md
   - Show exact edits to commands

4. APPLY after user approval

5. Return {"decision": "allow"}
```

## CLAUDE.md Router Format

```markdown
# Workflow
> Main playbook of the system

## Workflow Principles
1. **Determinism > improvisation** — use existing solutions, create new ones if needed
2. **Commands first** — Claude Code auto-discovers commands, prefer existing over improvising
3. **Progressive disclosure** — load context only when triggered
4. **Self-improvement** — suggest saving repetitive tasks as commands

## Context MAP
Load when triggered:

| File | Triggers | Purpose |
|------|----------|---------|
| `context/work.md` | work, project, company | Work context |
| `context/tasks/*.md` | current task | Active task context |
```

## Writing Style Summary

### Imperative Form (Body Content)

Verb-first instructions:
```
✓ To create a skill, define the trigger conditions.
✓ Configure the MCP server with authentication.
✓ Validate settings before use.

✗ You should create a skill by defining the trigger conditions.
✗ You need to configure the MCP server.
```

### Third-Person (Descriptions)

```yaml
✓ description: This skill should be used when the user asks to "create X"...
✗ description: Use this skill when you want to create X...
```

### First-Person (Output Styles)

```
✓ "I can delegate to research-agent"
✓ "My system includes..."
✓ "We built this..."

✗ "The assistant can delegate..."
✗ "The system includes..."
```
