# SESF v3 Reference

SESF v3 is a natural language for thinking programmatically. The precision comes from legal English conventions (MUST, SHOULD, MAY, CAN). Every line should read like an instruction to a competent human assistant. Non-programmers should be able to read or write SESF without programming experience.

This reference is organized in five parts:

1. **Shared Foundations** -- concepts and syntax used by both BEHAVIOR and PROCEDURE blocks
2. **Declarative Syntax** -- BEHAVIOR blocks for stating rules about what must be true
3. **Procedural Syntax** -- PROCEDURE blocks for describing step-by-step processes
4. **Function Syntax** -- FUNCTION and ACTION definitions
5. **Quality** -- anti-patterns and completeness checklist

---

## Part 1 -- Shared Foundations

These concepts apply to both BEHAVIOR and PROCEDURE blocks.

### Tier Comparison

| Tier     | Blocks Allowed                                      | Use When                                              | Target Length |
|----------|-----------------------------------------------------|-------------------------------------------------------|---------------|
| Micro    | 1 BEHAVIOR or 1 PROCEDURE                           | Single concern, 1-2 rules/steps                       | 20-40 lines   |
| Standard | Multiple BEHAVIORs and/or PROCEDUREs sharing types  | Multiple concerns                                     | 100-300 lines |
| Complex  | Everything + PRECEDENCE, State/Flow                  | Overlapping rules, state machines, mixed declarative+procedural | 300-600 lines |

**Required sections per tier:**

- **Micro**: Meta, Purpose, Behaviors/Procedures. Constraints is optional.
- **Standard**: Meta, Purpose, Scope, Inputs, Outputs, Types, Functions, Behaviors/Procedures, Constraints, Dependencies. Changelog is optional.
- **Complex**: All Standard sections plus Precedence. Behaviors MAY include State/Flow and Audience notes subsections.

### Requirement Keywords

Use these keywords with precise meanings (always capitalize):

| Keyword    | Meaning |
|------------|---------|
| MUST       | Absolute requirement. Failure = invalid output. |
| MUST NOT   | Absolute prohibition. Violation = invalid output. |
| SHOULD     | Recommended. Skip only with documented reason. |
| SHOULD NOT | Discouraged. Do only with documented reason. |
| MAY        | Optional. Include if relevant or beneficial. |
| CAN        | Capability. The system is able to do this. |

### Logical Connectors

```
and         -- both must be true
or          -- at least one must be true
not         -- negates the condition
but not     -- first is true, second is not (AND NOT)
either...or -- exactly one is true (XOR)
```

Grouping with parentheses: `WHEN (status is "active" or status is "pending") and not is_deleted`

### Comparisons

Natural phrasing is preferred. Mathematical symbols are valid as shorthand in numeric expressions.

| Natural Phrasing                    | Symbol Shorthand |
|-------------------------------------|------------------|
| is equal to / equals / is           | =                |
| is not equal to / is not / does not equal | !=         |
| is greater than / exceeds           | >                |
| is less than / is below             | <                |
| is at least / is greater than or equal to | >=         |
| is at most / is less than or equal to     | <=         |
| is between X and Y                  | (none)           |

### Arithmetic

Natural phrasing and shorthand symbols are both valid in formulas:

| Natural Phrasing          | Shorthand |
|---------------------------|-----------|
| plus / added to           | +         |
| minus / subtracted from   | -         |
| times / multiplied by     | *         |
| divided by                | /         |
| remainder of X divided by Y | %       |

### Collections

```
-- Asking about a collection (return true/false)
any item in the list satisfies condition
all items in the list satisfy condition
no items in the list satisfy condition

-- Measuring a collection (return a value)
the number of items in the list
the sum of field across the list
the minimum / maximum / average of field across the list

-- Membership
value is in the list
value is not in the list
value is between X and Y
```

### Null and Existence

```
field is missing / is null / is not provided
field is present / is not null / is provided
the list is empty
the list is not empty
a record exists in the collection where condition
no record exists in the collection where condition
use fallback_value if field is missing
```

### String Checks

```
string contains substring
string starts with prefix
string ends with suffix
string matches pattern
join the values with separator
convert string to uppercase / lowercase
trim whitespace from string
split string by delimiter
the length of string
```

### Type Definition Syntax

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

### Inline Comment Syntax

Use `-- comment` syntax for non-obvious logic:

