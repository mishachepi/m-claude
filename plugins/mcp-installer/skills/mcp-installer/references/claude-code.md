# Claude Code — worked example

Verified against `claude mcp add --help` on this machine, and smoke-tested end to end
(add → list → get → remove) with a real public MCP server, `@modelcontextprotocol/server-filesystem`
— no credentials required, so it's a safe server to use for a dry run without asking the user for
secrets first.

## Command shape

```bash
claude mcp add [options] <name> <commandOrUrl> [args...]
```

Key options:

- `-t, --transport <transport>` — `stdio` (default), `sse`, or `http`
- `-s, --scope <scope>` — `local` (default, this project only), `user` (all projects on this
  machine), or `project` (checked into `.mcp.json`, shared with anyone who clones the repo)
- `-e, --env <KEY=VALUE...>` — environment variables for stdio servers
- `-H, --header <header...>` — headers for http/sse servers (e.g. bearer tokens)

## Worked example (stdio, no credentials)

```bash
claude mcp add --scope local test-fs -- npx -y @modelcontextprotocol/server-filesystem /tmp
claude mcp list                 # confirms `test-fs` is registered
claude mcp get test-fs          # shows the launch command + scope
claude mcp remove test-fs       # clean up
```

## Worked example (http, with auth header)

```bash
claude mcp add --transport http --header "Authorization: Bearer $TOKEN" my-server https://example.com/mcp
```

## Scope choice for this skill

Default to `--scope local` unless the user says otherwise — it's confined to the current project
and easy to remove, and doesn't leak into other projects (`user`) or get checked into git
(`project`) without an explicit decision to share it.

## Verification commands

```bash
claude mcp list        # all configured servers, this scope + higher scopes
claude mcp get <name>  # launch command, scope, connection health
```
