# Update Plugin

Keep documentation in sync with code changes.

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `update` | Update docs from git diff (staged/commit) |

## Flow

```
code changes → git add        → stage
"update docs"                 → analyze diff → update docs
"update docs last-commit"     → analyze last commit
```

## What Gets Updated

- `CLAUDE.md` — docs index with progressive disclosure triggers
- `docs/*.md` — content reflecting code changes
- `README.md` — install, setup, structure sections

## Requires

The `init` plugin's docs structure to already exist.
