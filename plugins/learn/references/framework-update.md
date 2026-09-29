# Framework update — clone / edit / PR

Procedure for a learning classified as **Framework update**: the fix belongs in the m-claude
plugin framework itself (`github.com/mishachepi/m-claude`), not in the project currently open.
Deterministic, not improvised — follow these steps in order.

## Guardrails (never break these)

- **Never write the change into the current project.** It belongs in the m-claude repo, always.
- **Never commit or push to `main`.** Always a fresh clone, always a new branch, always a PR.
- **Never merge the PR.** Opening it is the deliverable; a human reviews and merges.
- **Never force-push, never touch history that isn't yours** (the scratch clone's own new branch).
- **Never silently drop the change** if push fails — hand off the local diff instead (Step 5).

## Steps

### 1. Scratch clone

```bash
tmp=$(mktemp -d)
git clone --quiet https://github.com/mishachepi/m-claude.git "$tmp"
```

Plain anonymous HTTPS clone, not `gh repo clone` — verified 2026-08-26 that `gh repo clone` refuses
outright (`exit 4`, "please run gh auth login") when `gh` has no stored auth, even though the repo
is public and a raw `git clone` over HTTPS needs no credentials at all for read access. Cloning
never needs auth here; only the push in Step 4 might.

### 2. Branch

```bash
cd "$tmp"
git checkout -b "learn/<short-slug>"
```

`<short-slug>` — a few kebab-case words naming the fix (e.g. `learn/fix-init-template-path`). Keep
it short; it's a branch name, not the commit message.

### 3. Apply the change

Edit the file(s) inside `$tmp` — same as any other edit, just rooted at the scratch clone instead of
the current project. Re-read this reference's own home (`${CLAUDE_PLUGIN_ROOT}` inside `$tmp`) if the
change touches the `learn` skill itself — you're editing a live copy of the tool you're currently
running, not the one currently loaded in this session.

### 4. Commit and push

```bash
git add -A
git commit -m "<type>(<plugin>): <what changed, imperative mood>

<why — the learning that prompted this, one or two lines>"
git push -u origin "learn/<short-slug>"
```

Match the existing commit style in `git log` (`type(scope): summary`, body explains why).

### 5. If the push fails

No SSH key and no `gh auth login` on this machine is a real, common case — don't treat it as the
flow failing. Stop here and report plainly:

```
Framework fix ready but not pushed: $tmp, branch learn/<short-slug>
This machine has no git push credentials for github.com/mishachepi/m-claude.
Diff:
<git diff main...HEAD, or a summary if it's long>
```

Leave `$tmp` in place — don't clean it up when the push didn't happen; the diff would be lost.

### 6. Open the PR

```bash
gh pr create --repo mishachepi/m-claude --base main --head "learn/<short-slug>" \
  --title "<same summary as the commit>" \
  --body "<why, what changed, how it was verified — e.g. claude plugin validate output>"
```

Report the PR URL to the user. Done — nothing after this step. No merge, no further pushes to the
branch unless the user asks for a follow-up fix, which is a new pass through this same procedure.
