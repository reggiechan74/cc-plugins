# Code Coherence Settings Template

Copy this file to `.claude/code-coherence.local.md` in your project root to configure the plugin.

```yaml
---
# High-stakes file patterns requiring verification
highStakesPatterns:
  - "src/auth/**"
  - "src/payment/**"
  - "src/financial/**"
  - "database/migrations/**"
  - "src/security/**"

# Maximum retry iterations before escalation
retryBudget: 6

# Critic configuration
critics:
  code:
    enabled: true
    model: opus
    vetoThreshold: strict  # strict | critical-only
  security:
    enabled: true
    model: opus
  domain:
    enabled: true
    model: opus
    specialization: financial  # financial | healthcare | legal | general

# Automatic verification
autoVerify: false  # false = ask user, true = auto-run on high-stakes

# Acceptable residual error rate (from research: 7.9%)
acceptableErrorRate: 0.079

# Consensus mode
consensusMode: unanimous  # unanimous | majority | weighted

# Execution mode
parallelExecution: true  # true = faster, false = cheaper

# Cost visibility
costVisibility:
  showTokens: true
  showTime: true
  estimateCost: true

# Escalation strategy when retry budget exhausted
escalationStrategy: human-review  # human-review | downgrade | fail-with-report
---

# Project-Specific Domain Rules

## Financial Calculations

All financial code must:
- Use Decimal type (not float/double)
- Apply banker's rounding (round half to even)
- Log all operations to audit trail
- Format currency to 2 decimal places
- Handle currency conversions explicitly

## Security Requirements

All authentication code must:
- Use httpOnly cookies for tokens
- Implement CSRF protection
- Rate limit authentication endpoints
- Log all auth events

## Performance Standards

All API endpoints must:
- Respond within 200ms (95th percentile)
- Use database indexes appropriately
- Implement caching for expensive operations
```
