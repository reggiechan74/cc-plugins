# structured-english

<!-- badges-start -->
[![Version](https://img.shields.io/badge/version-4.0.0-blue)](https://github.com/reggiechan74/cc-plugins/tree/main/structured-english)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-yellow)](https://www.python.org)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-blueviolet)](https://claude.ai/claude-code)
<!-- badges-end -->

Write specifications and procedural pseudocode using **Structured English Specification Format (SESF v3)** — a natural-language format for defining declarative rules, step-by-step workflows, and reusable logic for AI systems.

## Features

- **Dual-mode blocks**: BEHAVIOR for declarative rules, PROCEDURE for step-by-step workflows
- **Natural English syntax**: Non-programmers can read and write specs without programming experience
- **ACTION functions**: Distinguish pure calculations (FUNCTION) from side-effect operations (ACTION)
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

### Slash commands

```
/write-spec payment webhook handler
/write-spec email classification agent
/assess-doc path/to/existing-document.md
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
| **Skill** | SESF v3 authoring rules — tier selection, document structuring, BEHAVIOR and PROCEDURE composition, quality assurance |
| **Commands** | `/write-spec` — guided specification creation workflow; `/assess-doc` — evaluate whether an existing document would benefit from SESF conversion |
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
| Data pipelines | ETL processes — extract, transform, load with validation gates and error recovery |
| Automation workflows | Onboarding workflows, scheduled jobs, CI/CD orchestration |
| Agent task plans | Multi-step agent workflows with decision points, retries, and fallbacks |

### Don't use SESF for

Anything that's **narrative guidance or role descriptions without branching logic**:

| Content type | Why not | Use instead |
|--------------|---------|-------------|
| How-to guides | Steps are linear, not conditional | Numbered lists |
| Onboarding docs | Narrative explanation, not branching logic | Prose with headers |
| Style guides | Preferences, not rules with error handling | Bullet points |
| Meeting agendas | Sequential, time-boxed | Simple outline |
| Agent system prompts | Role and personality descriptions | Prose paragraphs |
| README files | Documentation for humans | Markdown |

### Rule of thumb

Ask: **"Does the same input sometimes produce different outputs depending on conditions?"** or **"Is there a step-by-step process with decisions, loops, or side effects?"** If yes to either, SESF helps make those conditions and steps explicit. If the process is purely narrative with no branching, prose is simpler and shorter.

## SESF at a glance

### BEHAVIOR — declarative rules

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

### PROCEDURE — step-by-step workflows

```
PROCEDURE process_refund: Handle a customer refund request

  STEP validate: Check the refund is eligible
    If the order is older than 90 days:
      Reject the refund with "Order outside refund window"
      Stop processing

  STEP process: Execute the refund
    Calculate refund_amount as order.total minus any restocking fee
    Send the refund to the customer's payment method
    Log: "Refund of {refund_amount} processed for order {order.id}"

  STEP notify: Confirm with the customer
    Send a confirmation email to customer.email

  ERROR payment_failure:
    WHEN the refund transaction fails
    SEVERITY critical
    ACTION retry once, then escalate to finance team
    MESSAGE "Refund failed for order {order.id}"

  EXAMPLE successful_refund:
    INPUT: { "order": { "id": "ORD-1234", "total": 89.99, "date": "2026-01-15" }, "restocking_fee": 0 }
    EXPECTED: { "refund_amount": 89.99, "status": "processed" }
```

## License

MIT
