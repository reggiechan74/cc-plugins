# SESF v4.1 Reference

The Structured English Specification Format (SESF v4.1) uses formal BEHAVIOR/PROCEDURE/RULE/STEP blocks to define agent behavior with explicit visual scaffolding. Human authors and reviewers scan these blocks faster than prose because the structure is visually distinct — BEHAVIOR blocks jump out from surrounding text, WHEN/THEN conditionals align vertically, and STEP → $var declarations make data flow explicit.

SESF v4.1 modernizes SESF v4 by consolidating errors into a single table (no more scattered inline ERROR declarations), adding rationale annotations, and removing boilerplate sections (Meta, Notation, Types, Functions, Precedence, Dependencies, Changelog). It keeps the same @route, @config, $variable, and RFC 2119 notation as HSF v5.

---

## Section Reference

Sections MUST appear in this order when present. Omit any section that would be empty.

### Purpose (all tiers — required)

A 1-3 sentence statement of what the spec does and why. This is the first paragraph after the `#` heading.

```markdown
# Invoice Processing Pipeline

Validate, classify, and route incoming invoices to the correct processing
team. Reject malformed invoices immediately; flag anomalies for review.
```

### Scope (all tiers — required)

What is IN scope and what is OUT. Use bullet lists or a single "Not in scope" line for micro specs.

```markdown
## Scope

**In scope:**
- Structural validation (required fields, types, formats)
- Policy checks (amount thresholds, duplicate detection)
- Routing to processing teams

**Not in scope:**
- Payment processing (handled by the payment service)
- Vendor onboarding or credit checks
```

For micro specs, a single line suffices:

```markdown
**Not in scope:** retry logic, authentication, batch processing.
```

### Configuration (all tiers — required when static params exist)

Use an `@config` block when 3 or more configuration values exist. For fewer values, state them inline in the text.

**Inline (1-2 values):**
```markdown
Signing secret loaded from WEBHOOK_SECRET env var. Tolerance: 300 seconds.
```

**@config block (3+ values):**
```markdown
## Configuration

@config
  max_retries: 3
  timeout_ms: 30000
  output_dir: /tmp/results/
  supported_currencies: [USD, CAD, EUR, GBP]
```

### Inputs / Outputs (standard + complex only)

Typed parameter lists describing what the spec receives and produces.

```markdown
## Inputs

- `transcript`: string — full meeting transcript, plain text or markdown
- `participant_list`: list of string — names of all attendees (optional)

## Outputs

- `summary`: markdown file — structured meeting summary with action items
- `signal_database`: JSON file — machine-readable extracted signals
```

### BEHAVIOR Blocks (all tiers — required when declarative rules exist)

BEHAVIOR blocks group related declarative rules. Each block has a name and a one-line description, followed by RULE entries.

**Full syntax:**

```markdown
**BEHAVIOR** validate_payment: Ensure payment requests meet processing requirements

  **RULE** positive_amount:
    payment.amount MUST be greater than zero
    (Rationale: zero or negative payments indicate data entry errors)

  **RULE** supported_currency:
    WHEN payment.currency is not in $config.supported_currencies
    THEN reject with unsupported_currency
    (Rationale: unsupported currencies cannot be converted by our payment processor)

  **RULE** high_value_approval:
    WHEN payment.amount > $config.high_value_threshold
    THEN require VP approval before processing
    ELSE process normally

  **RULE** duplicate_check:
    WHEN an invoice with the same number and vendor already exists
    THEN flag as duplicate_invoice but continue processing
```

**RULE variants:**

1. **WHEN/THEN/ELSE** — for conditional logic with 1-2 branches:
   ```
   **RULE** rule_name:
     WHEN condition
     THEN action
     ELSE alternative
   ```

2. **Declarative constraint** — for always-true requirements:
   ```
   **RULE** rule_name:
     constraint MUST/SHOULD/MAY be true
   ```

3. **With rationale** — append parenthetical explanation:
   ```
   **RULE** rule_name:
     constraint MUST be true
     (Rationale: explanation of why this rule exists)
   ```

### PROCEDURE Blocks (all tiers — required when sequential workflows exist)

PROCEDURE blocks define ordered workflows with STEP entries.

**Full syntax:**

```markdown
**PROCEDURE** process_document: Classify and extract data from uploaded document

  **STEP** validate_format: Check file is a supported type → $validated_file
    Verify the file extension is one of $config.supported_formats.
    WHEN format is unsupported THEN reject with unsupported_format.

  **STEP** run_ocr: Extract text from document → $ocr_output
    Submit $validated_file to the OCR engine.
    Record text content, bounding boxes, and confidence scores.

  **STEP** classify: Determine document type → $doc_type
    Apply the document_classification @route table to $ocr_output.
    WHEN document is unclassified THEN queue for manual review and HALT.

  **STEP** extract_fields: Pull structured data → $extracted_data
    Using $doc_type, apply the matching extraction template to $ocr_output.
    Record the source text span for each extracted field.
```

