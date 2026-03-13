# SESF v4.1 Authoring Guide

You're writing a spec that a human will read, review, and maintain. The output format (SESF v4.1) uses formal BEHAVIOR/PROCEDURE/RULE/STEP blocks — the structure IS the content. This guide teaches you the thinking process for deciding what to write and how to organize it.

The mental model: you think "this is a behavior" and write `**BEHAVIOR**`. You think "this is a procedure" and write `**PROCEDURE**`. You think "this rule has conditions" and write WHEN/THEN. The formal keywords in your head go directly onto the page.

---

## Step 1: Identify Behaviors (Declarative Rules)

Ask yourself: **"What are the rules? What conditions produce different outcomes?"**

Behaviors are declarative — they describe *what should be true*, not *when to check it*. Look for these patterns in your domain:

- **Validation rules** — "An invoice MUST have a positive amount." Conditions that reject or accept inputs.
- **Classification logic** — "Expense reports over $5,000 require VP approval." Inputs get sorted into categories with different handling.
- **Routing/escalation** — "Critical bugs go to the on-call engineer; minor bugs go to the backlog." Inputs get sent to different destinations.
- **Business rules with thresholds** — "Accounts with a balance under $100 cannot transfer internationally." Numeric boundaries that change behavior.
- **Error handling with severity levels** — "Missing a required field is critical; a formatting issue is a warning." Different failure types get different responses.

**How to spot them:** If you can phrase it as "When X is true, Y happens" — that's a behavior. If you find yourself listing conditions and outcomes, you're looking at behaviors.

**Where they go in SESF v4.1:**

- Each group of related rules → `**BEHAVIOR** name: description` block
- Conditional rules inside behaviors → `**RULE** name:` with WHEN/THEN/ELSE
- Always-true constraints → `**RULE** name:` with MUST/SHOULD/MAY statement
- Rules with 3+ branches → `@route` decision table inside the BEHAVIOR block
- Rules with 1-2 branches → WHEN/THEN/ELSE inside a RULE

---

## Step 2: Identify Procedures (Ordered Steps)

Ask yourself: **"What are the ordered steps? What happens first, second, third?"**

Procedures are imperative — they describe *what to do and in what order*. Look for:

- **Sequential workflows** — "First validate, then classify, then route." Steps that must happen in a specific order.
- **Data pipelines** — "Extract raw data, transform it, load it into the warehouse." Each stage feeds the next.
- **Approval chains** — "Submit to manager, then director, then VP if over threshold." Escalating approval with gates.
- **Multi-phase processes** — "Intake, processing, quality check, delivery." Distinct stages with clear boundaries.
- **Anything with side effects** — "Send an email, write a file, call an API." Steps that change the world outside the spec.

**How to spot them:** If the order matters — if doing step 3 before step 1 would produce a wrong result — that's a procedure.

**Where they go in SESF v4.1:**

- The overall workflow → `**PROCEDURE** name: description` block
- Each major action → `**STEP** name: description`
- Steps that produce outputs → `**STEP** name: description → $output_var`
- Step-level branching → WHEN/THEN inside the STEP body

---

## Step 3: Identify Decision Points

Ask yourself: **"Where does the logic branch? How many branches?"**

Every spec has decision points — moments where the path forward depends on a condition. The key question is how many branches a decision has, because that determines the notation:

| Branches | Notation | Example |
|----------|----------|---------|
| 1-2 | WHEN/THEN/ELSE in a RULE | `WHEN file > 10MB THEN process in chunks ELSE process inline` |
| 3+ | `@route` table | A decision table mapping conditions to outcomes |

**How to extract decision points from narrative prose:**

Your stakeholder says: *"Well, if it's an invoice we send it to AP, but if it's a contract over fifty grand it goes to legal, contracts under fifty grand just need department head sign-off, expense reports go to finance, and anything else we just triage manually."*

Count the branches: invoice → AP, big contract → legal, small contract → dept head, expense → finance, everything else → manual triage. That's 5 branches — clearly an `@route` table:

