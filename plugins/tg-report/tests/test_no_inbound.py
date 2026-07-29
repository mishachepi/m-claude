"""The outbound-only invariant, enforced instead of promised.

A second `getUpdates` consumer on the mesh bot silently steals updates from the
capture daemon — it already happened once and the messages were lost for good,
because the Bot API keeps no history. So this plugin must never grow an inbound
path, and "must never" is worth exactly as much as the test behind it.

The check ignores docstrings and comments — prose *about* the ban (this file,
the module docstrings explaining it) must stay legal, while a real call cannot:
invoking a Bot API method requires the method name in an executable string or an
identifier, never in a docstring.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]

# Bot API surface that would make this plugin an inbound consumer.
FORBIDDEN = ("getUpdates", "setWebhook", "deleteWebhook", "getWebhookInfo", "webhook")


def python_sources() -> list[Path]:
    return sorted(
        p
        for p in PLUGIN_ROOT.rglob("*.py")
        if "tests" not in p.relative_to(PLUGIN_ROOT).parts
    )


def executable_strings_and_names(tree: ast.AST) -> list[str]:
    """Every string constant and identifier that is not a docstring."""
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                docstrings.add(id(body[0].value))

    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) not in docstrings:
                found.append(node.value)
        elif isinstance(node, ast.Name):
            found.append(node.id)
        elif isinstance(node, ast.Attribute):
            found.append(node.attr)
    return found


def test_there_are_python_sources_to_check():
    """Guards the guard: an empty glob would make every check below vacuous."""
    names = {p.name for p in python_sources()}
    assert {"tg_send.py", "tg_deliver.py", "tg_summary.py"} <= names


def test_no_inbound_api_in_executable_code():
    offenders = []
    for source in python_sources():
        tree = ast.parse(source.read_text(), filename=str(source))
        for value in executable_strings_and_names(tree):
            for banned in FORBIDDEN:
                if banned.lower() in value.lower():
                    offenders.append(f"{source.name}: {banned} in {value!r}")
    assert not offenders, "inbound Telegram API reached executable code: " + "; ".join(offenders)


def test_the_check_would_catch_a_real_violation():
    """A check that cannot fail is not a check."""
    tree = ast.parse('"""Docstring mentioning getUpdates is fine."""\n'
                     'URL = f"{root}/bot{token}/getUpdates"\n')
    values = executable_strings_and_names(tree)
    assert any("getUpdates" in v for v in values)


def test_docstring_prose_is_not_flagged():
    tree = ast.parse('"""This module never calls getUpdates or a webhook."""\nX = 1\n')
    values = executable_strings_and_names(tree)
    assert not any("getUpdates" in v for v in values)


def test_hooks_json_registers_only_stop():
    hooks = json.loads((PLUGIN_ROOT / "hooks" / "hooks.json").read_text())
    assert list(hooks["hooks"]) == ["Stop"]
    command = hooks["hooks"]["Stop"][0]["hooks"][0]["command"]
    assert "${CLAUDE_PLUGIN_ROOT}" in command
    assert "tg_summary.py" in command


def test_plugin_declares_no_long_running_process():
    """No daemon, no launchd, no polling loop hiding in the manifest."""
    manifest = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "tg-report"
    assert "mcpServers" not in manifest