**STEP variants:**

1. **With output variable** — declares what the step produces:
   ```
   **STEP** step_name: Description → $output_var
   ```

2. **Without output variable** — for steps that act without producing named data:
   ```
   **STEP** step_name: Description
   ```

3. **With inline conditions** — WHEN/THEN inside a step:
   ```
   **STEP** step_name: Description
     WHEN condition THEN action.
   ```

### Errors (all tiers — required)

A consolidated table covering all error cases in the spec. Every error has a name, severity, and action.

```markdown
## Errors

| Error | Severity | Action |
|-------|----------|--------|
| missing_field | critical | HALT: "Required field {field} is missing." |
| over_budget | warning | Flag for review; suggest promotion to next tier. |
| empty_result | info | Generate empty report; log the date range queried. |
```

**Severity levels:**
- **critical** — Invalid output. Processing MUST stop or the result is rejected.
- **warning** — Degraded output. Note the issue and continue.
- **info** — Observation only. No action required.

**Key improvement over SESF v4:** Errors are consolidated into ONE table. Do NOT scatter `ERROR name: severity → action` declarations inline after individual rules.

### Examples (standard + complex only)

Edge cases only. If the happy path is obvious from the rules, do not exemplify it. Use compact single-line format for simple cases, multi-line for cases requiring explanation.

**Compact format:**
```markdown
## Examples

missing_speaker_id: transcript has turns with no speaker label → label as "[Unknown Speaker]", add warning
contradictory_claims: Speaker A says "$50K", later says "$75K" → include both with timestamps, flag as contradiction
```

**Multi-line format (when explanation is needed):**
```markdown
boundary_at_threshold:
  INPUT: { "invoice": { "amount": 10000 }, "policy": { "review_threshold": 10000 } }
  EXPECTED: Auto-approved (no review flag)
  NOTES: Threshold is "exceeds 10000", not "at least 10000" — exactly 10000 does not trigger review
```

---

## Notation Elements

### @config — Centralized Parameters

Declares all configurable values in a single block. Replaces scattered inline values.

**Syntax:**
```
@config
  key: value
  key: value
  nested:
    key: value
```

**Rules:**
- @config MUST appear before any BEHAVIOR or PROCEDURE blocks
- Keys use snake_case
- Values are literals: strings, numbers, lists `[a, b, c]`, nested objects
- Reference with `$config.key` anywhere in the spec
- `$config.nested.key` for nested values
- @config is for static values only — not for runtime variables (those use `$var` threading)
- Use @config only when 3 or more configuration values exist; fewer values go inline in the text

### @route — Decision Tables

Replaces chained WHEN/THEN/ELSE blocks for multi-branch routing.

**When to use:** Use @route when a conditional has **3 or more branches** mapping inputs to categories or destinations. Use WHEN/THEN/ELSE for 1-2 branch decisions. The form is determined by branch count, not author preference.

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
- `*` (wildcard) is the default case — it SHOULD be the last row when a meaningful default exists; MAY be omitted when all cases are explicitly enumerated
- Each row is `condition → outcome` with `→` as separator
- Conditions are natural English predicates (not code expressions)
- @route replaces verbose WHEN/THEN chains when branch count reaches 3+

### $variable Threading — Explicit Data Flow

Tracks data flowing between steps and procedures.

**When to use:** When data flows between STEP entries and the flow is complex enough that context alone would be ambiguous. For linear step-to-step flow, prose references are clear enough.

**Scope:** Document-global. Once a `$variable` is produced by any STEP, it is visible everywhere in the spec.

**STEP → $var syntax:**
```
**STEP** gather_data: Query the sales database → $raw_sales, $date_range

**STEP** benchmark: Fetch industry comparisons → $industry_averages
  Fetch industry averages for $date_range.

**STEP** analyze: Compare and report
  Compare $raw_sales against $industry_averages.
  Include $date_range in the report header.
```

**Rules:**
- `→ $var` after a STEP description declares output variables
- Variables use `$` prefix and snake_case naming
- `$config.key` references the @config block; `$var` references a STEP output
- Variable threading is optional — steps without outputs omit the `→` declaration
- Every `$var` reference MUST have a corresponding production point earlier in the spec

### ERROR Table Format

All errors are consolidated into a single table in the Errors section.

**Syntax:**
```
| Error | Severity | Action |
|-------|----------|--------|
| error_name | critical/warning/info | what to do |
```

**Rules:**
- Severity values: `critical` (halt), `warning` (continue with degradation), `info` (log only)
- `{variable}` in action strings indicates dynamic interpolation
- Every spec MUST have an Errors table (even micro tier)
- Errors belong in one consolidated table, not scattered inline throughout the spec

### EXAMPLES Format

Edge-case examples use compact single-line format or multi-line format.

**Compact syntax:**
```
example_name: input_description → expected_outcome
```

