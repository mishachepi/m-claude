#!/usr/bin/env python3
"""tg-deliver — the single delivery door for tg-report.

Everything this plugin sends to the user goes through `deliver()`. Nothing else
in the plugin may talk to a transport. That isolation is the whole point: SC1
(the mesh's Telegram layer) carries a standing obligation to flip its backend to
native `scion message --channel telegram`, and only code whose transport lives
behind one function survives that flip. See docs/DESIGN.md.

Backend order:
    1. `log-bot-notify` — the mesh lever. Preferred whenever it is on PATH.
       Same bot, same token, one-bot invariant intact. Text only.
    2. direct Bot API via tg_send — portable fallback, used ONLY when the lever
       is absent (non-LSA host), and for attachments, which the lever cannot do.

Hard invariant, enforced by tests/test_no_inbound.py: this plugin contains no
`getUpdates` and no webhook code. It is outbound-only, forever. A second inbound
consumer on the mesh bot silently steals updates from the capture daemon.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tg_send  # noqa: E402

LEVER = "log-bot-notify"

# ---------------------------------------------------------------------------
# Timeout budget.
#
# The Stop hook runs inside the agent's turn: every second spent here is a second
# the session hangs. hooks.json grants the hook 30s, and delivery must fit inside
# that with room for interpreter start-up — otherwise a slow Telegram stalls every
# turn and then gets killed mid-send. The invariant "delivery budget < hook budget"
# is enforced by tests/test_timeout_budget.py, not by these comments agreeing.
# ---------------------------------------------------------------------------
TEXT_TIMEOUT = 8.0
DOCUMENT_TIMEOUT = 15.0
TOTAL_BUDGET = TEXT_TIMEOUT + DOCUMENT_TIMEOUT

Backend = Literal["lever", "direct", "none"]


class DeliveryError(RuntimeError):
    """Nothing could deliver the message."""


def lever_path() -> str | None:
    """Absolute path to the mesh lever, or None on a host without it."""
    if os.environ.get("TG_REPORT_FORCE_DIRECT") == "1":
        return None
    return shutil.which(LEVER)


def _send_via_lever(text: str, lever: str, timeout: float) -> None:
    try:
        proc = subprocess.run(
            [lever, text], capture_output=True, timeout=timeout, text=True
        )
    except subprocess.TimeoutExpired as exc:
        raise DeliveryError(f"{LEVER} exceeded {timeout}s") from exc
    if proc.returncode != 0:
        raise DeliveryError(
            f"{LEVER} exited {proc.returncode}: {proc.stderr.strip()[:200]}"
        )


def _resolve_direct_config() -> tuple[str, str]:
    """Token/chat for the direct backend.

    Accepts the mesh bot's own variable names as a source so that a pilot host
    reuses the existing bot rather than provisioning a second one. This module
    never reads another package's config files — only the environment and this
    plugin's own config.
    """
    return tg_send.resolve_config(
        os.environ.get("LOG_BOT_TOKEN"),
        os.environ.get("TELEGRAM_USER_ID"),
    )


def deliver(
    text: str,
    *,
    document: Path | None = None,
    caption: str | None = None,
) -> Backend:
    """Deliver `text`, optionally followed by `document`. Returns the backend used.

    The document is best-effort: if it cannot be sent, the text still is. A
    summary that arrives without its attachment is a degraded report; a summary
    that never arrives is a lost one.
    """
    text = (text or "").strip()
    if not text:
        raise DeliveryError("refusing to deliver empty text")

    lever = lever_path()
    if lever:
        _send_via_lever(text, lever, TEXT_TIMEOUT)
        backend: Backend = "lever"
    else:
        token, chat_id = _resolve_direct_config()
        tg_send.send_message(text, token=token, chat_id=chat_id, timeout=TEXT_TIMEOUT)
        backend = "direct"

    if document is not None:
        _deliver_document(document, caption or "")

    return backend


def _deliver_document(document: Path, caption: str) -> None:
    """Attachments have no lever — `log-bot-notify` sends text only.

    So this one path talks to the Bot API directly even on a mesh host. It stays
    inside this module precisely so the SC1 backend flip has a single place to
    change. Documented as a deviation in docs/DESIGN.md.
    """
    if not document.exists():
        return
    try:
        token, chat_id = _resolve_direct_config()
    except tg_send.ConfigError:
        # No token reachable for the attachment path: the summary already went
        # out through the lever, and a missing attachment must not fail a turn.
        return
    try:
        tg_send.send_document(
            document,
            token=token,
            chat_id=chat_id,
            caption=caption,
            timeout=DOCUMENT_TIMEOUT,
        )
    except tg_send.SendError:
        return


if __name__ == "__main__":
    body = " ".join(sys.argv[1:]) or sys.stdin.read()
    try:
        used = deliver(body)
    except (DeliveryError, tg_send.ConfigError, tg_send.SendError) as exc:
        print(f"tg-deliver: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(used)
