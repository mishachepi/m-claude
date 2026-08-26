# Lead Research Plugin

Multi-agent research with parallel subagents.

## Components

| Type | Name | Color | Purpose |
|------|------|-------|---------|
| Skill | `lead-research` | — | Orchestrator methodology for parallel research |
| Agent | `lead-research:research-agent` | cyan | Information gathering (web, docs, codebase) |
| Agent | `lead-research:search-subagent` | cyan | Parallel exploration worker |
| Agent | `lead-research:citation-agent` | yellow | Verify and add citations to report |

Agents require the `lead-research:` prefix — the bare name fails with `Agent type not found`.

## Flow

```
Query → Analyze complexity → Spawn N subagents → Synthesize → Cite → Report
```
