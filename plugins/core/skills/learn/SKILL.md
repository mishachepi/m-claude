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
- `${CLAUDE_PLUGIN_ROOT}/skills/prompt-optimize/references/prompt-engineering.md` — Claude 4.x prompt engineering principles

## Flow

### 1. Ask What to Remember

**Skip this step when the learning was already supplied** — as arguments to the skill, or stated in
the conversation just before it was invoked. Asking a user to retype what they just wrote is the
fastest way to make a skill annoying. Go straight to Step 2 and classify what you were given.

Otherwise ask the user:

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
| **Gotcha** | Discovered behavior of a tool or system + the workaround ("X fails until you Y") | `./.claude/rules/{name}.md` |
| **Skill** | Complex reusable workflow (needs references, multi-step) | `./.claude/skills/{name}/SKILL.md` |
| **Command** | Simple reusable action (<10 steps) | `./.claude/commands/{name}.md` |
| **Context update** | Project info, architecture decisions, current focus | `./CLAUDE.local.md` |

**Check for an existing home first.** Glob `./.claude/rules/*.md` (and the relevant sibling
directory) and read anything on the same subject. If the learning refines something already
recorded, edit that file instead of creating a second one — two files on one subject means the next
agent reads whichever it finds first. Say which you chose and why.

Present your classification:

```
I'll save this as: {type}
Location: {path}
Content preview:

{draft content}

Look good?
```

Wait for user confirmation before saving.

Headless (`AskUserQuestion` unavailable — `claude -p`, spawned agents, CI): save without waiting,
then report the path and the classification so the choice is visible in the transcript. The user
asked for the learning to be captured; losing it to an unanswerable prompt serves nobody. Overwriting
an existing file still needs a human — headless, write a sibling file and flag the overlap instead.

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

{Instructions following the prompt-engineering reference principles}
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

- Always ask before saving — don't auto-capture (headless: save and report, see Step 2)
- Never silently overwrite: check `./.claude/rules/` for an existing file on the subject first
- Keep rules atomic: one concept per rule
- Everything stays local: `./.claude/` and `./CLAUDE.local.md`
- Rules take effect immediately in new conversations
- For skills/commands, follow the prompt-engineering reference principles: be explicit, add context (WHY), use positive instructions
