---
name: Plan Review
description: This skill should be used when the user asks to "review the plan", "check the execution plan", "validate this plan", "is this plan good", or automatically after the planner agent creates an execution plan. Validates plans for completeness, clarity, measurability, and proper acceptance criteria before execution begins.
version: 0.1.0
---

# Plan Review: Validate Execution Plans

## Purpose

Review and validate execution plans before code changes begin, ensuring plans have clear acceptance criteria, appropriate critic assignments, and realistic scope.

## When to Use

- After planner agent creates execution plan
- When user explicitly requests plan review
- Before high-stakes operations (configured in highStakesPatterns)

## Validation Criteria

### Completeness Checks

✓ **Scope defined**: Files, operations, and boundaries clear
✓ **Success criteria present**: At least 3 specific, measurable criteria
✓ **Critic assignment**: Each criterion mapped to responsible critic
✓ **Retry budget set**: Escalation path defined
✓ **Cost estimate included**: Token overhead calculated

### Quality Gates

**Acceptance criteria must be**:
- Specific (not "good code" but "all tests pass, coverage >80%")
- Measurable (binary pass/fail, not subjective)
- Pre-declared (before execution, not emergent)
- Mapped to critics (clear veto authority assignment)

**Domain-specific patterns**:
- Financial: Must specify precision, rounding method, audit requirements
- Security: Must reference OWASP checklist, auth patterns
- Performance: Must define latency SLAs, memory limits

## Review Process

1. **Parse plan structure** - Extract scope, criteria, critics, budget
2. **Check completeness** - Verify all required sections present
3. **Validate criteria** - Ensure specific and measurable
4. **Verify critic mapping** - Each criterion has responsible critic
5. **Check domain patterns** - Apply domain-specific requirements
6. **Estimate feasibility** - Scope appropriate for retry budget
7. **Present findings** - Show issues and recommendations

## Example Reviews

### Good Plan

```
EXECUTION PLAN ✓

Scope: Refactor auth to JWT ✓
Files: src/auth/*.ts ✓

SUCCESS CRITERIA: ✓
✓ All 18 existing tests pass (Code Critic validates)
✓ No OWASP Top 10 violations (Security Critic validates)
✓ Token storage uses httpOnly cookies (Security Critic validates)
✓ Token refresh handles 401 (Code Critic validates)
✓ Coverage maintains 85%+ (Code Critic validates)

Critics: code, security ✓
Budget: 6 iterations ✓
Cost: +40% tokens ($0.15) ✓
```

### Plan Needs Improvement

```
EXECUTION PLAN ❌

Scope: Make the code better ❌ TOO VAGUE
Files: Not specified ❌ MISSING

SUCCESS CRITERIA: ❌
- Code should be high quality ❌ NOT MEASURABLE
- No bugs ❌ NOT SPECIFIC
- Fast performance ❌ NO THRESHOLD

Critics: None assigned ❌
Budget: Not set ❌
```

**Required fixes**:
1. Define specific scope and files
2. Make criteria measurable (e.g., "all tests pass", "latency <200ms")
3. Assign critics to each criterion
4. Set retry budget

## Configuration

Plans automatically reviewed when `autoVerify: true` in settings.

For manual review, invoke explicitly after planning phase.

## Additional Resources

- **`references/acceptance-criteria-patterns.md`** - Domain-specific criteria templates
- **`references/plan-examples.md`** - Good and bad plan examples
