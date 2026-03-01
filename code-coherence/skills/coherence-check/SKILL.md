---
name: Coherence Check
description: This skill should be used when the user asks to "check this code", "validate this", "verify this implementation", "is this correct", "review this code", "check for errors", "multi-agent verification", or mentions production-critical code, financial calculations, security implementations, or high-stakes operations. Provides comprehensive multi-agent verification workflow with specialized critic agents.
version: 0.1.0
---

# Coherence Check: Multi-Agent Verification

## Purpose

Execute comprehensive multi-agent verification for production-critical code using the "Team of Rivals" architecture. This skill orchestrates specialized critic agents with opposing incentives to catch errors before they reach production, achieving 92%+ reliability versus 60% single-agent baseline.

## When to Use

Activate this skill for high-stakes code where errors have significant consequences:
- Financial calculations and payment processing
- Authentication and security implementations
- Database migrations and schema changes
- Production deployments and releases
- Regulatory compliance code
- Data transformations affecting business operations

**Do not use** for exploratory coding, prototypes, or low-stakes experiments.

## Core Workflow

### Phase 1: Pre-Execution Planning

Before any code changes, create an execution plan with pre-declared acceptance criteria:

1. **Analyze the request** - Identify scope, files, and operations required
2. **Define success criteria** - Establish non-negotiable acceptance gates upfront
3. **Select critics** - Determine which critic agents are needed (code, security, domain)
4. **Estimate cost** - Calculate token overhead (typically +38.6%)
5. **Present plan to user** - Show plan with acceptance criteria and get approval

**Acceptance criteria must be**:
- Specific and measurable (not "good code" but "all tests pass, coverage >80%")
- Declared before execution (not emergent)
- Mapped to critic veto authority (which critic validates which criterion)

Example plan structure:
```
EXECUTION PLAN

Scope: Refactor authentication to JWT tokens
Files: src/auth/login.ts, src/auth/middleware.ts

SUCCESS CRITERIA (Pre-Declared):
✓ All existing auth tests pass
✓ No OWASP Top 10 vulnerabilities introduced
✓ Token storage uses httpOnly cookies (not localStorage)
✓ Token refresh logic handles 401 responses
✓ Code coverage maintained at 85%+

CRITICS ASSIGNED:
- Code Critic: Test pass rate, coverage, logic correctness
- Security Critic: OWASP compliance, token storage, auth flow
- Domain Critic: Session management business rules

RETRY BUDGET: 6 iterations before escalation
ESTIMATED COST: +40% tokens (~$0.15 additional)

VETO AUTHORITY: ANY critic can reject (unanimous approval required)
```

### Phase 2: Execution with Context Isolation

Execute changes while maintaining strict context boundaries:

1. **Executor implements changes** - Make code modifications per plan
2. **Isolate execution context** - Keep raw data and tool outputs separate from reasoning
3. **Generate audit trail** - Log all operations for traceability
4. **Prepare for critics** - Package outputs with relevant context only

**Context isolation rules**:
- Critics never see raw data (only schemas, summaries, sample rows)
- No full file contents unless explicitly needed for validation
- Working set can exceed context window through selective summaries
- Prevents context contamination and hallucination

### Phase 3: Multi-Layer Critic Evaluation

Run specialized critics in parallel (default) or sequential (optional):

#### Layer 1: Code Critic (87.8% catch rate)
- **Scope**: Syntax, logic, performance, style, complexity
- **Validates**:
  - Code compiles/runs without errors
  - Logic correctness and edge case handling
  - Performance anti-patterns
  - Naming conventions and code style
  - Integration with linters (ESLint, Prettier, etc.)
- **Veto threshold**: Strict by default (any issue), configurable per project
- **Model**: Opus (default), user-configurable

**Code Critic evaluation**:
```
EVALUATION: Code Changes

✓ Syntax: All files parse correctly
✓ Logic: JWT token generation handles expiration
✓ Performance: No N+1 queries introduced
❌ VETO: Missing error handling in token refresh
   Reason: 401 response from refresh endpoint not caught
   Impact: Users experience silent logout without feedback
   Fix: Add try-catch around fetch(), show re-login modal
```

#### Layer 2: Security Critic (catches what Layer 1 misses)
- **Scope**: OWASP Top 10, data exposure, timing attacks, supply chain
- **Validates**:
  - Authentication/Authorization correctness
  - Data validation and sanitization
  - Cryptography usage
  - Secret management
  - Integration with security scanners (Snyk, etc.)
- **Domains**: All security aspects (auth, data, crypto)
- **Model**: Opus (default), user-configurable

