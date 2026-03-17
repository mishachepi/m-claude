---
name: Lead Research
description: |
  This skill should be used when the user asks to "research a topic", "исследуй тему", "изучи вопрос", "найди информацию о", "собери данные о", "сделай анализ", "multi-agent research", "глубокий анализ темы", or needs comprehensive information gathering before making decisions. Provides orchestrator-worker methodology for parallel research with subagents.
---

# Lead Research Methodology

Multi-agent research system using orchestrator-worker pattern for comprehensive information gathering.

## Core Architecture

**Orchestrator (You):** Plan research, spawn subagents, synthesize findings
**Workers (search-subagent):** Parallel exploration of different aspects
**Finalizer (citation-agent):** Add verified citations to report

## When to Use Multi-Agent Research

| Query Type | Approach |
|------------|----------|
| Simple fact | Direct answer, no subagents |
| Comparison (2-3 items) | 2-3 parallel subagents |
| Complex research | 4+ subagents with divided responsibilities |
| Deep analysis | Multiple rounds of subagent spawning |

## Research Process

### Step 1: Analyze Query

Determine complexity and required depth:
- What aspects need investigation?
- Which sources are relevant (web, docs, codebase)?
- How many parallel searches needed?

### Step 2: Plan Subagent Tasks

Create specific, non-overlapping tasks for each subagent:

```
Subagent 1: Research [aspect A] focusing on [specific angle]
Subagent 2: Research [aspect B] focusing on [different angle]
Subagent 3: Research [aspect C] with emphasis on [constraints]
```

**Critical:** Each subagent needs:
- Clear objective
- Specific scope boundaries
- Expected output format
- Tool guidance (web vs codebase)

### Step 3: Spawn Subagents in Parallel

Use Task tool with `research-agent` type or spawn `search-subagent` agents:

```
Launch multiple search-subagent agents in parallel:
- Each with distinct research aspect
- All running simultaneously
- Results collected when all complete
```

### Step 4: Synthesize Findings

Collect all subagent reports and:
- Identify key findings across all sources
- Resolve conflicting information
- Prioritize by relevance and authority
- Structure into coherent narrative

### Step 5: Add Citations

Spawn `citation-agent` to:
- Verify each claim has source
- Add proper citations
- Check source quality

## Output Format

Final research report structure:

```markdown
## Research: {Topic}

### Summary
{2-3 sentence overview of findings}

### Key Findings
- {Finding 1 with source}
- {Finding 2 with source}
- {Finding 3 with source}

### Detailed Analysis
{Synthesized information organized by theme}

### Recommendations
{Actionable suggestions based on research}

### Sources
- [Source 1](url) - {why authoritative}
- [Source 2](url) - {why authoritative}
```

## Best Practices

**Search Strategy:**
- Start with broad queries, then narrow
- Use current year in searches for recent info
- Check codebase first for existing patterns

**Subagent Coordination:**
- Give detailed task descriptions (not vague)
- Define clear boundaries between tasks
- Avoid duplicate work across subagents

**Quality Control:**
- Prioritize authoritative sources
- Note conflicting information
- Cite all claims

## Additional Resources

### Reference Files

For detailed methodology:
- **`references/methodology.md`** - Core principles from Anthropic research

### Examples

- **`examples/research-flow.md`** - Example research workflow
