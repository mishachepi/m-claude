# TG Report Plugin

> Agents report to Telegram when a turn ends — a short summary always, the full answer attached only when it carries more.

## Components

| Type | Path | Purpose |
|------|------|---------|
| Hook (`Stop`) | `hooks/tg_summary.py` | Transcript → summary → store full answer → deliver |
| Hook config | `hooks/hooks.json` | Registers the `Stop` hook, 30s timeout |
| Script | `scripts/tg_deliver.py` | Single delivery door; chooses the backend |
| Script | `scripts/tg_send.py` | Telegram Bot API transport (outbound only) |
| Tests | `tests/` | 80 tests, incl. the enforced outbound-only invariant |

## Mechanism

1. The `Stop` hook receives the hook payload on stdin and exits immediately on
   `stop_hook_active` (a continuation must not produce a second report).
2. It reads `transcript_path` (JSONL) and takes the **last assistant text block**.
3. The full text is written to `$XDG_STATE_HOME/tg-report/answers/<id>.md` (6-hex id);
   answers older than the retention window are pruned on write.
4. The summary is the text after the trigger emoji (`📨`) when the agent wrote one, otherwise
   the opening lines, capped in both lines and characters.
5. `tg_deliver.deliver()` sends `[<label>] <summary>`, attaching the stored file only above the
   threshold.
6. **Any failure exits 0.** A reporting channel must never break the work it reports on.

## Delivery backends

| Condition | Backend |
|---|---|
| `TG_REPORT_NOTIFY_CMD` set | that command, with the message as its last argument |
| otherwise (default) | Telegram Bot API via `tg_send.py` |
| attachments | always the Bot API — a command cannot portably take a file |

Both live inside `tg_deliver.py`, so routing reports through different
infrastructure means changing one function. The attachment exception is confined
to `_deliver_document()` by a test, so the exception cannot spread.

## Invariants

- **Outbound only.** No `getUpdates`, no webhook — enforced by `tests/test_no_inbound.py`,
  which parses the sources with `ast`, ignores docstrings, and also proves it would catch a
  planted violation. The Bot API gives each update to exactly one caller and keeps no history,
  so a second poller on a shared token steals messages irrecoverably.
- **No secrets in the repo.** Credentials come from the environment or
  `~/.config/tg-report/config.json`.
- **Delivery fits the hook's timeout budget**, asserted against `hooks.json` by a test.
- **The answer store never deletes files it did not write** — filename pattern plus a marker
  file, both required before pruning.

## Out of scope

Who reports, how often, and quiet hours are policy for whatever schedules your agents — not for
a Stop hook that must finish in seconds. Enable it for one agent first.

## Design record

`plugins/tg-report/docs/DESIGN.md` — the rationale behind the three layers, the outbound-only
ban, and the one recorded deviation (attachments cannot use a notify command).
