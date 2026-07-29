"""Tests for the delivery dispatcher — the one door to any transport."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import tg_deliver  # noqa: E402
import tg_send  # noqa: E402


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    for var in (
        "TG_REPORT_BOT_TOKEN",
        "TG_REPORT_CHAT_ID",
        "LOG_BOT_TOKEN",
        "TELEGRAM_USER_ID",
        "TG_REPORT_FORCE_DIRECT",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("TG_REPORT_CONFIG", str(tmp_path / "absent.json"))


@pytest.fixture
def no_lever(monkeypatch):
    monkeypatch.setattr(tg_deliver.shutil, "which", lambda _name: None)


@pytest.fixture
def lever(monkeypatch):
    monkeypatch.setattr(tg_deliver.shutil, "which", lambda _name: "/usr/local/bin/log-bot-notify")
    calls: list[list[str]] = []

    class Proc:
        returncode = 0
        stderr = ""

    def fake_run(cmd, **_kwargs):
        calls.append(cmd)
        return Proc()

    monkeypatch.setattr(tg_deliver.subprocess, "run", fake_run)
    return calls


@pytest.fixture
def direct(monkeypatch):
    """Capture what the direct Bot API backend would have sent."""
    messages: list[dict] = []
    documents: list[dict] = []

    monkeypatch.setattr(
        tg_send,
        "send_message",
        lambda text, **kw: messages.append({"text": text, **kw}),
    )
    monkeypatch.setattr(
        tg_send,
        "send_document",
        lambda path, **kw: documents.append({"path": path, **kw}),
    )
    return messages, documents


# ------------------------------------------------------------ backend choice


def test_lever_is_preferred_when_present(lever, direct):
    messages, _ = direct
    assert tg_deliver.deliver("done") == "lever"
    assert lever == [["/usr/local/bin/log-bot-notify", "done"]]
    assert messages == [], "the direct backend must not run when the lever exists"


def test_direct_used_only_without_lever(no_lever, direct, monkeypatch):
    monkeypatch.setenv("LOG_BOT_TOKEN", "TOK")
    monkeypatch.setenv("TELEGRAM_USER_ID", "42")
    messages, _ = direct

    assert tg_deliver.deliver("done") == "direct"
    assert messages[0]["text"] == "done"
    assert messages[0]["chat_id"] == "42"


def test_direct_reuses_the_mesh_bot_credentials(no_lever, direct, monkeypatch):
    """No second bot: the fallback rides the same token the mesh already uses."""
    monkeypatch.setenv("LOG_BOT_TOKEN", "MESH-TOKEN")
    monkeypatch.setenv("TELEGRAM_USER_ID", "1000000001")
    messages, _ = direct

    tg_deliver.deliver("done")
    assert messages[0]["token"] == "MESH-TOKEN"
    assert messages[0]["chat_id"] == "1000000001"


def test_direct_without_any_credentials_raises(no_lever, direct):
    with pytest.raises(tg_send.ConfigError):
        tg_deliver.deliver("done")


def test_lever_failure_is_reported(monkeypatch, direct):
    monkeypatch.setattr(tg_deliver.shutil, "which", lambda _n: "/bin/lever")

    class Proc:
        returncode = 3
        stderr = "boom"

    monkeypatch.setattr(tg_deliver.subprocess, "run", lambda cmd, **kw: Proc())
    with pytest.raises(tg_deliver.DeliveryError):
        tg_deliver.deliver("done")


def test_force_direct_escape_hatch(monkeypatch, direct):
    monkeypatch.setattr(tg_deliver.shutil, "which", lambda _n: "/bin/lever")
    monkeypatch.setenv("TG_REPORT_FORCE_DIRECT", "1")
    monkeypatch.setenv("LOG_BOT_TOKEN", "TOK")
    monkeypatch.setenv("TELEGRAM_USER_ID", "42")
    messages, _ = direct

    assert tg_deliver.deliver("done") == "direct"
    assert len(messages) == 1


def test_empty_text_refused(lever):
    with pytest.raises(tg_deliver.DeliveryError):
        tg_deliver.deliver("   ")
    assert lever == []


# ---------------------------------------------------------------- attachments


def test_document_sent_after_text(lever, direct, tmp_path, monkeypatch):
    monkeypatch.setenv("LOG_BOT_TOKEN", "TOK")
    monkeypatch.setenv("TELEGRAM_USER_ID", "42")
    doc = tmp_path / "answer.md"
    doc.write_text("full answer")
    _, documents = direct

    tg_deliver.deliver("summary", document=doc, caption="cap")

    assert lever, "summary still goes through the lever"
    assert documents[0]["path"] == doc
    assert documents[0]["caption"] == "cap"


def test_missing_document_is_skipped_silently(lever, direct, tmp_path):
    _, documents = direct
    tg_deliver.deliver("summary", document=tmp_path / "gone.md")
    assert documents == []
    assert lever, "the summary must still be delivered"


def test_attachment_without_token_does_not_break_the_summary(lever, direct, tmp_path):
    """Degraded report beats lost report."""
    doc = tmp_path / "answer.md"
    doc.write_text("full")
    _, documents = direct

    tg_deliver.deliver("summary", document=doc)

    assert lever, "summary delivered"
    assert documents == [], "attachment quietly dropped, no exception"


def test_attachment_send_failure_does_not_propagate(lever, tmp_path, monkeypatch):
    monkeypatch.setenv("LOG_BOT_TOKEN", "TOK")
    monkeypatch.setenv("TELEGRAM_USER_ID", "42")
    doc = tmp_path / "answer.md"
    doc.write_text("full")

    def boom(*_a, **_k):
        raise tg_send.SendError("nope")

    monkeypatch.setattr(tg_send, "send_document", boom)
    tg_deliver.deliver("summary", document=doc)  # must not raise
