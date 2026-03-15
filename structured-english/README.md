# structured-english

<!-- badges-start -->
[![Plugin](https://img.shields.io/badge/plugin-v8.0.0-blue)](https://github.com/reggiechan74/cc-plugins/tree/main/structured-english)
[![HSF](https://img.shields.io/badge/HSF-v6.0.0-blue)](https://github.com/reggiechan74/cc-plugins/tree/main/structured-english/skills/hsf)
[![SESF](https://img.shields.io/badge/SESF-v4.1.0-blue)](https://github.com/reggiechan74/cc-plugins/tree/main/structured-english/skills/sesf)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-yellow)](https://www.python.org)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-blueviolet)](https://claude.ai/claude-code)
<!-- badges-end -->

Most specifications fail not because the author forgot something, but because they *thought* they were clear. "Check that amounts look reasonable" feels complete — until three different people implement it three different ways. Prose hides ambiguity. The gaps only surface when someone (or some LLM) tries to execute the spec and fills each gap with their own assumptions.

This plugin gives you a structured format for writing specifications where every rule has an explicit condition and outcome, every decision point names its branches, every threshold is a concrete number, and every failure mode has a severity and an action. The format forces you to answer the questions you didn't know you were skipping.

Two formats, optimized for different readers:

- **HSF v6** (LLM-facing) — XML envelope with prose instructions. JSON config, XML route tables, output schemas. Unambiguous section boundaries that LLMs parse with near-perfect accuracy.
- **SESF v4.1** (human-facing) — formal BEHAVIOR/PROCEDURE/RULE/STEP blocks with WHEN/THEN syntax. Visual scaffolding, scannable structure, rationale annotations. What humans scan and maintain best.

Both share: decision tables, configuration parameters, $variable threading, consolidated error tables, RFC 2119 keywords, and 3-tier scaling (Micro/Standard/Complex).

## Installation

Add the marketplace, then install the plugin:

```bash
/plugin marketplace add reggiechan74/cc-plugins
/plugin install structured-english@cc-plugins
```

## Commands

### LLM-facing (HSF v6)

```
/write-LLM-spec payment webhook handler
/assess-LLM-doc path/to/document.md
/update-LLM-spec path/to/old-spec.md
```

### Human-facing (SESF v4.1)

```
/write-human-spec invoice processing pipeline
/assess-human-doc path/to/document.md
/update-human-spec path/to/old-sesf-spec.md
```

### Cross-format

```
/convert-human-to-llm path/to/sesf-spec.md
/assess-inferred-intent path/to/any-spec.md
```

### Natural language triggers

The skills activate automatically:

- "Write a spec for..." / "Write an LLM spec..." → HSF skill
- "Write a human spec..." / "Write a human-readable specification..." → SESF skill

## What's included

| Component | HSF (LLM) | SESF (Human) |
|-----------|-----------|--------------|
| **Skill** | `hsf` — XML envelope rules, JSON config, XML routes, output-schema, $variable threading | `sesf` — formal block rules, WHEN/THEN syntax, STEP → $var, rationale annotations |
| **Reference** | Format spec with XML tags, JSON config, XML routes, output-schema | Format spec for formal block output |
| **Templates** | Micro/Standard/Complex with XML envelope | Micro/Standard/Complex with BEHAVIOR/PROCEDURE blocks |
| **Examples** | 3 complete specs (Webhook, Document Pipeline, Meeting Analysis) | 3 complete specs (same domains, formal block syntax) |
| **Authoring Guide** | — | 6-step thinking process for human authors |
| **Validator** | `validate_sesf.py` (auto-detects format) | `validate_sesf.py` (auto-detects format) |

## When to use which format

| Audience | Format | Why |
|----------|--------|-----|
| LLM agent executing the spec | **HSF v6** | XML envelope with prose content. LLMs parse XML boundaries with near-perfect accuracy. JSON config and output schemas eliminate guesswork. |
| Human reading/reviewing the spec | **SESF v4.1** | Formal blocks create visual chapters. WHEN/THEN creates alignment points. Rationale explains *why*. |
| Human authoring → LLM executing | **SESF v4.1 → `/convert-human-to-llm`** | Author in formal blocks (easier to think through), then convert to XML envelope format for the agent. |

### Use HSF or SESF for

Anything with **conditional logic that branches differently based on inputs**, or **step-by-step processes with decisions, loops, or side effects**:

| Domain | Example |
|--------|---------|
| Data extraction | Lease abstraction — fields, validation, missing-field handling |
| Approval workflows | Purchase orders — thresholds, escalation, timeout logic |
| Classification | Email triage — categories, confidence scoring, priority rules |
| API contracts | Webhook handler — signature validation, idempotency, error codes |
| Business rules | Pricing tiers, eligibility, discount logic, tax calculations |
| Data pipelines | ETL with validation gates and error recovery |
| Agent task plans | Multi-step agent workflows with decision points and retries |

### Don't use HSF or SESF for

| Content type | Why not | Use instead |
|--------------|---------|-------------|
| How-to guides | Linear steps, no branching | Numbered lists |
| Style guides | Preferences, not rules with error handling | Bullet points |
| Agent system prompts | Role/personality descriptions | Prose paragraphs |
| README files | Documentation | Markdown |

## Before & after: how structured specs remove ambiguity

A real-world prompt that looks clear but is riddled with hidden ambiguity:

### Before (unstructured prose)

```markdown
# Expense Report Processor

Process expense reports submitted by employees. Check that receipts are
attached and amounts look reasonable. Reports over the limit need manager
approval. If something looks wrong, flag it. Send approved reports to
finance for reimbursement.
```

**What's wrong with this?** It *feels* complete — but try to implement it:

| Phrase | Ambiguity |
|--------|-----------|
| "receipts are attached" | What if 3 of 4 line items have receipts? Reject the whole report or just those items? |
| "amounts look reasonable" | Reasonable compared to what? What threshold? What happens at the boundary? |
| "over the limit" | What limit? Per line item or total? Is it $500, $1,000, $5,000? |
| "need manager approval" | The submitter's direct manager? What if the manager is unavailable? Timeout? |
| "something looks wrong" | What specifically? Duplicate submissions? Missing fields? Suspicious patterns? |
| "flag it" | Flag how? Block processing? Send an email? Add a warning and continue? |
| "approved reports" | What makes a report "approved"? All items valid? Manager signed off? Both? |

An LLM executing this spec would fill every gap with its own assumptions — different assumptions each time, producing inconsistent behavior.

### After (HSF v6 — LLM-facing)

```markdown
<purpose>
Validate employee expense reports, route for approval, and forward
approved reports to finance. Reject malformed reports immediately;
flag policy violations for manager review.
</purpose>

<scope>
**Not in scope:** Reimbursement processing, tax calculations, vendor payments.
</scope>

<config>
{
  "receipt_required_above": 25,
  "line_item_limit": 500,
  "total_report_limit": 5000,
  "manager_approval_timeout_days": 5,
  "duplicate_window_days": 90
}
</config>

<instructions>
### Phase 1: Validate Structure

For EACH line item in the report:

1. **Required fields:** MUST have description, amount, date, and category. If ANY field is missing, reject the entire report with `missing_field`.
2. **Receipt check:** If amount > `config.receipt_required_above`, a receipt MUST be attached. If missing, reject the line item (not the report) with `missing_receipt`.
3. **Amount validation:** Amount MUST be positive and ≤ `config.line_item_limit`. Amounts at exactly the limit pass (threshold is "exceeds", not "at or above").
4. **Duplicate detection:** Check if a line item with the same amount, date, and vendor exists in reports submitted within `config.duplicate_window_days`. If found, flag as `potential_duplicate` but continue processing.

### Phase 2: Route for Approval

Apply the approval route table using the report total and individual item amounts:

<route name="approval_path" mode="first_match_wins">
  <case when="total ≤ config.total_report_limit AND all items ≤ config.line_item_limit">auto-approve</case>
  <case when="total ≤ config.total_report_limit AND any item > config.line_item_limit">manager approval</case>
  <case when="total > config.total_report_limit">manager + director approval</case>
  <default>finance review</default>
</route>

If manager approval is required, notify the submitter's direct manager via email. If the manager does not respond within `config.manager_approval_timeout_days`, escalate to their skip-level manager.

### Phase 3: Forward to Finance

After approval, forward the report to the finance reimbursement queue with: employee ID, approved line items, total approved amount, approval chain (who approved and when), and any flags.
</instructions>

<errors>
| Error | Severity | Action |
|-------|----------|--------|
| missing_field | critical | Reject entire report: "Line item {n} missing {field}." |
| missing_receipt | warning | Reject line item only: "Receipt required for items over ${receipt_required_above}." Continue processing remaining items. |
| potential_duplicate | info | Flag: "Possible duplicate of {existing_report_id}, submitted {date}." Do not block. |
| approval_timeout | warning | Escalate to skip-level manager. Notify submitter: "Manager did not respond within {days} days." |
| over_line_limit | critical | Reject line item: "Amount ${amount} exceeds per-item limit of ${line_item_limit}." |
</errors>
```

Every ambiguity from the original is now resolved: thresholds are explicit numbers in `<config>` JSON, the approval path is a scannable `<route>` table, error handling names each failure mode with a severity and action, and boundary conditions are specified ("at exactly the limit" passes).

## HSF v6 at a glance (LLM format)

```markdown
<purpose>
Validate and process incoming payments.
</purpose>

<instructions>
### Phase 1: Validate Input

Read the payment request. Check amount is positive and currency is supported.

- **Positive amount:** payment.amount MUST be greater than zero.
- **Currency required:** payment.currency MUST NOT be empty.

### Phase 2: Process Payment

Submit the validated payment to the gateway.
</instructions>

<errors>
| Error | Severity | Action |
|-------|----------|--------|
| invalid_amount | critical | Reject: "Amount must be positive." |
| missing_currency | critical | Reject: "Currency is required." |
</errors>
```

## SESF v4.1 at a glance (Human format)

```markdown
**BEHAVIOR** validate_payment: Ensure payment meets processing requirements

  **RULE** positive_amount:
    WHEN payment.amount ≤ 0
    THEN reject with "Amount must be positive"
    (Negative amounts indicate data entry errors or test data)

  **RULE** currency_required:
    WHEN payment.currency is null
    THEN reject with "Currency is required"

**PROCEDURE** process_payment: Submit validated payment

  **STEP** validate: Check all payment rules
    Apply BEHAVIOR validate_payment.

  **STEP** submit: Send to gateway → $gateway_response
    Submit the validated payment to the gateway.
```

## Versioning

This plugin uses three version numbers:

- **Plugin version** (8.0.0) tracks the package release — commands, README, plugin.json
- **HSF version** (v6.0.0) tracks the LLM-facing specification language
- **SESF version** (v4.1.0) tracks the human-facing specification language

## License

MIT
