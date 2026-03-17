#!/usr/bin/env python3
"""
Stop Hook: Auto-speak text after trigger emoji in Claude's response.
Triggers VoiceMode TTS for the summary/TL;DR section.

This hook fires after every Claude response and extracts text
following the TRIGGER_EMOJI, then speaks it using VoiceMode CLI.
"""

import json
import subprocess
import sys
import re
from pathlib import Path

# ============================================
# VOICE SETTINGS
# ============================================
# OpenAI voices: nova, alloy, echo, fable, onyx, shimmer
# Kokoro voices: af_sky, af_bella, am_adam, am_michael
VOICE = "shimmer"  # Female, expressive voice
SPEED = 1.0        # Speed: 0.25 (slow) - 4.0 (fast), 1.0 = normal
TRIGGER_EMOJI = "🫦"  # Text after this emoji will be spoken
# ============================================


def extract_trigger_text(text: str) -> str | None:
    """Extract text after trigger emoji."""
    pattern = rf'{re.escape(TRIGGER_EMOJI)}\s*(.+?)(?:\n\n|\n---|$)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def get_last_assistant_message(transcript_path: str) -> str | None:
    """Read transcript JSONL and get last assistant message text."""
    path = Path(transcript_path)
    if not path.exists():
        return None

    last_message = None
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                msg = entry.get('message', {})
                if msg.get('role') == 'assistant':
                    content = msg.get('content', [])
                    if content and isinstance(content, list):
                        for item in content:
                            if item.get('type') == 'text':
                                last_message = item.get('text', '')
                    elif isinstance(content, str):
                        last_message = content
            except json.JSONDecodeError:
                continue

    return last_message


def speak(text: str):
    """Send text to VoiceMode TTS."""
    try:
        cmd = [
            'voicemode', 'converse',
            '-m', text,
            '--voice', VOICE,
            '--speed', str(SPEED),
            '--no-wait'
        ]
        subprocess.run(cmd, capture_output=True, timeout=30)
    except Exception as e:
        print(f"TTS error: {e}", file=sys.stderr)


def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    transcript_path = hook_input.get('transcript_path')
    if not transcript_path:
        sys.exit(0)

    # Don't run if this is a stop hook continuation
    if hook_input.get('stop_hook_active'):
        sys.exit(0)

    # Get last assistant message
    message = get_last_assistant_message(transcript_path)
    if not message:
        sys.exit(0)

    # Extract text after trigger emoji
    summary = extract_trigger_text(message)
    if summary:
        speak(summary)


if __name__ == '__main__':
    main()
