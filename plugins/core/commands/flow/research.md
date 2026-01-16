---
description: Research topic - first check local context, then search web
argument-hint: <topic or question>
allowed-tools: Read, Glob, Grep, WebSearch, WebFetch, AskUserQuestion
context: fork
agent: research-agent
hooks:
  PreToolUse:
    - matcher: "Read|Glob|Grep"
      hooks:
        - type: command
          command: "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/load_context_map.py"
          once: true
---

# Research

Research topic: first study our context, then search web if needed.

**Arguments:** `$ARGUMENTS` — topic or question to research

## Steps

### 1. Parse Topic

Topic: `$ARGUMENTS`

If empty, ask: "What to research?"

### 2. Search Local Context

Check our knowledge first:

1. Search in `./.claude/context/` and `~/.claude/context/`
2. Search in project files (Glob, Grep)
3. Check if relevant MCP available (Context7, etc.)

Report what was found locally.

### 3. Identify Gaps

What's missing? What needs external research?

Ask user: "Found {X} locally. Search web for {gaps}?"

### 4. Web Research

If needed:
- WebSearch for current information
- WebFetch for specific docs/pages
- Always cite sources

### 5. Synthesize

Combine local context + web findings:

```
## Research: {topic}

### From our context:
- {local findings}

### From web:
- {web findings}
- Sources: {links}

### Summary:
{key takeaways}
```

### 6. Offer to Save

If useful pattern discovered:
```
Save to context? → /core:create-context
```
