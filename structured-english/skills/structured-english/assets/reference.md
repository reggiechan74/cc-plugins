# SESF v4 Reference

SESF v4 is a natural language for thinking programmatically. The precision comes from legal English conventions (MUST, SHOULD, MAY, CAN) and formal logic (IF/THEN, AND/OR, FOR EACH, first_match_wins). Every line should read like an instruction to a competent human assistant. Non-programmers should be able to read or write SESF without programming experience.

This reference is organized in six parts:

1. **Shared Foundations** -- concepts and syntax used by both BEHAVIOR and PROCEDURE blocks
2. **Declarative Syntax** -- BEHAVIOR blocks for stating rules about what must be true
3. **Procedural Syntax** -- PROCEDURE blocks for describing step-by-step processes
4. **Function Syntax** -- FUNCTION and ACTION definitions
5. **Quality** -- anti-patterns and completeness checklist
6. **Hybrid Notation** -- @config, @route, $variable threading, compact tables, and precision keywords

---

## Part 1 -- Shared Foundations

These concepts apply to both BEHAVIOR and PROCEDURE blocks.

### Tier Comparison

| Tier     | Blocks Allowed                                      | Use When                                              | Target Length | Hybrid Elements |
|----------|-----------------------------------------------------|-------------------------------------------------------|---------------|-----------------|
| Micro    | 1 BEHAVIOR or 1 PROCEDURE                           | Single concern, 1-2 rules/steps                       | 20-40 lines   | Compact ERRORS/EXAMPLES optional; @config/@route not recommended |
| Standard | Multiple BEHAVIORs and/or PROCEDUREs sharing types  | Multiple concerns                                     | 100-300 lines | All hybrid elements available; Notation section optional |
| Complex  | Everything + PRECEDENCE, State/Flow                  | Overlapping rules, state machines, mixed declarative+procedural | 300-600 lines | All hybrid elements available; Notation section optional |

**Section ordering** (sections MUST appear in this order when present):

Meta, Notation, Purpose, Audience, Scope, Inputs, Outputs, @config, Types, Functions, Behaviors/Procedures, Constraints, Precedence, Dependencies, Changelog.

**Required sections per tier:**

- **Micro**: Meta, Purpose, Behaviors/Procedures. Constraints is optional. Notation is optional.
- **Standard**: Meta, Purpose, Scope, Inputs, Outputs, Types, Functions, Behaviors/Procedures, Constraints, Dependencies. Notation (optional). Audience and Changelog are optional.
- **Complex**: All Standard sections plus Precedence. Notation (optional). Audience is optional. Behaviors MAY include State/Flow subsections.

### Meta Section Format

**Standard/Complex tier** (multi-line):
```
Meta
  Version: X.X.X
  Date: YYYY-MM-DD
  Domain: ...
  Status: active
  Tier: standard
```

**Micro tier** (pipe-delimited single line):
```
Meta: Version X.X.X | Date: YYYY-MM-DD | Domain: ... | Status: active | Tier: micro
```

The `Date` field always uses `YYYY-MM-DD` format with a colon separator in both forms.

### Requirement Keywords

Use these keywords with precise meanings. All operative terms MUST be capitalized when used as operative keywords.

**Requirement Strength:**

| Keyword    | Meaning |
|------------|---------|
| MUST       | Absolute requirement. Failure = invalid output. |
| MUST NOT   | Absolute prohibition. Violation = invalid output. |
| SHOULD     | Recommended. Skip only with documented reason. |
| SHOULD NOT | Discouraged. Do only with documented reason. |
| MAY        | Optional. Include if relevant or beneficial. |
| CAN        | Capability. The system is able to do this. |

**Quantifiers:**

| Keyword    | Meaning |
|------------|---------|
| EACH       | One by one, sequentially. |
| EVERY / ALL | Universal -- all items must satisfy the condition. |
| ANY        | At least one item satisfies the condition. |
| NONE       | Zero items satisfy the condition. Use instead of "not any" or "no [items]". |
| EXACTLY N  | Precise count -- no more, no fewer. |
| AT MOST N  | Upper bound -- N or fewer. |
| AT LEAST N | Lower bound -- N or more. |

