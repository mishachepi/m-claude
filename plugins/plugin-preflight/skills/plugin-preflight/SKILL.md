---
name: plugin-preflight
description: This skill should be used before pushing or opening a PR in any repo that contains Claude Code plugins or a marketplace — "preflight", "pre-push check", "проверь перед пушем", "check plugins before push", "validate marketplace". Runs a deterministic four-part check and drives fixes until it is green.
user-invocable: true
allowed-tools: Bash, Read, Edit, Grep, Glob
---

# Plugin Preflight

Run this before every push of a plugin repo. Each check exists because a human review once had to
find the problem by hand:

| # | Check | Why it is needed |
|---|-------|------------------|
| 1 | `claude plugin validate` on the marketplace and every plugin | schema errors |
| 2 | Every `${CLAUDE_PLUGIN_ROOT}/...` path resolves to a real file inside its plugin | `validate` does **not** catch these; they fail silently at runtime |
| 3 | `name` agrees across dir, `plugin.json`, and `marketplace.json`; versions match; no plugin dir is unregistered; no `<name>@<marketplace>` reference points to a name that does not exist | renames leave stale names and gaps |
| 4 | Secret scan of the outgoing diff (added lines only) | a pushed secret is public and cached even if deleted later |

## Steps

1. From the repo root (the one about to be pushed), run:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/plugin-preflight/scripts/preflight.sh" [repo-path]
   ```

   Exit 0 = green, 1 = at least one FAIL. WARN lines do not fail the run but need a look.
2. Fix every FAIL at its source (edit the file the finding names). Do not silence a check by
   deleting the reference or the rule — if a finding is a genuine false positive, say so to the
   user and leave it reported.
3. A secret finding: remove it from the diff **and** from history if it is already committed
   (amend or rewrite unpushed commits — never force-push shared branches without asking). If the
   secret was ever pushed or shared, tell the user to rotate it.
4. Re-run until exit 0. Report the final output to the user, then proceed with the push only if
   the user asked for one.

## Notes

- The script needs `jq` and `git`; `claude` is optional (check 1 is skipped with a WARN without it).
  `gitleaks` is used for check 4 in addition to the built-in patterns when installed.
- Diff base for check 4: the upstream branch, else `origin/HEAD`/`origin/main`/`main`, else the
  root commit. Uncommitted changes are scanned too.
- Paths containing placeholders (`<name>`, `...`, `*`, `$`) are skipped — they document a
  pattern rather than point at a file.
