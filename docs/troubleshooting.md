# Troubleshooting

## `claude plugin marketplace update m-claude-plugins` fails: "corrupted installLocation"

```
Failed to refresh marketplace 'm-claude-plugins': Marketplace 'm-claude-plugins' has a
corrupted installLocation (...) — expected a path inside .../.claude/plugins/marketplaces.
This can happen after cross-platform path writes or manual edits to known_marketplaces.json.
```

Happens when the marketplace was registered from a different `$HOME` than the one currently
running Claude Code (e.g. a sandboxed agent home, or the same machine's config copied from
another user/host). The fix is exactly what the error says — don't try to hand-edit
`known_marketplaces.json`:

```bash
claude plugin marketplace remove m-claude-plugins
claude plugin marketplace add mishachepi/m-claude
```

Re-adding re-clones from GitHub over HTTPS (works even without a configured SSH key) and
re-registers under the current `$HOME`. Then re-enable/reinstall each plugin — `claude plugin
list` won't always reflect a just-changed marketplace or a plugin enabled in the same session;
check `enabledPlugins` in `settings.json` directly if `claude plugin list` looks stale, or just
restart the session.

## Remote MCP fails: "Incompatible auth server: does not support dynamic client registration"

Claude Code's default OAuth flow for `http`/`sse` servers registers itself as a client on the
fly (RFC 7591). The auth server behind this MCP refuses that, so every tool call fails with the
message above — `claude mcp list` may still show the server, and cached tool names may still
appear in a session. Fix: create an OAuth client with the provider, register the loopback
redirect URI, and re-add the server with `--client-id` / `--client-secret` / `--callback-port`
(see `plugins/mcp-installer/skills/mcp-installer/references/claude-code.md`). Known case:
Google Workspace MCP (`*mcp.googleapis.com`) — additionally gated on the Workspace Developer
Preview Program, which does not accept Gmail addresses.
