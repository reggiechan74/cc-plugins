# structured-english

<!-- badges-start -->
[![Plugin](https://img.shields.io/badge/plugin-v6.0.0-blue)](https://github.com/reggiechan74/cc-plugins/tree/main/structured-english)
[![HSF](https://img.shields.io/badge/hsf-v5.0.0-blue)](https://github.com/reggiechan74/cc-plugins/tree/main/structured-english)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-yellow)](https://www.python.org)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-blueviolet)](https://claude.ai/claude-code)
<!-- badges-end -->

Write specifications using **Hybrid Specification Format (HSF v5)** -- a natural-language format that combines prose instructions with structured notation for decision tables, centralized configuration, and explicit data flow. HSF specs are readable by both humans and AI systems -- use them to instruct an LLM, a junior analyst, or anyone who needs to follow branching logic precisely.

## Features

- **Prose instructions**: Natural language with markdown headers (`##`, `###`) and bold list items -- no formal BEHAVIOR/PROCEDURE blocks
- **Structured notation**: @config for centralized parameters, @route for multi-branch decision tables (3+ branches), $variable threading for explicit data flow
- **Consolidated error tables**: All errors in one scannable table (Error | Severity | Action)
- **RFC 2119 precision**: MUST, SHOULD, MAY keywords for unambiguous requirement strength
- **3-tier scaling**: Micro (20-80 lines), Standard (80-200 lines), Complex (200-400 lines)
- **Edge-case examples**: Boundary conditions and error paths only -- no happy-path bloat
- **Structural validator**: Python script that checks section completeness, @config/@route correctness, $variable threading, line budgets, and format compliance
- **Templates and examples**: Fill-in-the-blank templates for all tiers, plus 3 complete working examples
- **Backward compatible**: Validator still handles SESF v4 specs

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
/update-spec path/to/old-sesf-spec.md
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
| **Skill** | HSF v5 authoring rules -- tier selection, document structuring, prose instruction writing, @config/@route/$variable placement, quality assurance |
| **Commands** | `/write-spec` -- guided specification creation; `/assess-doc` -- evaluate whether a document benefits from HSF conversion; `/assess-inferred-intent` -- review a spec for ambiguity and resolve interactively; `/update-spec` -- upgrade from any previous version to HSF v5 |
| **Validator** | `validate_sesf.py` -- structural validation with pass/fail/warning output, auto-detects SESF v4 vs HSF v5 |
| **Templates** | Fill-in-the-blank starting points for micro, standard, and complex tiers |
| **Examples** | 3 complete specs covering all tiers (see table below) |

### Examples

| # | Name | Tier | Description |
|---|------|------|-------------|
| 1 | Webhook Signature Validator | Micro | Prose instructions with inline config and error table |
| 2 | Document Processing Pipeline | Standard | @config, @route table, prose rules, phased instructions |
| 3 | Multi-Phase Meeting Analysis | Complex | @config, @route, $variable threading, worked examples |

## When to use HSF (and when not to)

HSF adds value when ambiguity causes real failures -- whether the reader is an AI model, a junior team member, or a cross-functional stakeholder. The structured notation (@config, @route, $variable) makes conditional logic, configuration, and data flow explicit.

### Use HSF for

Anything with **conditional logic that branches differently based on inputs**, or **step-by-step processes with decisions, loops, or side effects**:

| Domain | Example |
|--------|---------|
| Data extraction | Lease abstraction -- which fields to extract, what validation to apply, what happens when a field is missing |
| Approval workflows | Purchase orders -- dollar thresholds, escalation chains, timeout logic, emergency overrides |
| Classification | Email triage -- what triggers each category, confidence scoring, priority sender rules |
| API contracts | Webhook handler -- signature validation, idempotency checks, error codes per event type |
| Business rules | Pricing tiers, eligibility criteria, discount logic, tax calculations |
| Data pipelines | ETL processes -- extract, transform, load with validation gates and error recovery |
| Agent task plans | Multi-step agent workflows with decision points, retries, and fallbacks |

### Don't use HSF for

Anything that's **narrative guidance or role descriptions without branching logic**:

| Content type | Why not | Use instead |
|--------------|---------|-------------|
| How-to guides | Steps are linear, not conditional | Numbered lists |
| Style guides | Preferences, not rules with error handling | Bullet points |
| Agent system prompts | Role and personality descriptions | Prose paragraphs |
| README files | Documentation for humans | Markdown |

### Rule of thumb

Ask: **"Does the same input sometimes produce different outputs depending on conditions?"** or **"Is there a step-by-step process with decisions, loops, or side effects?"** If yes to either, HSF helps make those conditions and steps explicit. If the process is purely narrative with no branching, prose is simpler.

## HSF at a glance

### Rules as prose with bold list items

```markdown
## Validation Rules

- **Positive amount:** payment.amount MUST be greater than zero.
- **Currency required:** payment.currency MUST NOT be empty. When missing, reject with "Currency required".
- **Supported currencies:** payment.currency MUST be one of [CAD, USD, EUR]. Unsupported currencies are rejected.
```

### @route decision table (3+ branches)

```markdown
@route currency_check [first_match_wins]
  payment.currency IN $config.supported_currencies  → accept
  payment.currency is empty                         → reject with "Currency required"
  *                                                 → reject with "Unsupported currency"
```

### Instructions as prose with phase headers

```markdown
## Instructions

### Phase 1: Validate Input

Read the payment request. Check amount is positive and currency is supported.
If validation fails, halt and return the error from the error table.

### Phase 2: Process Payment

Submit the validated payment to the gateway. If it fails with insufficient_funds,
notify the customer. If it fails for any other reason, escalate to finance.
```

### Consolidated error table

```markdown
## Errors

| Error | Severity | Action |
|-------|----------|--------|
| invalid_amount | critical | reject payment, "Amount must be positive" |
| unsupported_currency | critical | reject payment, "Currency not supported" |
| payment_failure | critical | retry once then escalate to finance |
```

## Versioning

This plugin uses two version numbers:

- **Plugin version** (6.0.0) tracks the package release -- plugin.json, README, commands, templates, examples, and validator.
- **Format version** (HSF v5.0.0) tracks the specification language -- syntax rules, notation, section requirements, and keyword semantics defined in the reference and SKILL.md.

The plugin version increments when any shipped file changes. The format version increments only when the specification language itself changes.

## License

MIT
