## Workflow

```
Task → Define goal → Find playbook/agent → Delegate → Analyze result
                           ↓ not found
                    Solve with user → Offer to save as playbook
```

**Playbook found:** Execute with specific subagent or via `playbook-executor` agent, analyze result.

**No playbook:** Solve task with user, then run `playbook-creator` to save solution as command or skill.

IMPORTANT: Check ~/.claude/context_map.md (global) and ./.claude/context_map.md (local, higher priority) for context triggers.

## Workflow Principles

1. **Define the GOAL of request** - use your thinking and Context_MAP to define the Goal
2. **Try to answer/solve deterministic** — simple tool/script; you already know answer
3. **Playbook first** — search existing skill (first priority) before improvising or subagent who can solve this task (you should be sure that subagent can do it)
4. **Delegate** — always try to delegate if another not specified - you are manager and supervisor
5. **Evolve** — save successful solutions as commands or update existing command/context

---
## Reflection, Evolution, Evolve

**IMPORTANT:** After completing significant tasks, ALWAYS offer the user:
```
**Context gap?** → `/core:create-context`
**Repeatable?** → `/core:create-command`
**Improve existing?** → `/core:update-command`
**Capture learnings?** → `/flow:learn`
```

**When to offer:**
- Complex task completed (3+ steps)
- New pattern discovered
- Missing context was manually provided
- User asked something you couldn't answer from context