```
RULE apply_late_fee:
  WHEN invoice.days_overdue > 30  -- grace period is 30 days per policy
  THEN add_fee(invoice, 0.015)    -- 1.5% monthly late fee
```

### Example Syntax

Examples within a behavior or procedure demonstrate that block's rules, steps, and error cases.
Use concrete values -- never placeholders:

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

---

## Part 2 -- Declarative Syntax

BEHAVIOR blocks state rules about what must be true. They describe *what*, not *how*.

### BEHAVIOR Block Syntax

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

### Rule Syntax Variants

**Conditional rules** -- use WHEN/THEN/ELSE for rules that depend on conditions:

```
RULE discount_eligibility:
  WHEN order.total > 500
       AND customer.tier = "gold"
  THEN apply discount of 15%
  ELSE apply standard pricing
  PRIORITY 2
```

**Simple rules** -- for rules that always apply without conditions:

```
RULE positive_quantity:
  line_item.quantity MUST be greater than zero

RULE currency_required:
  payment.currency MUST NOT be null
```

**Multi-branch rules** -- combine branches of the same decision:

```
RULE select_output_format:
  WHEN output = "text"  THEN add "-o /tmp/result.md"
  ELSE WHEN output = "json"    THEN add "--json"
  ELSE WHEN output = "schema"  THEN add "--output-schema <file>"
```

### Severity Levels

- **critical**: Invalid output. Processing MUST stop or the result is rejected.
- **warning**: Degraded output. Note the issue and continue.
- **info**: Observation only. No action required.

### PRECEDENCE and PRIORITY Syntax

#### Global PRECEDENCE Block (Complex tier)

Define a global priority ordering when rules from different behaviors can match the same input:

```
PRECEDENCE:
  1. security_check (from BEHAVIOR authentication)
  2. rate_limit_check (from BEHAVIOR throttling)
  3. input_validation (from BEHAVIOR validation)
  4. business_rule_check (from BEHAVIOR processing)
```

Rules listed earlier take priority. If a higher-priority rule rejects the input, lower-priority rules are not evaluated.

#### Inline PRIORITY Tags

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
the same input, you do not need a PRECEDENCE block -- even at Complex tier.
Precedence resolves ambiguity when conditions overlap.

---

## Part 3 -- Procedural Syntax

PROCEDURE blocks describe step-by-step processes. They describe *how* something is done, in order.

### PROCEDURE Block Structure

```
PROCEDURE procedure_name: Brief description of what this procedure does

  STEP step_name: Description
    action or actions

  STEP another_step: Description
    action or actions

  ERROR error_name:
    WHEN error_condition
    SEVERITY critical | warning | info
    ACTION what_to_do
    MESSAGE "user-facing message"

  EXAMPLE example_name:
    INPUT: { concrete input }
    EXPECTED: { concrete output or side effects }
    NOTES: clarification
```

### Assignment

Describe the value being created or calculated -- do not write code:

```
Start with total at 0
Calculate result as item.quantity times item.unit_price
Record the customer name as input.first_name joined with input.last_name
```

### Control Flow

Control flow reads as decisions, not programming constructs:

```
If the customer is a gold member and the order exceeds 500:
  Apply a 15% discount
Otherwise if the customer is a silver member:
  Apply a 5% discount
Otherwise:
  Use standard pricing
```

### Iteration

Natural descriptions of repetition. No END markers -- use indentation to show scope.

**For each** (iterate over a collection):

```
For each item in the order:
  Add item.price to total
```

**Counted repetition** (do something a specific number of times):

```
Do the following 5 times:
  Retry the connection
  Wait 2 seconds
```

**While** (pre-condition -- may execute zero times):

```
While there are unprocessed records:
  Fetch the next batch of 100 records
  Validate each record in the batch
```

**Repeat...until** (post-condition -- always executes at least once):

```
Repeat the following until the queue is empty:
  Take the next message from the queue
  Process the message
```

### Stopping and Skipping

```
Stop processing if a critical error is found
Skip this item if it has already been processed
Return the result
Return nothing
```

### Side Effects

Verb-first natural actions describing interactions with the outside world:

```
Send a confirmation email to the customer
Write the report to /output/report.pdf
Read the configuration from settings.yaml
Log a warning: "Duplicate entry detected for {id}"
Wait for approval from the manager
Notify the admin team about the failure
Emit an "order_completed" event with the order details
Wait 30 seconds
```

### State Transitions

```
Move the order from "pending" to "approved" when all approvals are received
```

State transitions explicitly name the from-state and the to-state.

