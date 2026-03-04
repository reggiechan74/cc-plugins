# structured-english

<!-- badges-start -->
[![Plugin](https://img.shields.io/badge/plugin-v5.2.0-blue)](https://github.com/reggiechan74/cc-plugins/tree/main/structured-english)
[![SESF](https://img.shields.io/badge/sesf-v4.0.0-blue)](https://github.com/reggiechan74/cc-plugins/tree/main/structured-english)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-yellow)](https://www.python.org)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-blueviolet)](https://claude.ai/claude-code)
<!-- badges-end -->

Write specifications and procedural pseudocode using **Structured English Specification Format (SESF v4)** -- a natural-language format with hybrid notation for defining declarative rules, step-by-step workflows, decision tables, and centralized configuration. SESF specs are readable by both humans and AI systems -- use them to instruct an LLM, a junior analyst, or anyone who needs to follow branching logic precisely.

## Features

- **Dual-mode blocks**: BEHAVIOR for declarative rules, PROCEDURE for step-by-step workflows
- **Hybrid notation**: @config for centralized parameters, @route for multi-branch decision tables, $variable threading for explicit data flow between steps
- **Compact notation**: Inline ERROR format and single-line EXAMPLES reduce verbosity while preserving structure
- **Notation section**: Optional symbol glossary that bridges readability for non-technical readers
- **Natural English syntax**: Non-programmers can read and write specs without programming experience
- **ACTION functions**: Distinguish pure calculations (FUNCTION) from side-effect operations (ACTION)
- **3-tier scaling**: Micro (20-100 lines), Standard (100-300 lines), Complex (300-600 lines)
- **Behavior-centric grouping**: Rules, errors, and examples grouped by concern -- not separated by type
- **Structural validator**: Python script that checks section completeness, behavior/procedure structure, @config/@route correctness, $variable threading, and tier compliance
- **Templates and examples**: Fill-in-the-blank templates for all tiers, plus 7 complete working examples

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
/assess-inferred-intent path/to/spec.md
/update-spec path/to/old-v2-spec.md
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
| **Skill** | SESF v4 authoring rules -- tier selection, document structuring, BEHAVIOR and PROCEDURE composition, hybrid notation placement (@config, @route, $variable), quality assurance |
| **Commands** | `/write-spec` -- guided specification creation workflow; `/assess-doc` -- evaluate whether an existing document would benefit from SESF conversion; `/assess-inferred-intent` -- review a spec for ambiguity, contradiction, and inferred intent, then resolve interactively; `/update-spec` -- upgrade an existing SESF spec from any previous version to v4 |
| **Validator** | `validate_sesf.py` -- structural validation with pass/fail/warning output, including hybrid notation checks |
| **Templates** | Fill-in-the-blank starting points for micro, standard, and complex tiers with hybrid notation placeholders |
| **Examples** | 7 complete specs covering all tiers and styles (see table below) |

### Examples

| # | Name | Tier | Style | Description |
|---|------|------|-------|-------------|
| 1 | Email Address Validator | Micro | Declarative | Single BEHAVIOR with inline ERROR and compact EXAMPLES |
| 2 | Commercial Lease Abstraction | Standard | Declarative | Multi-BEHAVIOR spec with @config, @route, shared Types, and Notation section |
| 3 | Purchase Order Approval Workflow | Complex | Declarative | @route decision tables, PRECEDENCE block, overlapping rules across behaviors |
| 4 | Daily Sales Report Generator | Micro | Procedural | Single PROCEDURE with $variable threading and compact tables |
| 5 | Customer Onboarding Workflow | Standard | Mixed | BEHAVIOR + PROCEDURE with ACTION definitions, $variable threading, @config |
| 6 | Data Pipeline Processor | Complex | Procedural | Multi-PROCEDURE with PRECEDENCE, State/Flow, $variable threading, @route |
| 7 | GIST Newsletter Briefing | Standard | Mixed | Real-world hybrid spec combining BEHAVIORs and PROCEDUREs with @config and @route |

## When to use SESF (and when not to)

SESF adds value when ambiguity causes real failures -- whether the reader is an AI model, a junior team member, or a cross-functional stakeholder. The hybrid notation (@config, @route, $variable) makes conditional logic, configuration, and data flow explicit -- reducing the gap between what the spec says and what the reader does.

### Use SESF for

Anything with **conditional logic that branches differently based on inputs**, or **step-by-step processes with decisions, loops, or side effects**:

| Domain | Example |
|--------|---------|
| Data extraction | Lease abstraction -- which fields to extract, what validation to apply, what happens when a field is missing |
| Approval workflows | Purchase orders -- dollar thresholds, escalation chains, timeout logic, emergency overrides |
| Classification | Email triage -- what triggers each category, confidence scoring, priority sender rules |
| API contracts | Webhook handler -- signature validation, idempotency checks, error codes per event type |
| Business rules | Pricing tiers, eligibility criteria, discount logic, tax calculations |
| Validation | Input validation with multiple field-level rules, severity levels, and error messages |
| State machines | Order lifecycle, deployment pipelines, support ticket routing |
| Data pipelines | ETL processes -- extract, transform, load with validation gates and error recovery |
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

### BEHAVIOR with @config and @route

```
@config
  max_retries: 3
  supported_currencies: [CAD, USD, EUR]

BEHAVIOR validate_payment: Check payment meets business rules

  RULE positive_amount:
    payment.amount MUST be greater than zero

  @route currency_check [first_match_wins]
    payment.currency IN $config.supported_currencies  -> accept
    payment.currency is empty                         -> reject with "Currency required"
    *                                                 -> reject with "Unsupported currency"

  ERROR invalid_amount: critical -> reject payment, "Payment amount must be positive"
  ERROR unsupported_currency: critical -> reject payment, "Currency '{currency}' is not supported"

  EXAMPLES:
    valid_payment: amount=49.99, currency="CAD" -> accepted
    invalid_amount: amount=-10, currency="CAD" -> rejected with "Payment amount must be positive"
    bad_currency: amount=25, currency="GBP" -> rejected with "Currency 'GBP' is not supported"
```

### PROCEDURE with $variable threading

```
PROCEDURE process_refund: Handle a customer refund request

  STEP validate -> $eligibility
    Check the order date against the 90-day refund window -> $eligibility
    If $eligibility is "ineligible":
      Reject the refund with "Order outside refund window"
      Stop processing

  STEP calculate -> $refund_amount
    Calculate $refund_amount as order.total minus any restocking fee

  STEP execute:
    Send $refund_amount to the customer's payment method
    Log: "Refund of {$refund_amount} processed for order {order.id}"

  STEP notify:
    Send a confirmation email to customer.email

  ERROR outside_window: critical -> reject refund, "Order outside refund window"
  ERROR payment_failure: critical -> retry once then escalate to finance, "Refund failed for order {order.id}"

  EXAMPLES:
    successful_refund: order="ORD-1234", total=89.99, restocking_fee=0 -> { "refund_amount": 89.99, "status": "processed" }
```

## Versioning

This plugin uses two version numbers:

- **Plugin version** (5.0.0) tracks the package release -- plugin.json, README, commands, templates, examples, and validator.
- **SESF format version** (4.0.0) tracks the specification language -- syntax rules, hybrid notation, section ordering, and keyword semantics defined in the reference and SKILL.md.

The plugin version increments when any shipped file changes. The SESF format version increments only when the specification language itself changes (new block types, new notation, changed semantics).

## License

MIT
