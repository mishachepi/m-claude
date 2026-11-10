# Arc Plugin

Companion plugin for [arc-mcp](https://github.com/mishachepi/arc-mcp): MCP server for the Arc browser. macOS only, needs `uv`.

## Components

| Type | Name | Purpose |
|------|------|---------|
| MCP server | `arc` | `list_spaces`, `list_tabs`, `focus_space`, `open_url` |

Write tools stay off. The arc-mcp commit is pinned in `plugins/arc/.claude-plugin/plugin.json` — bumping it is a plugin change, so bump the plugin version too.
