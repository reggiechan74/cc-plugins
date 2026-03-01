# structured-english

<!-- badges-start -->
[![Version](https://img.shields.io/badge/version-3.0.0-blue)](https://github.com/reggiechan74/cc-plugins/tree/main/structured-english)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-yellow)](https://www.python.org)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-blueviolet)](https://claude.ai/claude-code)
<!-- badges-end -->

Write specifications using **Structured English Specification Format (SESF)** — a behavior-centric format for defining instructions, rules, and behaviors for AI systems.

## Features

- **3-tier scaling**: Micro (20-40 lines), Standard (100-300 lines), Complex (300-600 lines)
- **Behavior-centric grouping**: Rules, errors, and examples grouped by concern
- **Structural validator**: Python script that checks section completeness, behavior structure, and tier compliance
- **Templates and examples**: Fill-in-the-blank templates for all tiers, plus complete working examples

## Installation

Add the marketplace, then install the plugin:

```bash
/plugin marketplace add reggiechan74/cc-plugins
/plugin install structured-english@cc-plugins
```

## Usage

### Slash command

```
/write-spec payment webhook handler
/write-spec email classification agent
```

### Natural language triggers

The skill activates automatically when you ask Claude to:

- "Write a spec for..."
- "Create a specification..."
- "Define requirements for..."
- "Specify the behavior of..."

## What's included

| Component | Description |
|-----------|-------------|
| **Skill** | SESF v2 authoring rules — tier selection, document structuring, behavior composition, quality assurance |
| **Command** | `/write-spec` — guided specification creation workflow |
| **Validator** | `validate_sesf.py` — structural validation with pass/fail/warning output |
| **Templates** | Fill-in-the-blank starting points for micro, standard, and complex tiers |
| **Examples** | Complete specs: email validator (micro), lease abstraction (standard), PO approval workflow (complex) |

## When to use SESF (and when not to)

SESF adds value when ambiguity causes real failures. It's overkill when prose communicates the same intent with less noise.

### Use SESF for

Anything with **conditional logic that branches differently based on inputs**:

| Domain | Example |
|--------|---------|
| Data extraction | Lease abstraction — which fields to extract, what validation to apply, what happens when a field is missing |
| Approval workflows | Purchase orders — dollar thresholds, escalation chains, timeout logic, emergency overrides |
| Classification | Email triage — what triggers each category, confidence scoring, priority sender rules |
| API contracts | Webhook handler — signature validation, idempotency checks, error codes per event type |
| Business rules | Pricing tiers, eligibility criteria, discount logic, tax calculations |
| Validation | Input validation with multiple field-level rules, severity levels, and error messages |
| State machines | Order lifecycle, deployment pipelines, support ticket routing |

### Don't use SESF for

Anything that's **sequential instructions, narrative guidance, or role descriptions**:

| Content type | Why not | Use instead |
|--------------|---------|-------------|
| How-to guides | Steps are linear, not conditional | Numbered lists |
| Onboarding docs | Narrative explanation, not branching logic | Prose with headers |
| Style guides | Preferences, not rules with error handling | Bullet points |
| Meeting agendas | Sequential, time-boxed | Simple outline |
| Claude Code skills | Instructions for Claude to follow step-by-step | Prose workflow |
| Claude Code commands | Sequential checklists with no branching | Numbered steps |
| Agent system prompts | Role and personality descriptions | Prose paragraphs |
| README files | Documentation for humans | Markdown |

### Rule of thumb

Ask: **"Does the same input sometimes produce different outputs depending on conditions?"** If yes, SESF helps make those conditions explicit. If the process is the same every time, prose is simpler and shorter.

## SESF at a glance

```
BEHAVIOR validate_payment: Check payment meets business rules

  RULE positive_amount:
    payment.amount MUST be greater than zero

  RULE currency_supported:
    WHEN payment.currency NOT IN ["CAD", "USD"]
    THEN reject with error

  ERROR invalid_amount:
    WHEN payment.amount <= 0
    SEVERITY critical
    ACTION reject payment
    MESSAGE "Payment amount must be positive"

  EXAMPLE valid_payment:
    INPUT: { "amount": 49.99, "currency": "CAD" }
    EXPECTED: { "valid": true }
```

## License

MIT
