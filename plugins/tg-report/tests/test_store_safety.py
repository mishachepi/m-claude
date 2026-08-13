"""The answer store must never delete files it did not write.

`TG_REPORT_STATE_DIR` is operator input. The original prune removed every `*.md`
older than the retention window under that directory — one wrong export pointed
at a notes folder and it would quietly eat someone's writing. Silent data loss
from a reporting plugin is not an acceptable failure mode, so both guards below
are tested from the attacker's side: what happens when the directory is *not* ours.
"""

from __future__ import annotations

import os
import stat
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "hooks"))

import tg_summary  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_state(monkeypatch, tmp_path):
    monkeypatch.setenv("TG_REPORT_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("TG_REPORT_LABEL", "pilot")


def age(path: Path, days: int) -> None:
    old = time.time() - days * 86400
    os.utime(path, (old, old))


# ------------------------------------------------------- foreign directory guard


def test_prune_refuses_a_directory_it_did_not_create(monkeypatch, tmp_path):
    """The nightmare case: state dir pointed at a notes folder."""
    notes = tmp_path / "my-notes"
    (notes / "answers").mkdir(parents=True)
    precious = notes / "answers" / "important-note.md"
    precious.write_text("a year of writing")
    age(precious, 400)

    monkeypatch.setenv("TG_REPORT_STATE_DIR", str(notes))
    tg_summary.prune_answers()

    assert precious.exists(), "prune deleted a file in a directory it never created"


def test_prune_refuses_even_when_names_look_like_answers(monkeypatch, tmp_path):
    """Marker absent ⇒ nothing is touched, however tempting the filename."""
    foreign = tmp_path / "foreign"
    (foreign / "answers").mkdir(parents=True)
    decoy = foreign / "answers" / "abc123.md"
    decoy.write_text("not ours")
    age(decoy, 400)

    monkeypatch.setenv("TG_REPORT_STATE_DIR", str(foreign))
    tg_summary.prune_answers()

    assert decoy.exists()


# ------------------------------------------------------------- filename guard


def test_prune_spares_foreign_files_inside_our_own_store():
    """Even in our store, only files we named are removable."""
    answers = tg_summary.answers_dir()
    stranger = answers / "notes.md"
    stranger.write_text("dropped here by a human")
    age(stranger, 400)

    tg_summary.prune_answers()

    assert stranger.exists()


def test_prune_removes_expired_answers_and_keeps_fresh_ones():
    old_id, old_path = tg_summary.store_answer("old answer", "pilot")
    fresh_id, fresh_path = tg_summary.store_answer("fresh answer", "pilot")
    age(old_path, tg_summary.ANSWER_RETENTION_DAYS + 1)

    tg_summary.prune_answers()

    assert not old_path.exists()
    assert fresh_path.exists()
    assert old_id != fresh_id


def test_prune_spares_subdirectories():
    answers = tg_summary.answers_dir()
    nested = answers / "aaaaaa.md"
    nested.mkdir()
    age(nested, 400)

    tg_summary.prune_answers()

    assert nested.is_dir()


def test_marker_is_created_by_the_store():
    answers = tg_summary.answers_dir()
    assert (answers / tg_summary.STORE_MARKER).exists()


def test_retention_zero_disables_pruning(monkeypatch):
    _, path = tg_summary.store_answer("x", "pilot")
    age(path, 9999)
    monkeypatch.setattr(tg_summary, "ANSWER_RETENTION_DAYS", 0)

    tg_summary.prune_answers()
    assert path.exists()


# ------------------------------------------------------------------ permissions


def test_stored_answers_are_not_world_readable():
    """A verbatim assistant answer is whatever the agent was working on."""
    _, path = tg_summary.store_answer("secret-ish content", "pilot")
    mode = stat.S_IMODE(path.stat().st_mode)
    assert mode & (stat.S_IRGRP | stat.S_IROTH) == 0, oct(mode)


def test_store_directory_is_private():
    answers = tg_summary.answers_dir()
    mode = stat.S_IMODE(answers.stat().st_mode)
    assert mode & (stat.S_IRGRP | stat.S_IROTH | stat.S_IXGRP | stat.S_IXOTH) == 0, oct(mode)
