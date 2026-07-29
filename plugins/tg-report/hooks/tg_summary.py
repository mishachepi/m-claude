#!/usr/bin/env python3
"""Stop hook: report the finished turn to Telegram.

Mirrors ~/dotfiles/claude/hooks/speak-summary.py — read the transcript, take the
last assistant text, extract a summary — but delivers to Telegram instead of TTS,
and additionally stores the full answer so a long result is not lost to the
4096-char message limit.

Contract with the rest of the system:
  * delivery goes through scripts/tg_deliver.deliver() and nowhere else;
  * the full answer is attached only above a threshold, never on every turn —
    a channel that ships a file after each Stop gets muted by the user;
  * this hook NEVER fails a turn. Any error exits 0. A reporting channel must
    not be able to break the work it reports on.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import tg_deliver  # noqa: E402

# Text after this emoji, when present, is the summary the agent chose to send.
TRIGGER_EMOJI = os.environ.get("TG_REPORT_TRIGGER", "📨")

# Fallback summary size when no trigger is present.
SUMMARY_LINES = int(os.environ.get("TG_REPORT_SUMMARY_LINES", "4"))
SUMMARY_CHARS = int(os.environ.get("TG_REPORT_SUMMARY_CHARS", "600"))

# Attach the full answer only when it carries materially more than the summary.
# 0 disables attachments entirely.
ATTACH_THRESHOLD = int(os.environ.get("TG_REPORT_ATTACH_THRESHOLD", "1500"))

ANSWER_RETENTION_DAYS = int(os.environ.get("TG_REPORT_RETENTION_DAYS", "14"))

# Answers are named <6 hex>.md and nothing else is ever removed. `TG_REPORT_STATE_DIR`
# is operator input: point it at a notes folder by mistake and a naive "delete *.md
# older than N days" would quietly eat someone's writing. Two guards, both required:
# the filename must match a stored answer, and the directory must carry the marker
# this plugin writes. A directory we did not create is never pruned.
ANSWER_NAME = re.compile(r"^[0-9a-f]{6}\.md$")
STORE_MARKER = ".tg-report-store"


def state_dir() -> Path:
    override = os.environ.get("TG_REPORT_STATE_DIR")
    if override:
        return Path(override)
    base = os.environ.get("XDG_STATE_HOME")
    root = Path(base) if base else Path.home() / ".local" / "state"
    return root / "tg-report"


def agent_slug() -> str:
    """Who is reporting. Without this a phone full of reports is unreadable."""
    for var in ("SCION_AGENT_SLUG", "CLAUDE_AGENT_SLUG"):
        value = os.environ.get(var)
        if value:
            return value
    return Path.cwd().name or "agent"


def last_assistant_text(transcript_path: str) -> str | None:
    """Last assistant text block in the transcript JSONL."""
    path = Path(transcript_path)
    if not path.exists():
        return None

    last: str | None = None
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = entry.get("message") or {}
            if message.get("role") != "assistant":
                continue
            content = message.get("content")
            if isinstance(content, str):
                last = content
            elif isinstance(content, list):
                texts = [
                    item.get("text", "")
                    for item in content
                    if isinstance(item, dict) and item.get("type") == "text"
                ]
                joined = "\n".join(t for t in texts if t)
                if joined:
                    last = joined
    return last


def extract_summary(text: str) -> str:
    """Trigger-marked summary if the agent wrote one, else the opening lines."""
    pattern = rf"{re.escape(TRIGGER_EMOJI)}\s*(.+?)(?:\n\n|\n---|$)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    lines = [line for line in text.strip().splitlines() if line.strip()]
    summary = "\n".join(lines[:SUMMARY_LINES]).strip()
    if len(summary) > SUMMARY_CHARS:
        summary = summary[:SUMMARY_CHARS].rstrip() + "…"
    return summary


def answers_dir() -> Path:
    """The answer store, created private and marked as ours."""
    answers = state_dir() / "answers"
    answers.mkdir(parents=True, exist_ok=True)
    try:
        answers.chmod(0o700)
        marker = answers / STORE_MARKER
        if not marker.exists():
            marker.write_text("tg-report answer store\n")
    except OSError:
        pass
    return answers


def store_answer(text: str, slug: str) -> tuple[str, Path]:
    """Persist the full answer under a short id; returns (id, path).

    Written 0600: this is a verbatim assistant answer, which routinely contains
    whatever the agent was working on.
    """
    answers = answers_dir()
    answer_id = uuid.uuid4().hex[:6]
    path = answers / f"{answer_id}.md"
    path.write_text(f"# {slug} — {time.strftime('%Y-%m-%d %H:%M')}\n\n{text}\n")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return answer_id, path


def prune_answers() -> None:
    """Delete expired answers — and only answers this plugin itself wrote."""
    answers = state_dir() / "answers"
    if not answers.is_dir() or ANSWER_RETENTION_DAYS <= 0:
        return
    if not (answers / STORE_MARKER).exists():
        # Not our store. Someone pointed TG_REPORT_STATE_DIR at a foreign directory;
        # refusing beats deleting their files.
        return

    cutoff = time.time() - ANSWER_RETENTION_DAYS * 86400
    for item in answers.iterdir():
        if not item.is_file() or not ANSWER_NAME.match(item.name):
            continue
        try:
            if item.stat().st_mtime < cutoff:
                item.unlink()
        except OSError:
            continue


def should_attach(full: str, summary: str) -> bool:
    """Attach only when the full answer materially exceeds what was already sent."""
    if ATTACH_THRESHOLD <= 0:
        return False
    return len(full) >= ATTACH_THRESHOLD and len(full) > 2 * len(summary)


def build_message(slug: str, summary: str, answer_id: str | None) -> str:
    head = f"[{slug}] {summary}"
    return f"{head}\n\n· {answer_id}" if answer_id else head


def run(hook_input: dict) -> str | None:
    """Core logic, separated from stdin/exit handling so it is testable."""
    if hook_input.get("stop_hook_active"):
        return None

    transcript_path = hook_input.get("transcript_path")
    if not transcript_path:
        return None

    full = last_assistant_text(transcript_path)
    if not full or not full.strip():
        return None

    summary = extract_summary(full)
    if not summary:
        return None

    slug = agent_slug()
    answer_id, answer_path = store_answer(full, slug)
    prune_answers()

    attach = should_attach(full, summary)
    tg_deliver.deliver(
        build_message(slug, summary, answer_id if attach else None),
        document=answer_path if attach else None,
        caption=f"[{slug}] full answer {answer_id}" if attach else None,
    )
    return answer_id


def main() -> int:
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    try:
        run(hook_input)
    except Exception as exc:  # noqa: BLE001 — a report must never break the turn
        print(f"tg-report: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
