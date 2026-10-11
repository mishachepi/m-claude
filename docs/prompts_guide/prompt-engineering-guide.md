# Prompt Engineering Guide

> Based on Claude 4.x Best Practices from Anthropic.

## Core Principles

### 1. Be Explicit — Say It Directly

Claude 4.x excels at following precise instructions. Don't rely on it to "fill in the gaps".

```
❌ Bad:
Create an analytics dashboard

✅ Good:
Create an analytics dashboard. Include relevant features
and interactions. Go beyond basics to create a fully-featured
implementation.
```

**Quality modifiers:**
- "Go beyond the basics"
- "Include all relevant features"
- "Be thorough and comprehensive"
- "Create a fully-featured implementation"

### 2. Add Context — Explain WHY

Context and motivation help Claude understand the goal.

```
❌ Bad:
NEVER use ellipses

✅ Good:
Your response will be read aloud by text-to-speech engine,
so never use ellipses since TTS won't know how to pronounce them.
```

Claude is smart — it will generalize the explanation to similar cases.

### 3. Positive Instructions — What TO Do, Not What NOT To Do

```
❌ Bad:
Do not use markdown in your response

✅ Good:
Your response should be composed of smoothly flowing
prose paragraphs.
```

### 4. Use XML Tags — Structure Your Sections

XML tags help organize both the prompt and the response.

```xml
<context>
You are a personal AI manager.
</context>

<instructions>
When given a task:
1. Check if command exists
2. If yes, execute it
3. If no, plan and solve
</instructions>

<output_format>
Respond in this format:
- GOAL: [one sentence]
- ACTIONS: [what done]
- RESULT: [outcome]
</output_format>
```

### 5. Examples Matter — Examples Are Key

Claude 4.x pays close attention to examples. They should reflect the desired behavior.

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

### 6. Match Style — Prompt Style = Response Style

Prompt formatting influences the response:
- Prompt with markdown → response with markdown
- Prompt in prose → response in prose
- Prompt with bullets → response with bullets

---

## Patterns

## Anti-Patterns

### Avoid These

1. **Over-engineering prompts**
   - No need for "CRITICAL", "MUST", "IMPORTANT" everywhere
   - Claude 4.x follows instructions anyway

2. **Negative instructions**
   - "Don't do X" → "Do Y instead"

3. **Vague modifiers**
   - "be good" → "include X, Y, Z features"
   - "be helpful" → specific actions

4. **Redundant sections**
   - Each instruction once
   - Don't repeat across sections

5. **Missing context**
   - Always explain WHY, not just WHAT

---

## Claude 4.x Specific Tips

### Tool Usage

Claude 4.x can be conservative. For action-first behavior:

```xml
<default_to_action>
Implement changes rather than only suggesting them.
If intent is unclear, infer the most useful action
and proceed.
</default_to_action>
```

### Parallel Tool Calls

Claude 4.x is great at parallelization. Reinforce it:

```xml
<use_parallel_tool_calls>
If multiple tools needed with no dependencies,
call them all in parallel. Maximize efficiency.
</use_parallel_tool_calls>
```

### Avoid Over-Engineering

Claude can create unnecessary files and abstractions:

```xml
<keep_it_simple>
Only make changes directly requested.
Don't add features beyond what was asked.
Don't create helpers for one-time operations.
Minimum complexity for current task.
</keep_it_simple>
```

### Code Exploration

Claude can make assumptions without reading code:

```xml
<investigate_first>
ALWAYS read relevant files before proposing edits.
Never speculate about code not inspected.
</investigate_first>
```

---

## Template: Complete Prompt Structure

```xml
<!-- Identity & Role -->
<identity>
[Who is this agent, what is their role]
</identity>

<!-- Context & Background -->
<context>
[Relevant information for this task/session]
</context>

<!-- Core Instructions -->
<instructions>
[Step-by-step what to do]
</instructions>

<!-- Decision Logic -->
<decision_flow>
[When to do what, decision tree]
</decision_flow>

<!-- Output Format -->
<output_format>
[How to structure responses]
</output_format>

<!-- Examples -->
<examples>
[2-3 concrete examples of correct behavior]
</examples>

<!-- Constraints -->
<constraints>
[Limits, what NOT to do (use positive framing)]
</constraints>
```

---

## Checklist: Before Shipping a Prompt

- [ ] Explicit instructions (no ambiguity)
- [ ] Context explains WHY
- [ ] Positive framing (do X, not "don't Y")
- [ ] XML tags for structure
- [ ] Examples match desired behavior
- [ ] No redundant sections
- [ ] Tested with real use cases

---

## Sources

- [Claude 4 Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
