# Context Engineering

> Based on https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

## Core Principles

- Competent context design implies finding the **smallest possible set of high-leverage tokens** that maximize the probability of achieving the desired outcome.
- The optimal level is a balance: **specific enough** to effectively guide behavior, yet **flexible enough** to provide the model with robust heuristics for behavior management.
- Selecting a **minimum viable toolset** for the agent can also lead to more reliable maintenance and context optimization during prolonged interactions.

## Progressive Disclosure

Load context only when triggered — not all at once.

| Level | When Loaded | Examples |
|-------|------------|---------|
| **Hot** | Auto-load always | CLAUDE.md, CLAUDE.local.md |
| **Warm** | Triggered by keywords | docs/*.md via Context MAP triggers |
| **Cold** | Explicit request only | External docs, vault, APIs |

## Context MAP Pattern

```markdown
## Documentation

| File | Triggers | Purpose |
|------|----------|---------|
| `docs/architecture.md` | architecture, design | System design |
| `docs/api.md` | api, endpoints | API reference |
```

When user mentions a trigger word → load the corresponding file.

## Key Guidelines

1. **Smaller is better** — fewer tokens = higher quality responses
2. **Reference don't duplicate** — point to existing docs
3. **Trigger-based loading** — load context when relevant, not upfront
4. **Keep CLAUDE.md lean** — index/router, not encyclopedia
5. **Test context changes** — measure if they actually improve results
