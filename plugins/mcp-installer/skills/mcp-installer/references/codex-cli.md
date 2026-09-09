# Codex CLI — worked example

Verified against `codex mcp add --help` on this machine, and smoke-tested end to end
(add → list → get → remove) with the same server used for the Claude Code example,
`@modelcontextprotocol/server-filesystem` — no credentials required.

## Important difference from Claude Code: no per-project scope

Codex CLI's `mcp` commands write to a single global file, `~/.codex/config.toml` — there is no
`local`/`project` scope flag like `claude mcp add` has. Every server added is available in every
Codex session on the machine. Say this out loud to the user before installing — it's the
project-vs-global tradeoff decision that Claude Code makes explicit with `--scope` and Codex
CLI doesn't.

(Testing this skill itself: redirect with the `CODEX_HOME` env var to a scratch directory so a
dry run never touches the user's real `~/.codex/config.toml`.)

## Command shape

```bash
codex mcp add <NAME> (--url <URL> | -- <COMMAND>...)
```

Key options:

- `--url <URL>` — streamable HTTP MCP server (mutually exclusive with a stdio command)
- `--env <KEY=VALUE>` — environment variables, stdio servers only
- `--bearer-token-env-var <ENV_VAR>` — env var to read a bearer token from, HTTP servers only
- `--oauth-client-id`, `--oauth-client-registration <AUTO|CIMD|DCR>` — OAuth for HTTP servers

## Worked example (stdio, no credentials)

```bash
codex mcp add test-fs -- npx -y @modelcontextprotocol/server-filesystem /tmp
codex mcp list             # confirms `test-fs`, enabled
codex mcp get test-fs      # shows command/args/transport
codex mcp remove test-fs   # clean up
```

## Worked example (HTTP, with bearer token)

```bash
codex mcp add my-server --url https://example.com/mcp --bearer-token-env-var MY_SERVER_TOKEN
```

## Verification commands

```bash
codex mcp list           # table: name, command, args, status, auth
codex mcp get <name>     # full detail for one server
```
