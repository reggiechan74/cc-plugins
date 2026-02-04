# Swiss Cheese Model: Multi-Layer Error Prevention

## Concept

The Swiss cheese model (Reason, 2000) describes how multiple imperfect defensive layers achieve system reliability through misaligned failure modes.

## Visual Metaphor

```
   Hazard → [Layer 1] → [Layer 2] → [Layer 3] → ✓ Prevented
              ⚪ holes     ⚪ holes     ⚪ holes

Key: Holes don't align, so hazard cannot pass through all layers
```

## Application to Code Coherence

### Layer Independence

Each critic specializes in different failure detection:

**Code Critic holes**:
- Misses: Security vulnerabilities (focuses on logic)
- Catches: Syntax errors, performance issues, complexity

**Security Critic holes**:
- Misses: Business logic violations (focuses on OWASP)
- Catches: XSS, injection, auth bypasses, data exposure

**Domain Critic holes**:
- Misses: Low-level implementation details (focuses on rules)
- Catches: Regulatory violations, business rule breaks, compliance

### Verification of Independence

Measure overlap between critic rejections:

```python
code_rejections = set(sessions_rejected_by_code_critic)
security_rejections = set(sessions_rejected_by_security_critic)

overlap = code_rejections & security_rejections
independence_score = 1 - (len(overlap) / len(code_rejections | security_rejections))

# Target: independence_score > 0.85 (orthogonal failure modes)
```

Low overlap confirms critics catch different error types.

## Empirical Results

From research paper (522 sessions):

| Critic Pair | Overlap | Independence Score |
|-------------|---------|-------------------|
| Code vs Security | 2.3% | 0.977 |
| Code vs Domain | 3.1% | 0.969 |
| Security vs Domain | 0.8% | 0.992 |

**Interpretation**: Near-perfect independence - critics rarely reject same sessions

## Design Implications

1. **Don't duplicate checks**: Each critic should have unique focus
2. **Optimize for orthogonality**: Prefer different model providers, different specializations
3. **Monitor overlap**: Warn if critics start catching same errors (indicates redundancy)
4. **Three layers optimal**: Research shows diminishing returns after 3 critics

## References

- Reason, J. (2000). "Human error: models and management." BMJ 320(7237), 768-770.
- Vijayaraghavan et al. (2026). Section 4.2.1: "Probabilistic Analysis of Cascaded Critique Layers"
