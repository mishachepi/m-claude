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
        "TG_REPORT_NOTIFY_CMD",
        "TG_REPORT_FORCE_DIRECT",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("TG_REPORT_CONFIG", str(tmp_path / "absent.json"))


@pytest.fixture
def credentials(monkeypatch):
    monkeypatch.setenv("TG_REPORT_BOT_TOKEN", "TOK")
    monkeypatch.setenv("TG_REPORT_CHAT_ID", "42")


@pytest.fixture
def notify_cmd(monkeypatch):
    """Configure an external notify command and capture what it is invoked with."""
    monkeypatch.setenv("TG_REPORT_NOTIFY_CMD", "my-notifier")
    monkeypatch.setattr(
        tg_deliver.shutil, "which", lambda name: f"/usr/local/bin/{name}"
    )
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


def test_direct_is_the_default(direct, credentials):
    """With nothing configured beyond credentials, reports go straight to Telegram."""
    messages, _ = direct

    assert tg_deliver.deliver("done") == "direct"
    assert messages[0]["text"] == "done"
    assert messages[0]["token"] == "TOK"
    assert messages[0]["chat_id"] == "42"


def test_notify_command_takes_over_when_configured(notify_cmd, direct):
    messages, _ = direct

    assert tg_deliver.deliver("done") == "command"
    assert notify_cmd == [["/usr/local/bin/my-notifier", "done"]]
    assert messages == [], "the Bot API must not run when a command is configured"


def test_notify_command_keeps_its_own_arguments(monkeypatch, direct):
    monkeypatch.setenv("TG_REPORT_NOTIFY_CMD", "my-notifier --channel reports")
    monkeypatch.setattr(tg_deliver.shutil, "which", lambda name: f"/bin/{name}")
    calls: list[list[str]] = []

    class Proc:
        returncode = 0
        stderr = ""

    monkeypatch.setattr(
        tg_deliver.subprocess, "run", lambda cmd, **kw: (calls.append(cmd), Proc())[1]
    )

    tg_deliver.deliver("done")
    assert calls == [["/bin/my-notifier", "--channel", "reports", "done"]]


def test_unresolvable_notify_command_fails_before_any_send(monkeypatch, direct):
    """A typo in the command must not silently fall back to a different transport."""
    monkeypatch.setenv("TG_REPORT_NOTIFY_CMD", "does-not-exist")
    monkeypatch.setattr(tg_deliver.shutil, "which", lambda _name: None)
    messages, _ = direct

    with pytest.raises(tg_deliver.DeliveryError):
        tg_deliver.deliver("done")
    assert messages == [], "a broken command must not leak the report to the Bot API"


def test_direct_without_any_credentials_raises(direct):
    with pytest.raises(tg_send.ConfigError):
        tg_deliver.deliver("done")


def test_notify_command_failure_is_reported(monkeypatch, direct):
    monkeypatch.setenv("TG_REPORT_NOTIFY_CMD", "my-notifier")
    monkeypatch.setattr(tg_deliver.shutil, "which", lambda name: f"/bin/{name}")

    class Proc:
        returncode = 3
        stderr = "boom"

    monkeypatch.setattr(tg_deliver.subprocess, "run", lambda cmd, **kw: Proc())
    with pytest.raises(tg_deliver.DeliveryError):
        tg_deliver.deliver("done")


def test_force_direct_escape_hatch(notify_cmd, direct, monkeypatch, credentials):
    monkeypatch.setenv("TG_REPORT_FORCE_DIRECT", "1")
    messages, _ = direct

    assert tg_deliver.deliver("done") == "direct"
    assert len(messages) == 1
    assert notify_cmd == [], "the configured command is bypassed, not merely ignored"


def test_empty_text_refused(notify_cmd):
    with pytest.raises(tg_deliver.DeliveryError):
        tg_deliver.deliver("   ")
    assert notify_cmd == []


# ---------------------------------------------------------------- attachments


def test_document_sent_after_text(notify_cmd, direct, tmp_path, credentials):
    doc = tmp_path / "answer.md"
    doc.write_text("full answer")
    _, documents = direct

    tg_deliver.deliver("summary", document=doc, caption="cap")

    assert notify_cmd, "summary still goes through the configured command"
    assert documents[0]["path"] == doc
    assert documents[0]["caption"] == "cap"


def test_missing_document_is_skipped_silently(notify_cmd, direct, tmp_path):
    _, documents = direct
    tg_deliver.deliver("summary", document=tmp_path / "gone.md")
    assert documents == []
    assert notify_cmd, "the summary must still be delivered"


def test_attachment_without_token_does_not_break_the_summary(
    notify_cmd, direct, tmp_path
):
    """Degraded report beats lost report."""
    doc = tmp_path / "answer.md"
    doc.write_text("full")
    _, documents = direct

    tg_deliver.deliver("summary", document=doc)

    assert notify_cmd, "summary delivered"
    assert documents == [], "attachment quietly dropped, no exception"


def test_attachment_send_failure_does_not_propagate(
    notify_cmd, tmp_path, monkeypatch, credentials
):
    doc = tmp_path / "answer.md"
    doc.write_text("full")

    def boom(*_a, **_k):
        raise tg_send.SendError("nope")

    monkeypatch.setattr(tg_send, "send_document", boom)
    tg_deliver.deliver("summary", document=doc)  # must not raise
