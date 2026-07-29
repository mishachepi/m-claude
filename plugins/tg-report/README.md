# TG Report Plugin

> Agents report to Telegram when they finish a turn — a short summary always, the full answer attached only when it carries more.

## Components

| Type | Name | Purpose |
|------|------|---------|
| Hook | `Stop` → `hooks/tg_summary.py` | Read the transcript, summarise the final answer, store it, deliver |
| Script | `scripts/tg_deliver.py` | The single delivery door — picks a backend, isolates the transport |
| Script | `scripts/tg_send.py` | Direct Bot API transport (outbound only) |

## Flow

```
agent finishes turn
   → Stop hook reads transcript JSONL → last assistant text
   → full answer stored at $XDG_STATE_HOME/tg-report/answers/<id>.md
   → summary = text after 📨, else the opening lines
   → tg_deliver.deliver()  ──▶  log-bot-notify   (mesh host)
                            └─▶  Bot API direct  (host without the lever)
   → full answer attached as a document ONLY above the threshold
```

## Transport contract

**This plugin does not own a Telegram transport.** The LSA mesh has a ratified one-bot layer
(epic `SC1 - Telegram Layer Convergence`), and everything here rides it:

- **Inside the mesh, delivery goes through `log-bot-notify`** — same bot, same token. The plugin
  never provisions a bot of its own.
- **The direct Bot API path is a portable fallback only**, for hosts where the lever is not on
  `PATH`. It reuses the same credentials; it is never a "faster default".
- **All transport lives inside `tg_deliver.py`.** SC1 carries a standing obligation to flip its
  backend to native `scion message --channel telegram`. Code that calls the Bot API from
  anywhere else would not survive that flip. When the flip lands, one function changes here and
  nothing else does.
- **`page` is not used.** `page` is the CRITICAL tier with a mesh-contract threshold; routine
  task-completion reports through it would be exactly the page inflation `flow` has to suppress.

### Interim debt: the attachment path

**Temporary, not architecture.** The mesh lever sends text only (`notify.send(text)`), so
document attachments go direct to the Bot API even on a mesh host — contained inside
`tg_deliver._deliver_document()`, on the same token, still outbound-only, and kept there by
`tests/test_no_inbound.py::test_attachment_path_does_not_spread`. It retires with the SC1
sunset flip, together with the text path.

**When flipping:** `scion message --attach` accepts paths under `/workspace` or
`/scion-volumes` and **silently drops absolute paths outside those roots**. The answer store
lives outside both, so a naive flip yields "sent successfully, no file". Relocate the store or
stage a copy first. Details in `docs/DESIGN.md`.

### Outbound-only, forever

The plugin contains no `getUpdates` and no webhook code, and `tests/test_no_inbound.py` enforces
it rather than the README promising it. A second inbound consumer on the mesh bot silently
steals updates from the capture daemon — it happened once and those messages were unrecoverable,
because the Bot API keeps no history.

This is why there is no `/full <id>` command: pulling an answer needs an inbound route, and the
mesh has exactly one, already routed elsewhere. The full answer is **pushed** as a document
instead. If a pull style is ever wanted, it belongs to `flow` (serving it from the store on the
existing capture route), not to this plugin.

## Configuration

Nothing is required on a mesh host — the lever already knows the bot.

| Variable | Default | Purpose |
|---|---|---|
| `TG_REPORT_TRIGGER` | `📨` | Text after this emoji becomes the summary |
| `TG_REPORT_SUMMARY_LINES` | `4` | Fallback summary size when no trigger is present |
| `TG_REPORT_SUMMARY_CHARS` | `600` | Hard cap on the summary |
| `TG_REPORT_ATTACH_THRESHOLD` | `1500` | Attach the full answer above this length; `0` disables |
| `TG_REPORT_RETENTION_DAYS` | `14` | Prune stored answers older than this |
| `TG_REPORT_STATE_DIR` | `$XDG_STATE_HOME/tg-report` | Where answers are stored |
| `TG_REPORT_FORCE_DIRECT` | unset | `1` bypasses the lever (debugging only) |

Fallback credentials, used only when the lever is absent: `TG_REPORT_BOT_TOKEN` /
`TG_REPORT_CHAT_ID`, or `LOG_BOT_TOKEN` / `TELEGRAM_USER_ID`, or
`~/.config/tg-report/config.json` (`{"bot_token": …, "chat_id": …}`, mode `0600`).
**No secret belongs in this repository**, and no code path here writes one.

## Not in this plugin's lane

- **Who reports, how often, quiet hours** — tiering is `flow`'s engine (SC1 put threshold and
  anti-inflation there explicitly). Enabling this fleet-wide without it is spam: 20+ agents ×
  every Stop.
- **Distribution across the fleet** — `orchestrator` / harness-config.
- **The Telegram layer itself** — `area-scion` / SC1.

## Requirements

| Tool | Required for |
|---|---|
| Python 3 (stdlib only) | everything |
| `log-bot-notify` | delivery on an LSA mesh host (otherwise the direct fallback runs) |
| pytest | tests |

## Tests

```bash
pytest plugins/tg-report/tests/ -q
```
