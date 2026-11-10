# MCP Installer Plugin

Find the MCP server a task needs and install it through the running harness — always after confirmation.

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `mcp-installer` | Discover → confirm → install via native command → verify |

## Flow

```
"we need an MCP for X" → find candidate → confirm with user → claude mcp add / codex mcp add → verify
```

## Harnesses

Verified references in `plugins/mcp-installer/skills/mcp-installer/references/`: Claude Code, Codex CLI.
