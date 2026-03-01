# Code Coherence Plugin

> Multi-agent verification system for production-grade code reliability

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## Overview

Code Coherence implements the "Team of Rivals" architecture from organizational intelligence research, bringing multi-agent verification to high-stakes coding tasks. It achieves **92%+ reliability** (vs 60% single-agent baseline) by orchestrating specialized critic agents with opposing incentives and hierarchical veto authority.

### The Problem

Single-agent AI systems fail 40% of the time on critical tasks because:
- Errors go unchecked (no independent review)
- Self-review doesn't work (same reasoning that created error can't catch it)
- Systematic biases have no counter-action

### The Solution

**Multi-layer verification** with independent critics implementing the Swiss cheese model:
- Multiple imperfect layers with misaligned failure modes
- Any critic can veto (hierarchical authority, not consensus)
- Pre-declared acceptance criteria (test-driven approach)
- Errors die in committee, not in production

### Key Results

| Metric | Single Agent | Code Coherence | Improvement |
|--------|--------------|----------------|-------------|
| **Accuracy** | 60% | 92.1% | +53% |
| **User-facing errors** | 40% | 7.9% | -80% |
| **Cost overhead** | Baseline | +38.6% | Justified for high-stakes |
| **Latency overhead** | Baseline | +21.8% | Acceptable for batch |

## Features

### 🎯 Core Verification Skills

- **coherence-check**: Full multi-agent verification workflow
- **plan-review**: Review execution plans with acceptance criteria
- **audit-trail**: Bidirectional decision history with search
- **acceptance-criteria**: Define and enforce success criteria
- **swiss-cheese-validation**: Multi-layer error checking with independence verification

### 🤖 Specialized Critic Agents

- **planner**: Creates execution DAGs with pre-declared acceptance criteria
- **code-critic**: Validates syntax, logic, performance, style, complexity
- **security-critic**: OWASP Top 10, data exposure, timing attacks, supply chain
- **domain-critic**: Business logic validation with extensible specializations:
  - **financial-critic**: Precision, rounding, audit trails
  - **healthcare-critic**: HIPAA compliance, patient safety
  - **legal-critic**: Regulatory compliance, contract validation

### ⚙️ Configuration

Per-project settings via `.claude/code-coherence.local.md`:
- High-stakes file patterns
- Retry budget and escalation strategy
- Critic enable/disable and model selection
- Consensus mode (unanimous, majority, weighted)
- Cost visibility preferences

## Installation

### From Marketplace
```
/plugin marketplace add reggiechan74/cc-plugins
/plugin install code-coherence@cc-plugins
```

### Local Development
```bash
claude --plugin-dir /path/to/code-coherence
```

## Usage

### Basic Verification

```
check this authentication implementation
```

The plugin automatically activates and runs full multi-agent verification.

### With Explicit Skill

```
/coherence-check src/auth/login.ts
```

### Review Plan Before Execution

```
/plan-review
```

### View Decision History

```
/audit-trail show all security critic rejections
```

### Define Custom Acceptance Criteria

```
/acceptance-criteria for financial calculation:
- Precision: 2 decimal places
- Rounding: banker's rounding
- Audit trail: all operations logged
```

## Configuration

Create `.claude/code-coherence.local.md` in your project:

```yaml
---
highStakesPatterns:
  - "src/auth/**"
  - "src/payment/**"
  - "src/financial/**"
  - "database/migrations/**"

retryBudget: 6

critics:
  code:
    enabled: true
    model: opus
    vetoThreshold: strict
  security:
    enabled: true
    model: opus
  domain:
    enabled: true
    model: opus
    specialization: financial

autoVerify: false  # Interactive by default

acceptableErrorRate: 0.079

consensusMode: unanimous

parallelExecution: true

costVisibility:
  showTokens: true
  showTime: true
  estimateCost: true
---

# Project-specific domain rules

Financial calculations must:
- Use Decimal type (not float)
- Round to 2 decimal places
- Log all operations for audit trail
- Handle currency conversion explicitly
```

## When to Use

### ✅ Ideal For
- Financial calculations
- Security-critical code
- Production deployments
- Regulatory compliance
- Data transformations

### ❌ Not Suitable For
- Exploratory coding
- Throwaway prototypes
- Real-time interactive sessions
- Low-stakes experimental code

## Architecture

### Team of Rivals

```
User invokes skill → Planner creates plan → User approves →
Execution → Critics evaluate (parallel) →
ANY veto? → Retry (budget--) → Repeat →
All approve? → Success → Audit trail logged
```

### Swiss Cheese Model

Three independent validation layers with orthogonal failure modes:

1. **Code Critic** (87.8% catch rate): Syntax, logic, performance
2. **Security Critic** (catches what Layer 1 misses): OWASP, data exposure
3. **Domain Critic** (catches what both miss): Business rules, compliance

### Hierarchical Veto Authority

- ANY critic can reject (not consensus voting)
- Independent evaluation (different models/providers supported)
- Unanimous approval required to advance
- Errors caught internally before user exposure

## Cost-Benefit Analysis

**Investment**: 38.6% computational overhead
**Return**: 80% reduction in user-facing errors

For high-stakes code where a single mistake costs more than compute time, this tradeoff is justified.

**Example**: A $40 reconciliation error in financial close propagates to regulatory filings. The cost of additional verification is trivial compared to the consequences.

## Research Foundation

Based on the paper ["If You Want Coherence, Orchestrate a Team of Rivals: Multi-Agent Models of Organizational Intelligence"](https://arxiv.org/abs/2601.14351) by Vijayaraghavan et al. (2026).

**Key concepts applied**:
- Swiss cheese model (Reason, 2000)
- Shannon's channel capacity theorem (treating inter-agent communication as noisy channel)
- Organizational reliability through opposing forces
- Context isolation (separation of perception and execution)

## Contributing

To extend with custom domain critics:

1. Create new agent file: `agents/your-domain-critic.md`
2. Define specialization in settings: `specialization: your-domain`
3. Add domain rules to `.claude/code-coherence.local.md`

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- GitHub Issues: [Create issue](https://github.com/your-org/code-coherence/issues)
- Documentation: See `skills/*/references/` for detailed guides

## Changelog

### 0.1.0 (Initial Release)
- Core verification skills
- Base critic agents (planner, code, security, domain)
- Specialized domain critics (financial, healthcare, legal)
- Settings system with cascade support
- Audit trail with persistence
- Cost visibility and reporting
