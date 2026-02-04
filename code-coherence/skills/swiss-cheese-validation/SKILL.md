---
name: Swiss Cheese Validation
description: This skill should be used when the user asks to "verify critic independence", "check for overlapping failures", "validate swiss cheese model", "are the critics independent", "measure orthogonality", or needs to verify that multiple critic layers have misaligned failure modes as required by the swiss cheese model.
version: 0.1.0
---

# Swiss Cheese Validation: Verify Critic Independence

## Purpose

Verify that multiple critic layers have orthogonal failure modes, ensuring the Swiss cheese model is working correctly. Measure overlap in critic rejections and warn if critics catch the same errors.

## Theory

The Swiss cheese model achieves reliability through **misaligned holes**:
- Each critic has failure modes (errors it misses)
- Holes don't align across critics
- Errors caught by different critics don't overlap significantly

**Target**: Independence score > 0.85 (less than 15% overlap)

## Validation Process

### Measure Overlap

Analyze rejection patterns across sessions:

```python
code_rejections = sessions_where_code_critic_vetoed
security_rejections = sessions_where_security_critic_vetoed

overlap = code_rejections ∩ security_rejections
union = code_rejections ∪ security_rejections

independence_score = 1 - (|overlap| / |union|)
```

**Interpretation**:
- Score > 0.90: Excellent independence (orthogonal)
- Score 0.80-0.90: Good independence (acceptable)
- Score < 0.80: Poor independence (critics overlapping)

### Expected Results

From research paper (522 sessions):

| Critic Pair | Overlap | Independence |
|-------------|---------|--------------|
| Code vs Security | 2.3% | 0.977 ✓ |
| Code vs Domain | 3.1% | 0.969 ✓ |
| Security vs Domain | 0.8% | 0.992 ✓ |

### Warning Indicators

**High overlap detected** when:
- Same sessions rejected by multiple critics
- Similar rejection reasons across critics
- Independence score < 0.80

**Causes**:
- Critics using same model/provider (cognitive monoculture)
- Similar training data
- Overlapping validation logic

**Solutions**:
- Use different model providers per critic
- Adjust critic specializations
- Review critic prompts for duplication

## Configuration

### Layer Definition

**Default (hardcoded)**:
```yaml
layers:
  - code-critic
  - security-critic
  - domain-critic
```

**Custom (user-configured)**:
```yaml
layers:
  - code-critic
  - security-critic
  - financial-critic
  - performance-critic
```

**Dynamic (context-based)**:
```yaml
layers:
  financial_files: [code-critic, financial-critic]
  auth_files: [code-critic, security-critic]
  api_files: [code-critic, performance-critic]
```

## Validation Report

```
SWISS CHEESE VALIDATION REPORT

Analysis Period: Last 30 days (87 sessions)

INDEPENDENCE SCORES:
✓ Code vs Security: 0.981 (excellent)
✓ Code vs Domain: 0.973 (excellent)
✓ Security vs Domain: 0.995 (excellent)

OVERLAP ANALYSIS:
- Code & Security both rejected: 2 sessions (2.3%)
  Reasons: Authentication logic had both syntax error AND security flaw

- Code & Domain both rejected: 3 sessions (3.4%)
  Reasons: Financial calculation had logic error AND violated precision rules

- Security & Domain both rejected: 1 session (1.1%)
  Reasons: Data validation missing AND violated GDPR requirements

CONCLUSION: ✓ Swiss cheese model working correctly
All critics demonstrate orthogonal failure modes.
```

### When Validation Fails

```
⚠ INDEPENDENCE CONCERN DETECTED

Analysis: Last 30 days (87 sessions)

POOR INDEPENDENCE:
❌ Code vs Security: 0.72 (poor - 28% overlap)

ISSUE: Both critics rejecting same sessions frequently
Sample overlaps:
- Session #42: Both caught missing input validation
- Session #55: Both caught SQL injection in user input
- Session #61: Both caught unescaped HTML in output

ROOT CAUSE: Security critic checking code-level details
RECOMMENDATION: Refocus security critic on OWASP patterns only,
let code critic handle general logic validation
```

## Active Monitoring

Run validation automatically after every 20 sessions:

```yaml
monitoring:
  frequency: every_20_sessions
  alert_threshold: 0.80
  action: warn_user
```

## Additional Resources

- **`references/independence-verification.md`** - Statistical methods for measuring orthogonality
- **`references/failure-mode-analysis.md`** - Common causes of critic overlap
- **`examples/poor-independence.md`** - Case study of overlapping critics and remediation
