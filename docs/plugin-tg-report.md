# TG Report Plugin

> Agents report to Telegram when a turn ends — a short summary always, the full answer attached only when it carries more.

## Components

| Type | Path | Purpose |
|------|------|---------|
| Hook (`Stop`) | `hooks/tg_summary.py` | Transcript → summary → store full answer → deliver |
| Hook config | `hooks/hooks.json` | Registers the `Stop` hook, 30s timeout |
| Script | `scripts/tg_deliver.py` | Single delivery door; chooses the backend |
| Script | `scripts/tg_send.py` | Direct Bot API transport (outbound only) |
| Tests | `tests/` | 57 tests, incl. the enforced outbound-only invariant |

## Mechanism

1. The `Stop` hook receives the hook payload on stdin and exits immediately on
   `stop_hook_active` (a continuation must not produce a second report).
2. It reads `transcript_path` (JSONL) and takes the **last assistant text block**.
3. The full text is written to `$XDG_STATE_HOME/tg-report/answers/<id>.md` (6-hex id);
   answers older than the retention window are pruned on write.
4. The summary is the text after the trigger emoji (`📨`) when the agent wrote one, otherwise
   the opening lines, capped in both lines and characters.
5. `tg_deliver.deliver()` sends `[<slug>] <summary>`, attaching the stored file only above the
   threshold.
6. **Any failure exits 0.** A reporting channel must never break the work it reports on.

## Delivery backends

| Condition | Backend |
|---|---|
| `log-bot-notify` on `PATH` | the mesh lever — same bot, same token |
| lever absent (non-LSA host) | direct Bot API via `tg_send.py`, same credentials |
| attachments (any host) | direct Bot API — the lever is text-only |

All of it lives inside `tg_deliver.py` so that the SC1 backend flip to
`scion message --channel telegram` touches exactly one function.

## Invariants

- **Outbound only.** No `getUpdates`, no webhook — enforced by `tests/test_no_inbound.py`,
  which parses the sources with `ast`, ignores docstrings, and also proves it would catch a
  planted violation.
- **No bot of its own.** The plugin never provisions a token; on a mesh host it does not even
  need one.
- **No secrets in the repo.** Credentials come from the environment or
  `~/.config/tg-report/config.json`.

## Out of scope

Tiering (who reports, how often, quiet hours) and fleet distribution belong to the mesh's
`flow` and `orchestrator` lanes, not to this plugin. Ship it to one pilot agent first.

## Design record

`plugins/tg-report/docs/DESIGN.md` — recon findings, the Area ruling of 2026-07-29, and the one
recorded deviation (attachments have no lever).