**Multi-line syntax:**
```
example_name:
  INPUT: { concrete input data }
  EXPECTED: { concrete expected output }
  NOTES: clarification if needed
```

**Rules:**
- `→` separates input from expected output in compact format
- Input side uses `key=value` pairs separated by commas
- Include ONLY edge cases — no happy-path examples
- Use compact format for self-evident cases; multi-line when NOTES or complex data are needed

### Requirement Keywords

Use these keywords with precise meanings. All operative terms MUST be capitalized when used as operative keywords.

**Requirement Strength:**

| Keyword | Meaning |
|---------|---------|
| MUST | Absolute requirement. Failure = invalid output. |
| MUST NOT | Absolute prohibition. Violation = invalid output. |
| SHOULD | Recommended. Skip only with documented reason. |
| SHOULD NOT | Discouraged. Do only with documented reason. |
| MAY | Optional. Include if relevant or beneficial. |
| CAN | Capability. The system is able to do this. |

**Quantifiers:**

| Keyword | Meaning |
|---------|---------|
| EACH | One by one, sequentially. |
| EVERY / ALL | Universal — all items must satisfy the condition. |
| ANY | At least one item satisfies the condition. |
| NONE | Zero items satisfy the condition. Use instead of "not any". |
| EXACTLY N | Precise count — no more, no fewer. |
| AT MOST N | Upper bound — N or fewer. |
| AT LEAST N | Lower bound — N or more. |

**Temporal:**

| Keyword | Meaning |
|---------|---------|
| BEFORE | Prerequisite — must complete before this begins. |
| AFTER | Postcondition — only begins after this completes. |
| IMMEDIATELY | Next action, no intervening steps. |
| ALWAYS | Invariant — condition holds continuously. |
| UNTIL | Condition holds up to a specified event. |

**Flow:**

| Keyword | Meaning |
|---------|---------|
| SKIP | Bypass the current item, continue with next. |
| HALT | Stop all processing. |
| RETRY [UP TO N TIMES] | Attempt again, with bounded retries. |

**Precision:**

| Keyword | Meaning |
|---------|---------|
| VERBATIM | Character-for-character, no paraphrasing. |
| SILENTLY | Perform without reporting to user. |
| INDEPENDENTLY | No dependency between items. |

---

## Writing Rules

### How to Write BEHAVIOR Blocks

A BEHAVIOR block groups related declarative rules under a named heading. Think of it as a container for rules that belong to the same concern.

```markdown
**BEHAVIOR** classify_document: Determine document type from content signals

  **RULE** invoice_detection:
    WHEN document contains "Invoice" or "Bill To" or "Amount Due"
    THEN classify as invoice
    (Rationale: these terms appear in 95% of standard invoice formats)

  **RULE** purchase_order_detection:
    WHEN document contains "Purchase Order" or "PO Number"
    THEN classify as purchase_order

  **RULE** fallback_classification:
    WHEN document matches none of the above patterns
    THEN classify as unclassified and route to manual review
    (Rationale: automated extraction on misclassified documents produces garbage data)
```

**Best practices:**
- Name the BEHAVIOR after the concern it represents (validate_payment, classify_document, enforce_policy)
- Keep each BEHAVIOR focused on one concern — if rules span multiple unrelated areas, split into separate BEHAVIORs
- Order RULEs from most common to least common case
- Use WHEN/THEN for conditional rules, declarative statements for invariants

### How to Write PROCEDURE Blocks

A PROCEDURE block defines an ordered workflow. Each STEP is a discrete action.

```markdown
**PROCEDURE** ingest_claim: Receive and validate an insurance claim submission

  **STEP** receive: Accept uploaded document → $raw_document
    Accept PDF, TIFF, PNG, or JPEG uploads.
    WHEN format is unsupported THEN reject with unsupported_format.

  **STEP** validate_size: Check document is within limits
    WHEN $raw_document exceeds $config.max_document_pages pages
    THEN reject with exceeds_page_limit.

  **STEP** extract: Run OCR and pull structured fields → $extracted_fields
    Submit $raw_document to the OCR engine. For EACH extracted field,
    record text content, bounding box, and confidence score.
```

**Best practices:**
- Name the PROCEDURE after the workflow it represents (process_invoice, analyze_transcript, generate_report)
- Each STEP should be a single logical action — if a step has 5 sub-actions, consider splitting
- Use → $var to declare outputs that subsequent steps consume
- Include WHEN/THEN inside steps for step-level branching

### How to Write RULE with WHEN/THEN

WHEN/THEN is the conditional syntax for rules inside BEHAVIOR blocks:

```
**RULE** rule_name:
  WHEN condition_is_true
  THEN take_this_action
  ELSE take_alternative_action
```

For simple always-true constraints, skip WHEN/THEN:

```
**RULE** rule_name:
  The amount MUST be positive.
```

