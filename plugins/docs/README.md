# Docs Plugin

> Keep documentation in sync with code changes.

## Philosophy

- **Docs live in `docs/`** — single source of truth
- **CLAUDE.md is the index** — progressive disclosure via triggers
- **AGENT.md is the entry point** — redirects AI agents to CLAUDE.md
- **Code changes → doc updates** — not the other way around

## Skills

| Skill | Description |
|-------|-------------|
| `init` | Set up docs structure: `docs/`, CLAUDE.md index, AGENT.md |
| `update` | Update docs based on git changes (staged/commit) |

## Usage

```
# First time — initialize docs structure
"init docs" or "setup documentation"

# After code changes — update docs
"update docs"              # staged changes (default)
"update docs last-commit"  # last commit
```

## What Gets Updated

| File | When |
|------|------|
| `CLAUDE.md` | New/removed docs in `docs/`, structure changes |
| `docs/*.md` | Code changes affecting documented features |
| `README.md` | Install, setup, API, or structure changes |

## Created Structure

```
./
├── CLAUDE.md          # Contains docs index with triggers
├── AGENT.md           # Entry point for AI agents → CLAUDE.md
├── README.md          # Updated with docs reference
└── docs/              # Project documentation
    └── *.md
```