**Logical Connectives:**

| Keyword    | Meaning |
|------------|---------|
| AND        | Both conditions required. |
| OR         | At least one condition (inclusive: A or B or both). |
| EITHER...OR | Exactly one, not both (exclusive). |

For compound grouping, use:
- "ALL of the following:" for grouped AND
- "ANY of the following:" for grouped OR

**Negation:**

Never combine NOT with EVERY/ALL/ANY -- rewrite using NONE or UNLESS:
- Write "NONE of the files are processed" not "not any files are processed"
- Write "SKIP invalid items" not "don't process invalid items"

**Temporal:**

| Keyword     | Meaning |
|-------------|---------|
| BEFORE      | Prerequisite -- must complete before this begins. |
| AFTER       | Postcondition -- only begins after this completes. |
| IMMEDIATELY | Next action, no intervening steps. |
| EVENTUALLY  | At some future point, not necessarily next. |
| ALWAYS      | Invariant -- condition holds continuously. |
| UNTIL       | Condition holds up to a specified event. |

**Conditions:**

| Keyword       | Meaning |
|---------------|---------|
| UNLESS        | Exception to a rule. |
| ONLY          | Exclusive restriction. |
| ONLY WHEN     | Necessary condition (if and only if). |
| REGARDLESS OF | Override a condition. |

**Flow:**

| Keyword              | Meaning |
|----------------------|---------|
| SKIP                 | Bypass the current item, continue with next. |
| HALT                 | Stop all processing. |
| RETRY [UP TO N TIMES] | Attempt again, with bounded retries. |

**Precision:**

| Keyword       | Meaning |
|---------------|---------|
| VERBATIM      | Character-for-character, no paraphrasing. |
| SILENTLY      | Perform without reporting to user. |
| INDEPENDENTLY | No dependency between items. |

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

### Empty Section Stubs

When a required section has no content, use the `-- none` stub with a brief reason:

```
Types
-- none: all data structures are inline within behavior and procedure blocks

Functions
-- none: all logic is expressed directly in behavior rules and procedure steps
```

This prevents the validator from flagging empty required sections.

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

### Markdown Formatting

SESF specs are stored as `.md` files and are often read in markdown-rendering editors (VS Code, GitHub). Selective markdown formatting improves visual scanning without sacrificing plain-text readability.

**Backticks for identifiers** (SHOULD):

Use backtick formatting for system tokens that are distinct from surrounding prose:
- `$variable` names: `$refund_amount`, `$eligibility`
- `@config` keys: `$config.max_retries`, `$config.supported_currencies`
- Block references: `validate_payment`, `process_refund`
- Literal values: `"Currency required"`, `500`, `[CAD, USD, EUR]`

Backticks create a clear visual layer between "things in the system" and "English instructions about those things."

**Bold for block keywords** (SHOULD):

Block keywords SHOULD use `**bold**` to stand out in rendered editors:
- `**BEHAVIOR** validate_payment:` instead of `BEHAVIOR validate_payment:`
- `**RULE** positive_amount:` instead of `RULE positive_amount:`
- `**STEP** validate -> $eligibility` instead of `STEP validate -> $eligibility`

**Heading syntax for sections** (SHOULD):

Section headers SHOULD use markdown heading syntax for TOC navigation and collapsible sections:
- `### Behaviors` instead of `Behaviors`
- `### Types` instead of `Types`

Specs MUST remain readable as plain text without rendering.

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

  -- Or use inline format for simple errors:
  ERROR error_name: severity → action, "message"

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

### Decision Tables (@route)

For conditionals with 3 or more branches, use an @route decision table instead of
chained WHEN/THEN/ELSE WHEN blocks. See Part 6 for full @route syntax.

A BEHAVIOR block MAY contain both:
- @route tables for multi-branch classification (3+ branches)
- WHEN/THEN rules for binary constraints

The form is determined by branch count, not author preference.

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

### Variable Threading ($variable)