```
@route document_type [first_match_wins]
  is_invoice                           → Accounts Payable
  is_contract AND value > $50,000      → Legal Review
  is_contract AND value ≤ $50,000      → Department Head Approval
  is_expense_report                    → Finance
  *                                    → Manual Triage
```

**Common mistake:** Using `@route` for binary decisions. "Is it valid? Yes or no" has only 2 branches — write it as WHEN/THEN/ELSE.

---

## Step 4: Identify Data Flow

Ask yourself: **"What does each step produce that the next step needs?"**

Most of the time, data flow is obvious from step ordering. "STEP 2 processes the output of STEP 1" is clear enough — you don't need any special notation.

**Use STEP → $variable when:**

- Multiple steps produce outputs consumed non-linearly (STEP 3 needs outputs from both STEP 1 and STEP 2)
- The same intermediate result is used in 3+ places and you need a stable name for it
- Ambiguity would cause bugs — "the extracted data" could refer to data from STEP 1 or STEP 3

**Don't use $variable threading when:**

- Data flows linearly from one step to the next
- The step names make the data flow obvious
- You're only writing a micro-tier spec (too small to benefit)

**Example where threading helps:**

```
**STEP** gather: Query the sales database → $raw_sales, $date_range
**STEP** benchmark: Fetch industry comparisons → $industry_averages
  Fetch industry averages for $date_range.
**STEP** analyze: Compare and report
  Compare $raw_sales against $industry_averages.
  Include $date_range in the report header.
```

The analyze step consumes outputs from both gather and benchmark. Without `$variable` names, you'd need awkward sentences like "the sales data from the gather step" and "the averages from the benchmark step."

---

## Step 5: Identify Failure Modes

Ask yourself: **"What can go wrong at each step?"**

Walk through every step and ask: what if the input is missing? Malformed? Too large? What if an external service is down? What if the data contradicts itself?

**Building the error table:**

For each failure mode, decide three things:

1. **Name it** — a snake_case identifier: `missing_required_field`, `amount_exceeds_limit`
2. **Assign severity:**
   - **critical** — processing MUST stop. The output would be wrong or dangerous if you continued.
   - **warning** — processing continues with degradation. The output is usable but imperfect.
   - **info** — log it and move on. No impact on the output.
3. **Define the action** — exactly what happens. Not "handle the error" but "reject with HTTP 422 and list the missing fields."

**All errors go in one place.** SESF v4.1 consolidates errors into a single `## Errors` table at the end of the spec. Don't scatter ERROR declarations after individual rules — that's the old v4 style and makes them hard to find and easy to miss.

```markdown
## Errors

| Error | Severity | Action |
|-------|----------|--------|
| missing_field | critical | HALT: "Required field {field} is missing." |
| over_budget | warning | Flag for review; suggest promotion to next tier. |
| empty_result | info | Generate empty report; log the date range queried. |
```

---

## Step 6: Choose a Tier

Ask yourself: **"How complex is this, really?"**

| Tier | Line Budget | When to Use | Typical Notation |
|------|-------------|-------------|------------------|
| **Micro** | 20-80 lines | Single concern, ≤5 rules, no shared structures | 1 PROCEDURE block, inline config, error table |
| **Standard** | 80-200 lines | 2-5 concerns, OR shared structures, OR multi-phase procedures | BEHAVIOR + PROCEDURE blocks, @route, @config, examples |
| **Complex** | 200-400 lines | 5+ concerns, overlapping rules needing precedence, complex interactions | Multiple BEHAVIORs + PROCEDUREs, $variable threading, @route, worked examples |

**Decision guide:**

- Can you explain the entire spec in one paragraph? → **Micro**
- Do you have multiple concerns that interact, or a multi-phase workflow? → **Standard**
- Do concerns overlap (same input, different rules from different concerns)? → **Complex**

**When in doubt, start with Standard.** You can always demote to Micro if it fits in 80 lines, or promote to Complex if interactions get tangled.

---

## Mapping Table: Thinking → Writing

In SESF v4.1, the mapping is direct — the thinking concepts ARE the output syntax:

