# tg-report

> Your Claude Code agent tells you in Telegram when it finishes — a short summary
> always, the full answer attached when it carries materially more.

Long-running agents finish while you are somewhere else. The result sits in a
terminal you are not looking at. This plugin reverses the direction: when a turn
ends, the agent reports to your phone.

## Install

```bash
claude plugin add ./plugins/tg-report
```

Then give it a bot and a chat:

1. Create a bot with [@BotFather](https://t.me/botfather) and copy the token.
2. Get your chat id — message your bot, then open
   `https://api.telegram.org/bot<TOKEN>/getUpdates` in a browser and read
   `message.chat.id`.
3. Provide both, either as environment variables:

   ```bash
   export TG_REPORT_BOT_TOKEN="123456:ABC…"
   export TG_REPORT_CHAT_ID="987654321"
   ```

   or in `~/.config/tg-report/config.json` (keep it `chmod 600`):

   ```json
   {"bot_token": "123456:ABC…", "chat_id": "987654321"}
   ```

No secret belongs in this repository, and no code path here writes one.

## How it works

```
agent finishes a turn
   → Stop hook reads the transcript → last assistant message
   → full answer stored at $XDG_STATE_HOME/tg-report/answers/<id>.md
   → summary = the text after 📨, otherwise the opening lines
   → delivered via the notify command if configured, else the Bot API
   → full answer attached as a document only above the size threshold
```

Write `📨` in your answer and everything after it becomes the summary — that is
how an agent chooses what you see on your phone. Without it, the plugin falls
back to the first few lines.

## Components

| Type | Name | Purpose |
|------|------|---------|
| Hook | `Stop` → `hooks/tg_summary.py` | Read the transcript, summarise, store, deliver |
| Script | `scripts/tg_deliver.py` | The single delivery door — picks a backend |
| Script | `scripts/tg_send.py` | Telegram Bot API transport (outbound only) |

## Configuration

Everything is optional except the credentials.

| Variable | Default | Purpose |
|---|---|---|
| `TG_REPORT_BOT_TOKEN` | — | Bot token (or use the config file) |
| `TG_REPORT_CHAT_ID` | — | Chat to report to (or use the config file) |
| `TG_REPORT_CONFIG` | `~/.config/tg-report/config.json` | Alternative config file path |
| `TG_REPORT_LABEL` | working directory name | Who is reporting — prefixed to every message |
| `TG_REPORT_TRIGGER` | `📨` | Text after this marker becomes the summary |
| `TG_REPORT_SUMMARY_LINES` | `4` | Fallback summary size when no marker is present |
| `TG_REPORT_SUMMARY_CHARS` | `600` | Hard cap on the summary |
| `TG_REPORT_ATTACH_THRESHOLD` | `1500` | Attach the full answer above this length; `0` disables |
| `TG_REPORT_RETENTION_DAYS` | `14` | Prune stored answers older than this |
| `TG_REPORT_STATE_DIR` | `$XDG_STATE_HOME/tg-report` | Where answers are stored |
| `TG_REPORT_NOTIFY_CMD` | unset | Deliver text through this command instead of the Bot API |
| `TG_REPORT_FORCE_DIRECT` | unset | `1` bypasses the notify command (debugging) |

Running several agents at once? Set `TG_REPORT_LABEL` per agent — otherwise a
phone full of reports is unreadable.

### Routing through your own notifier

If you already run something that pushes to Telegram, point the plugin at it and
it will not touch the Bot API for text at all:

```bash
export TG_REPORT_NOTIFY_CMD="my-notifier --channel reports"
```

The message text is appended as the last argument; a non-zero exit is treated as
a delivery failure. Attachments still go through the Bot API, because there is no
portable way to hand a file to an arbitrary command — so credentials are still
worth configuring if you want them.

## Design properties

**Outbound only, forever.** The plugin contains no `getUpdates` and no webhook
code, and `tests/test_no_inbound.py` enforces that by parsing the AST rather than
by this README promising it. The reason is not neatness: the Bot API hands each
update to exactly one caller and keeps no history, so a second poller on the same
token silently steals messages from whatever else is reading them. This is also
why there is no `/full <id>` command — pulling an answer back needs an inbound
route. The full answer is pushed as a document instead.

**The store never deletes what it did not write.** `TG_REPORT_STATE_DIR` is
operator input, so pruning requires *both* that the filename matches a stored
answer (`<6 hex>.md`) *and* that the directory carries this plugin's marker file.
Point the variable at your notes folder and the plugin refuses to prune rather
than eating them. Answers are written `0600` inside a `0700` directory — a stored
answer is a verbatim transcript of whatever the agent was working on.

**Delivery cannot outlast the hook.** The Stop hook runs inside the agent's turn,
so the delivery budget (`TEXT_TIMEOUT + DOCUMENT_TIMEOUT`) is asserted to fit
inside the `timeout` declared in `hooks.json`, with margin for interpreter
start-up. Otherwise a slow Telegram would stall every turn and then be killed
mid-send.

**Errors never carry the token.** The token sits in the request URL and some
`urllib` failures quote that URL back; every error string is scrubbed before it
can reach stderr.

**A report never breaks the work it reports on.** Every failure path in the hook
exits 0.

## Before you enable it everywhere

One agent reporting is a convenience; twenty agents reporting on every Stop is
spam you will mute within a day — and a muted channel reports nothing. Decide who
reports and how often before rolling it out widely.

## Requirements

| Tool | Required for |
|---|---|
| Python 3 (standard library only) | everything |
| pytest | tests |

## Tests

```bash
pytest plugins/tg-report/tests/ -q
```
