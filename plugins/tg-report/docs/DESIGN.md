# tg-report — design

> Status: **transport built and tested, architecture blocked on an Area ruling.**
> Recon (2026-07-29) found that the LSA mesh already has a ratified Telegram
> architecture that this plugin must fit into rather than parallel. See
> §"What recon changed" — it is the most important section in this document.

## Problem

Agents of the mesh finish tasks while the user is away from the terminal. The outcome lands in
a vault note or a tmux pane and the user has to go look for it. We want the opposite direction:
**the agent reports to the user's phone** — short by default, full on demand.

## Original shape

Mirror of `~/dotfiles/claude/hooks/speak-summary.py`, the proven pattern on this machine: a
`Stop` hook reads the session transcript, extracts the final assistant text, and hands it to a
delivery channel. `speak-summary` delivers to TTS; tg-report delivers to Telegram.

```
Claude Code agent finishes turn
        │
        ▼
  Stop hook  tg_summary.py        ← the genuinely new piece
        │  read transcript JSONL → last assistant text
        │  ├── store full text  → ~/.local/state/tg-report/answers/<id>.md
        │  └── build summary
        ▼
  delivery lever                   ← NOT new; see below
        ▼
  Telegram
```

Three layers, deliberately separable — the split is what makes the recon result survivable:

| Layer | Owner after recon |
|---|---|
| **Producer** — transcript → summary + stored full answer | **this plugin.** Nothing else in the mesh does it. |
| **Delivery** — bytes → Telegram | **already exists** (SC1 / log-bot). Do not rebuild. |
| **Retrieval** — user asks for the full answer | **contested** — needs an inbound route that SC1 deliberately does not have. |

## What recon changed (2026-07-29)

The task note said "study the existing scion telegram channel, do not break it". What recon
actually found is stronger than a don't-break warning:

**1. There is a live, ratified, one-bot Telegram layer.**
Epic `SC1 - Telegram Layer Convergence` (owner `area-scion`) states as its goal, verbatim:
*"ОДИН TG-бот/токен … Не строим параллельный транспорт"*. The single live bot is
**@finimch_bot** (`LOG_BOT_TOKEN`, chat `TELEGRAM_USER_ID`, in the `log-bot` package `.env`).
The `telegram` MCP plugin runs on a *different*, **dead** token (bot id `5774910895`, `getMe`
→ 401) and was formally taken out of the capture/notify path.

