---
name: Audit Trail
description: This skill should be used when the user asks to "show audit trail", "why did we make this decision", "what happened after this", "trace this decision", "show decision history", "search audit log", or needs to understand the decision history and rationale behind code changes verified through coherence check.
version: 0.1.0
---

# Audit Trail: Decision History and Traceability

## Purpose

Provide bidirectional traversal of decision history, enabling users to understand why decisions were made, what happened after them, and search for specific patterns across verification sessions.

## Capabilities

### Bidirectional Traversal

**Forward**: "What happened after this decision?"
**Backward**: "Why did we make this decision?"
**Search**: "Show all security critic rejections"

### Persistence Layers

1. **In-memory** - Current session only
2. **File-based** - `.claude/coherence-audit/` directory
3. **Git commits** - Decision rationale in commit messages

## Usage Patterns

### View Session Audit Trail

```
/audit-trail show session-abc123
```

Returns complete decision history for verification session.

### Search by Criteria

```
/audit-trail search security critic rejections
```

Finds all sessions where security critic vetoed.

### Backward Trace

```
/audit-trail why was token storage changed to httpOnly
```

Traces decision back through critic evaluations to original requirement.

### Forward Trace

```
/audit-trail what files depend on auth/middleware.ts
```

Shows downstream impacts of changes (exposure analysis).

## Audit Log Format

```json
{
  "session_id": "session-abc123",
  "timestamp": "2026-02-03T14:30:00Z",
  "user": "reggie",
  "operation": "coherence-check",
  "scope": {
    "files": ["src/auth/login.ts"],
    "operation": "refactor to JWT"
  },
  "plan": {
    "acceptance_criteria": [
      "All tests pass",
      "No OWASP violations",
      "httpOnly cookies used"
    ],
    "critics": ["code", "security", "domain"]
  },
  "iterations": [
    {
      "iteration": 1,
      "code_critic": {"verdict": "approve", "reason": "..."},
      "security_critic": {"verdict": "veto", "reason": "XSS in error msgs"},
      "domain_critic": {"verdict": "approve", "reason": "..."}
    },
    {
      "iteration": 2,
      "code_critic": {"verdict": "approve", "reason": "..."},
      "security_critic": {"verdict": "approve", "reason": "Fixed XSS"},
      "domain_critic": {"verdict": "veto", "reason": "Missing audit log"}
    },
    {
      "iteration": 3,
      "all_critics": "approve"
    }
  ],
  "final_status": "approved",
  "cost": {"tokens": 15420, "overhead_pct": 38.6},
  "files_changed": ["src/auth/login.ts", "src/auth/middleware.ts"]
}
```

## Storage Locations

### Session Files

Path: `.claude/coherence-audit/{session_id}.json`

Created after each verification session with complete decision history.

### Git Commit Messages

Format:
```
feat(auth): refactor to JWT tokens

Verified by Code Coherence (session-abc123)
- 3 iterations required
- Security critic caught XSS vulnerability
- Domain critic ensured audit trail present

Critics: code✓ security✓ domain✓
Files: src/auth/login.ts src/auth/middleware.ts
```

### Search Index

Path: `.claude/coherence-audit/index.json`

Maintains searchable index of all sessions for fast querying.

## Search Queries

### By Critic

```
/audit-trail search "security critic rejections"
```

### By File

```
/audit-trail search "changes to src/auth/**"
```

### By Date Range

```
/audit-trail search "sessions from 2026-02-01 to 2026-02-03"
```

### By Iteration Count

```
/audit-trail search "sessions with >4 iterations"
```

## Exposure Analysis

When cited facts are corrected, identify downstream impacts:

```
/audit-trail exposure analyze "token storage decision"
```

Returns all sessions that depend on the token storage approach, enabling impact assessment of changes.

## Additional Resources

- **`references/traversal-examples.md`** - Detailed query examples
- **`references/audit-schema.md`** - Complete audit log JSON schema
