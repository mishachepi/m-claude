# Voice Output for Claude Code

Automatically speak Claude's response summaries (text after 🟢 emoji) using TTS.

## How It Works

```
Claude responds → Stop Hook triggers → Extract text after 🟢 → VoiceMode TTS → 🔊
```

## Requirements

- macOS (tested on Apple Silicon)
- Python 3.10+
- OpenAI API key (for cloud TTS) OR Kokoro (for local TTS)

## Installation

### Step 1: Install System Dependencies

```bash
brew install portaudio ffmpeg
```

### Step 2: Install VoiceMode

```bash
uvx voice-mode-install --yes
```

### Step 3: Set OpenAI API Key

```bash
# Add to ~/.zshrc:
export OPENAI_API_KEY="sk-..."

# Reload:
source ~/.zshrc
```

### Step 4: Copy Hook Script

```bash
mkdir -p ~/.claude/hooks
cp speak-summary.py ~/.claude/hooks/
```

### Step 5: Configure Claude Code Hook

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/speak-summary.py"
          }
        ]
      }
    ]
  }
}
```

### Step 6: Restart Claude Code

```bash
# Exit current session
/exit

# Start new session
claude
```

## Optional: Add MCP Server

For manual voice control (explicit `speak` commands):

```bash
claude mcp add --scope user voicemode -- uvx voice-mode
```

## Configuration

Edit `~/.claude/hooks/speak-summary.py` to change voice settings:

```python
# Available OpenAI voices: nova, alloy, echo, fable, onyx, shimmer
VOICE = "shimmer"  # Female, expressive

# Speed: 0.25 (slow) to 4.0 (fast)
SPEED = 1.0
```

### Voice Options

| Voice | Type | Description |
|-------|------|-------------|
| `nova` | Female | Warm, friendly |
| `alloy` | Neutral | Balanced |
| `echo` | Male | Soft, calm |
| `fable` | Neutral | British accent |
| `onyx` | Male | Deep, authoritative |
| `shimmer` | Female | Bright, expressive |

## Pricing

OpenAI TTS costs ~$0.01 per minute of speech (~1 cent) (actual on 18.01.2026).

For short summaries (~30 chars): ~$0.0005 per response.

## Local/Free Alternative: Kokoro

Install Kokoro for offline TTS (no API costs):

```bash
voicemode kokoro install
```

Then change voice in script:
```python
VOICE = "af_sky"  # Kokoro voice
```

## Troubleshooting

### Hook not working
1. Restart Claude Code (`/exit` → `claude`)
2. Check config: `cat ~/.claude/settings.json | grep -A10 hooks`

### No audio
1. Test VoiceMode: `voicemode converse -m "test" --no-wait`
2. Check API key: `echo $OPENAI_API_KEY`

### Script error
```bash
echo '{"transcript_path": "/tmp/test.jsonl"}' | python3 ~/.claude/hooks/speak-summary.py
```

## Files

```
~/.claude/
├── settings.json              # Hook configuration
└── hooks/
    └── speak-summary.py       # TTS hook script

~/.local/bin/
└── voicemode                  # VoiceMode CLI
```

## Security

VoiceMode is open source (MIT license): https://github.com/mbailey/voicemode

- Local mode available (Kokoro) - no external calls
- No data stored by default
