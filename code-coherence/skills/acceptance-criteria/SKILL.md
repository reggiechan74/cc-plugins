---
name: Acceptance Criteria
description: This skill should be used when the user asks to "define acceptance criteria", "what are the success criteria", "set quality gates", "establish acceptance tests", "define what success looks like", or needs to specify pre-declared success criteria before code execution begins.
version: 0.1.0
---

# Acceptance Criteria: Define Success Before Execution

## Purpose

Define specific, measurable acceptance criteria before any code execution, following test-driven development principles. Criteria serve as quality gates that critics evaluate with veto authority.

## Criteria Requirements

**Must be**:
- Specific (not "good code" but "all 18 tests pass")
- Measurable (binary pass/fail)
- Pre-declared (before execution)
- Mapped to critics (clear validation responsibility)

## Input Formats

### Natural Language (Default)

```
/acceptance-criteria define for authentication refactoring:
- All existing tests must pass
- No OWASP Top 10 vulnerabilities
- Token storage uses httpOnly cookies
- Coverage maintains above 85%
```

Parsed automatically into structured format.

### Structured YAML

```yaml
criteria:
  - name: Test Pass Rate
    description: All existing auth tests pass
    validator: code-critic
    threshold: 100%

  - name: Security Compliance
    description: No OWASP Top 10 vulnerabilities introduced
    validator: security-critic
    checklist: OWASP-2021

  - name: Code Coverage
    description: Maintain test coverage
    validator: code-critic
    threshold: ">= 85%"
```

### Template-Based

```
/acceptance-criteria use template financial
```

Loads pre-built criteria set for financial calculations.

## Pre-Built Templates

### Financial Template

```yaml
---
domain: financial
criteria:
  - Decimal precision maintained (no float arithmetic)
  - Banker's rounding applied (IEEE 754)
  - All operations logged to audit trail
  - Results formatted to 2 decimal places
  - Currency conversion explicit (no implicit conversions)
validators:
  - domain-critic (financial specialization)
  - code-critic (logic verification)
---
```

### Security Template

```yaml
---
domain: security
criteria:
  - No SQL injection vectors (parameterized queries only)
  - No XSS vulnerabilities (output escaping verified)
  - Authentication bypass prevented (auth required on protected routes)
  - HTTPS enforced (no plaintext transmission)
  - Secrets not in code (environment variables used)
  - Password hashing with bcrypt/argon2
validators:
  - security-critic
  - code-critic (implementation check)
---
```

### Performance Template

```yaml
---
domain: performance
criteria:
  - API latency < 200ms (95th percentile)
  - Database queries < 10ms
  - No N+1 query patterns
  - Memory usage < 512MB
  - Caching implemented for expensive operations
validators:
  - code-critic (performance checks)
  - domain-critic (SLA validation)
---
```

## Validation During Execution

Each criterion evaluated by assigned critic:

**Code Critic checks**:
- Test pass rates
- Code coverage percentages
- Performance metrics
- Logic correctness

**Security Critic checks**:
- OWASP compliance
- Authentication patterns
- Data exposure risks
- Cryptography usage

**Domain Critic checks**:
- Business rule compliance
- Regulatory requirements
- Domain-specific conventions
- Integration contracts

## Criteria Evolution

Update criteria based on lessons learned:

```
/acceptance-criteria add to financial template:
- Handle leap year calculations correctly
- Timezone conversions must be explicit
```

Criteria library grows with project experience.

## Additional Resources

- **`templates/financial.yaml`** - Financial calculation standards
- **`templates/security.yaml`** - OWASP checklist and auth patterns
- **`templates/performance.yaml`** - Latency SLAs and optimization
- **`references/criteria-library.md`** - All available criteria sets