**Security Critic evaluation**:
```
EVALUATION: Security Review

✓ OWASP: No SQL injection vectors
✓ Auth: JWT signature validation correct
✓ Data: No sensitive data in logs
❌ VETO: XSS vulnerability in error messages
   Reason: User input echoed in error modal without escaping
   Impact: Reflected XSS if attacker controls username
   Fix: Use textContent instead of innerHTML for error display
```

#### Layer 3: Domain Critic (catches what both miss)
- **Scope**: Business rules, regulatory compliance, domain conventions
- **Validates**:
  - Domain-specific logic correctness
  - Compliance with business rules from `.claude/rules/`
  - Regulatory requirements (financial precision, audit trails)
  - Integration contracts and API guarantees
- **Specializations**: Financial, healthcare, legal (user-extensible)
- **Model**: Opus (default), user-configurable

**Domain Critic evaluation**:
```
EVALUATION: Domain Rules (Financial)

✓ Precision: Using Decimal type, not float
✓ Rounding: Banker's rounding applied
❌ VETO: Missing audit trail for token generation
   Reason: Financial regulations require logging all auth events
   Impact: Cannot prove compliance during audit
   Fix: Log token generation with user_id, timestamp, IP to audit table
```

### Phase 4: Consensus and Retry

Process critic verdicts following hierarchical veto authority:

1. **Check for vetoes** - ANY critic rejection triggers retry
2. **Unanimous approval required** - All critics must approve to advance
3. **Retry with context** - If vetoed, executor implements fixes (budget--)
4. **Exponential backoff** - Provide more context each retry
5. **Track retry history** - Log all iterations in audit trail
6. **Escalate if exhausted** - Human review required after retry budget depleted

**Retry loop example**:
```
Iteration 1: Security Critic vetoes (XSS vulnerability)
  → Executor fixes: Use textContent instead of innerHTML

Iteration 2: Domain Critic vetoes (missing audit trail)
  → Executor fixes: Add logging to audit table

Iteration 3: All Critics approve ✓
  → Advance to user review
```

**Retry budget**: 6 iterations (default), configurable per project
**Escalation**: Require human review, downgrade to single-agent, or fail with report

### Phase 5: User Review and Audit

Present final results with complete decision history:

1. **Summary report** - Show critic verdicts, retry count, final status
2. **Detailed report option** - Full audit trail with each critic's evaluation
3. **Cost breakdown** - Token usage per critic, time spent, overhead percentage
4. **Decision log** - Why each critic approved/rejected at each iteration
5. **Commit to audit trail** - Save decision history for future reference

**Summary report format**:
```
✓ COHERENCE CHECK COMPLETE

Status: All Critics Approved
Iterations: 3 (budget: 6 remaining)
Time: 4.2 minutes (verification: 1.8min, execution: 2.4min)
Cost: +38.6% tokens ($0.15 additional)

CRITIC VERDICTS:
✓ Code Critic: Approved (iteration 1)
✓ Security Critic: Approved (iteration 2, after XSS fix)
✓ Domain Critic: Approved (iteration 3, after audit trail added)

FILES CHANGED:
- src/auth/login.ts (+42, -15)
- src/auth/middleware.ts (+28, -8)

ACCEPTANCE CRITERIA MET:
✓ All existing auth tests pass (18/18)
✓ No OWASP Top 10 vulnerabilities
✓ Token storage uses httpOnly cookies
✓ Token refresh handles 401 responses
✓ Code coverage maintained (87%, was 85%)

View detailed audit trail: /audit-trail show session-abc123
```

## Configuration

Load settings from `.claude/code-coherence.local.md`:

### High-Stakes Pattern Matching

Define file patterns requiring automatic verification:
```yaml
highStakesPatterns:
  - "src/auth/**"
  - "src/payment/**"
  - "src/financial/**"
  - "database/migrations/**"
```

When user requests changes to files matching these patterns, proactively suggest coherence check.

### Critic Configuration

Enable/disable critics and select models:
```yaml
critics:
  code:
    enabled: true
    model: opus
    vetoThreshold: strict  # or critical-only
  security:
    enabled: true
    model: opus
  domain:
    enabled: true
    model: opus
    specialization: financial  # or healthcare, legal, custom
```

### Execution Preferences

```yaml
retryBudget: 6
consensusMode: unanimous  # unanimous, majority, weighted
parallelExecution: true   # parallel (faster) or sequential (cheaper)
autoVerify: false         # false = ask user, true = auto-run on high-stakes
acceptableErrorRate: 0.079  # 7.9% residual per research paper
```

### Cost Visibility

