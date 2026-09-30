# arc

Companion plugin for [arc-mcp](https://github.com/mishachepi/arc-mcp) — MCP server for the Arc browser.

**macOS only** (Arc exists only there). Requires [`uv`](https://docs.astral.sh/uv/): the server runs via
`uvx --from git+https://github.com/mishachepi/arc-mcp arc-mcp`, no clone or venv needed.

## Install

```bash
claude plugin install arc@m-claude-plugins
```

## Tools

Read-only by default: `list_spaces`, `list_tabs`, `focus_space`, `open_url`.

Write tools (`create_space`, `delete_space`, `add_tab`, `delete_tab`) are not enabled by this plugin.
Enable them only on explicit request, as a separate user-scope server — they require
`ARC_MCP_ENABLE_WRITES=1`, Arc Sync off and Arc closed:

```bash
claude mcp add --scope user -e ARC_MCP_ENABLE_WRITES=1 arc-rw -- uvx --from git+https://github.com/mishachepi/arc-mcp arc-mcp
```
