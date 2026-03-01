# structured-english

Write specifications using **Structured English Specification Format (SESF)** — a behavior-centric format for defining instructions, rules, and behaviors for AI systems.

## Features

- **3-tier scaling**: Micro (20-40 lines), Standard (100-300 lines), Complex (300-600 lines)
- **Behavior-centric grouping**: Rules, errors, and examples grouped by concern
- **Structural validator**: Python script that checks section completeness, behavior structure, and tier compliance
- **Templates and examples**: Fill-in-the-blank templates for all tiers, plus complete working examples

## Installation

```bash
claude plugin add /path/to/structured-english
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
