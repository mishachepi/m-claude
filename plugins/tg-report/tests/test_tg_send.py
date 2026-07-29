"""Tests for the tg-send transport. No network: _post is stubbed."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import tg_send  # noqa: E402


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    """No ambient config leaks into a test."""
    for var in ("TG_REPORT_BOT_TOKEN", "TG_REPORT_CHAT_ID"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("TG_REPORT_CONFIG", str(tmp_path / "absent.json"))


@pytest.fixture
def captured(monkeypatch):
    """Capture what would have been POSTed."""
    calls: list[dict] = []

    def fake_post(url, data, content_type, timeout):
        calls.append(
            {
                "url": url,
                "data": data,
                "content_type": content_type,
                "timeout": timeout,
            }
        )
        return {"ok": True, "result": {"message_id": 1}}

    monkeypatch.setattr(tg_send, "_post", fake_post)
    return calls


# --------------------------------------------------------------------- config


def test_env_config_wins_over_file(monkeypatch, tmp_path):
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"bot_token": "from-file", "chat_id": "999"}))
    monkeypatch.setenv("TG_REPORT_CONFIG", str(cfg))
    monkeypatch.setenv("TG_REPORT_BOT_TOKEN", "from-env")
    monkeypatch.setenv("TG_REPORT_CHAT_ID", "111")

    assert tg_send.resolve_config() == ("from-env", "111")


def test_config_file_used_when_env_absent(monkeypatch, tmp_path):
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"bot_token": "from-file", "chat_id": "999"}))
    monkeypatch.setenv("TG_REPORT_CONFIG", str(cfg))

    assert tg_send.resolve_config() == ("from-file", "999")


def test_explicit_args_win_over_everything(monkeypatch):
    monkeypatch.setenv("TG_REPORT_BOT_TOKEN", "from-env")
    monkeypatch.setenv("TG_REPORT_CHAT_ID", "111")

    assert tg_send.resolve_config("arg-token", "222") == ("arg-token", "222")


def test_missing_config_raises_naming_the_missing_key():
    with pytest.raises(tg_send.ConfigError) as exc:
        tg_send.resolve_config()
    assert "bot_token" in str(exc.value)
    assert "chat_id" in str(exc.value)


def test_partial_config_raises(monkeypatch):
    monkeypatch.setenv("TG_REPORT_BOT_TOKEN", "t")
    with pytest.raises(tg_send.ConfigError) as exc:
        tg_send.resolve_config()
    assert "chat_id" in str(exc.value)
    assert "bot_token" not in str(exc.value)


def test_corrupt_config_file_raises(monkeypatch, tmp_path):
    cfg = tmp_path / "config.json"
    cfg.write_text("{not json")
    monkeypatch.setenv("TG_REPORT_CONFIG", str(cfg))
    with pytest.raises(tg_send.ConfigError):
        tg_send.resolve_config()


# ------------------------------------------------------------------- truncate


def test_truncate_leaves_short_text_alone():
    assert tg_send.truncate("hi") == "hi"


def test_truncate_clips_to_limit_including_marker():
    long = "x" * (tg_send.TEXT_LIMIT + 500)
    out = tg_send.truncate(long)
    assert len(out) == tg_send.TEXT_LIMIT
    assert out.endswith(tg_send.TRUNCATION_MARK)


def test_truncate_boundary_is_not_clipped():
    exact = "x" * tg_send.TEXT_LIMIT
    assert tg_send.truncate(exact) == exact


# --------------------------------------------------------------- send_message


def test_send_message_payload(captured):
    tg_send.send_message("hello", token="TOK", chat_id="42")

    (call,) = captured
    assert call["url"] == f"{tg_send.API_ROOT}/botTOK/sendMessage"
    body = json.loads(call["data"])
    assert body["chat_id"] == "42"
    assert body["text"] == "hello"
    assert body["disable_notification"] is False
    assert body["link_preview_options"] == {"is_disabled": True}
    assert "parse_mode" not in body


def test_send_message_silent_and_parse_mode(captured):
    tg_send.send_message(
        "hi", token="TOK", chat_id="42", parse_mode="HTML", silent=True
    )
    body = json.loads(captured[0]["data"])
    assert body["parse_mode"] == "HTML"
    assert body["disable_notification"] is True


def test_send_message_truncates_oversized_text(captured):
    tg_send.send_message("y" * 9000, token="TOK", chat_id="42")
    body = json.loads(captured[0]["data"])
    assert len(body["text"]) == tg_send.TEXT_LIMIT


def test_send_message_raises_on_api_error(monkeypatch):
    def fake_post(*_args, **_kwargs):
        raise tg_send.SendError("HTTP 401: unauthorized")

    monkeypatch.setattr(tg_send, "_post", fake_post)
    with pytest.raises(tg_send.SendError):
        tg_send.send_message("hi", token="TOK", chat_id="42")


# -------------------------------------------------------------- send_document


def test_send_document_multipart(captured, tmp_path):
    f = tmp_path / "run.log"
    f.write_text("line one\n")

    tg_send.send_document(f, token="TOK", chat_id="42", caption="see log")

    (call,) = captured
    assert call["url"] == f"{tg_send.API_ROOT}/botTOK/sendDocument"
    assert call["content_type"].startswith("multipart/form-data; boundary=")
    body = call["data"].decode("utf-8", "replace")
    assert 'name="chat_id"' in body
    assert 'name="document"; filename="run.log"' in body
    assert "line one" in body
    assert "see log" in body


def test_send_document_caption_uses_caption_limit(captured, tmp_path):
    f = tmp_path / "a.txt"
    f.write_bytes(b"x")
    tg_send.send_document(f, token="TOK", chat_id="42", caption="c" * 5000)
    body = captured[0]["data"].decode("utf-8", "replace")
    assert "[truncated]" in body
    assert "c" * (tg_send.CAPTION_LIMIT + 1) not in body


# --------------------------------------------------------------------- CLI


def test_main_sends_text(captured, monkeypatch):
    monkeypatch.setenv("TG_REPORT_BOT_TOKEN", "TOK")
    monkeypatch.setenv("TG_REPORT_CHAT_ID", "42")

    assert tg_send.main(["--text", "from cli"]) == 0
    assert json.loads(captured[0]["data"])["text"] == "from cli"


def test_main_exit_2_when_unconfigured(captured):
    assert tg_send.main(["--text", "orphan"]) == 2
    assert captured == []


def test_main_exit_3_when_nothing_to_send(monkeypatch, captured):
    monkeypatch.setenv("TG_REPORT_BOT_TOKEN", "TOK")
    monkeypatch.setenv("TG_REPORT_CHAT_ID", "42")
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)

    assert tg_send.main([]) == 3
    assert captured == []


def test_main_exit_1_on_send_failure(monkeypatch):
    monkeypatch.setenv("TG_REPORT_BOT_TOKEN", "TOK")
    monkeypatch.setenv("TG_REPORT_CHAT_ID", "42")

    def fake_post(*_args, **_kwargs):
        raise tg_send.SendError("boom")

    monkeypatch.setattr(tg_send, "_post", fake_post)
    assert tg_send.main(["--text", "hi"]) == 1
