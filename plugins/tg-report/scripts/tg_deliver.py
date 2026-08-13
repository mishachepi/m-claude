#!/usr/bin/env python3
"""tg-deliver — the single delivery door for tg-report.

Everything this plugin sends goes through `deliver()`. Nothing else in the plugin
may talk to a transport. That isolation is the point: swapping how reports reach
you should change one function here and nothing anywhere else.

Backends, in order:
    1. An external notify command, when `TG_REPORT_NOTIFY_CMD` is set. Use this
       to route reports through infrastructure you already run (a notifier of
       your own, a bot wrapper, a queue). It receives the message text as its
       last argument and is expected to exit 0. Text only.
    2. The direct Bot API via tg_send — the default, and the only path that can
       carry attachments.

Hard invariant, enforced by tests/test_no_inbound.py: this plugin contains no
`getUpdates` and no webhook code. It is outbound-only, forever. Anything that
polls for updates competes with every other consumer of the same bot token, and
the Bot API delivers each update exactly once — whoever asks first wins, and the
loser never learns what it missed.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tg_send  # noqa: E402

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

Backend = Literal["command", "direct"]


class DeliveryError(RuntimeError):
    """Nothing could deliver the message."""


def notify_command() -> list[str] | None:
    """The configured external notify command, or None to use the Bot API.

    Returns the argv prefix; the message text is appended by the caller. The
    executable is resolved through PATH so a misconfigured command fails here,
    loudly and before any network call, rather than as an opaque OSError later.
    """
    if os.environ.get("TG_REPORT_FORCE_DIRECT") == "1":
        return None

    raw = (os.environ.get("TG_REPORT_NOTIFY_CMD") or "").strip()
    if not raw:
        return None

    try:
        argv = shlex.split(raw)
    except ValueError as exc:
        raise DeliveryError(f"TG_REPORT_NOTIFY_CMD is not parseable: {exc}") from exc
    if not argv:
        return None

    resolved = shutil.which(argv[0])
    if not resolved:
        raise DeliveryError(f"TG_REPORT_NOTIFY_CMD not found on PATH: {argv[0]}")
    return [resolved, *argv[1:]]


def _send_via_command(text: str, argv: list[str], timeout: float) -> None:
    try:
        proc = subprocess.run(
            [*argv, text], capture_output=True, timeout=timeout, text=True
        )
    except subprocess.TimeoutExpired as exc:
        raise DeliveryError(f"{argv[0]} exceeded {timeout}s") from exc
    if proc.returncode != 0:
        raise DeliveryError(
            f"{argv[0]} exited {proc.returncode}: {proc.stderr.strip()[:200]}"
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

    argv = notify_command()
    if argv:
        _send_via_command(text, argv, TEXT_TIMEOUT)
        backend: Backend = "command"
    else:
        token, chat_id = tg_send.resolve_config()
        tg_send.send_message(text, token=token, chat_id=chat_id, timeout=TEXT_TIMEOUT)
        backend = "direct"

    if document is not None:
        _deliver_document(document, caption or "")

    return backend


def _deliver_document(document: Path, caption: str) -> None:
    """Attachments always go through the Bot API.

    An external notify command takes text, so there is no portable way to hand it
    a file. This is the one place in the plugin where the transport choice is not
    free, and it stays inside this module so that changing transports still means
    changing one file.

    Best-effort by design: the summary has already been delivered by the time we
    get here, and a missing attachment must never turn into a failed turn.
    """
    if not document.exists():
        return
    try:
        token, chat_id = tg_send.resolve_config()
    except tg_send.ConfigError:
        # No credentials for the attachment path — e.g. a setup that delivers text
        # through a command and never configured the Bot API directly.
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
