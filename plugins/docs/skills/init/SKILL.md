---
name: Docs Init
description: This skill should be used when the user says "init docs", "setup documentation", "create docs structure", "add AGENT.md", "инициализируй документацию", or needs to set up documentation structure in a repository. Creates docs/ folder, CLAUDE.md index with progressive disclosure, and AGENT.md entry point.
version: 1.0.0
user-invocable: true
allowed-tools: Read, Write, Edit, Bash(mkdir:*), Glob, AskUserQuestion
---

# Docs Init

Set up documentation structure in the current repository.

## What It Creates

1. `docs/` folder (if not exists)
2. `## Documentation` section in `CLAUDE.md` — progressive disclosure index
3. `AGENT.md` — entry point for AI agents → CLAUDE.md
4. Documentation section in `README.md`

## Flow

### 1. Check Current State

Read (if they exist):
- `CLAUDE.md`
- `README.md`
- `AGENT.md`

Use Glob to scan `docs/**/*.md` for existing documentation.

### 2. Create docs/ Directory

```bash
mkdir -p docs
```

### 3. Update CLAUDE.md — Add Docs Index

Read `CLAUDE.md`. Find or create a `## Documentation` section.

Add progressive disclosure index:

```markdown
## Documentation

Project documentation lives in `docs/`. Load relevant files when working on related topics.

| File | Triggers | Purpose |
|------|----------|---------|
{for each .md file found in docs/:}
| `docs/{filename}` | {keywords from filename and h1} | {first line or h1 of file} |
```

**Trigger rules:**
- Extract keywords from filename (e.g., `architecture.md` → `architecture, design`)
- Extract keywords from first heading
- Keep 2-3 triggers per file

If no docs exist yet, add empty table:

```markdown
## Documentation

Project documentation lives in `docs/`. Load relevant files when working on related topics.

| File | Triggers | Purpose |
|------|----------|---------|

<!-- Use docs:update skill after adding docs to refresh this index -->
```

### 4. Create AGENT.md

Create `AGENT.md` at project root:

```markdown
<!-- This file provides context for AI agents. See CLAUDE.md for full project instructions. -->

Read CLAUDE.md for project instructions and documentation index.
```

Gives AI agents (Copilot, Cursor, etc.) an entry point → canonical `CLAUDE.md`.

### 5. Update README.md

If `README.md` exists and has no "Documentation" section, ask user:

"Add Documentation section to README.md?" (Yes/No)

If yes, add:

```markdown
## Documentation

See `docs/` for detailed documentation. AI agents: see `CLAUDE.md`.
```

### 6. Report

```
Docs initialized:

Created/Updated:
- docs/               — documentation folder
- CLAUDE.md           — docs index ({N} entries)
- AGENT.md            — AI agent entry point → CLAUDE.md
- README.md           — {added docs section | skipped}

Next: add .md files to docs/, then use docs:update skill
```
