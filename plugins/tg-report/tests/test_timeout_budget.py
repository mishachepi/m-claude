"""The delivery budget must fit inside the Stop hook's budget.

The hook runs inside the agent's turn, so every second here is a second the
session hangs. Before this was enforced, hooks.json granted 30s while delivery
could spend 20s on the summary plus a hard-coded 60s on the attachment — 80s
worst case. The visible symptom would not be a crash but a per-turn stall ending
in the hook being killed mid-send, on every agent the plugin is rolled out to.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tg_deliver  # noqa: E402
import tg_send  # noqa: E402

# Python start-up, module imports and the lever's own process spawn all happen
# inside the hook's allowance but outside our timeouts.
STARTUP_MARGIN_SECONDS = 5.0


def hook_timeout() -> float:
    hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())
    return float(hooks["hooks"]["Stop"][0]["hooks"][0]["timeout"])


def test_hook_declares_a_timeout():
    """Guards the guard — without a declared timeout the comparison is vacuous."""
    assert hook_timeout() > 0


def test_delivery_budget_fits_in_the_hook_budget():
    assert tg_deliver.TOTAL_BUDGET + STARTUP_MARGIN_SECONDS <= hook_timeout(), (
        f"delivery may take {tg_deliver.TOTAL_BUDGET}s + startup, "
        f"hook allows {hook_timeout()}s"
    )


def test_total_budget_is_the_sum_of_its_parts():
    assert tg_deliver.TOTAL_BUDGET == tg_deliver.TEXT_TIMEOUT + tg_deliver.DOCUMENT_TIMEOUT


def test_the_budget_check_would_fail_if_a_timeout_grew(monkeypatch):
    """A check that cannot fail is not a check."""
    monkeypatch.setattr(tg_deliver, "TOTAL_BUDGET", hook_timeout() + 1)
    with pytest.raises(AssertionError):
        test_delivery_budget_fits_in_the_hook_budget()


# --------------------------------------------------------- applied, not just declared


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    for var in ("TG_REPORT_BOT_TOKEN", "TG_REPORT_CHAT_ID", "TG_REPORT_FORCE_DIRECT"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("TG_REPORT_CONFIG", str(tmp_path / "absent.json"))
    monkeypatch.delenv("TG_REPORT_NOTIFY_CMD", raising=False)
    monkeypatch.setenv("TG_REPORT_BOT_TOKEN", "TOK")
    monkeypatch.setenv("TG_REPORT_CHAT_ID", "42")


def test_document_uses_the_document_timeout_not_an_escalated_one(monkeypatch, tmp_path):
    """The old code forced max(timeout, 60) here — that was the whole defect."""
    monkeypatch.setenv("TG_REPORT_NOTIFY_CMD", "my-notifier")
    monkeypatch.setattr(tg_deliver.shutil, "which", lambda name: f"/bin/{name}")
    monkeypatch.setattr(
        tg_deliver.subprocess, "run", lambda *a, **k: type("P", (), {"returncode": 0, "stderr": ""})()
    )
    seen: list[float] = []
    monkeypatch.setattr(
        tg_send, "send_document", lambda p, **kw: seen.append(kw["timeout"])
    )

    doc = tmp_path / "a.md"
    doc.write_text("x")
    tg_deliver.deliver("summary", document=doc)

    assert seen == [tg_deliver.DOCUMENT_TIMEOUT]
    assert seen[0] <= tg_deliver.TOTAL_BUDGET


def test_text_uses_the_text_timeout(monkeypatch):
    monkeypatch.setattr(tg_deliver.shutil, "which", lambda _n: None)
    seen: list[float] = []
    monkeypatch.setattr(tg_send, "send_message", lambda t, **kw: seen.append(kw["timeout"]))

    tg_deliver.deliver("summary")
    assert seen == [tg_deliver.TEXT_TIMEOUT]


def test_lever_gets_the_text_timeout_and_a_hang_is_reported(monkeypatch):
    monkeypatch.setenv("TG_REPORT_NOTIFY_CMD", "my-notifier")
    monkeypatch.setattr(tg_deliver.shutil, "which", lambda name: f"/bin/{name}")

    def hang(*_a, **kwargs):
        raise tg_deliver.subprocess.TimeoutExpired(cmd="lever", timeout=kwargs["timeout"])

    monkeypatch.setattr(tg_deliver.subprocess, "run", hang)
    with pytest.raises(tg_deliver.DeliveryError) as exc:
        tg_deliver.deliver("summary")
    assert str(tg_deliver.TEXT_TIMEOUT) in str(exc.value)