**When to use WHEN/THEN vs @route:**
- 1-2 branches → WHEN/THEN/ELSE
- 3+ branches → @route table

### How to Add Rationale Annotations

Rationale annotations are parenthetical explanations that follow a rule. They explain *why* the rule exists, not *what* it does.

```
**RULE** constant_time_compare:
  Signature comparison MUST use a constant-time function.
  (Rationale: prevents timing side-channel attacks that could leak signature bytes)

**RULE** no_partial_results:
  WHEN extraction times out THEN discard all partial results.
  (Rationale: partial extractions create data integrity risks — downstream consumers assume complete data)
```

**When to add rationale:**
- The rule prevents a non-obvious security vulnerability
- The rule exists because of a past incident or edge case
- The rule contradicts what a reader might expect
- The rule has a threshold that needs justification

**When to skip rationale:**
- The rule is self-evident ("amount MUST be positive")
- The rationale would just restate the rule in different words

### Consolidating Errors into a Table

**Before (SESF v4 scattered inline):**
```
ERROR invalid_amount: critical → halt, "Amount must be positive"
ERROR missing_currency: critical → halt, "Currency is required"
```

**After (SESF v4.1 consolidated table):**
```markdown
## Errors

| Error | Severity | Action |
|-------|----------|--------|
| invalid_amount | critical | HALT: "Amount must be positive." |
| missing_currency | critical | HALT: "Currency is required." |
```

### When to Use @route vs WHEN/THEN

Use **WHEN/THEN/ELSE** for 1-2 branches:

```
**RULE** size_check:
  WHEN file size > 10MB THEN process in chunks
  ELSE process in a single pass
```

Use **@route** for 3 or more branches:

```
@route file_processing [first_match_wins]
  file size ≤ 1MB        → inline processing (load entire file)
  file size ≤ 50MB       → chunked processing (10MB chunks)
  file size ≤ 500MB      → streaming processing (line by line)
  *                      → reject with "File too large for processing"
```

The threshold is 3 branches. This is not a style preference — it is a hard rule.

### When to Use $variable Threading

**Do not use $variable threading** when the data flow is linear and obvious between consecutive steps:

```
**STEP** extract: Pull ideas from transcript
**STEP** synthesize: Group the extracted ideas by theme
```

"The extracted ideas" is unambiguous. No `$variables` needed.

**Use $variable threading** when multiple steps produce outputs consumed non-linearly:

```
**STEP** gather: Query the sales database → $raw_sales, $date_range
**STEP** benchmark: Fetch industry comparisons → $industry_averages
  Fetch industry averages for $date_range.
**STEP** analyze: Compare and report
  Compare $raw_sales against $industry_averages.
  Include $date_range in the report header.
```

---

## Quality Checklist

Before finalizing a spec, verify:

| Check | Rule |
|-------|------|
| **Every behavior has a block** | Rules grouped under `**BEHAVIOR** name:` |
| **Every procedure has steps** | Steps under `**PROCEDURE** name:` |
| **WHEN/THEN for conditionals** | Not prose "if/then" inside rules |
| **@route only for 3+ branches** | Fewer branches use WHEN/THEN/ELSE |
| **@config only for 3+ values** | Fewer values stated inline in the text |
| **Errors consolidated** | All errors in single `## Errors` table |
| **Rationale on non-obvious rules** | Parenthetical after the rule |
| **No empty sections** | Omit unused sections entirely |
| **RFC 2119 keywords preserved** | MUST, SHOULD, MAY capitalized for precision |
| **Line budget compliance** | Micro ≤80, Standard ≤200, Complex ≤400 |
| **Edge-case examples only** | No happy-path examples |
| **Section-level summaries** | Each BEHAVIOR/PROCEDURE has a one-line description |

### Anti-Patterns

| If you catch yourself writing... | Fix |
|----------------------------------|-----|
| Prose "If X, then Y" inside a RULE | Use WHEN/THEN/ELSE syntax |
| Numbered list `1. 2. 3.` inside a PROCEDURE | Use `**STEP** name:` entries |
| Rules floating outside any BEHAVIOR block | Wrap in `**BEHAVIOR** name:` |
| Steps floating outside any PROCEDURE block | Wrap in `**PROCEDURE** name:` |
| `ERROR name: severity → action` inline after a rule | Move to consolidated `## Errors` table |
| A Notation section explaining `$`, `@`, `→` | Delete it — symbols are self-evident |
| A Types section defining data structures | Inline the field descriptions where they are used |
| A Meta section with version/date/domain | Move to YAML frontmatter or delete |
| `@route` with only 2 branches | Use WHEN/THEN/ELSE in a RULE |
| `@config` for 1-2 values | State the values inline in the text |
| Happy-path examples | Delete them — examples are for edge cases only |
| "Handle errors appropriately" | Specify each error case in the Errors table |
| "Extract relevant fields" | List exactly which fields |
| Nested WHEN/THEN 3+ deep | Break into @route table or separate rules |
| Same constraint in two BEHAVIOR blocks | State it once in the block where it applies |
| BEHAVIOR block with no RULE entries | Either add rules or remove the block |
| PROCEDURE block with no STEP entries | Either add steps or remove the block |

