#!/usr/bin/env python3
"""
Load context_map.md files into Claude Code context.
Outputs JSON with systemMessage for hooks.

Usage:
  - SessionStart hook: loads context at session start
  - Command hook: loads context for specific commands (e.g., /flow:research)
"""

import json
from pathlib import Path


def read_context_map(path: Path) -> str | None:
    """Read context_map.md if exists."""
    if path.exists():
        return path.read_text().strip()
    return None


def main():
    home = Path.home()
    cwd = Path.cwd()

    # Paths to check
    global_map = home / ".claude" / "context_map.md"
    local_map = cwd / ".claude" / "context_map.md"

    parts = []

    # Load global context_map
    global_content = read_context_map(global_map)
    if global_content:
        parts.append(f"## Global Context Map (~/.claude/context_map.md)\n\n{global_content}")

    # Load local context_map (higher priority)
    local_content = read_context_map(local_map)
    if local_content:
        parts.append(f"## Local Context Map (./.claude/context_map.md)\n\n{local_content}")

    # Build output
    if parts:
        message = "\n\n---\n\n".join(parts)
        output = {
            "continue": True,
            "systemMessage": f"<context-map>\n{message}\n</context-map>"
        }
    else:
        output = {
            "continue": True,
            "systemMessage": "<context-map>No context_map.md found. Run /system:init to create one.</context-map>"
        }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