PROCEDURE steps can declare output variables using → $var syntax.
All variables have document-global scope -- once produced by any STEP in any PROCEDURE,
they are visible everywhere in the spec. See Part 6 for full $variable syntax.

```
STEP gather_data → $raw_sales, $date_range
  Query the database → $raw_sales
  Determine the date range → $date_range
```

Variable threading replaces prose like "record the result" with explicit declarations.

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
| `@route` with only 2 branches        | Use WHEN/THEN instead (threshold: 3+ branches) |
| `$config` for runtime values          | Use $variable threading; @config is for static values only |
| Omitting Notation for human-audience specs | Notation helps human readers but is optional |

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
- [ ] @config values referenced correctly ($config.key matches @config entries)
- [ ] $variable references produced before use (document-global scope)
- [ ] @route tables have wildcard default row
- [ ] Notation section present if spec targets human readers
- [ ] Validator runs clean: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/scripts/validate_sesf.py <spec.md>`

---

## Part 6 -- Hybrid Notation

SESF v4 adds five structured notations for cases where compact syntax is more precise
than prose. Each element is optional — use it when it reduces ambiguity.

### Notation Section (Optional)

Specs MAY include a Notation section after the Meta block. It is optional but helpful for human readers.

**Template:**

```
Notation
* $ — references a variable or config value (e.g., $today, $config.path)
* @ — marks a structured block (@config for parameters, @route for decision tables)
* → — means "produces" (in steps), "routes to" (in tables), or "yields" (in examples)

Requirement Strength
* MUST / MUST NOT — mandatory / prohibited
* SHOULD / SHOULD NOT — recommended / discouraged
* MAY — optional (permission)
* CAN — capability (ability)

Quantifiers
* EACH — one by one, sequentially
* EVERY / ALL — universal (all must satisfy)
* ANY — at least one
* NONE — zero matches (use instead of "not any" or "no [items]")
* EXACTLY N / AT MOST N / AT LEAST N — precise bounds
* WHERE — filter qualifier (EACH item WHERE condition)

Logical Connectives
* AND — both conditions required
* OR — at least one condition (inclusive: A or B or both)
* EITHER A OR B — exactly one, not both (exclusive)
* Compound grouping:
  - "ALL of the following:" for grouped AND
  - "ANY of the following:" for grouped OR

Negation
* Never combine NOT with EVERY/ALL/ANY — rewrite using NONE or UNLESS
* "NONE of the files are processed" NOT "not any files are processed"
* "SKIP invalid items" NOT "don't process invalid items"

Temporal
* BEFORE — prerequisite (must complete before this begins)
* AFTER — postcondition (only begins after this completes)
* IMMEDIATELY — next action, no intervening steps
* EVENTUALLY — at some future point, not necessarily next
* ALWAYS — invariant (condition holds continuously)
* UNTIL — condition holds up to a specified event

Conditions
* UNLESS — exception to a rule
* ONLY — exclusive restriction
* ONLY WHEN — necessary condition (if and only if)
* REGARDLESS OF — override a condition

Flow
* SKIP — bypass, continue with next
* HALT — stop all processing
* RETRY [UP TO N TIMES] — attempt again

Collections
* EXCLUDING — items in one set but not another (set difference)
* EXCEPT — all items minus a specified subset (complement)
* INCLUDES — membership test (item is in collection)

Precision
* VERBATIM — character-for-character, no paraphrasing
* SILENTLY — perform without reporting to user
* INDEPENDENTLY — no dependency between items
```

Notation sections are optional at all tiers. When included, they bridge readability for human readers.
When included at micro tier, it MAY use an abbreviated form covering only the categories actually used in that spec.

### @config — Centralized Parameters

Declares all configurable values in a single block. Replaces scattered inline values.

**Placement:** After Outputs, before Types (or before Behaviors in micro tier).

**Syntax:**
```
@config
  key: value
  key: value
  nested:
    key: value
