# Init Plugin

> Set up a project's documentation structure.

## Philosophy

- **Docs live in `docs/`** — single source of truth
- **CLAUDE.md is the index** — progressive disclosure via triggers
- **AGENT.md is the entry point** — redirects AI agents to CLAUDE.md

## Skills

| Skill | Description |
|-------|-------------|
| `init` | Set up docs structure: `docs/`, CLAUDE.md index, AGENT.md |

## Usage

```
"init docs" or "setup documentation"
```

## Created Structure

```
./
├── CLAUDE.md          # Contains docs index with triggers
├── AGENT.md           # Entry point for AI agents → CLAUDE.md
├── README.md          # Updated with docs reference
└── docs/              # Project documentation
    └── *.md
```
