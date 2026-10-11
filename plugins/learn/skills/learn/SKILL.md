---
name: Learn
description: This skill should be used when the user says "learn", "запомни", "remember this", "save this learning", "update rules", "add rule", "make this a plugin", "we needed an MCP for this" — or when the agent itself just hit a tool gotcha, had an assumption refuted, or was corrected. Persists the lesson where the next session will actually read it — project `.claude/`, a scion agent's template, an MCP install, or the m-claude framework itself.
version: 1.3.0
user-invocable: true
allowed-tools: Read, Write, Edit, Bash(mkdir:*), Bash(mktemp:*), Bash(git:*), Bash(gh:*), Bash(claude:*), Bash(scion:*), Glob, Skill, AskUserQuestion
---

# Learn

Move a lesson out of the transcript (which dies with the session) into the layer the next session
reads. The whole skill is three questions: is it a lesson, where does it live, write it there.

## 1. Get the lesson

Already stated — as skill arguments or just before invocation → use it, don't ask again.
Otherwise ask once (AskUserQuestion), free form: "What should I capture from this session?"

## 2. Quality gate

- **Its check could have failed.** "Looks like", one truncated run, a command that didn't error but
  silently ignored a flag — not a lesson yet.
- **One case is a case, not a class.** Record it marked `(1 case)`, not as a rule.
- **It names what would refute it.** Can't → it's an opinion.

Fails → don't record, or record explicitly as a hypothesis. Not lessons at all: session
play-by-play (the transcript has it), an unresolved problem (that's a task), a metric (tracked
data), someone else's lesson (its author records it).

## 3. Classify — where it lives

**Scion agent?** If `$SCION_AGENT` is set, your home is ephemeral and `./.claude/` is whatever
directory you sit in — neither survives a respawn. Your memory is your **template**: follow
`${CLAUDE_PLUGIN_ROOT}/references/scion-agent.md` for the Rule / Gotcha / Context rows below.
The MCP, Framework and New-plugin rows work the same for agents and humans.

| Type | Signal | Destination |
|---|---|---|
| **Rule / Gotcha** | "always/never X"; "X fails until you Y" | `./.claude/rules/<name>.md` — one rule per file |
| **Context** | project facts, decisions, current focus | `./CLAUDE.local.md` |
| **Skill** | multi-step workflow, this project only | `./.claude/skills/<name>/SKILL.md` |
| **Command** | simple action, < 10 steps | `./.claude/commands/<name>.md` |
| **MCP need** | stalled because a tool/data source was missing ("scraped X by hand") | installed MCP server — §4 |
| **New plugin** | a workflow every project should have, no plugin covers it | new `plugins/<name>/` in m-claude, via PR |
| **Framework update** | a bug or gap in an installed m-claude plugin itself | PR against `github.com/mishachepi/m-claude` |

Tie-breakers: would it help an unrelated project tomorrow with project specifics stripped? Yes →
New plugin, no → Skill. Missing *capability* (data, API, system) → MCP; missing *procedure* →
Skill/plugin. Unsure → ask: a framework fix written into `./.claude/` is silently lost, a project
preference written into m-claude pollutes every other project.

**Check for an existing home first** — Glob the destination directory, read anything on the same
subject; refine that file instead of creating a second one, and say which you chose.

## 4. Confirm, then write

Interactive: show type, path and the draft content; wait for yes. Headless (`claude -p`, spawned
agents, CI): write without waiting, then report path + type in the final output. Overwriting an
existing file always needs a human — headless, write a sibling and flag the overlap.

- **Rule / Context / Skill / Command** — write the file. Skills and commands get frontmatter
  (`name`/`description` = when to trigger, `allowed-tools`) and follow
  `${CLAUDE_PLUGIN_ROOT}/references/prompt-engineering.md`: explicit steps, the WHY behind each
  constraint.
- **MCP need** — hand off to `mcp-installer:mcp-installer` (Skill tool) with the need in one
  sentence; not installed → run its flow inline: search, present candidates, native `mcp add`,
  verify with `mcp list`/`get`. **Its own confirmation, always** — approving a lesson is not
  approving new credentials or network access; headless → report *found, not installed* with the
  exact command. Afterwards one line in `./CLAUDE.local.md` (what, scope, why) unless installed at
  user scope.
- **New plugin** — `${CLAUDE_PLUGIN_ROOT}/references/new-plugin.md`.
- **Framework update** — `${CLAUDE_PLUGIN_ROOT}/references/framework-update.md`.

Both m-claude paths: fresh clone, new branch, PR — never `main`, never merge; the PR review is the
human checkpoint for a tool every project uses. Any plugin change bumps its `version`.

## 5. Report

`Saved: <path> (<type>)` — then "Anything else from this session?" Repeat from §1 or stop.
