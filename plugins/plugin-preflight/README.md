# Plugin Preflight Plugin

> Run before pushing any repo that ships Claude Code plugins: catches what `claude plugin validate` misses — broken `${CLAUDE_PLUGIN_ROOT}` paths, stale plugin names, marketplace gaps, secrets in the outgoing diff.

## Skills

| Skill | Description |
|-------|-------------|
| `plugin-preflight` | Run `scripts/preflight.sh` in a plugin repo, fix each finding, re-run until green; only then push |
