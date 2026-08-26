# Prompt Engineering Guide

> Based on Claude 4.x Best Practices from Anthropic.

## Core Principles

### 1. Be Explicit — Say It Directly

Claude 4.x excels at following precise instructions. Don't rely on it to "fill in the gaps".

```
Bad:  Create an analytics dashboard
Good: Create an analytics dashboard. Include relevant features
      and interactions. Go beyond basics to create a fully-featured implementation.
```

**Quality modifiers:**
- "Go beyond the basics"
- "Include all relevant features"
- "Be thorough and comprehensive"
- "Create a fully-featured implementation"

### 2. Add Context (Explain WHY)

Context and motivation help Claude understand the goal. Claude generalizes from explanations.

```
Bad:  NEVER use ellipses
Good: Your response will be read aloud by text-to-speech engine,
      so never use ellipses since TTS won't know how to pronounce them.
```

### 3. Positive Instructions

Tell what TO DO, not what NOT to do.

```
Bad:  Do not use markdown in your response
Good: Your response should be composed of smoothly flowing prose paragraphs.
```

### 4. Use XML Tags

XML tags organize prompt and response structure.

```xml
<context>You are a personal AI manager.</context>
<instructions>
When given a task:
1. Check if command exists
2. If yes, execute it
3. If no, plan and solve
</instructions>
<output_format>
- GOAL: [one sentence]
- ACTIONS: [what done]
- RESULT: [outcome]
</output_format>
```

### 5. Examples Matter

Claude 4.x pays close attention to examples. They must reflect desired behavior.

```xml
<examples>
<example>
User: "commit my changes"
Action: Find git-commit command → Execute it
</example>
<example>
User: "research best practices for X"
Action: No command → Delegate to research-agent
</example>
</examples>
```

### 6. Style Matching

Prompt formatting influences response:
- Prompt with markdown → response with markdown
- Prose prompt → prose response
- Bulleted prompt → bulleted response

## Quick Reference

| Principle | Do | Don't |
|-----------|-----|-------|
| Explicit | "Include X, Y, Z features" | "Be good" |
| Context | "Because TTS can't handle..." | "NEVER do X" |
| Positive | "Use prose paragraphs" | "Don't use markdown" |
| Structure | Use XML tags | Flat text blocks |
| Examples | Show desired behavior | Vague descriptions |

## Claude 4.x Specific Tips

### Action-First Behavior

```xml
<default_to_action>
Implement changes rather than only suggesting them.
If intent is unclear, infer the most useful action and proceed.
</default_to_action>
```

### Parallel Tool Calls

```xml
<use_parallel_tool_calls>
If multiple tools needed with no dependencies,
call them all in parallel. Maximize efficiency.
</use_parallel_tool_calls>
```

### Avoid Over-Engineering

```xml
<keep_it_simple>
Only make changes directly requested.
Don't add features beyond what was asked.
Don't create helpers for one-time operations.
</keep_it_simple>
```

### Investigate First

```xml
<investigate_first>
ALWAYS read relevant files before proposing edits.
Never speculate about code not inspected.
</investigate_first>
```

## Anti-Patterns

1. **Over-engineering prompts** — no need for "CRITICAL", "MUST", "IMPORTANT" everywhere
2. **Negative instructions** — "Don't do X" → "Do Y instead"
3. **Vague modifiers** — "be good" → "include X, Y, Z features"
4. **Redundant sections** — each instruction once
5. **Missing context** — always explain WHY, not just WHAT

## Prompt Template

```xml
<identity>[Who is this agent, what's their role]</identity>
<context>[Relevant information for this task/session]</context>
<instructions>[Step-by-step what to do]</instructions>
<decision_flow>[When to do what, decision tree]</decision_flow>
<output_format>[How to structure responses]</output_format>
<examples>[2-3 concrete examples of correct behavior]</examples>
<constraints>[Limits, what NOT to do (positive framing)]</constraints>
```

## Checklist Before Shipping

- [ ] Explicit instructions (no ambiguity)
- [ ] Context explains WHY
- [ ] Positive framing (do X, not don't Y)
- [ ] XML tags for structure
- [ ] Examples match desired behavior
- [ ] No redundant sections
- [ ] Tested with real use cases
