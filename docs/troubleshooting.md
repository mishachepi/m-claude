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
