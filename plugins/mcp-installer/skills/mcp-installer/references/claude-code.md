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
- `--client-id <clientId>` / `--client-secret` (prompts, or `MCP_CLIENT_SECRET` env) /
  `--callback-port <port>` — pre-registered OAuth client for http/sse servers whose auth server
  has no dynamic client registration (present in 2.1.278; `claude mcp add --help` to confirm)

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

## Worked example (http, OAuth without dynamic client registration)

Remote servers whose auth server does not support RFC 7591 dynamic client registration fail at
first tool call with `Incompatible auth server: does not support dynamic client registration`
(all Google Workspace MCP servers — `gmailmcp` / `drivemcp` / `calendarmcp.googleapis.com` —
do this as of 2026-09-20). Register a client on the provider side first, with the loopback
redirect URI, then pass it in:

```bash
claude mcp add -s user -t http --client-id "$CLIENT_ID" --client-secret --callback-port 8765 \
  gmail https://gmailmcp.googleapis.com/mcp/v1
```

The redirect URI to register for that command is `http://localhost:8765/callback`. Only the
flags are verified here; the Google flow itself is gated on the Workspace Developer Preview
Program (Workspace-domain account, not Gmail), so this example is not smoke-tested end to end.

## Scope choice for this skill

Default to `--scope local` unless the user says otherwise — it's confined to the current project
and easy to remove, and doesn't leak into other projects (`user`) or get checked into git
(`project`) without an explicit decision to share it.

## Verification commands

```bash
claude mcp list        # all configured servers, this scope + higher scopes
claude mcp get <name>  # launch command, scope, connection health
```
