---
name: Learn
description: This skill should be used when the user says "learn", "запомни", "save this learning", "remember this", "let's capture what we learned", "update rules", "add rule". Captures session learnings as rules, skills, or CLAUDE.local.md updates.
version: 1.0.0
user-invocable: true
allowed-tools: Read, Write, Edit, Bash(mkdir:*), Glob, AskUserQuestion
---

# Learn

Capture learnings from the current session and persist them as actionable improvements: rules, skills, or CLAUDE.local.md updates.

All artifacts are created **locally** in the current project (`./.claude/`). Never write to global `~/.claude/`.

## References

When writing prompts for skills or commands, follow best practices from:
- `docs/prompt-engineering-guide.md` — Claude 4.x prompt engineering principles

## Flow

### 1. Ask What to Remember

Ask the user:

```
What would you like to remember from this session?

Examples:
- A rule/preference (→ .claude/rules/)
- A reusable workflow (→ .claude/skills/ or .claude/commands/)
- Project context update (→ CLAUDE.local.md)

What should I capture?
```

Use AskUserQuestion. Let the user describe in free form.

### 2. Classify and Confirm

Based on the user's response, classify:

| Type | When | Where |
|------|------|-------|
| **Rule** | Behavioral preference, coding convention, "always/never do X" | `./.claude/rules/{name}.md` |
| **Skill** | Complex reusable workflow (needs references, multi-step) | `./.claude/skills/{name}/SKILL.md` |
| **Command** | Simple reusable action (<10 steps) | `./.claude/commands/{name}.md` |
| **Context update** | Project info, architecture decisions, current focus | `./CLAUDE.local.md` |

Present your classification:

```
I'll save this as: {type}
Location: {path}
Content preview:

{draft content}

Look good?
```

Wait for user confirmation before saving.

### 3. Save

#### For Rules:

Create `./.claude/rules/{descriptive-name}.md`:

```markdown
{Rule content — clear, actionable instruction}
```

Keep rules concise. One rule per file. Name should describe the rule.

#### For Skills:

Create `./.claude/skills/{name}/SKILL.md` with proper frontmatter:

```markdown
---
name: {Name}
description: {When to trigger this skill}
user-invocable: true
allowed-tools: {tools needed}
---

# {Title}

{Instructions following prompt-engineering-guide.md principles}
```

#### For Commands:

Create `./.claude/commands/{name}.md`:

```markdown
---
description: {one-line description}
argument-hint: {expected arguments}
allowed-tools: {tools needed}
---

# {Title}

{Steps}
```

#### For Context Updates:

Read existing `./CLAUDE.local.md` (create if missing), then append or update the relevant section.

### 4. Offer to Continue

```
Saved: {path}

Anything else to capture from this session?
```

If yes, repeat from step 1. If no, done.

## Notes

- Always ask before saving — don't auto-capture
- Keep rules atomic: one concept per rule
- Everything stays local: `./.claude/` and `./CLAUDE.local.md`
- Rules take effect immediately in new conversations
- For skills/commands, follow prompt-engineering-guide.md principles: be explicit, add context (WHY), use positive instructions
