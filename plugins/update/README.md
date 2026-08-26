# Update Plugin

> Keep documentation in sync with code changes.

## Skills

| Skill | Description |
|-------|-------------|
| `update` | Update docs based on git changes (staged/commit) |

## Usage

```
"update docs"              # staged changes (default)
"update docs last-commit"  # last commit
```

## What Gets Updated

| File | When |
|------|------|
| `CLAUDE.md` | New/removed docs in `docs/`, structure changes |
| `docs/*.md` | Code changes affecting documented features |
| `README.md` | Install, setup, API, or structure changes |

## Requires

The [`init`](../init/) plugin's docs structure to already exist.
