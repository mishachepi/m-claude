---
name: brainshtorm
description: Deep brainstorming and spec creation through structured interview. Use when user has an idea but needs to think it through, says "brainstorm", "let's think about", "spec out", or "help me plan".
version: 1.0.0
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, AskUserQuestion
---

# Brainstorm

Transform a vague idea into a detailed specification through structured interview.

## When to Use

- User has an idea but hasn't thought through details
- Need to explore tradeoffs and alternatives
- Creating a spec/PRD for a feature or project
- Planning before implementation

## Requires a live human

This skill is an interview: its entire value is the user's answers. It depends on
`AskUserQuestion`, which does not exist in headless runs (`claude -p`, spawned agents,
CI) and may be denied by permission settings.

**Before Step 1, check whether `AskUserQuestion` is available.** If it is not:

1. Stop. Do not run the interview.
2. Do not invent answers on the user's behalf — a spec built from guessed answers looks
   authoritative and is worthless, which is worse than no spec.
3. Report: "brainshtorm needs an interactive session; `AskUserQuestion` is unavailable here."
4. Offer the honest alternative: draft an **assumptions document** instead — the questions
   that would have been asked, each with a proposed default and the risk of getting it
   wrong — clearly labelled as unvalidated, for a human to answer later.

## Workflow

```
Brainstorm Session:
- [ ] Step 1: Capture the idea
- [ ] Step 2: Deep interview (5-10 rounds)
- [ ] Step 3: Synthesize findings
- [ ] Step 4: Write spec document
- [ ] Step 5: Review with user
```

## Step 1: Capture the Idea

Start by understanding the core idea:

```
"Tell me about your idea in 1-2 sentences. What problem does it solve?"
```

Store:
- `IDEA_NAME` — short name for the idea
- `PROBLEM` — what problem it solves
- `INITIAL_DESCRIPTION` — user's first description

## Step 2: Deep Interview

Use AskUserQuestion tool for structured exploration. Interview in rounds, covering:

### Round 1: Problem Space
- Who has this problem?
- How painful is it? (1-10)
- How do they solve it today?
- What's wrong with current solutions?

### Round 2: Solution Vision
- What does success look like?
- What's the core interaction?
- What's the minimum viable version?
- What's the dream version?

### Round 3: Technical Approach
- What technologies would you use?
- What are the main components?
- What data do you need?
- What integrations are required?

### Round 4: Edge Cases & Risks
- What could go wrong?
- What are the hardest parts?
- What assumptions are we making?
- What would make this fail?

### Round 5: Scope & Priorities
- What's in v1 vs later?
- What's a must-have vs nice-to-have?
- What would you cut if you had to ship in half the time?
- What's the one thing that must work perfectly?

### Interview Technique

**Ask non-obvious questions:**
- "What happens when X fails?"
- "How would a power user abuse this?"
- "What's the embarrassing version of this?"
- "If you couldn't use [technology], what would you do?"

**Go deep on vague answers:**
- "Can you give me an example?"
- "What specifically would that look like?"
- "Walk me through the user flow"

**Challenge assumptions:**
- "Why that approach instead of X?"
- "What if we did the opposite?"
- "Is that a requirement or a preference?"

## Step 3: Synthesize Findings

After interview, compile:

```
## Summary
- Problem: {PROBLEM}
- Solution: {SOLUTION_SUMMARY}
- Target User: {TARGET_USER}
- Core Value: {WHY_THIS_MATTERS}

## Key Decisions Made
1. {decision 1}
2. {decision 2}
...

## Open Questions
- {unresolved question 1}
- {unresolved question 2}

## Risks Identified
- {risk 1}
- {risk 2}
```

## Step 4: Write Spec Document

Create spec using template:

```markdown
# {IDEA_NAME} Spec

## Overview
{One paragraph summary}

## Problem
{Problem description from interview}

## Solution
{Solution description}

## User Stories
- As a {user}, I want to {action} so that {benefit}
- ...

## Technical Approach
{Architecture decisions, tech stack, components}

## Scope
### v1 (MVP)
- {feature 1}
- {feature 2}

### Future
- {feature 3}
- {feature 4}

## Open Questions
- {question 1}
- {question 2}

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| {risk} | {mitigation} |

## Next Steps
1. {step 1}
2. {step 2}
```

**Save location:** Ask user where to save, suggest:
- `./SPEC.md` — current directory
- `./docs/specs/{name}.md` — alongside project documentation
- User's preferred location

## Step 5: Review with User

Present spec and ask:

```
"Here's the spec based on our brainstorm.

Key points:
- {summary point 1}
- {summary point 2}
- {summary point 3}

Does this capture your vision? What would you change?"
```

Iterate if needed, then confirm:

```
Brainstorm complete: {IDEA_NAME}

Spec saved to: {path}
Duration: {time}
Interview rounds: {count}

Next steps:
1. Review spec
2. Share with stakeholders
3. Start implementation
```

## Tips for Good Brainstorms

1. **Don't rush** — better to ask 10 good questions than 30 shallow ones
2. **Write down everything** — capture quotes, not just summaries
3. **Challenge politely** — "That's interesting, but what about X?"
4. **Look for contradictions** — they reveal unclear thinking
5. **End with priorities** — what matters most?

## Notes

- Minimum 5 interview rounds for a real brainstorm
- Save intermediate notes if session is long
- User can say "skip" to move past a topic
- User can say "go deeper" to explore more
