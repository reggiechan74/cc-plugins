# SESF v2 Reference

Syntax examples, keyword definitions, and quality checklists for writing SESF specifications.

## Tier Comparison

| Tier     | Required Sections                              | Use When                            | Target Length |
|----------|------------------------------------------------|-------------------------------------|---------------|
| Micro    | Meta, Purpose, Behaviors, Constraints (opt.)   | Single behavior, 1-2 rules          | 20-40 lines   |
| Standard | Meta, Purpose, Scope, Inputs, Outputs, Types, Functions, Behaviors, Constraints, Dependencies | Multiple behaviors sharing types | 100-300 lines |
| Complex  | Everything in Standard + Precedence, State/Flow, Audience notes | Overlapping rules, state machines | 300-600 lines |

## Requirement Keywords

Use these keywords with precise meanings (always capitalize):

| Keyword | Meaning |
|---------|---------|
| MUST | Absolute requirement. Failure = invalid output. |
| MUST NOT | Absolute prohibition. Violation = invalid output. |
| SHOULD | Recommended. Skip only with good reason. |
| SHOULD NOT | Discouraged. Do only with good reason. |
| MAY | Optional. Include if relevant or beneficial. |

## BEHAVIOR Block Syntax

```
BEHAVIOR behavior_name: Brief description of what this behavior does

  RULE rule_name:
    WHEN condition
    THEN action
    ELSE alternative
    PRIORITY 1

  RULE another_rule:
    WHEN condition
    THEN action

  RULE simple_rule:
    field MUST satisfy constraint

  ERROR error_name:
    WHEN error_condition
    SEVERITY critical | warning | info
    ACTION what_to_do
    MESSAGE "user-facing message"

  EXAMPLE example_name:
    INPUT: { concrete input data }
    EXPECTED: { concrete expected output }
    NOTES: clarification if needed

```

## Rule Syntax Variants

**Conditional rules** — use WHEN/THEN/ELSE for rules that depend on conditions:

```
RULE discount_eligibility:
  WHEN order.total > 500
       AND customer.tier = "gold"
  THEN apply discount of 15%
  ELSE apply standard pricing
  PRIORITY 2
```

**Simple rules** — for rules that always apply without conditions:

```
RULE positive_quantity:
  line_item.quantity MUST be greater than zero

RULE currency_required:
  payment.currency MUST NOT be null
```

**Multi-branch rules** — combine branches of the same decision:

```
RULE select_output_format:
  WHEN output = "text"  THEN add "-o /tmp/result.md"
  ELSE WHEN output = "json"    THEN add "--json"
  ELSE WHEN output = "schema"  THEN add "--output-schema <file>"
```

## Type Definition Syntax

```
Order {
  id: string, required
  customer: Customer, required
  items: list of LineItem, required
  total: number, required
  status: enum [pending, approved, rejected, fulfilled], required
  created_at: datetime, required
}

LineItem {
  product_id: string, required
  quantity: integer, required
  unit_price: number, required
  description: string, optional
}
```

**Supported primitive types**:
string, number (includes decimals), integer (whole numbers only),
boolean, date (YYYY-MM-DD), datetime (ISO 8601),
enum [option1, option2, ...], list of [type],
[TypeName] (reference to a defined type).

## Function Definition Syntax

Functions are pure — inputs in, outputs out, no side effects.

```
FUNCTION calculate_line_total(item):
  result = item.quantity * item.unit_price
  RETURNS result

FUNCTION calculate_order_total(items):
  result = sum of calculate_line_total(item) for each item in items
  RETURNS result
```

Functions support conditional logic using IF/ELSE IF/ELSE:

```
FUNCTION apply_tax_rate(amount, jurisdiction):
  IF jurisdiction = "ON" THEN rate = 0.13
  ELSE IF jurisdiction = "AB" THEN rate = 0.05
  ELSE rate = 0.00
  RETURNS amount * rate
```

## Severity Levels

- **critical**: Invalid output. Processing MUST stop or the result is rejected.
- **warning**: Degraded output. Note the issue and continue.
- **info**: Observation only. No action required.

## PRECEDENCE and PRIORITY Syntax

### Global PRECEDENCE Block (Complex tier)

Define a global priority ordering when rules from different behaviors can match the same input:

```
PRECEDENCE:
  1. security_check (from BEHAVIOR authentication)
  2. rate_limit_check (from BEHAVIOR throttling)
  3. input_validation (from BEHAVIOR validation)
  4. business_rule_check (from BEHAVIOR processing)
```

Rules listed earlier take priority. If a higher-priority rule rejects the input, lower-priority rules are not evaluated.

### Inline PRIORITY Tags

Within a single behavior, use PRIORITY tags on individual rules to control evaluation order:

```
BEHAVIOR validation:

  RULE check_required_fields:
    WHEN any required field is null
    THEN reject with error "Missing required fields"
    PRIORITY 1

  RULE check_field_formats:
    WHEN any field fails format validation
    THEN reject with error "Invalid field format"
    PRIORITY 2

```

**Consistency**: Inline PRIORITY tags within behaviors
MUST NOT contradict the global PRECEDENCE block.

**When to use**: If no two rules from different behaviors can ever match
the same input, you do not need a PRECEDENCE block — even at Complex tier.
Precedence resolves ambiguity when conditions overlap.

## Inline Comment Syntax

Use `-- comment` syntax for non-obvious rule logic:

```
RULE apply_late_fee:
  WHEN invoice.days_overdue > 30  -- grace period is 30 days per policy
  THEN add_fee(invoice, 0.015)    -- 1.5% monthly late fee
```

## Example Syntax

Examples within a behavior demonstrate that behavior's rules and error cases.
Use concrete values — never placeholders:

```
EXAMPLE valid_gold_discount:
  INPUT: { "order": { "total": 750 }, "customer": { "tier": "gold" } }
  EXPECTED: { "discount": 0.15, "final_total": 637.50 }
  NOTES: Gold customer with order over 500 triggers 15% discount

EXAMPLE standard_pricing_fallback:
  INPUT: { "order": { "total": 750 }, "customer": { "tier": "silver" } }
  EXPECTED: { "discount": 0, "final_total": 750 }
  NOTES: Non-gold customer gets standard pricing via ELSE branch

```

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| "Handle errors appropriately" | Specify each error case explicitly |
| "Extract relevant fields" | List exactly which fields |
| "Validate the data" | State each validation rule |
| "Use common sense" | Define the expected behavior |
| Nested conditionals 3+ deep | Break into separate rules |
| Ambiguous pronouns ("it", "this") | Name the specific thing |
| All rules in one section, all errors in another | Group rules, errors, and examples together by behavior |

## Completeness Checklist

Before finalizing a spec, verify:

- [ ] Tier declared in Meta section
- [ ] Purpose stated in 1-3 sentences
- [ ] All inputs listed with types (Standard+)
- [ ] All outputs defined with structure (Standard+)
- [ ] Every behavior has rules, at least one error case, and at least one example
- [ ] Rules use MUST/SHOULD/MAY consistently
- [ ] No ambiguous instructions remain
- [ ] No rule is restated in Constraints (deduplicated)
- [ ] No Type or Function is defined but never referenced by a BEHAVIOR
- [ ] Every input enum value maps to at least one rule
- [ ] Related rules consolidated (one decision = one rule with branches)
- [ ] Reference/lookup data extracted to `assets/` if over 10 lines
- [ ] PRECEDENCE declared if overlapping conditions exist (Complex)
- [ ] Validator runs clean: `python3 scripts/validate_sesf.py <spec.md>`
