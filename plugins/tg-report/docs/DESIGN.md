# tg-report — design

Why the plugin is shaped the way it is. Usage lives in `README.md`; this file is
for whoever changes the code.

## Problem

An agent finishes work while you are away from the terminal. The result stays
where nobody is looking. Notification channels that already exist tend to be
either too loud (every event) or reserved for emergencies — there is usually no
tier for "a routine piece of work is done, here is the outcome."

That tier is what this plugin provides, and its whole design follows from two
constraints: it runs **inside the agent's turn**, and it talks to a **shared bot
token**.

## Three layers, one door

```
hooks/tg_summary.py     producer   transcript → summary + stored answer
scripts/tg_deliver.py   dispatcher chooses a backend, owns the timeout budget
scripts/tg_send.py      transport  Bot API calls, nothing else
```

Everything the plugin sends passes through `tg_deliver.deliver()`. No other
module may talk to a transport, and `tests/test_no_inbound.py` checks that claim
by walking the AST. The reason is replaceability: people route notifications
through wildly different infrastructure, and a plugin whose transport is smeared
across three files cannot be adapted without a rewrite. One door means one edit.

`TG_REPORT_NOTIFY_CMD` is the seam. Set it and text delivery becomes "run this
command with the message as its last argument" — a Telegram wrapper, a queue
publisher, a desktop notifier, anything that exits 0. Unset, the Bot API is used
directly.

### The one deviation: attachments

An external command takes text; there is no portable way to hand it a file. So
`_deliver_document()` always uses the Bot API, even when a notify command is
configured. This is the single place where the transport choice is not free, and
a test pins it to that one call site — otherwise the exception would spread and
the seam would stop meaning anything.

## Outbound only, and why it is a test rather than a promise

The Telegram Bot API delivers each update to exactly one `getUpdates` caller and
keeps no history. Two pollers on the same token is not a race that resolves
itself — it is silent, unrecoverable message theft, and the loser cannot even
detect what it missed.

A plugin that grows one innocent inbound feature (`/full <id>`, "reply to
re-run") becomes that second poller on whatever token you gave it. Since the
danger is invisible at the call site, the ban is enforced structurally:
`tests/test_no_inbound.py` parses every source file and fails on any Bot API
method that reads updates. Prose *about* the ban stays legal; a call does not.

The consequence is deliberate: the full answer is **pushed** as a document when
it is long, because pulling it on demand would need an inbound route.

## Safety properties worth keeping

These exist because each one was, at some point, a real defect:

**The store never deletes what it did not write.** `TG_REPORT_STATE_DIR` is
operator input, and pruning by "every `*.md` older than N days" beneath it turns
one wrong export into silent data loss. Pruning now requires both a filename
matching `<6 hex>.md` and this plugin's marker file in the directory. A directory
the plugin did not create is never touched.

**Delivery fits inside the hook's budget.** The hook runs inside the turn: time
spent here is time the session hangs. `hooks.json` declares a timeout;
`TEXT_TIMEOUT + DOCUMENT_TIMEOUT` must fit inside it with room for interpreter
start-up, and `tests/test_timeout_budget.py` asserts it against the actual JSON
rather than trusting comments to stay in sync. Without this, a slow network
stalls every turn and then gets killed mid-send — the worst of both.

**Errors never carry the token.** The token lives in the request URL, and several
`urllib` failures quote that URL back (`ValueError: unknown url type: …`).
Every error string is scrubbed before it can reach stderr.

**The hook cannot fail a turn.** Every path in `main()` returns 0. A reporting
channel that can break the work it reports on is worse than no channel.

## Summary extraction

The agent decides what you see: text after the trigger marker (`📨` by default)
becomes the summary. Without a marker, the opening lines are used, capped by
`TG_REPORT_SUMMARY_LINES` and `TG_REPORT_SUMMARY_CHARS`.

Attachment is not merely a length check: the full answer must exceed the
threshold **and** be more than twice the summary. A long answer that the agent
already summarised well should not arrive twice.

## Layout note

The plugin keeps its code in `hooks/` and `scripts/`, with tests beside them in
`tests/`. Delivery logic sits in `scripts/` rather than `hooks/` because it is
importable by anything, and the hook is only its first caller.

## Growth path

Deliberately not built: message threading per agent, quiet hours, retry queues,
delivery receipts. Each is reasonable, and each becomes necessary only once many
agents report at once — at which point the right home for that policy is a
scheduler above this plugin, not inside a Stop hook that must finish in seconds.
