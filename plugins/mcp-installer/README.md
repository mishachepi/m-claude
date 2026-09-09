# MCP Installer Plugin

> Find the MCP server a task needs, confirm it with the user, and install it via whichever
> harness is running — Claude Code, Codex CLI, or another one as it comes up.

## Skills

| Skill | Description |
|-------|-------------|
| `mcp-installer` | Discover a matching MCP server for a stated need, confirm before install, install via the current harness's native command, verify |

## Harness coverage

One worked, verified example per harness lives under `skills/mcp-installer/references/`:

| Harness | Native install command | Status |
|---------|------------------------|--------|
| Claude Code | `claude mcp add` | Worked example verified; smoke-tested end to end (add → list → get → remove) |
| Codex CLI | `codex mcp add` | Worked example verified against `codex mcp add --help` |

Other harnesses (Gemini CLI, Cursor, etc.) get a reference added the same way once someone
actually needs one — this plugin does not pre-build unverified command syntax for harnesses
not present on the machine.

## Design decisions

- **Always confirm before installing.** An MCP server is new credentials and/or new network
  access. This plugin follows m-claude's own Core Belief #5 (safety by default,
  human-in-the-loop) rather than auto-installing a match — see the epic note
  [[mcp-installer plugin discover, install, scaffold companion plugin]] for the open question
  this resolves.
- **No per-MCP auto-scaffolding.** A `plugin.json` + marketplace entry already *is* a companion
  plugin (confirmed working end to end on `m-claude-plugins`) — this skill installs the MCP
  server itself, it does not generate a wrapper plugin around it.