**2. An outbound lever already exists and is fleet-wide.**
`log-bot-notify` — a one-shot `sendMessage` CLI, explicitly built as the non-conflicting
outbound path ("*Plain sendMessage (NOT long-polling) so it never conflicts with the running
bot*"). On top of it, `page` — the SC1-commissioned agent→user push, already distributed to
every agent in the fleet, with a stable interface and a planned `_dispatch()` backend flip to
`scion message --channel telegram`.

⇒ **`scripts/tg_send.py` as written duplicates `log-bot-notify`.** Building it as *the* mesh
transport would be exactly the "параллельный транспорт" SC1 exists to prevent.

**3. The inbound slot is taken, and its routing is already decided.**
`com.mch.log-bot` (launchd, `KeepAlive=true`) owns the `getUpdates` slot on @finimch_bot and
guards it with a flock — a second poller silently steals updates, which already happened once
(2026-07-02, messages lost for good; the Bot API has no history). SC1 additionally decided
that **all** inbound text takes one route — capture → flow-keeper — with no corr-id and no
pending table.

⇒ **`/full <id>` as designed cannot be built**: it needs either a second poller on the one bot
(forbidden, and it breaks capture) or a second bot (forbidden by the one-bot invariant).

**4. Tiering is someone else's lane.** SC1 puts *"tiering/порог/анти-инфляция"* explicitly out
of scope, assigned to `flow`. `page` is CRITICAL-tier only — its own help says routine belongs
in the flow-brief. A routine, per-task-completion tier has **no owner and no implementation
today**. That gap is the real justification for this plugin.

## Proposed architecture after recon (needs an Area ruling — not implemented)

**A. Delivery: dispatch, don't duplicate.**
Mirror `page`'s `_dispatch()` pattern — a stable local interface over a swappable backend:

1. `log-bot-notify` when present (inside the LSA mesh: same bot, same token, one-bot invariant
   held, zero risk to capture — `sendMessage` has no exclusivity);
2. direct Bot API via `tg_send.py` only as the **portable** fallback, for hosts where the
   vault-tools package does not exist.

This keeps the built transport honest: m-claude plugins install anywhere, `log-bot` is
LSA-specific. But inside the mesh the mesh's lever wins.

**B. Retrieval: drop the second poller entirely.**
Instead of `/full <id>` over a new `getUpdates` loop — **send the full answer as a document**
alongside the summary when it exceeds the message limit. `sendDocument` is outbound-only,
needs no inbound route, no second bot, and no ruling from SC1. The user gets the summary as a
notification and the full text attached, one tap away.

If a pull-style `/full` is still wanted later, the SC1-compatible way is for **flow-keeper** to
serve it out of the answer store on the existing capture route — a request to `flow`, not code
here.

**C. No new BotFather bot.** The original open question assumed a new bot was likely. Recon
inverts that: a new bot contradicts the ratified one-bot invariant, and with retrieval solved
by (B), nothing in the MVP needs one.

**None of A/B/C is implemented.** They change the MVP's shape (the DoD names `/full <id>`), so
they are a proposal to `area-system-architect`, not a decision taken here.

## What is built (step 1)

`scripts/tg_send.py`, stdlib-only Python 3 (`urllib`), no third-party dependencies — it runs
anywhere `python3` runs, which matters for a hook that fires on every turn on any host.

```bash
tg_send.py --text "hello"
echo "hello" | tg_send.py
tg_send.py --text "see log" --file /tmp/run.log      # sendDocument, text becomes the caption
tg_send.py --text "quiet" --silent                   # disable_notification
```

Decisions:

- **Outbound only, by construction.** There is no `getUpdates` code path in this file and there
  must never be one — that is the invariant that keeps it safe to point at @finimch_bot.
- **Config resolution: CLI flag → env → config file.** Env (`TG_REPORT_BOT_TOKEN`,
  `TG_REPORT_CHAT_ID`) is the development path. The file (`$TG_REPORT_CONFIG` or
  `~/.config/tg-report/config.json`) is the deployed path — outside any git tree, expected mode
  `0600`. **No secret enters this repo**, and no code path here writes one.
- **Distinct exit codes** — `0` sent, `1` send failed, `2` misconfigured, `3` nothing to send.
  A hook must distinguish "the user never set this up" (silent no-op) from "Telegram is down"
  without parsing message strings.
- **Truncation at the transport boundary.** Bot API caps text at 4096 and captions at 1024;
  exceeding it is a hard API error. Clipping with a `…[truncated]` marker here means no caller
  can construct an unsendable message — and it is precisely why the full answer must be stored
  and attached (proposal B).
- **Link previews off, notifications on by default.** A report should ping; a preview of
  whatever URL an agent happened to mention is noise.
- **Multipart built by hand** rather than depending on `requests` — ~20 lines to keep the
  zero-dependency guarantee.

Verified 2026-07-29: 19 unit tests green (`pytest tests/ -q`); network smoke against the real
Bot API returns `HTTP 401 Unauthorized` and exit `1` with an invalid token — the request
reaches Telegram and the failure path works end to end; only a valid token is absent.

## Step 2 — Stop hook (specified, not built)

`hooks/hooks.json` registers a `Stop` hook running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/tg_summary.py`.
Logic mirrors `speak-summary.py`:

1. Read hook JSON from stdin; bail on `stop_hook_active` — no double reports.
2. Read `transcript_path` JSONL, take the last assistant text block.
3. Summary = text after the trigger emoji if present, else the first N lines of the final text.
4. Persist the full text under a short id; send the summary through the delivery dispatcher.
5. **Never fail the turn.** Any exception → `exit 0`. A reporting channel must not be able to
   break the work it reports on. Unconfigured is a silent no-op, so installing the plugin
   without a token is harmless.

Agent identity: the slug comes from `SCION_AGENT_SLUG` — the same variable `page` uses —
falling back to the working directory name. Without it a phone full of reports is unreadable.

## Layout, and where it deviates from repo convention

```
plugins/tg-report/
├── .claude-plugin/plugin.json
├── docs/DESIGN.md            ← this file
├── hooks/hooks.json          (step 2)
├── hooks/tg_summary.py       (step 2)
├── scripts/tg_send.py        portable delivery backend
└── tests/test_tg_send.py
```

Repo precedent puts hook scripts in `hooks/scripts/`. Here delivery sits in a plugin-level
`scripts/` because it is not hook-private — the dispatcher and any future feature call it.
Burying a shared CLI under `hooks/` would mislead the next reader about who owns it.

This is the first plugin in `m-claude` with executable code and a test suite; the repo is
otherwise pure markdown. Conventions taken from repo history rather than invented: stdlib-only
Python, `#!/usr/bin/env python3`, `python3 ${CLAUDE_PLUGIN_ROOT}/…` invocation, the
`hooks/hooks.json` schema.

## Growth path (not MVP)

- More bot commands: agent status, day digest, task launch — all of which hit the same inbound
  constraint and therefore belong to the SC1 layer, not here.
- Source events from the scion hub's state-changes, not only the `Stop` hook — that catches
  agents that die without a final turn.
- Delivery policy: which agents and task classes report, rate limiting, quiet hours. Note this
  is `flow`'s lane per SC1, so it is a contract to consume, not to build.