---

## Tier Examples

### Micro Example: Webhook Signature Validator (~40 lines)

```markdown
# Webhook Signature Validator

Validate HMAC-SHA256 signatures on incoming webhook payloads.

**Not in scope:** Payload parsing, retry logic, authentication.

## Configuration

Signing secret loaded from WEBHOOK_SECRET env var. Tolerance: 300 seconds.

**PROCEDURE** validate_signature: Validate incoming webhook request

  **STEP** extract_header: Get signature from request
    Read the X-Hub-Signature-256 header.
    WHEN header is missing THEN reject with missing_signature.

  **STEP** check_timestamp: Verify request freshness
    Read the X-Hub-Timestamp header, parse as Unix epoch.
    WHEN timestamp differs from server time by > 300s THEN reject with stale_request.

  **STEP** compute_signature: Calculate expected HMAC
    Concatenate timestamp + "." + raw body. Compute HMAC-SHA256 with signing secret.

  **STEP** compare: Verify signatures match
    Use constant-time comparison.
    (Rationale: prevents timing side-channel attacks.)
    WHEN signatures differ THEN reject with invalid_signature.

  **STEP** accept: Forward to processing
    Forward raw payload VERBATIM to processing queue. Return HTTP 200.

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| missing_signature | critical | HTTP 401: "X-Hub-Signature-256 header required" |
| missing_timestamp | critical | HTTP 401: "X-Hub-Timestamp header required" |
| stale_request | critical | HTTP 403: "Request timestamp outside tolerance" |
| invalid_signature | critical | HTTP 403: "Signature verification failed". Log remote IP. |
```

### Standard Example: Document Processing Pipeline (~150 lines)

```markdown
# Document Processing Pipeline

Process uploaded business documents through classification, data extraction,
and validation. Each document is classified by type, routed to the appropriate
extraction template, and validated against business rules before storage.

**Not in scope:** Document storage, user authentication, OCR engine selection, multi-language support, handwritten text.

## Configuration

@config
  ocr_confidence_threshold: 0.85
  max_file_size_mb: 25
  supported_formats: [pdf, png, jpg, tiff]
  extraction_timeout_ms: 30000
  validation_strict_mode: true
  output_format: json

**BEHAVIOR** classify_document: Determine document type from content signals

  @route document_type [first_match_wins]
    contains "Invoice" or "Bill To" or "Amount Due"      → invoice
    contains "Purchase Order" or "PO Number"              → purchase_order
    contains "Packing Slip" or "Shipping Label"           → shipping_doc
    contains "W-9" or "Taxpayer Identification"           → tax_form
    *                                                     → unclassified

  **RULE** unclassified_handling:
    WHEN document is unclassified THEN halt automated processing and queue for human review
    (Rationale: automated extraction on misclassified documents produces garbage data)

**BEHAVIOR** validate_extracted_data: Ensure extracted fields meet business rules

  **RULE** required_fields:
    ALL common fields (vendor_name, invoice_number, date, amount) MUST be present and non-empty.
    WHEN ANY required field is missing THEN flag as missing_required_field.

  **RULE** date_consistency:
    Date of service MUST NOT be in the future.
    WHEN document is UB-04 THEN discharge date MUST be on or after admission date.

  **RULE** code_validity:
    ALL diagnosis codes MUST be valid ICD-10 codes.
    ALL procedure codes MUST be valid for the form type.

  **RULE** amount_reasonableness:
    WHEN billed amount exceeds 3 standard deviations of the average for that procedure code
    THEN flag as amount_outlier
    (Rationale: extreme outliers usually indicate data entry errors or upcoding)

**PROCEDURE** process_document: Full document processing pipeline

  **STEP** intake: Receive and validate upload → $raw_file
    Verify file extension is one of $config.supported_formats.
    WHEN format is unsupported THEN reject with unsupported_format.
    WHEN file exceeds $config.max_file_size_mb THEN reject with file_too_large.

  **STEP** ocr: Extract text from document → $ocr_output
    Submit $raw_file to the OCR engine.
    For EACH text block, record content, bounding box, and confidence score.
    WHEN ANY block has confidence below $config.ocr_confidence_threshold
    THEN flag that block as low_confidence.

  **STEP** classify: Determine document type → $doc_type
    Apply first 500 characters of $ocr_output to the document_type @route table.
    (Rationale: using only the first 500 chars avoids misclassification from footer boilerplate.)

  **STEP** extract: Pull structured fields → $extracted_data
    Using $doc_type, apply the matching extraction template to $ocr_output.
    For EACH extracted field, record source text span for audit tracing.

  **STEP** validate: Check business rules
    Apply ALL rules from validate_extracted_data to $extracted_data.
    WHEN $config.validation_strict_mode is true THEN reject on ANY failure.
    ELSE flag failures as warnings and continue.

  **STEP** output: Generate structured record
    Produce a $config.output_format record containing all extracted fields,
    confidence scores, validation results, and any flags.

## Rules

- **Source traceability:** EVERY extracted field MUST include the character offset span from the OCR output.
- **No silent defaults:** WHEN a field cannot be extracted THEN set to null, NEVER to empty string or zero.
- **Idempotency:** Submitting the same file twice MUST produce identical results.

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| unsupported_format | critical | Reject upload. Return list of $config.supported_formats. |
| file_too_large | critical | Reject upload. Return $config.max_file_size_mb in error. |
| ocr_failure | critical | Log OCR engine error. Queue for manual processing. |
| extraction_timeout | critical | Abort. Log elapsed time. Queue for retry with 2x timeout. |
| missing_required_field | critical (strict) / warning (lenient) | Include field name and document type. |
| cross_field_mismatch | warning | Flag discrepancy with both values. Route to human review. |
| potential_duplicate | warning | Flag with existing record ID. Do not block processing. |
| amount_outlier | info | Include flag in output. Do not block processing. |

## Examples

low_confidence_propagation: OCR extracts invoice_number with confidence 0.72 (below 0.85) → entire record carries requires_review: true, even if all other fields above 0.95
cross_field_rounding: line items total $1,249.995, subtotal reads $1,250.00 → passes ($0.005 within $0.01 tolerance)
cross_field_real_mismatch: line items total $4,200.00 but subtotal reads $4,800.00 → fails with cross_field_mismatch ($600 gap)
duplicate_different_vendor: invoice "INV-001" from "Acme Corp" exists, new "INV-001" from "Beta Industries" → no duplicate flag (keyed on number + vendor combo)
```