| You're thinking... | Write it as... |
|---------------------|----------------|
| "This is a behavior — a group of related rules" | `**BEHAVIOR** name: description` block with `**RULE**` entries |
| "This is a procedure — ordered steps" | `**PROCEDURE** name: description` block with `**STEP**` entries |
| "This rule has a condition and an action" | `**RULE** name:` with WHEN/THEN/ELSE |
| "This rule is always true" | `**RULE** name:` with MUST/SHOULD/MAY statement |
| "This step produces output for later steps" | `**STEP** name: description → $output_var` |
| "This rule isn't obvious — I should explain why" | Rationale annotation: `(Rationale: explanation)` |
| "These errors need to be documented" | Row in the consolidated `## Errors` table |
| "This has 3+ branches" | `@route` table inside the BEHAVIOR or at spec level |
| "This has 3+ config values" | `@config` block in Configuration section |

---

## Worked Walkthrough: Invoice Processing Pipeline

Let's take a concrete domain from "I have a vague idea" through all six thinking steps.

**The vague idea:** "We need a spec for processing incoming invoices — validate them, classify by type, route to the right team, and handle errors."

### Thinking Step 1: Behaviors

I notice several rule sets:

- **Validation rules:** Required fields (vendor, amount, date), positive amounts, valid currency
- **Classification logic:** Different invoice types (standard, recurring, credit note, pro-forma, debit memo) — that's 5 types, so an `@route`
- **Routing logic:** Based on classification, invoices go to different teams — another `@route`
- **Threshold rules:** Invoices over $50K need additional approval

### Thinking Step 2: Procedures

The overall workflow is sequential:

1. Receive and validate the invoice
2. Classify by document type
3. Route to the appropriate team
4. Generate confirmation

### Thinking Step 3: Decision Points

- Document type classification: 5 branches → `@route` table
- Team routing: depends on classification, so 5+ branches → `@route` table
- Amount threshold: 2 branches (over/under $50K) → WHEN/THEN/ELSE

### Thinking Step 4: Data Flow

Linear flow — each step reads the previous step's output. No need for `$variable` threading. "The validated invoice from STEP 1" is unambiguous.

### Thinking Step 5: Failure Modes

