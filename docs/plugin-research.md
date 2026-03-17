# Research Plugin

Research and brainstorming — multi-agent research with parallel subagents, structured spec creation.

## Components

| Type | Name | Color | Purpose |
|------|------|-------|---------|
| Skill | `lead-research` | — | Orchestrator methodology for parallel research |
| Skill | `brainshtorm` | — | Deep brainstorming → spec document |
| Agent | `research` | cyan | Information gathering (web, docs, codebase) |
| Agent | `search-subagent` | cyan | Parallel exploration worker |
| Agent | `citation-agent` | yellow | Verify and add citations to report |

## Flows

**Research:**
```
Query → Analyze complexity → Spawn N subagents → Synthesize → Cite → Report
```

**Brainstorm:**
```
Idea → Interview (5+ rounds) → Synthesize → Write spec → Review
```