### Complex Example: Multi-Phase Meeting Analysis (~350 lines)

```markdown
# Multi-Phase Meeting Analysis

Analyze a meeting transcript through six sequential phases: extraction,
second-order analysis, framework mapping, synthesis, contradiction resolution,
and deliverable assembly. Each phase produces a scratchpad artifact that the
next phase consumes.

**Not in scope:** Real-time transcription, speaker diarization, sentiment analysis, action-item tracking, translation.

## Inputs

- `transcript`: string — full meeting transcript with speaker labels (required)
- `meeting_context`: string — 1-3 sentence description of meeting purpose (required)
- `focus_areas`: list of string — topics to prioritize during extraction (optional)
- `output_format`: enum [markdown, json] — format for final deliverable (optional, default: markdown)

## Outputs

- `deliverable`: file — final synthesis document organized by theme
- `scratchpad/`: directory — working artifacts from each phase, preserved for audit
- `metadata.json`: file — processing statistics (token counts, phase durations, idea counts)

## Configuration

@config
  scratchpad_dir: /tmp/meeting-analysis/scratchpad
  max_input_tokens: 200000
  min_ideas_per_phase1: 15
  min_second_order_per_idea: 2
  framework_match_threshold: 0.7
  contradiction_severity_levels: [minor, moderate, critical]
  final_deliverable_max_sections: 8

## Routing

@route token_routing [first_match_wins]
  ≤ 25,000 tokens    → direct: process full transcript in single context window
  ≤ 100,000 tokens   → chunked: split into 20,000-token overlapping chunks (2,000 overlap)
  ≤ 200,000 tokens   → delegated: create sub-agent tasks for each chunk, aggregate
  > 200,000 tokens   → reject with input_too_large

@route signal_priority [first_match_wins]
  matches focus_area AND confidence = high     → priority 1 (lead the report)
  matches focus_area AND confidence = medium   → priority 2 (include with analysis)
  is new market entry or product launch        → priority 1 (always lead-worthy)
  confidence = high                            → priority 2
  confidence = medium                          → priority 3 (supporting evidence)
  *                                            → priority 4 (appendix only)

**BEHAVIOR** analytical_rigor: Maintain intellectual standards throughout all phases

  **RULE** professional_skepticism:
    WHEN a speaker claims something is easy, obvious, or inevitable
    THEN document both the claim AND a counter-scenario with evidence
    (Rationale: unchallenged optimism is the most common failure mode in meeting analysis)

  **RULE** no_fabrication:
    The analysis MUST NOT introduce intelligence not present in the provided transcripts.
    WHEN external knowledge would be relevant THEN note as "[analyst context, not from source]".

  **RULE** balanced_representation:
    EACH speaker SHOULD receive proportional analytical depth.
    WHEN one transcript is 3x longer than others THEN normalize by depth of insight, not volume.

  **RULE** confidence_calibration:
    Low-confidence signals MUST NOT be presented with the same certainty as high-confidence ones.
    ALWAYS include the confidence level when citing a signal.

**BEHAVIOR** artifact_integrity: Ensure phase outputs are consistent and traceable

  **RULE** phase_isolation:
    EACH phase MUST read only the outputs specified in its instructions.
    Phase 2 MUST NOT re-read the transcript.
    (Rationale: violating phase boundaries produces circular reasoning)

  **RULE** label_consistency:
    Once an item is labeled (E1, I3, D-E1.2), that label MUST refer to the same item
    throughout ALL phases. MUST NOT relabel or renumber between phases.

  **RULE** scratchpad_preservation:
    ALL intermediate artifacts MUST be preserved in $config.scratchpad_dir.
    MUST NOT delete or overwrite phase outputs during processing.

  **RULE** derivation_chains:
    ANY claim in the deliverable MUST support full derivation tracing:
    claim → theme → source ideas/effects → transcript passage.
    WHEN any link in this chain is broken THEN the claim is invalid.

**PROCEDURE** setup: Initialize workspace and determine processing strategy

  **STEP** create_workspace: Prepare output directory
    Run `mkdir -p $config.scratchpad_dir`. Create all six phase tasks upfront.

  **STEP** determine_strategy: Select processing mode → $processing_strategy
    Record transcript token count. Apply token_routing @route table.

**PROCEDURE** extract_ideas: Phase 1 — pull all ideas from transcript → $phase1_output

  **STEP** read_transcript: Process full transcript content
    Read the entire transcript without skimming.
    For chunked/delegated strategies, process EACH chunk fully before moving to next.

  **STEP** extract_explicit: Label explicit ideas → E1, E2, E3...
    Statements where a speaker directly proposes, claims, or asserts something.
    Quote the relevant passage and attribute to the speaker.

  **STEP** extract_implicit: Label implicit ideas → I1, I2, I3...
    Ideas implied by conversation but never stated outright.
    EACH implicit idea MUST include a 1-sentence justification explaining the inference.

  **STEP** extract_frameworks: Label frameworks → F1, F2, F3...
    Any reasoning framework, analogy, or mental model a speaker employs.

  **STEP** extract_critical: Label critical observations → C1, C2, C3...
    Claims deserving scrutiny. Note supporting evidence, contradicting evidence, and missing information.

  **STEP** check_focus_areas: Verify coverage of requested areas
    WHEN focus_areas list is provided THEN extraction MUST cover ALL focus areas.
    WHEN a focus area has no relevant content THEN explicitly state
    "No relevant content found for [area]" — MUST NOT omit silently.

  **STEP** validate_count: Ensure minimum extraction yield
    The artifact MUST contain AT LEAST $config.min_ideas_per_phase1 labeled items.
    WHEN transcript yields fewer THEN include a note explaining why.

  Store as $phase1_output in $config.scratchpad_dir/phase1_extraction.md.

**PROCEDURE** analyze_effects: Phase 2 — generate second-order effects → $phase2_output

  **STEP** read_phase1: Load extraction results
    Read ONLY $phase1_output. MUST NOT re-read the transcript.

  **STEP** generate_direct: Direct consequences → D-E1.1, D-E1.2...
    For EVERY explicit and implicit idea, what happens next if implemented or true?

  **STEP** generate_indirect: Indirect consequences → N-E1.1, N-E1.2...
    Two or three steps downstream. Who else is affected? What systems break or benefit?

  **STEP** generate_interactions: Interaction effects → X-E1-I3, X-E2-F1...
    Where do ideas from different speakers or categories interact?
    EVERY effect MUST cite its source idea by label.

  Each idea MUST have AT LEAST $config.min_second_order_per_idea effects.
  Store as $phase2_output.

**PROCEDURE** map_frameworks: Phase 3 — map ideas to analytical frameworks → $phase3_output

  **STEP** read_inputs: Load phase 1 and phase 2 outputs
    Read $phase1_output and $phase2_output.

  **STEP** apply_frameworks: Match ideas to known frameworks
    Map EACH idea and effect to frameworks where match confidence exceeds
    $config.framework_match_threshold.

    Categories: strategic (Porter's, SWOT, JTBD, Blue Ocean, Wardley),
    systems (feedback loops, stock-and-flow, leverage points, Cynefin),
    decision (expected value, reversibility, regret minimization),
    risk (pre-mortem, failure modes, Black Swan, antifragility).

  **STEP** record_mappings: Document each mapping
    For EACH mapping record: idea/effect label, framework name,
    match confidence (0.0-1.0), and 1-2 sentence explanation.
    WHEN confidence below threshold THEN omit UNLESS it reveals a non-obvious insight.
    (Rationale: spurious framework mappings degrade synthesis quality.)

  Store as $phase3_output.

**PROCEDURE** synthesize_themes: Phase 4 — cluster into themes → $phase4_output

  **STEP** read_all_prior: Load phases 1-3
    Read $phase1_output, $phase2_output, $phase3_output.

  **STEP** cluster: Group items into coherent themes
    EACH theme MUST have a descriptive title, reference AT LEAST 2 source items,
    include a 2-4 sentence narrative, and include a "so what?" statement.

  **STEP** limit_themes: Enforce section count
    Limit to $config.final_deliverable_max_sections or fewer.
    WHEN clustering produces more THEN merge the least distinct ones.

  Store as $phase4_output.

**PROCEDURE** resolve_contradictions: Phase 5 — identify and assess contradictions → $phase5_output

  **STEP** read_all: Load all prior phase outputs

  **STEP** find_speaker_contradictions: Two speakers assert incompatible claims
    Cite both by label. Assess which has stronger evidence.

  **STEP** find_idea_effect_contradictions: Idea undermined by its own effects
    Label as paradoxes. Example: idea proposes cost reduction but effect shows increased costs.

  **STEP** find_theme_tensions: Two themes pull in opposite directions
    Propose resolution path or acknowledge genuine tension.

  **STEP** classify_severity: Assign severity to each contradiction
    Use $config.contradiction_severity_levels: minor (cosmetic), moderate (substantive),
    critical (blocks action).

  Store as $phase5_output.

**PROCEDURE** assemble_deliverable: Phase 6 — produce final output

  **STEP** read_all: Load all phase outputs ($phase1_output through $phase5_output)

  **STEP** write_executive_summary: 3-5 sentences
    State meeting's key outcome, most important theme, most critical contradiction or risk.

  **STEP** write_themes: One section per theme from Phase 4
    Include narrative, supporting evidence with labels, second-order effects, framework mappings.

  **STEP** write_contradictions: Present unresolved conflicts
    Include recommended next steps from Phase 5.

  **STEP** write_orphans: Ideas not captured by themes
    These are often the most novel items a meeting overlooked.
    (Rationale: orphan ideas frequently represent blind spots the group failed to discuss.)

  **STEP** write_appendix: Full idea index
    ALL labeled items from Phase 1 with their downstream effects.

  **STEP** validate_citations: Verify all claims are sourced
    EVERY claim in the deliverable MUST cite its source label.
    WHEN unsourced assertion found THEN HALT and backfill the citation.

  Produce deliverable in the format specified by output_format.
  Produce signal_database.json with ALL signals and metadata.
  Produce executive_summary.md with top 3 threats, top 3 opportunities, immediate actions.

## Rules

- **No sycophantic synthesis:** The deliverable MUST NOT validate participants' ideas without challenge.
- **Equal scrutiny:** Apply the same critical analysis to EVERY speaker regardless of seniority.
- **Inference transparency:** EVERY implicit idea MUST include a justification the reader can evaluate.
- **Proportional confidence:** Use "suggests" for single-source, "indicates" for multi-source, "demonstrates" only for direct evidence.
- **Cross-phase references:** WHEN Phase N references an item from Phase M THEN use the original label. MUST NOT summarize without citing.

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| input_too_large | critical | Reject transcript. Return $config.max_input_tokens limit and actual count. |
| insufficient_extraction | warning | Phase 1 produced fewer than $config.min_ideas_per_phase1. Continue but note in deliverable. |
| missing_source_citation | critical | Claim cannot be traced to a labeled source. HALT assembly, backfill citation. |
| broken_derivation_chain | critical | A chain has a gap (e.g., theme references D-E5.1 but no such label exists). HALT and repair. |
| phase_boundary_violation | critical | A phase accessed an input it should not have. Discard output and re-run. |
| low_framework_confidence | warning | Mapping below $config.framework_match_threshold included anyway. Flag with disclaimer. |
| duplicate_idea_merge_conflict | warning | Two ideas with Jaccard similarity > 0.6 but different content. Keep both with overlap note. |
| empty_focus_area | warning | Focus area produced no results. Include: "No relevant content found for [area]." |
| contradiction_deadlock | warning | Critical contradiction with equal evidence. Present both positions, recommend what info would break tie. |

## Examples

implicit_idea_requires_justification:
  Transcript: "Alice: We tried microservices last year. Bob: Right, and we ended up reverting after three months."
  Extraction labels I4: "The team's microservices migration failed."
  But I4 has no justification sentence.
  → Fail. Correct: I4 with justification citing "tried" (past tense) and "reverting after three months."

orphan_idea_not_silently_dropped:
  Phase 1 extracts E12: "The office lease expires in Q3 and has not been discussed."
  Phase 4 produces 6 themes, none related to real estate. E12 absent from deliverable.
  → Fail. E12 MUST appear in "Ideas not captured by themes" section.

phase_boundary_violation:
  During Phase 4 (synthesis), the agent re-reads the original transcript.
  → Fail with phase_boundary_violation. Phase 4 reads $phase1_output through $phase3_output only.

focus_area_with_no_content:
  focus_areas includes "supply chain" but transcript discusses only software and hiring.
  → Pass ONLY if extraction states: "No relevant content found for: supply chain."
```
