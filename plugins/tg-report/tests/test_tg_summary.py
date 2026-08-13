"""Tests for the Stop-hook producer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "hooks"))

import tg_summary  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_state(monkeypatch, tmp_path):
    monkeypatch.setenv("TG_REPORT_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("TG_REPORT_LABEL", "reporter")


@pytest.fixture
def delivered(monkeypatch):
    calls: list[dict] = []
    monkeypatch.setattr(
        tg_summary.tg_deliver,
        "deliver",
        lambda text, **kw: calls.append({"text": text, **kw}) or "lever",
    )
    return calls


def transcript(tmp_path: Path, *messages: str) -> str:
    path = tmp_path / "transcript.jsonl"
    lines = []
    for text in messages:
        lines.append(
            json.dumps(
                {"message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}
            )
        )
    path.write_text("\n".join(lines))
    return str(path)


# ------------------------------------------------------------------ transcript


def test_last_assistant_text_wins(tmp_path):
    path = transcript(tmp_path, "first", "second", "third")
    assert tg_summary.last_assistant_text(path) == "third"


def test_user_turns_are_ignored(tmp_path):
    path = tmp_path / "t.jsonl"
    path.write_text(
        json.dumps({"message": {"role": "assistant", "content": "answer"}})
        + "\n"
        + json.dumps({"message": {"role": "user", "content": "question"}})
    )
    assert tg_summary.last_assistant_text(str(path)) == "answer"


def test_malformed_lines_do_not_break_parsing(tmp_path):
    path = tmp_path / "t.jsonl"
    path.write_text(
        "{not json\n"
        + json.dumps({"message": {"role": "assistant", "content": "ok"}})
        + "\n\n"
    )
    assert tg_summary.last_assistant_text(str(path)) == "ok"


def test_missing_transcript_returns_none(tmp_path):
    assert tg_summary.last_assistant_text(str(tmp_path / "nope.jsonl")) is None


# --------------------------------------------------------------------- summary


def test_trigger_emoji_selects_the_summary(monkeypatch):
    text = "long preamble\n\n📨 the bit that matters\n\nmore prose"
    assert tg_summary.extract_summary(text) == "the bit that matters"


def test_without_trigger_the_opening_lines_are_used():
    text = "\n".join(f"line {i}" for i in range(1, 10))
    summary = tg_summary.extract_summary(text)
    assert summary.startswith("line 1")
    assert summary.endswith(f"line {tg_summary.SUMMARY_LINES}")


def test_summary_is_capped_in_characters():
    text = "x" * 5000
    assert len(tg_summary.extract_summary(text)) <= tg_summary.SUMMARY_CHARS + 1


# ------------------------------------------------------------------- threshold


def test_short_answer_is_not_attached():
    """The core anti-spam rule: no file on every turn."""
    full = "short answer"
    assert tg_summary.should_attach(full, full) is False


def test_long_answer_beyond_the_summary_is_attached():
    full = "x" * (tg_summary.ATTACH_THRESHOLD + 100)
    assert tg_summary.should_attach(full, "tiny summary") is True


def test_long_answer_fully_covered_by_summary_is_not_attached():
    """If the summary already carries it, the file adds nothing."""
    full = "y" * (tg_summary.ATTACH_THRESHOLD + 100)
    assert tg_summary.should_attach(full, full) is False


def test_threshold_zero_disables_attachments(monkeypatch):
    monkeypatch.setattr(tg_summary, "ATTACH_THRESHOLD", 0)
    assert tg_summary.should_attach("z" * 99999, "s") is False


# ------------------------------------------------------------------------ run


def test_run_delivers_summary_with_slug(tmp_path, delivered):
    path = transcript(tmp_path, "the result is ready")
    tg_summary.run({"transcript_path": path})

    assert delivered[0]["text"].startswith("[reporter] the result is ready")
    assert delivered[0]["document"] is None


def test_run_stores_the_full_answer(tmp_path, delivered):
    path = transcript(tmp_path, "full text of the answer")
    answer_id = tg_summary.run({"transcript_path": path})

    stored = tg_summary.state_dir() / "answers" / f"{answer_id}.md"
    assert "full text of the answer" in stored.read_text()


def test_run_attaches_only_above_threshold(tmp_path, delivered):
    long_answer = "📨 tiny summary\n\n" + "x" * (tg_summary.ATTACH_THRESHOLD + 500)
    path = transcript(tmp_path, long_answer)
    answer_id = tg_summary.run({"transcript_path": path})

    assert delivered[0]["document"] is not None
    assert answer_id in delivered[0]["text"], "the id must be visible when a file is attached"


def test_run_is_a_noop_on_stop_hook_continuation(tmp_path, delivered):
    path = transcript(tmp_path, "text")
    assert tg_summary.run({"transcript_path": path, "stop_hook_active": True}) is None
    assert delivered == []


def test_run_is_a_noop_without_transcript(delivered):
    assert tg_summary.run({}) is None
    assert delivered == []


def test_run_is_a_noop_on_empty_final_text(tmp_path, delivered):
    path = transcript(tmp_path, "   ")
    assert tg_summary.run({"transcript_path": path}) is None
    assert delivered == []


def test_label_falls_back_to_the_working_directory(monkeypatch):
    monkeypatch.delenv("TG_REPORT_LABEL", raising=False)
    assert tg_summary.agent_label()


def test_label_is_used_when_set(monkeypatch):
    monkeypatch.setenv("TG_REPORT_LABEL", "build-agent")
    assert tg_summary.agent_label() == "build-agent"


# ----------------------------------------------------------------------- main


def test_main_never_fails_the_turn(monkeypatch, tmp_path, capsys):
    """A reporting channel must not be able to break the work it reports on."""
    path = transcript(tmp_path, "text")

    def boom(*_a, **_k):
        raise RuntimeError("telegram is on fire")

    monkeypatch.setattr(tg_summary.tg_deliver, "deliver", boom)
    monkeypatch.setattr(
        "sys.stdin", __import__("io").StringIO(json.dumps({"transcript_path": path}))
    )

    assert tg_summary.main() == 0
    assert "telegram is on fire" in capsys.readouterr().err


def test_main_survives_garbage_stdin(monkeypatch):
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("not json"))
    assert tg_summary.main() == 0
