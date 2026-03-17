# Docs Plugin

Keep documentation in sync with code changes.

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `init` | Create docs/, CLAUDE.md index, AGENT.md |
| Skill | `update` | Update docs from git diff (staged/commit) |

## Flow

```
"init docs"                   → set up structure
code changes → git add        → stage
"update docs"                 → analyze diff → update docs
"update docs last-commit"     → analyze last commit
```

## What Gets Updated

- `CLAUDE.md` — docs index with progressive disclosure triggers
- `docs/*.md` — content reflecting code changes
- `README.md` — install, setup, structure sections
- `AGENT.md` — entry point for AI agents → CLAUDE.md
