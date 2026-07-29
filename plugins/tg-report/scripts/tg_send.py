#!/usr/bin/env python3
"""tg-send — thin Telegram transport for the tg-report plugin.

One job: take text (and optionally a file) and deliver it to the user's
Telegram chat via the Bot API. No hook logic, no formatting policy, no state.

Usage:
    tg_send.py --text "hello"
    echo "hello" | tg_send.py
    tg_send.py --text "quiet ping" --silent

`send_document()` is a library primitive with exactly one caller —
`tg_deliver._deliver_document()`. It is deliberately NOT exposed on this CLI: the
attachment path is interim debt owed to the SC1 sunset flip, and it is worth
keeping to a single site (enforced by tests/test_no_inbound.py).

Config resolution (first hit wins), see docs/DESIGN.md:
    1. CLI flags        --token / --chat-id
    2. env              TG_REPORT_BOT_TOKEN / TG_REPORT_CHAT_ID
    3. config file      $TG_REPORT_CONFIG or ~/.config/tg-report/config.json
                        {"bot_token": "...", "chat_id": "..."}

Secrets never live in this repo. The config file is expected to be mode 0600
and outside any git tree.

Exit codes:
    0  delivered
    1  send failed (network / Bot API error)
    2  misconfigured (no token or no chat_id)
    3  nothing to send (empty text and no file)
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

API_ROOT = "https://api.telegram.org"

# Telegram hard limits (Bot API docs).
TEXT_LIMIT = 4096
CAPTION_LIMIT = 1024
TRUNCATION_MARK = "\n…[truncated]"

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "tg-report" / "config.json"


class ConfigError(RuntimeError):
    """Token or chat_id could not be resolved."""


class SendError(RuntimeError):
    """The Bot API refused or the network failed."""


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------


def _config_path() -> Path:
    override = os.environ.get("TG_REPORT_CONFIG")
    return Path(override) if override else DEFAULT_CONFIG_PATH


def _read_config_file() -> dict[str, Any]:
    path = _config_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"config file {path} is unreadable: {exc}") from exc


def resolve_config(
    token: str | None = None, chat_id: str | None = None
) -> tuple[str, str]:
    """Return (bot_token, chat_id) or raise ConfigError."""
    token = token or os.environ.get("TG_REPORT_BOT_TOKEN")
    chat_id = chat_id or os.environ.get("TG_REPORT_CHAT_ID")

    if not token or not chat_id:
        file_cfg = _read_config_file()
        token = token or file_cfg.get("bot_token")
        chat_id = chat_id or file_cfg.get("chat_id")

    missing = [
        name
        for name, value in (("bot_token", token), ("chat_id", chat_id))
        if not value
    ]
    if missing:
        raise ConfigError(
            f"missing {', '.join(missing)} — set TG_REPORT_BOT_TOKEN / "
            f"TG_REPORT_CHAT_ID or write {_config_path()}"
        )
    return str(token), str(chat_id)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def truncate(text: str, limit: int = TEXT_LIMIT) -> str:
    """Clip to the Bot API limit, leaving room for the truncation marker."""
    if len(text) <= limit:
        return text
    return text[: limit - len(TRUNCATION_MARK)] + TRUNCATION_MARK


def scrub(message: str, secret: str | None) -> str:
    """Remove the bot token from anything that may be printed or logged.

    The token sits in the request URL, and several urllib failures quote that URL
    back in their message (`ValueError: unknown url type: …`). Without this, a
    malformed token turns a hook's stderr line into a credential leak.
    """
    if not secret:
        return message
    return message.replace(secret, "***")


def _post(
    url: str, data: bytes, content_type: str, timeout: float, secret: str | None = None
) -> dict[str, Any]:
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": content_type}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise SendError(scrub(f"HTTP {exc.code}: {body}", secret)) from exc
    except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError) as exc:
        # ValueError covers urlopen rejecting a malformed URL built from a bad token.
        raise SendError(scrub(f"transport failure: {exc}", secret)) from exc

    if not payload.get("ok"):
        raise SendError(scrub(f"Bot API error: {payload}", secret))
    return payload


def _multipart(fields: dict[str, str], file_field: str, file_path: Path) -> tuple[bytes, str]:
    """Build a multipart/form-data body without pulling in `requests`."""
    boundary = f"----tgreport{uuid.uuid4().hex}"
    sep = f"--{boundary}\r\n".encode()
    body = bytearray()

    for name, value in fields.items():
        body += sep
        body += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        body += f"{value}\r\n".encode()

    mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    body += sep
    body += (
        f'Content-Disposition: form-data; name="{file_field}"; '
        f'filename="{file_path.name}"\r\n'
    ).encode()
    body += f"Content-Type: {mime}\r\n\r\n".encode()
    body += file_path.read_bytes()
    body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    return bytes(body), f"multipart/form-data; boundary={boundary}"


# --------------------------------------------------------------------------
# API calls
# --------------------------------------------------------------------------


def send_message(
    text: str,
    *,
    token: str,
    chat_id: str,
    parse_mode: str | None = None,
    silent: bool = False,
    timeout: float = 15.0,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "chat_id": chat_id,
        "text": truncate(text, TEXT_LIMIT),
        "disable_notification": silent,
        "link_preview_options": {"is_disabled": True},
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode

    return _post(
        f"{API_ROOT}/bot{token}/sendMessage",
        json.dumps(payload).encode("utf-8"),
        "application/json",
        timeout,
        secret=token,
    )


def send_document(
    file_path: Path,
    *,
    token: str,
    chat_id: str,
    caption: str = "",
    silent: bool = False,
    timeout: float = 60.0,
) -> dict[str, Any]:
    fields = {"chat_id": chat_id, "disable_notification": "true" if silent else "false"}
    if caption:
        fields["caption"] = truncate(caption, CAPTION_LIMIT)

    body, content_type = _multipart(fields, "document", file_path)
    return _post(
        f"{API_ROOT}/bot{token}/sendDocument", body, content_type, timeout, secret=token
    )


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tg-send", description="Send text (and optionally a file) to Telegram."
    )
    parser.add_argument("--text", help="message text; read from stdin when omitted")
    parser.add_argument("--chat-id", help="override the configured chat id")
    parser.add_argument("--token", help="override the configured bot token")
    parser.add_argument(
        "--parse-mode",
        choices=("MarkdownV2", "HTML"),
        help="Telegram parse mode; plain text when omitted",
    )
    parser.add_argument(
        "--silent", action="store_true", help="deliver without a push notification"
    )
    parser.add_argument(
        "--timeout", type=float, default=15.0, help="HTTP timeout in seconds"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    text = args.text
    if text is None and not sys.stdin.isatty():
        text = sys.stdin.read()
    text = (text or "").strip()

    if not text:
        print("tg-send: nothing to send", file=sys.stderr)
        return 3

    try:
        token, chat_id = resolve_config(args.token, args.chat_id)
    except ConfigError as exc:
        print(f"tg-send: {exc}", file=sys.stderr)
        return 2

    try:
        send_message(
            text,
            token=token,
            chat_id=chat_id,
            parse_mode=args.parse_mode,
            silent=args.silent,
            timeout=args.timeout,
        )
    except SendError as exc:
        print(f"tg-send: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
