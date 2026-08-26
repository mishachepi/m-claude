# Anthropic Research Methodology

Key principles from Anthropic's multi-agent research system.

## Why Multi-Agent

- **Compression:** Subagents distill insights from vast corpus, return only essential tokens
- **Parallelism:** Explore different aspects simultaneously
- **Separation of concerns:** Each subagent has distinct tools, prompts, trajectories
- **Reduced path dependency:** Independent investigations avoid tunnel vision

## Performance Insights

Token usage explains 80% of performance variance. Multi-agent architecture scales token usage for tasks exceeding single agent limits.

**Trade-off:** Agents use ~4x more tokens than chat, multi-agent ~15x more. Use for high-value tasks.

## Orchestrator Responsibilities

1. **Decompose queries** into non-overlapping subtasks
2. **Describe tasks clearly** — objective, output format, tool guidance, boundaries
3. **Scale effort to complexity** — simple queries need 1 agent, complex need 10+
4. **Synthesize results** — resolve conflicts, prioritize authoritative sources

## Subagent Design

Each subagent needs:
- Specific objective (not vague "research X")
- Clear output format
- Tool guidance (which sources to use)
- Scope boundaries (what NOT to research)

**Anti-pattern:** Vague instructions like "research semiconductors" → duplicated work, missed coverage.

## Search Strategy

1. **Start wide, then narrow** — broad queries first, then specific
2. **Evaluate before drilling** — check what's available
3. **Parallel tool calls** — 3+ searches simultaneously
4. **Current year in queries** — for recent information

## Tool Selection

- Match tool to intent (web for external, grep for codebase)
- Examine all available tools first
- Prefer specialized tools over generic
- Bad tool descriptions derail agents

## Quality Signals

- **Source authority:** Official docs > blogs > forums
- **Recency:** Last 1-2 years preferred
- **Specificity:** Concrete facts > general statements
- **Verification:** Cross-reference multiple sources

## Common Failures

| Failure | Solution |
|---------|----------|
| Too many subagents for simple query | Scale effort to complexity |
| Duplicate work across subagents | Clear task boundaries |
| Endless searching | Set stopping criteria |
| Poor source selection | Explicit quality heuristics |
| Vague task descriptions | Detailed objectives + format |

## Subagent Output

Subagents should write to filesystem (not through lead agent) to:
- Minimize information loss
- Reduce token overhead
- Preserve structured outputs
