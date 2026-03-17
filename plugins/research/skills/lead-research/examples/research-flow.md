# Example: Research Workflow

## Query
"What are the best practices for implementing authentication in a Node.js API?"

## Step 1: Analyze Query

**Complexity:** Medium (comparison + best practices)
**Aspects:**
- Authentication methods (JWT, sessions, OAuth)
- Security best practices
- Node.js specific libraries
- Current trends (2025)

**Decision:** 3 parallel subagents

## Step 2: Plan Subagent Tasks

```
Subagent 1: Research authentication methods
- Focus: JWT vs sessions vs OAuth comparison
- Sources: Web (official docs, security blogs)
- Output: Comparison table with pros/cons

Subagent 2: Research security best practices
- Focus: OWASP guidelines, common vulnerabilities
- Sources: Web (security resources)
- Output: Security checklist

Subagent 3: Research Node.js libraries
- Focus: passport.js, jose, auth0
- Sources: Web (npm, GitHub) + codebase
- Output: Library comparison with examples
```

## Step 3: Spawn Subagents

```
Launch 3 search-subagent agents in parallel with above tasks.
Wait for all to complete.
```

## Step 4: Synthesize

Combine findings:
- JWT recommended for stateless APIs
- passport.js most popular, jose for pure JWT
- Critical: secure token storage, HTTPS, rate limiting

## Step 5: Add Citations

Spawn citation-agent with:
- Research report draft
- All sources from subagents

## Final Output

```markdown
## Research: Node.js API Authentication Best Practices

### Summary
JWT-based authentication is recommended for modern Node.js APIs due to stateless nature and scalability. Use established libraries (passport.js or jose) with proper security measures.

### Key Findings
- JWT preferred for stateless APIs, sessions for traditional web apps [1]
- passport.js offers flexibility, jose for lightweight JWT [2]
- Critical security: HTTPS, secure storage, rate limiting [3]

### Recommendations
1. Use JWT with short expiration + refresh tokens
2. Implement passport.js with JWT strategy
3. Follow OWASP authentication guidelines
4. Add rate limiting and brute-force protection

### Sources
- [1] Auth0 Documentation - JWT Best Practices
- [2] passport.js Official Guide
- [3] OWASP Authentication Cheatsheet
```