- Missing required fields (critical — can't process)
- Invalid currency (critical — can't convert)
- Duplicate invoice number (warning — flag but don't block)
- Amount outlier (info — log for review)
- Unclassified document type (warning — route to manual review)

### Thinking Step 6: Tier

Multiple concerns (validation, classification, routing), two `@route` tables, a multi-step workflow. That's **Standard** tier, probably ~120 lines.

### The SESF v4.1 Output

Here's what those thinking steps produce:

```markdown
# Invoice Processing Pipeline

Validate, classify, and route incoming invoices to the correct processing
team. Reject malformed invoices immediately; flag anomalies for review.

**Not in scope:** Payment processing, vendor onboarding, currency conversion rates.

## Configuration

@config
  required_fields: [vendor_name, invoice_number, invoice_date, amount, currency]
  supported_currencies: [USD, CAD, EUR, GBP]
  high_value_threshold: 50000

**BEHAVIOR** classify_invoice: Determine invoice type from document content

  @route invoice_type [first_match_wins]
    has "Credit" or negative amount            → credit_note
    has "Recurring" or matches prior schedule   → recurring_invoice
    has "Pro Forma" or "Proforma"              → pro_forma
    has "Debit Memo" or "Debit Note"           → debit_memo
    *                                          → standard_invoice

**BEHAVIOR** route_to_team: Assign invoice to processing team based on type

  @route team_assignment [first_match_wins]
    credit_note                                → Accounts Receivable (credit processing queue)
    recurring_invoice                          → Accounts Payable (auto-match to schedule)
    pro_forma                                  → Procurement (confirmation required before payment)
    debit_memo                                 → Accounts Payable (dispute resolution queue)
    standard_invoice                           → Accounts Payable (standard processing)

**BEHAVIOR** validate_invoice: Ensure invoice data meets processing requirements

  **RULE** required_fields:
    ALL fields in $config.required_fields MUST be present and non-empty.
    WHEN ANY field is missing THEN reject with missing_required_field.

  **RULE** positive_amount:
    For non-credit-note invoices, the amount MUST be positive.

  **RULE** valid_currency:
    currency MUST be one of $config.supported_currencies.
    WHEN currency is not supported THEN reject with unsupported_currency.

  **RULE** duplicate_check:
    WHEN an invoice with the same invoice_number and vendor_name already exists
    THEN flag as duplicate_invoice but continue processing
    (Rationale: duplicates may be legitimate resubmissions — block would cause delays)

**PROCEDURE** process_invoice: Full invoice processing pipeline

  **STEP** validate: Check all required fields and constraints
    Apply ALL rules from validate_invoice.

  **STEP** classify: Determine invoice type
    Apply the invoice_type @route table.

  **STEP** route: Send to appropriate team
    Apply the team_assignment @route table.
    WHEN amount > $config.high_value_threshold THEN add VP approval flag.

  **STEP** confirm: Generate processing receipt
    Produce receipt with: invoice number, classified type, assigned team,
    any flags (duplicate, high-value), and timestamp.

## Rules

- **No silent modification:** The pipeline MUST NOT alter any invoice field values. Flag anomalies; do not correct them.
- **Audit trail:** EVERY routing decision MUST be logged with the rule that triggered it.

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| missing_required_field | critical | Reject: "Missing fields: {field_list}." |
| unsupported_currency | critical | Reject: "Currency {currency} not supported." |
| duplicate_invoice | warning | Flag for review: "Possible duplicate of {existing_id}." Continue processing. |
| amount_outlier | info | Log: "Amount {amount} exceeds 3 sigma for this vendor." |
| unclassified_type | warning | Route to manual review queue. |
```

Notice how the thinking steps mapped directly to blocks. The BEHAVIOR blocks came from identifying rule groups. The PROCEDURE block came from the sequential workflow. The `@route` tables came from recognizing 5-branch decisions. The error table came from the failure mode analysis. The formal block syntax makes everything scannable.

---

## Common Mistakes

Things human authors get wrong when writing SESF v4.1 specs:

**1. Forgetting to wrap rules in BEHAVIOR blocks.** Every declarative rule belongs inside a `**BEHAVIOR** name:` block. Rules floating outside any block are orphans — wrap them or move them to the cross-cutting Rules section.

**2. Using prose "if/then" instead of WHEN/THEN.** Inside a RULE, write `WHEN condition THEN action`, not "If the condition is true, then do the action." The formal syntax is the point — it makes rules scannable.

**3. Scattering errors inline instead of consolidating.** Don't write `ERROR invalid_amount: critical → halt` after a rule. Collect ALL errors into the `## Errors` table at the end. One place to find them, one place to maintain them. This is a key improvement over SESF v4.

**4. Using numbered lists instead of STEP entries.** Inside a PROCEDURE, write `**STEP** name: description`, not `1. Do the first thing. 2. Do the second thing.` The STEP syntax gives each action a name and optional output variable.

**5. Creating empty sections.** If there are no cross-cutting rules, don't write `## Rules` followed by nothing. Omit the section entirely.

**6. Using @route for 2-branch decisions.** "Is it valid? Yes or no" is a WHEN/THEN/ELSE, not a routing table. Reserve `@route` for 3+ branches.

**7. Overusing $variable threading.** Most micro specs don't need it. "The next STEP uses the output from the previous STEP" is obvious from ordering. Only name variables when the data flow is genuinely non-linear or ambiguous.

**8. Writing happy-path examples.** Examples are for edge cases only — boundary conditions, error paths, non-obvious behavior. If the happy path is obvious from the rules, don't exemplify it.

**9. Adding Meta/Notation/Types sections.** These are removed in v4.1. Version info goes in YAML frontmatter. Symbols are self-evident. Types are described inline where used.

**10. Missing rationale on non-obvious rules.** If a rule exists because of a past incident, a security concern, or a non-intuitive design choice, add a `(Rationale: ...)` annotation. Future readers will thank you.