```yaml
costVisibility:
  showTokens: true      # Display token counts per critic
  showTime: true        # Show time breakdown
  estimateCost: true    # Estimate before running
```

## Integration with Other Skills

### Call plan-review After Planning

After creating execution plan, automatically invoke:
```
/plan-review
```

This validates the plan itself before execution, checking for completeness, clarity, and measurability.

### Use acceptance-criteria for Custom Gates

For domain-specific criteria not covered by pre-built templates:
```
/acceptance-criteria define for this authentication refactoring
```

### Log to audit-trail

All decisions automatically logged. Retrieve with:
```
/audit-trail show session-abc123
```

Or search:
```
/audit-trail search security critic rejections
```

### Verify independence with swiss-cheese-validation

After running coherence check, optionally validate critics have orthogonal failure modes:
```
/swiss-cheese-validation verify independence
```

## Cost-Benefit Analysis

**Investment**: 38.6% computational overhead (research-validated)
**Return**: 80% reduction in user-facing errors

**When justified**:
- Financial close operations (error cost >> compute cost)
- Security implementations (breach cost >> verification cost)
- Production deployments (downtime cost >> validation cost)
- Regulatory compliance (penalty cost >> overhead cost)

**When not justified**:
- Exploratory coding (iteration speed matters more)
- Throwaway prototypes (code won't reach production)
- Low-stakes scripts (error consequences minimal)

## Swiss Cheese Model in Practice

Three independent critics with misaligned failure modes:

**Code Critic** catches 87.8% of errors:
- Syntax errors
- Logic bugs
- Performance issues
- API misuse

**Security Critic** catches what Code Critic misses:
- XSS and injection vulnerabilities
- Authentication bypasses
- Data exposure
- Cryptographic weaknesses

**Domain Critic** catches what both miss:
- Business rule violations
- Regulatory non-compliance
- Domain-specific edge cases
- Integration contract violations

**Result**: Errors that slip through one layer encounter another. With orthogonal failure modes, 92.1% of errors caught before user exposure.

## Troubleshooting

### Critics disagree on same issue

**Problem**: Multiple critics veto for conflicting reasons
**Solution**: Escalate to human review with detailed rationale from each critic

### Retry budget exhausted

**Problem**: 6 iterations completed, critics still rejecting
**Solution**: Three escalation options (user-configurable):
1. Require human review (default)
2. Downgrade to single-agent mode (fast but less reliable)
3. Fail with detailed error report (safest for high-stakes)

### Cost exceeds expectations

**Problem**: Token usage higher than estimated
**Solution**:
- Switch to sequential critic evaluation (stop on first rejection)
- Disable less critical critics for specific tasks
- Adjust veto threshold to critical-only

### Critics approve but user sees issues

**Problem**: 7.9% residual error rate (expected per research)
**Cause**: Errors requiring external context (requirement ambiguity, subjective preferences, domain edge cases)
**Solution**: Refine acceptance criteria with more specificity, add custom domain critic

## Additional Resources

### Reference Files

For detailed patterns, advanced techniques, and implementation guides:
- **`references/research-paper.md`** - Original "Team of Rivals" research paper summary
- **`references/swiss-cheese-model.md`** - Error prevention through layered validation
- **`references/organizational-intelligence.md`** - How organizational principles apply to AI systems
- **`references/critic-patterns.md`** - Common critic evaluation patterns and heuristics
- **`references/cost-optimization.md`** - Strategies for reducing overhead while maintaining reliability

### Example Files

Working examples demonstrating coherence check in action:
- **`examples/financial-calculation.md`** - Multi-agent verification for compound interest calculator
- **`examples/auth-refactoring.md`** - JWT implementation with security and domain critics
- **`examples/data-migration.md`** - Database schema change with rollback validation

### Templates

Pre-built acceptance criteria for common scenarios:
- **`templates/financial.yaml`** - Financial calculation standards (precision, rounding, audit)
- **`templates/security.yaml`** - OWASP Top 10 checklist, auth patterns
- **`templates/performance.yaml`** - Latency SLAs, memory limits, query optimization

## Implementation Notes

**Triggering**: Broad patterns for accessibility - users don't need to know exact command
**Default behavior**: Interactive (ask user for approval), option for automation
**Output format**: Summary by default, detailed report on request
**Critic execution**: Parallel by default (faster), sequential option (cheaper)
**Consensus**: Unanimous approval required (any veto blocks), majority/weighted as options

**Integration points**:
- Agents: Planner, code-critic, security-critic, domain-critic work together
- Settings: Per-project configuration in `.claude/code-coherence.local.md`
- Audit: All decisions logged to `.claude/coherence-audit/` with git commit references
