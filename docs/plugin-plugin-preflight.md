# Plugin Preflight Plugin

Pre-push check for any repo that ships Claude Code plugins.

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `plugin-preflight` | Run `scripts/preflight.sh`, fix findings, re-run until green |
| Script | `preflight.sh` | Deterministic four-part check (exit 0 green / 1 red) |

## Checks

1. `claude plugin validate` — marketplace and every plugin
2. `${CLAUDE_PLUGIN_ROOT}/...` paths resolve inside their plugin (`validate` misses these)
3. `name` consistent across dir / `plugin.json` / `marketplace.json`; versions match; no unregistered plugin dir; no stale `<name>@<marketplace>` references
4. Secret scan of added lines in the outgoing diff (+ `gitleaks` if installed)

## Requires

`jq`, `git`; `claude` CLI optional (check 1 skipped without it).
