---
name: MCP Installer
description: This skill should be used when the user needs a capability that an MCP server would provide — says "install an MCP for X", "find an MCP server that can Y", "add MCP for...", "какой MCP мне нужен для...", "поставь MCP для...", or a task clearly needs external tool/data access no current MCP provides. Searches for a matching MCP server, always confirms with the user before installing (new creds/network access), then installs it via the current harness's native mechanism.
version: 1.0.0
user-invocable: true
allowed-tools: Read, Bash(claude:*), Bash(codex:*), Bash(npm:*), Bash(npx:*), WebSearch, WebFetch, AskUserQuestion, Grep, Glob
---

# MCP Installer

Harness-agnostic: find the MCP server a task needs, confirm before installing (MCP = new
credentials and/or network access), install it with whatever harness is actually running, verify
it registered.

## When NOT to use this

- The need can already be met by an installed MCP or a plugin skill — check `claude mcp list`
  (or the equivalent for the running harness) first. Don't install a duplicate.
- The user is asking to *configure* an already-installed MCP (auth, scope change) — that's normal
  harness usage, not discovery.

## Flow

### 1. Pin down the need

Restate what capability is missing in one sentence ("needs to query a Postgres DB", "needs Slack
read access", "needs to search Brave/web"). If the ask is too vague to search on ("get me some
MCP"), ask one clarifying question — don't guess a server and install it.

### 2. Detect the harness

Check what's actually running/installed, in this order — don't assume:

```bash
command -v claude   # Claude Code
command -v codex     # Codex CLI
command -v gemini    # Gemini CLI
```

If more than one is present and it's not obvious which one the install should target, ask.
Read the matching file in `references/` for the exact native command — do not invent syntax for
a harness whose reference doesn't exist yet in this skill; run `<harness> mcp --help` (or
equivalent) live, verify the flags, and only then propose the command. Add a reference file for it
once verified (see `references/README.md` pattern in the existing two files).

### 3. Search for a matching server

Try in order, stop at the first that yields a credible match:

1. **Official registry** — `modelcontextprotocol/servers` on GitHub (reference servers:
   filesystem, fetch, git, memory, sequential-thinking, etc.) via `WebFetch` on
   `https://github.com/modelcontextprotocol/servers`.
2. **npm** — `npm search @modelcontextprotocol` or a targeted `npm search <keyword> mcp` for
   third-party servers; check download counts and last-publish date as trust signals.
3. **Web search** — `WebSearch` for `"<need>" MCP server` when the above turns up nothing;
   prefer a repo with an actual `package.json`/README showing an MCP server entrypoint over a
   blog post about one.

Present candidates with: package/repo name, what it does, auth/creds it needs (if any), and a
trust signal (official org, maintenance recency, or stars). If nothing credible turns up, say so
— don't install the closest-sounding but unrelated package.

### 4. Confirm before installing — always

Never run the install command without an explicit yes from the user first, even when a single
candidate looks obviously right. An MCP server means new credentials and/or new network access —
this skill follows m-claude's Core Belief #5 (safety by default, human-in-the-loop) rather than
auto-installing a match. Use `AskUserQuestion` (or state the exact command and wait, if
`AskUserQuestion` is unavailable — never silently proceed in a headless context; report the
server as *found but not installed* instead).

State plainly before asking: the exact install command, the scope it will use (project-local vs
user-global), and any credentials it will need supplied.

### 5. Install via the harness's native command

Use the verified command from the matching `references/<harness>.md` file. Do not hand-edit a
harness's config file directly when it has a native `mcp add` — that's what caused the config
drift this skill exists to avoid.

### 6. Verify

After install, confirm registration with the harness's own list/get command (e.g. `claude mcp
list` / `claude mcp get <name>`, or `codex mcp list` / `codex mcp get <name>`). If the server
needs credentials that weren't supplied yet, say so explicitly — "installed but not yet
authenticated" is a different state from "working."

### 7. Report

One paragraph: what was installed, on which harness, at what scope, and the one command to remove
it if the user changes their mind.

## Notes

- This skill does **not** scaffold a companion plugin around the installed MCP. A `plugin.json` +
  marketplace entry is already a companion plugin by itself — building a second layer on top of
  the MCP server would duplicate that.
- `references/` carries one **verified** worked example per harness. A harness with no verified
  reference yet gets its command checked live via `--help` before anything is proposed to the
  user, and a new reference file added once confirmed — not left to memory or the model's guess
  at flag names.