### Error Recovery

```
Attempt to process the payment:
  If it fails with insufficient_funds:
    Notify the customer and mark the order as pending
  If it fails for any other reason:
    Log the error and escalate to support
  Regardless of outcome:
    Record the transaction attempt
```

### Collection Manipulation

```
Keep only the items where status is "active"
Sort the results by date, newest first
Find the first record where amount exceeds the threshold
Group the transactions by month
Get the unique values of category from the product list
Add the new item to the list
Remove the expired entry from the list
```

---

## Part 4 -- Function Syntax

### FUNCTION (pure -- no side effects)

Functions are pure -- same inputs always produce same outputs. Safe to retry.

```
FUNCTION calculate_line_total(item):
  result = item.quantity multiplied by item.unit_price
  RETURNS result

FUNCTION calculate_order_total(items):
  result = sum of calculate_line_total(item) for each item in items
  RETURNS result
```

Functions support conditional logic using IF/ELSE IF/ELSE. Function bodies may use either `=` assignment or natural phrasing (`Calculate X as...`) -- both are valid:

```
FUNCTION apply_tax_rate(amount, jurisdiction):
  IF jurisdiction = "ON" THEN rate = 0.13
  ELSE IF jurisdiction = "AB" THEN rate = 0.05
  ELSE rate = 0.00
  RETURNS amount * rate
```

### ACTION (impure -- has side effects)

ACTIONs signal that the operation has real-world consequences. Not safe to blindly retry.

```
ACTION send_invoice(customer, order):
  Generate the invoice PDF from the order details
  Send the invoice to customer.email
  Log: "Invoice sent to {customer.email} for order {order.id}"
  RETURNS the delivery confirmation
```

**When to choose**:
- Use **FUNCTION** when the operation is a pure calculation with no side effects.
- Use **ACTION** when the operation sends emails, writes files, calls APIs, or changes external state.

---

## Part 5 -- Quality

### Anti-Patterns

If you catch yourself writing programming syntax, you already know the natural way to say it:

| If you catch yourself writing...     | You already know the natural way            |
|--------------------------------------|---------------------------------------------|
| `SET x = x + 1`                     | Add 1 to x                                 |
| `FOR i = 0 TO len(items)`           | For each item in the list                   |
| `IF condition THEN ... END IF`       | If the condition holds: (indent)            |
| `RETURN NULL`                        | Return nothing                              |
| `item != null`                       | the item is present                         |
| Deeply nested If/Otherwise blocks    | Break into separate steps or rules          |
| Side effects inside a FUNCTION       | Use ACTION for anything with side effects   |
| "Handle errors appropriately"        | Specify each error case explicitly          |
| "Extract relevant fields"            | List exactly which fields                   |
| "Validate the data"                  | State each validation rule                  |
| "Use common sense"                   | Define the expected behavior                |
| Nested conditionals 3+ deep          | Break into separate rules                   |
| Ambiguous pronouns ("it", "this")    | Name the specific thing                     |
| All rules in one section, all errors in another | Group by behavior/procedure      |

### Completeness Checklist

Before finalizing a spec, verify:

- [ ] Tier declared in Meta section
- [ ] Purpose stated in 1-3 sentences
- [ ] All inputs listed with types (Standard+)
- [ ] All outputs defined with structure (Standard+)
- [ ] Every BEHAVIOR has rules, at least one error case, and at least one example
- [ ] Every PROCEDURE has ordered steps, at least one error case, and at least one example
- [ ] PROCEDURE steps are ordered logically (each step has what it needs from prior steps)
- [ ] Side effects use ACTION, not FUNCTION
- [ ] Iteration uses natural English phrasing (not programming syntax)
- [ ] No programming-language idioms (no `i++`, no `arr[i]`, no `x = x + 1`)
- [ ] Rules and steps use MUST/SHOULD/MAY/CAN consistently
- [ ] No ambiguous instructions remain
- [ ] No rule is restated in Constraints (deduplicated)
- [ ] No Type, Function, or Action is defined but never referenced
- [ ] Every input enum value maps to at least one rule
- [ ] Related rules consolidated (one decision = one rule with branches)
- [ ] Reference/lookup data extracted to `assets/` if over 10 lines
- [ ] PRECEDENCE declared if overlapping conditions exist (Complex)
- [ ] State transitions explicitly name the from-state and to-state
- [ ] Validator runs clean: `python3 scripts/validate_sesf.py <spec.md>`
