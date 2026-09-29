# New plugin — scaffold a skill into m-claude

Procedure for a learning classified as **New plugin**: a reusable workflow worth having in *every*
project, not just the one currently open. It becomes a new plugin in the m-claude marketplace
(`github.com/mishachepi/m-claude`), shipped through the same clone/PR path as a framework update.

m-claude rule: **one skill = one plugin** — each installs, enables, and disables independently.
Never bolt a new, unrelated skill onto an existing plugin.

## 0. Is it really a new plugin?

- Only this project needs it → it's a **Skill** (`./.claude/skills/`), not a plugin. Stop here.
- It fixes or extends an *existing* m-claude plugin → it's a **Framework update**. Follow
  `framework-update.md` instead.
- An installed plugin (any marketplace — check `claude plugin list`) already does it → say so,
  don't build a duplicate.

## 1. Clone and branch

Steps 1–2 of `framework-update.md` exactly: anonymous HTTPS clone into `mktemp -d`, then
`git checkout -b learn/new-plugin-<name>`. All paths below are relative to that scratch clone.

`<name>` — kebab-case, names the capability, not the project it came from (`pr-triage`, not
`myapp-pr-triage`). Check `plugins/<name>/` doesn't exist and no marketplace entry already uses it.

## 2. Files

```
plugins/<name>/
├── .claude-plugin/plugin.json
├── README.md
└── skills/<name>/SKILL.md        # + references/ if the skill needs them
```

`plugins/<name>/.claude-plugin/plugin.json`:

```json
{
  "name": "<name>",
  "version": "0.1.0",
  "description": "<one sentence: what it does and when>",
  "author": { "name": "mikhail_chepkin", "url": "https://github.com/mishachepi" },
  "repository": "https://github.com/mishachepi/m-claude",
  "keywords": ["<2-4 keywords>"]
}
```

`skills/<name>/SKILL.md` — same frontmatter and prompt-engineering rules as a local Skill (see
`prompt-engineering.md`): a `description` that says *when to trigger*, explicit steps, the WHY behind
each constraint. Write it for an agent with zero context about the project the learning came from —
strip project paths, names, and credentials. Reference bundled files as
`${CLAUDE_PLUGIN_ROOT}/skills/<name>/references/...`, never a repo-relative or absolute path.

`README.md` — title, one-line summary, a `## Skills` table (copy the shape from
`plugins/mcp-installer/README.md`).

## 3. Register it

- `.claude-plugin/marketplace.json` — append to `plugins[]`: `name`, `description`,
  `version` (same as plugin.json), `author: {"name": "Mikhail Chepkin"}`,
  `source: "./plugins/<name>"`, `category`, `strict: false`.
- `README.md` — a row in the **Plugins** table and a `claude plugin install <name>@m-claude-plugins`
  line in **Quick Start**.
- `CLAUDE.md` — a row in the **Plugins** table.
- `docs/plugin-<name>.md` — component table (copy the shape of an existing `docs/plugin-*.md`),
  plus a row for it in `CLAUDE.md`'s **Documentation** table.

## 4. Validate — must be green before commit

```bash
claude plugin validate plugins/<name>
claude plugin validate .
```

Then check every `${CLAUDE_PLUGIN_ROOT}/...` path in the new files resolves to a real file under
`plugins/<name>/`. A broken path fails silently at runtime, not at validate time.

## 5. Commit, push, PR

Steps 4–6 of `framework-update.md` — `feat(<name>): new plugin — <summary>`, push the branch, open
the PR, report the URL. Same guardrails: never `main`, never merge, push failure → hand off the
scratch clone path and diff.

After the PR merges, the user installs it with
`claude plugin marketplace update m-claude-plugins && claude plugin install <name>@m-claude-plugins`
— include that line in the report.
