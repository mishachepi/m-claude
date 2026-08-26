# Lead Research Plugin

> Multi-agent research — orchestrator methodology for parallel research with subagents.

## Skills

| Skill | Description |
|-------|-------------|
| `lead-research` | Orchestrator methodology for parallel research with subagents |

## Agents

| Agent | Color | Description |
|-------|-------|-------------|
| `lead-research:research-agent` | cyan | Information gathering (web, docs, codebase) |
| `lead-research:search-subagent` | cyan | Parallel exploration worker |
| `lead-research:citation-agent` | yellow | Verify and add citations to report |

Agents must be invoked with the `lead-research:` prefix — the bare agent name fails with `Agent type not found`.

## Flow

```
Query → Analyze complexity → Spawn N subagents → Synthesize → Cite → Report
```

| Query Type | Approach |
|------------|----------|
| Simple fact | Direct answer |
| Comparison | 2-3 parallel subagents |
| Complex research | 4+ subagents |
| Deep analysis | Multiple rounds |
