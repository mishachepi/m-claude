---
name: Docs Update
description: This skill should be used when the user says "update docs", "обнови документацию", "sync docs", "refresh docs", "docs outdated", or after code changes that may affect documentation. Analyzes git diff and updates docs/, CLAUDE.md index, and README.md.
version: 1.0.0
user-invocable: true
allowed-tools: Read, Write, Edit, Bash(git:*), Glob, Grep, AskUserQuestion
---

# Docs Update

Analyze code changes and update project documentation.

## Input

The user may specify a source of changes:
- `staged` or no input — analyze `git diff --staged`
- `last-commit` — analyze `git diff HEAD~1..HEAD`
- `commit <hash>` — analyze specific commit

Default: staged changes, fall back to last commit if nothing staged.

## Flow

### 1. Get Changes

Based on input:

**Staged (default):**
```bash
git diff --staged --stat
git diff --staged
```

**Last commit:**
```bash
git log -1 --oneline
git diff HEAD~1..HEAD --stat
git diff HEAD~1..HEAD
```

**Specific commit:**
```bash
git log -1 --oneline <hash>
git diff <hash>~1..<hash> --stat
git diff <hash>~1..<hash>
```

If no changes found: "No changes to document" — stop.

### 2. Analyze Impact

Categorize changed files:

| Category | Impact on Docs |
|----------|---------------|
| New feature files | May need new doc or section |
| Modified API/interfaces | Update existing docs |
| Config changes | Update setup/config docs |
| Deleted files | Remove stale doc references |
| New docs in `docs/` | Update CLAUDE.md index |
| Test files only | Usually no doc update needed |

### 3. Propose Updates

Present to user:

```
Changes analyzed: {N} files

Documentation updates needed:

1. [CLAUDE.md] Update docs index — new file docs/X.md added
2. [docs/architecture.md] Update — module Y restructured
3. [README.md] Update install section — new dependency added

Apply all / select numbers / skip?
```

Use AskUserQuestion for selection.

### 4. Apply Updates

#### CLAUDE.md Docs Index

New `.md` files in `docs/`:
- Read file, extract purpose from h1/first paragraph
- Generate triggers from filename + content keywords
- Add rows to Documentation table

Removed `.md` files from `docs/`:
- Remove corresponding rows

#### Existing Docs

Code changes affecting documented features:
- Read the doc file and the changed code
- Update doc to reflect new behavior
- Keep existing structure, modify only affected sections

#### README.md

Changes affecting:
- Installation/setup → update relevant section
- Public API → update usage examples
- Project structure → update structure section

### 5. Report

```
Documentation updated:

Modified:
- CLAUDE.md — {what changed}
- docs/X.md — {what changed}
- README.md — {what changed}

No changes needed:
- docs/Y.md — still accurate
```

## Notes

- Show diff preview before applying changes
- Preserve existing doc structure and style
- Only update sections affected by code changes
- If unsure, ask the user
- Never remove documentation without confirmation
