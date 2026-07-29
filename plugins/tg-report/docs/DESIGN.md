# tg-report — design

> Status: **MVP built, pilot smoke green on M1.** Recon (2026-07-29) found that the
> LSA mesh already has a ratified Telegram architecture this plugin must fit into
> rather than parallel; the Area ruled on it the same day. See §"What recon changed"
> and §"Architecture" — the ruling is what this code implements.

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

## Architecture (ruled by `area-system-architect`, 2026-07-29 — implemented)

**A. Delivery: dispatch, don't duplicate.** `scripts/tg_deliver.py` mirrors `page`'s
`_dispatch()` — a stable local interface over a swappable backend:

1. `log-bot-notify` whenever it is on `PATH` (inside the mesh: same bot, same token, one-bot
   invariant held, zero risk to capture — `sendMessage` has no exclusivity);
2. direct Bot API via `tg_send.py` **only** when the lever is absent (non-LSA host), on the
   same credentials.

The Area's decisive argument was not 409 risk — there is none for `sendMessage` — but **sunset
survival**: SC1 owes a backend flip to native `scion message --channel telegram`, and only code
whose transport sits behind one function survives it. The boundary is "will this outlive
go-live", not "whose script is it".

**B. Retrieval: no second poller, ever.** `/full <id>` needs both an inbound consumer *and*
id↔answer correlation — SC1 ratified the opposite on both counts (single inbound route to
flow-keeper; corr-id and pending-table explicitly deprecated). So it is not an expensive
feature, it is two reversals of a ratified decision. Dropped.

Replacement: the full answer is stored locally under a short id and **pushed as a document**
next to the summary — outbound, occupies no slot. If a pull style is ever wanted, flow-keeper
serves it from the store on the existing capture route: a request to `flow`, not code here.

**C. The attachment is thresholded, not default.** Ruled explicitly: a channel that ships a
file after every Stop gets muted wholesale and the feature dies of its own success. So the
document is attached only when the full answer is materially longer than what the summary
already delivered — `len(full) ≥ 1500 and len(full) > 2 × len(summary)`. Both conditions matter:
the first stops noise, the second stops attaching a file that merely repeats the message.

**D. No new BotFather bot** — a second bot contradicts the one-bot invariant, and with (B)
nothing needs one.

**E. Fleet rollout is not this plugin's lane.** Who reports, how often, quiet hours = tiering,
`flow`'s engine per SC1. Distribution = `orchestrator`. MVP ships one pilot agent on M1.

### ⚠️ Interim debt — the attachment path (ratified by Area 2026-07-29, not architecture)

**This is a debt with a scheduled payoff, not a design decision.** Read it as temporary.

The ruling says that on a mesh host the plugin talks to the Bot API "not at all". That is
achievable for text but **not** for documents: `log-bot-notify` sends text only
(`notify.send(text: str) -> dict`, endpoint hard-wired to `sendMessage`), so no lever carries
`sendDocument`.

Interim resolution, ratified with conditions: the attachment path calls the Bot API directly
even on a mesh host, but strictly inside `tg_deliver._deliver_document()` — inside the very
isolation the ruling exists to create, same token, still outbound-only.

Ratification conditions, all binding:

1. **The path never spreads beyond `_deliver_document()`.** Enforced by
   `tests/test_no_inbound.py::test_attachment_path_does_not_spread`, not by prose.
2. **It is recorded as interim debt**, here and in the README, tied to the SC1 sunset.
3. **It flips together with the text path**, tracked in the SC1 sunset inventory.

Asking `epic-log-bot` to add a document mode to the lever was explicitly rejected: SC1 carries a
cross-repo tripwire against extending log-bot beyond need, and the target backend already has
it — `scion message --attach`.

#### Gotcha for whoever performs the flip

`scion message --attach`, per its own help, takes paths **under `/workspace` or
`/scion-volumes`**; *"absolute paths outside these roots are silently dropped on delivery"*.
The answer store lives in `$XDG_STATE_HOME/tg-report/answers/`, outside both roots. A naive
flip therefore yields **"sent successfully, no file"** — silent loss, the worst defect class,
and trivially easy to hit here. The flip must either relocate the store under an accepted root
or copy the answer there before attaching.

Attachment failures are swallowed by design: a summary that arrives without its file is a
degraded report, one that never arrives is a lost one.

