---
name: Record Session
description: This skill should be used when the user says "record session", "start recording", "capture this task", "document this workflow", "I want to create a playbook from this", "записывай", "запиши сессию". Enables session recording mode where Claude documents all actions for future playbook creation.
version: 1.0.0
---

# Record Session

Enable session recording mode to document actions during a complex task. The recording captures what works, filters out mistakes, and produces a learning document that can be converted into a reusable playbook (command, skill, or script).

## Purpose

When working on a new complex task, the user may want to:
1. Solve the task collaboratively with Claude
2. Document the successful approach
3. Later convert this documentation into a reusable playbook

This skill enables "recording mode" — Claude actively documents actions while working, creating a structured learning file.

## When to Use

- Before starting a complex task that might become a reusable workflow
- When exploring a new problem domain and wanting to capture the solution
- When the user explicitly requests recording

## Recording Process

### 1. Initialize Recording

When recording starts:

```
🔴 RECORDING STARTED
Task: {task_name}
Output: .claude/learnings/{task_name_kebab}.md

I will document all significant actions as we work.
Mistakes will be noted but marked for exclusion.
```

Create the learning file with initial metadata.

### 2. Document Actions

As work progresses, mentally track:

**For each significant action:**
- Tool used (Read, Write, Edit, Bash, etc.)
- Purpose (why this action)
- Input/parameters (what was provided)
- Result (what happened)
- Success/Failure status

**What counts as "significant":**
- File operations (read, write, edit)
- Command executions
- API calls
- Decision points
- User clarifications received

**What to skip:**
- Exploratory reads that didn't contribute
- Failed attempts (note them separately)
- Repetitive actions (summarize as pattern)

### 3. Handle Mistakes

When something fails or is wrong:

```
⚠️ MISTAKE NOTED: {what went wrong}
   Cause: {why it failed}
   Skip in final playbook: yes
```

Track mistakes separately — they inform the playbook but aren't part of the workflow.

### 4. Track Decision Points

When a choice is made:

```
📍 DECISION: {what was decided}
   Options considered: {alternatives}
   Chosen because: {reasoning}
```

Decision points often become conditional logic or user prompts in playbooks.

### 5. End Recording

When task is complete:

```
🔴 RECORDING ENDED
Duration: {time}
Actions recorded: {count}
Mistakes filtered: {count}

Learning saved to: .claude/learnings/{filename}.md
```

Generate the final learning document.

## Learning Document Structure

The learning document has two sections:

### Concrete Version
Specific to THIS task — exact files, exact commands, exact values used.

### Abstract Version
Generalized pattern — placeholders, variable names, reusable logic.

See `templates/session-learning.md` for the full template.

## Recording Commands

During recording, the user can say:

| Command | Action |
|---------|--------|
| "mark this as mistake" | Flag last action as mistake |
| "this is important" | Highlight action as key step |
| "add note: {text}" | Add annotation to current step |
| "skip this" | Exclude action from recording |
| "pause recording" | Temporarily stop recording |
| "resume recording" | Continue recording |
| "end recording" | Finalize and save learning |

## Integration with Playbook Creation

After recording ends, offer:

```
Recording complete. Next steps:

**Create command?** → /core:create-command {filename}
**Create skill?** → (for complex multi-step workflows)
**Just keep learning?** → File saved for later review
```

The learning file serves as input for playbook creation commands.

## Best Practices

### During Recording

1. **Narrate intentions** — Explain what each action is meant to accomplish
2. **Note alternatives** — When choosing between approaches, document why
3. **Highlight gotchas** — Issues that weren't obvious, edge cases discovered
4. **Mark reusable patterns** — Sequences that could apply to other tasks

### For Good Learnings

1. **Clear task definition** — What problem is being solved
2. **Prerequisites listed** — What must exist before starting
3. **Steps are atomic** — Each step does one thing
4. **Error handling noted** — What can go wrong and how to handle it
5. **Success criteria defined** — How to know the task is complete

## File Location

Learnings are saved to:
- Local project: `./.claude/learnings/{name}.md`
- Global (if no local): `~/.claude/learnings/{name}.md`

Filename is derived from task name in kebab-case with date prefix:
`YYYY-MM-DD-task-name.md`

## Example Recording Flow

```
User: "record session"
Claude: 🔴 RECORDING STARTED. What task are we working on?

User: "setting up a new Python project with poetry"
Claude: Task: "Setting up Python project with Poetry"
        Output: .claude/learnings/2024-01-15-python-poetry-setup.md

        Let's begin. First, I'll check if poetry is installed...

        [Records: Bash - check poetry version - success]
        [Records: Bash - poetry new project - success]
        [Records: Edit - pyproject.toml - add dependencies]
        ...

User: "end recording"
Claude: 🔴 RECORDING ENDED

        Learning saved with:
        - 12 actions recorded
        - 2 mistakes filtered
        - 3 decision points documented

        **Create command?** → /core:create-command python-poetry-setup
```

## Templates

### Template Location
`templates/session-learning.md` — Full template for learning documents

## Notes

- Recording mode is conversational, not automatic
- Claude narrates significant actions but doesn't interrupt flow
- The learning document is a draft — user reviews before creating playbook
- Both concrete and abstract versions enable flexible reuse
