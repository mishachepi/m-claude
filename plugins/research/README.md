# Research Plugin

> Multi-agent research and structured brainstorming.

## Skills

| Skill | Description |
|-------|-------------|
| `lead-research` | Orchestrator methodology for parallel research with subagents |
| `brainshtorm` | Deep brainstorming through structured interview → spec document |

## Agents

| Agent | Color | Description |
|-------|-------|-------------|
| `research` | cyan | Information gathering (web, docs, codebase) |
| `search-subagent` | cyan | Parallel exploration worker |
| `citation-agent` | yellow | Verify and add citations to report |

## Flows

### Research

```
Query → Analyze complexity → Spawn N subagents → Synthesize → Cite → Report
```

| Query Type | Approach |
|------------|----------|
| Simple fact | Direct answer |
| Comparison | 2-3 parallel subagents |
| Complex research | 4+ subagents |
| Deep analysis | Multiple rounds |

### Brainstorm

```
Idea → Interview (5+ rounds) → Synthesize → Write spec → Review
```

Rounds: Problem Space → Solution Vision → Technical Approach → Edge Cases → Scope & Priorities