## What is built (step 1)

`scripts/tg_send.py`, stdlib-only Python 3 (`urllib`), no third-party dependencies — it runs
anywhere `python3` runs, which matters for a hook that fires on every turn on any host.

```bash
tg_send.py --text "hello"
echo "hello" | tg_send.py
tg_send.py --text "quiet" --silent                   # disable_notification
```

`send_document()` exists as a library primitive but is deliberately **not** on this CLI: the
attachment path is interim debt, and keeping it to a single call site is a ratification
condition (below). Removing the `--file` flag was how that condition was actually met — the
containment test failed on the flag before it was dropped, which is the evidence that the test
is real.

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

## Step 2 — Stop hook producer (built)

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

Verified 2026-07-29 on M1, one pilot agent (`epic-tg-bot`): a synthetic Stop payload produced a
stored answer and a live Telegram message through the lever — `log-bot.log` records
`[notify] sent 110 chars` at 14:18:33. 57 tests green.

## The outbound-only invariant, enforced

`tests/test_no_inbound.py` parses every non-test Python file with `ast`, strips docstrings, and
fails if `getUpdates` / `setWebhook` / `webhook` appears in any executable string or identifier.
Prose explaining the ban stays legal; a real call cannot hide, because invoking a Bot API method
needs the name in an executable string. The suite also asserts the check itself would catch a
planted violation and that the file list is non-empty — a guard that cannot fail guards nothing.

## Layout, and where it deviates from repo convention

```
plugins/tg-report/
├── .claude-plugin/plugin.json
├── README.md
├── docs/DESIGN.md            ← this file
├── hooks/hooks.json
├── hooks/tg_summary.py       producer — the genuinely new piece
├── scripts/tg_deliver.py     the single delivery door
├── scripts/tg_send.py        direct Bot API backend
└── tests/                    test_tg_send · test_tg_deliver · test_tg_summary · test_no_inbound
```

Repo precedent puts hook scripts in `hooks/scripts/`. Here delivery sits in a plugin-level
`scripts/` because it is not hook-private — the dispatcher and any future feature call it.
Burying a shared CLI under `hooks/` would mislead the next reader about who owns it.

This is the first plugin in `m-claude` with executable code and a test suite; the repo is
otherwise pure markdown. Conventions taken from repo history rather than invented: stdlib-only
Python, `#!/usr/bin/env python3`, `python3 ${CLAUDE_PLUGIN_ROOT}/…` invocation, the
`hooks/hooks.json` schema.

## Defects found in review and fixed (2026-07-29)

Found by `epic-mclaude` during merge review — by reading the code, not the test names, which is
why they were found at all. All three classes are now enforced by tests rather than avoided by
care:

1. **Timeout budget did not close.** `hooks.json` allowed the hook 30s while delivery could
   spend 20s on the summary plus a hard-coded `max(timeout, 60)` on the attachment — 80s worst
   case. The symptom would not have been a crash but a per-turn stall ending in the hook being
   killed mid-send, on every agent it was rolled out to. Now `TEXT_TIMEOUT + DOCUMENT_TIMEOUT`
   is a single declared budget, asserted against `hooks.json` with start-up margin.
2. **`TG_REPORT_STATE_DIR` was unvalidated** while prune removed every `*.md` older than the
   retention window beneath it. One wrong export at a notes folder was silent data loss. Prune
   now requires both a matching answer filename and this plugin's marker in the directory; a
   directory we did not create is never touched.
3. **The bot token could reach stderr.** `urlopen` raises `ValueError` on a malformed URL and
   quotes the URL — which contains the token — and that exception escaped the `except` clause
   into the hook's stderr. Now caught, and every error string is scrubbed.

Also fixed from the same review: answers written `0600` in a `0700` directory rather than at the
default umask, and a real-looking Telegram user id replaced with an obvious fake in tests.

## Growth path (not MVP)

- More bot commands: agent status, day digest, task launch — all of which hit the same inbound
  constraint and therefore belong to the SC1 layer, not here.
- Source events from the scion hub's state-changes, not only the `Stop` hook — that catches
  agents that die without a final turn.
- Delivery policy: which agents and task classes report, rate limiting, quiet hours. Note this
  is `flow`'s lane per SC1, so it is a contract to consume, not to build.