```

**Rules:**
- @config MUST appear before any BEHAVIOR or PROCEDURE block
- Keys use snake_case
- Values are literals: strings, numbers, lists `[a, b, c]`, nested objects
- Reference with `$config.key` anywhere in the spec
- `$config.nested.key` for nested values
- @config is for static values only — not for runtime variables (those use `$var` threading)

**Example:**
```
@config
  max_retries: 3
  output_path: /reports/daily
  recipients: [alice@example.com, bob@example.com]
  thresholds:
    warning: 80
    critical: 95
```

### @route — Decision Tables

Replaces WHEN/THEN/ELSE WHEN chains for multi-branch conditional routing.

**Placement:** Inside a BEHAVIOR block, replacing multiple RULE blocks.

**When to use:** Use @route when a conditional has **3 or more branches** mapping inputs
to categories or destinations. Use WHEN/THEN rules for **binary constraints** (true/false,
valid/invalid) or single-condition guards. The form is determined by branch count,
not author preference.

**Syntax:**
```
@route table_name [first_match_wins]
  condition_1  → outcome_1
  condition_2  → outcome_2
  *            → default_outcome
```

**Modes:**
- `first_match_wins` — stop at first matching row (default, can be omitted)
- `all_matches` — apply all matching rows

**Rules:**
- @route MUST appear inside a BEHAVIOR block
- `*` (wildcard) is the default case — it MUST be the last row
- Each row is `condition → outcome` with `→` as separator
- Conditions are natural English predicates (not code expressions)
- A @route table replaces multiple RULE blocks for multi-branch routing
- A BEHAVIOR MAY contain both @route (for 3+ branch routing) AND individual
  RULE blocks (for binary constraints)

**Example:**
```
BEHAVIOR classify_document: Route incoming documents to the correct handler

  @route document_type [first_match_wins]
    is_invoice AND has_PO_number     → Accounts Payable (auto-match to PO)
    is_invoice AND no_PO_number      → Accounts Payable (manual review queue)
    is_contract AND value > $50,000  → Legal Review
    is_contract AND value <= $50,000 → Department Head Approval
    is_expense_report                → Finance (reimburse within 5 business days)
    *                                → General Inbox (manual triage)

  RULE retention_policy:
    all classified documents MUST be archived for 7 years
    -- This binary constraint doesn't fit the routing table
```

### $variable Threading — Explicit Data Flow

Replaces implicit data flow between PROCEDURE steps with explicit variable declarations.

**Scope:** Document-global. Once a $variable is produced by any STEP in any PROCEDURE,
it is visible everywhere in the spec. The validator checks that a variable is produced
somewhere in the spec before it is referenced.

**Syntax:**
```
STEP step_name → $output1, $output2
  Action description → $output1
  Action description → $output2
```

**Rules:**
- `→ $var` after a STEP name declares output variables
- `→ $var` after an action line within a step shows which action produces which variable
- Variables use `$` prefix and snake_case naming
- `$config.key` references the @config block; `$var` references a step output
- Variable threading is optional — steps without outputs omit the `→` declaration
- `$var` replaces "Record the result as X" or "Store the output for later use" prose

**Example:**
```
PROCEDURE prepare_report: Generate and format the weekly sales report

  STEP gather_data → $raw_sales, $date_range
    Query the sales database for the current week → $raw_sales
    Determine the Monday-to-Sunday date range → $date_range

  STEP calculate_totals → $summary
    Group $raw_sales by product category
    Calculate subtotals and grand total → $summary

  STEP format_output:
    Render $summary into the report template
    Include $date_range in the header
    -- No output variable needed; this step produces the final file
```

### Error Formats

**Inline ERROR format (preferred):**

Single-line error declarations. This SHOULD be the default format for error cases.

**Syntax:**
```
ERROR error_name: severity → action, "message"
```

**Example:**
```
ERROR file_not_found: critical → halt and inform user, "File '{path}' not found."
ERROR parse_error: warning → skip bad rows, "Skipped {count} malformed rows."
ERROR empty_result: info → generate empty report, "No data for {date_range}. Empty report."
```

**Compact ERRORS table (alternative for backward compatibility):**

An alternative tabular format accepted for multiple error cases in a single block.

**Syntax:**
```
ERRORS:
| name | when | severity | action | message |
|------|------|----------|--------|---------|
| error_name | condition | critical/warning/info | recovery action | "user message" |
```

**Example:**
```
ERRORS:
| name             | when                     | severity | action                | message                                    |
|------------------|--------------------------|----------|-----------------------|--------------------------------------------|
| file_not_found   | input file does not exist | critical | halt and inform user  | "File '{path}' not found."                 |
| parse_error      | CSV has malformed rows    | warning  | skip bad rows         | "Skipped {count} malformed rows."          |
| empty_result     | query returns zero rows   | info     | generate empty report | "No data for {date_range}. Empty report."  |
```

**Rules:**
- Inline ERROR format SHOULD be preferred for simple error cases
- ERRORS tables are accepted as an alternative, especially for blocks with many error cases
- Use full multi-line ERROR blocks only for complex recovery logic that needs multiple sentences
- Severity values: `critical` (halt), `warning` (continue with degradation), `info` (log only)
- `{variable}` in message strings indicates dynamic interpolation
- Mixed usage allowed: a block can combine inline errors, error tables, and full ERROR blocks

### Compact Examples

Single-line format SHOULD be preferred for simple, self-evident test cases. Use full EXAMPLE blocks only when NOTES or multi-line INPUT/EXPECTED are needed.

**Syntax:**
```
EXAMPLES:
  example_name: input_description → expected_outcome
```

**Rules:**
- `→` separates input from expected output
- Input side uses `key=value` pairs separated by commas
- Compact examples are for simple, self-evident cases
- For examples needing NOTES or multi-line INPUT/EXPECTED, use full EXAMPLE blocks
- Mixed usage allowed: a block can have both compact EXAMPLES and full EXAMPLE blocks

**Example:**
```
EXAMPLES:
  valid_email: input="user@example.com" → accepted
  missing_domain: input="user@" → rejected with "missing domain"
  unicode_local: input="ü@example.com" → accepted (RFC 6531)
```

### Anti-Patterns for Hybrid Notation

| Anti-pattern | Fix |
|---|---|
| @route with only 2 branches | Use WHEN/THEN instead (threshold: 3+ branches) |
| $config for runtime values | Use $variable threading; @config is for static values only |
| @route outside BEHAVIOR block | @route replaces RULE chains; it belongs in BEHAVIORs only |
| Mixing $config.key and hardcoded values for same parameter | Move all instances to @config |
| Error table with complex multi-sentence recovery | Use traditional ERROR block for that case |
| $variable referenced but never produced | Every $var needs a STEP with → $var declaration |
| Omitting Notation for human-audience specs | Notation helps human readers but is optional |
| "Process the files" (no quantifier) | "Process EACH file" or "Process ALL files" |
| "If there are errors" (ambiguous quantifier) | "If ANY error exists" or "If EVERY check fails" |
| "Don't process any files" (NOT + ANY = ambiguous) | "Process NONE of the files" or "SKIP ALL files" |
| "Not all files should be included" (NOT + ALL) | "SKIP files that match [condition]" |
| "Update the file after scanning" (vague temporal) | "IMMEDIATELY AFTER scanning, update the file" |
| "Do this eventually" (vague temporal) | "EVENTUALLY update the file (AFTER ALL scans complete)" |
| "Don't do X if Y" (negated condition) | "SKIP X UNLESS Y is false" or "X UNLESS Y" |
| "Try again if it fails" (unbounded retry) | "RETRY UP TO 3 TIMES" |
| "Copy the text" (may paraphrase) | "Copy the text VERBATIM" |
| "A AND B OR C" (ungrouped compound) | "ALL of the following: A, B" OR C separately |
| "A or B" (ambiguous inclusive/exclusive) | "A OR B" (inclusive) or "EITHER A OR B" (exclusive) |
| "The file must be locked" (when?) | "The file MUST ALWAYS be locked during processing" |
| "Process files that are large" (vague filter) | "Process EACH file WHERE size > 100MB" |
