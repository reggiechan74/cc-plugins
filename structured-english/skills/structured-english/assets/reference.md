# HSF v5 Reference

The Hybrid Specification Format (HSF v5) uses natural language prose with markdown structure to define agent behavior. LLMs follow prose better than formal notation — an A/B test showed hybrid specs produce 65% more synthesis items while consuming 55% fewer tokens than equivalent formal specs. The formal scaffolding of SESF v4 (BEHAVIOR, PROCEDURE, RULE, STEP blocks, Type definitions, Notation legends) consumed tokens without improving compliance.

HSF keeps what works: `@route` decision tables for multi-branch logic, `@config` blocks for centralized parameters, `$variable` threading for complex data flows, consolidated error tables, and RFC 2119 precision keywords (MUST, SHOULD, MAY). Everything else is natural language with markdown headers and bold list items.

---

## Section Reference

Sections MUST appear in this order when present. Omit any section that would be empty.

### Purpose (all tiers — required)

A 1-3 sentence statement of what the spec does and why. This is the first paragraph after the `#` heading.

```markdown
# Invoice Validator

Validate incoming invoices against accounting rules before they enter the
payment queue. Reject malformed invoices immediately; flag policy violations
for human review.
```

### Scope (all tiers — required)

What is IN scope and what is OUT. Use bullet lists or a single "Not in scope" line for micro specs.

```markdown
## Scope

**In scope:**
- Structural validation (required fields, types, formats)
- Policy checks (amount thresholds, duplicate detection)
- Currency conversion for non-USD invoices

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
The maximum retry count is 3. Output files are written to `/tmp/results/`.
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
- `focus_topics`: list of string — topics to prioritize in extraction (optional)

## Outputs

- `summary`: markdown file — structured meeting summary with action items
- `extracted_ideas`: markdown file — labeled ideas (E1, E2, ...) with source attribution
```

### Instructions (all tiers — required)

The core of the spec. Prose instructions organized with `###` headers for phases or logical groups, numbered lists for sequences, and bullet lists for parallel concerns.

```markdown
## Instructions

### Phase 1: Extract Raw Data

Read the entire transcript without skimming. For EACH speaker turn, identify:

1. **Explicit ideas** — statements of opinion, proposal, or recommendation
2. **Implicit ideas** — assumptions, unstated frameworks, or values revealed by word choice
3. **Action items** — commitments with an owner and deadline

Label each extracted item sequentially: E1, E2, E3...

### Phase 2: Synthesize Themes

Group the extracted items by theme. EACH theme MUST have at least 2 supporting items.
Themes with only 1 item SHOULD be merged into the closest related theme.
```

### Rules (standard + complex only)

Cross-cutting rules that apply across multiple phases. Use bold list items with RFC 2119 keywords. Phase-specific rules belong inline in the Instructions section, not here.

```markdown
## Rules

### Quality Standards

- **Source attribution:** EVERY claim in the output MUST trace back to a specific transcript location. Use the format `[Speaker, timestamp]`.
- **No fabrication:** The spec MUST NOT introduce ideas not present in the transcript. If a connection is inferred, label it as `[inferred]`.
- **Balanced representation:** EACH speaker SHOULD receive proportional coverage. If one speaker dominates, note this in the summary.

### Output Constraints

- **Artifact isolation:** EACH output file MUST be self-contained — no cross-references that require reading another artifact to understand the content.
- **Markdown formatting:** ALL outputs MUST use valid markdown with heading hierarchy (h2 for sections, h3 for subsections).
```

### Errors (all tiers — required)

A consolidated table covering all error cases in the spec. Every error has a name, severity, and action.

```markdown
## Errors

| Error | Severity | Action |
|-------|----------|--------|
| empty_transcript | critical | HALT and inform user: "Transcript is empty or unreadable." |
| no_ideas_extracted | critical | HALT and inform user: "No actionable content found in transcript." |
| single_speaker | warning | Continue but note in summary: "Only one speaker detected — cross-pollination analysis skipped." |
| ambiguous_timestamp | info | Use best-effort timestamp with `[approx]` label. |
```

**Severity levels:**
- **critical** — Invalid output. Processing MUST stop or the result is rejected.
- **warning** — Degraded output. Note the issue and continue.
- **info** — Observation only. No action required.

### Examples (standard + complex only)

Edge cases only. If the happy path is obvious from the rules, do not exemplify it. Use compact single-line format for simple cases, multi-line for cases requiring explanation.

**Compact format:**
```markdown
## Examples

missing_speaker_id: transcript has turns with no speaker label → label as "[Unknown Speaker]", add warning to summary
duplicate_action_item: same commitment stated twice by same speaker → deduplicate, keep the version with more detail
contradictory_claims: Speaker A says "budget is $50K", later says "budget is $75K" → include both with timestamps, flag as contradiction
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
- @config MUST appear before any Instructions section
- Keys use snake_case
- Values are literals: strings, numbers, lists `[a, b, c]`, nested objects
- Reference with `$config.key` anywhere in the spec
- `$config.nested.key` for nested values
- @config is for static values only — not for runtime variables (those use `$var` threading)
- Use @config only when 3 or more configuration values exist; fewer values go inline in the text

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

Replaces chained prose conditionals for multi-branch routing.

**When to use:** Use @route when a conditional has **3 or more branches** mapping inputs to categories or destinations. Use prose conditionals for binary decisions (true/false, valid/invalid). The form is determined by branch count, not author preference.

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
- @route replaces verbose prose when branch count reaches 3+

**Example:**
```
@route document_type [first_match_wins]
  is_invoice AND has_PO_number     → Accounts Payable (auto-match to PO)
  is_invoice AND no_PO_number      → Accounts Payable (manual review queue)
  is_contract AND value > $50,000  → Legal Review
  is_contract AND value <= $50,000 → Department Head Approval
  is_expense_report                → Finance (reimburse within 5 business days)
  *                                → General Inbox (manual triage)
```

### $variable Threading — Explicit Data Flow

Tracks data flowing between phases when the flow is complex enough that prose alone would be ambiguous.

**When to use:** Only for complex multi-phase data flows where it is not obvious what data each phase consumes and produces. For most specs, "Phase 2 reads the output of Phase 1" is clear enough in prose.

**Scope:** Document-global. Once a `$variable` is produced in any phase, it is visible everywhere in the spec.

**Syntax:**
```
### Phase Name → $output1, $output2

Action description → $output1
Action description → $output2
```

**Rules:**
- `→ $var` after a phase header declares output variables
- `→ $var` after an action line shows which action produces which variable
- Variables use `$` prefix and snake_case naming
- `$config.key` references the @config block; `$var` references a phase output
- Variable threading is optional — phases without outputs omit the `→` declaration
- Every `$var` reference MUST have a corresponding production point earlier in the spec

**Example:**
```
### Phase 1: Gather Data → $raw_sales, $date_range

Query the sales database for the current week → $raw_sales
Determine the Monday-to-Sunday date range → $date_range

### Phase 2: Calculate Totals → $summary

Group $raw_sales by product category.
Calculate subtotals and grand total → $summary

### Phase 3: Format Output

Render $summary into the report template.
Include $date_range in the header.
```

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

### How to Write Prose Instructions

Instructions are the core of every spec. Structure them with:

1. **`###` headers for phases** — each major stage of processing gets its own header
2. **Numbered lists for sequences** — when order matters, use 1, 2, 3
3. **Bullet lists for parallel concerns** — when order does not matter
4. **Bold for key terms** — the first mention of an important concept or output name
5. **RFC 2119 keywords for precision** — MUST, SHOULD, MAY when the strength of a requirement matters

Write each instruction as a sentence you would say to a competent human assistant. If a non-programmer cannot understand the instruction, rewrite it.

### How to Write Rules

Rules use bold list items under a `##` or `###` header. Each rule is a single statement with an RFC 2119 keyword.

```markdown
## Rules

### Data Integrity

- **No fabrication:** The output MUST NOT contain claims not supported by the input data.
- **Source attribution:** EVERY extracted item MUST include a reference to its source location.
- **Deduplication:** When the same idea appears multiple times, keep the most detailed version and SKIP duplicates.
```

Rules that apply to a single phase belong inline in that phase's Instructions section. The Rules section is only for cross-cutting rules that apply across all phases.

### Converting Rules to Prose

**Before (SESF v4):**
```
**BEHAVIOR** validate_payment: Ensure payment is valid

  **RULE** positive_amount:
    payment.amount MUST be greater than zero

  **RULE** currency_required:
    payment.currency MUST NOT be null

  **RULE** supported_currency:
    WHEN payment.currency is not in $config.supported_currencies
    THEN reject with "Unsupported currency"

  ERROR invalid_payment: critical → halt, "Payment validation failed"
```

**After (HSF v5):**
```markdown
### Payment Validation

Before processing, validate EACH payment:

- **Positive amount:** The amount MUST be greater than zero.
- **Currency required:** The currency field MUST NOT be null.
- **Supported currency:** The currency MUST be one of the values in `$config.supported_currencies`. If not, reject with "Unsupported currency."
```

The error moves to the consolidated Errors table. The BEHAVIOR wrapper and RULE keywords are gone. The same constraints are stated once, in natural sentences.

### Consolidating Errors into a Table

**Before (scattered inline):**
```
ERROR invalid_amount: critical → halt, "Amount must be positive"
ERROR missing_currency: critical → halt, "Currency is required"
ERROR unsupported_currency: warning → reject invoice, "Currency not supported"
ERROR duplicate_invoice: info → flag for review, "Possible duplicate detected"
```

**After (consolidated table):**
```markdown
## Errors

| Error | Severity | Action |
|-------|----------|--------|
| invalid_amount | critical | HALT: "Amount must be positive." |
| missing_currency | critical | HALT: "Currency is required." |
| unsupported_currency | warning | Reject invoice: "Currency {currency} not supported." |
| duplicate_invoice | info | Flag for review: "Possible duplicate of invoice {existing_id}." |
```

### When to Use @route vs Prose Conditionals

Use **prose conditionals** for 1-2 branches:

```markdown
If the file is larger than 10MB, process it in chunks. Otherwise, process it in a single pass.
```

Use **@route** for 3 or more branches:

```markdown
@route file_processing [first_match_wins]
  file size ≤ 1MB        → inline processing (load entire file)
  file size ≤ 50MB       → chunked processing (10MB chunks)
  file size ≤ 500MB      → streaming processing (line by line)
  *                      → reject with "File too large for processing"
```

The threshold is 3 branches. This is not a style preference — it is a hard rule. Two-branch @route tables waste the table structure; four-branch prose conditionals become hard to scan.

### When to Use $variable Threading

**Do not use $variable threading** when the data flow is linear and obvious:

```markdown
### Phase 1: Extract Data

Read the transcript and produce a list of labeled ideas.

### Phase 2: Synthesize

Group the ideas from Phase 1 by theme.
```

"The ideas from Phase 1" is unambiguous. No `$variables` needed.

**Use $variable threading** when multiple phases produce outputs that are consumed non-linearly:

```markdown
### Phase 1: Gather Data → $raw_sales, $date_range

Query the sales database for the current week → $raw_sales
Determine the reporting period → $date_range

### Phase 2: Benchmark → $industry_averages

Fetch industry averages for $date_range → $industry_averages

### Phase 3: Analyze

Compare $raw_sales against $industry_averages.
Flag any category where sales are below 80% of the industry average.
Include $date_range in the report header.
```

Here, Phase 3 consumes outputs from both Phase 1 and Phase 2. Without `$variable` names, the prose would require awkward cross-references. The `$variable` threading makes data dependencies explicit.

---

## Quality Checklist

Before finalizing a spec, verify:

| Check | Rule |
|-------|------|
| **No empty sections** | If a section would say "none" or be blank, omit it entirely |
| **No duplicate constraints** | Each rule stated once, in the section where it applies |
| **No formal wrappers on prose** | No BEHAVIOR, RULE, PROCEDURE, STEP keywords |
| **@route only for 3+ branches** | Fewer branches use a prose conditional |
| **@config only for 3+ values** | Fewer values stated inline in the text |
| **Errors as consolidated table** | Not scattered inline after rules |
| **RFC 2119 keywords preserved** | MUST, SHOULD, MAY still capitalized for precision |
| **Line budget compliance** | Micro ≤80, Standard ≤200, Complex ≤400 |
| **Edge-case examples only** | No happy-path examples |
| **No notation legend** | Symbols explained inline on first use if non-obvious |

### Anti-Patterns

| If you catch yourself writing... | Fix |
|----------------------------------|-----|
| `**BEHAVIOR** name:` or `**RULE** name:` | Use `##` / `###` headers and bold list items |
| `**PROCEDURE** name:` or `**STEP** name:` | Use `###` phase headers and numbered lists |
| A Notation section explaining `$`, `@`, `→` | Delete it — symbols are self-evident or explained inline on first use |
| A Types section defining data structures | Inline the field descriptions where they are used |
| `@route` with only 2 branches | Use a prose conditional (if/otherwise) |
| `@config` for 1-2 values | State the values inline in the text |
| `$config.key` for runtime values | Use `$variable` threading; @config is for static values only |
| Errors scattered after individual rules | Move all errors to the consolidated Errors table |
| Happy-path examples | Delete them — examples are for edge cases only |
| "Handle errors appropriately" | Specify each error case in the Errors table |
| "Extract relevant fields" | List exactly which fields |
| "Validate the data" | State each validation rule explicitly |
| "Process the files" (no quantifier) | "Process EACH file" or "Process ALL files" |
| "If there are errors" (ambiguous) | "If ANY error exists" or "If EVERY check fails" |
| "Don't process any files" (NOT + ANY) | "Process NONE of the files" or "SKIP ALL files" |
| "Try again if it fails" (unbounded) | "RETRY UP TO 3 TIMES" |
| "Copy the text" (may paraphrase) | "Copy the text VERBATIM" |
| Nested conditionals 3+ deep | Break into separate rules or use @route |
| Same constraint in Instructions AND Rules | State it once, in whichever section it applies to |

---

## Tier Examples

### Micro Example: Webhook Payload Validator (~40 lines)

```markdown
---
title: Webhook Payload Validator
description: "Validate incoming webhook payloads before forwarding to handlers."
---

# Webhook Payload Validator

Validate incoming webhook payloads from payment providers. Accept well-formed
payloads and forward them to the processing queue. Reject malformed payloads
with a structured error response.

**Not in scope:** payload processing, retry logic, authentication.

## Configuration

Maximum payload size is 1MB. The accepted event types are
`payment.completed`, `payment.failed`, and `refund.issued`.

## Instructions

For EACH incoming webhook payload:

1. **Check content type** — the `Content-Type` header MUST be `application/json`. If not, reject immediately.
2. **Parse JSON** — attempt to parse the body as JSON. If parsing fails, reject with a parse error.
3. **Validate required fields** — the payload MUST contain `event_type` (string), `timestamp` (ISO 8601), and `data` (object). If ANY required field is missing, reject with a field error listing the missing fields.
4. **Check event type** — the `event_type` MUST be one of the accepted types. If not, reject with an unknown event error.
5. **Check payload size** — the raw body MUST NOT exceed the maximum size. If it does, reject with an oversize error.
6. **Forward** — if all checks pass, forward the payload to the processing queue VERBATIM.

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| invalid_content_type | critical | Reject with HTTP 415: "Expected application/json." |
| json_parse_failure | critical | Reject with HTTP 400: "Malformed JSON body." |
| missing_required_field | critical | Reject with HTTP 422: "Missing fields: {field_list}." |
| unknown_event_type | warning | Reject with HTTP 422: "Unknown event type: {event_type}." |
| payload_too_large | critical | Reject with HTTP 413: "Payload exceeds 1MB limit." |
```

### Standard Example: Document Processing Pipeline (~150 lines)

```markdown
---
title: Insurance Claim Document Processor
description: "Classify, extract, and validate insurance claim documents."
---

# Insurance Claim Document Processor

Process incoming insurance claim documents by classifying them, extracting
structured data, and validating the extracted data against policy rules.
Output a structured claim record ready for adjudication.

## Scope

**In scope:**
- Document classification (form type identification)
- Field extraction from PDFs and scanned images
- Cross-field validation against policy rules
- Structured output generation

**Not in scope:**
- Claim adjudication or payment decisions
- Fraud detection (separate pipeline)
- Customer communication

## Configuration

@config
  supported_form_types: [CMS-1500, UB-04, ADA-J400, pharmacy_claim]
  max_document_pages: 50
  extraction_confidence_threshold: 0.85
  output_format: JSON

## Document Classification

@route form_classifier [first_match_wins]
  has CMS-1500 header or NPI in Box 33         → CMS-1500 (professional claim)
  has UB-04 header or revenue codes in FL 42    → UB-04 (institutional claim)
  has ADA claim form header or tooth numbers    → ADA-J400 (dental claim)
  has NDC codes and pharmacy identifiers        → pharmacy_claim
  *                                             → unclassified (route to manual review)

## Instructions

### Phase 1: Receive and Classify

1. Verify the document is a PDF or supported image format (TIFF, PNG, JPEG).
2. If the document exceeds `$config.max_document_pages`, reject it.
3. Run the document through the form classifier above to determine the form type.
4. If the document is unclassified, route it to manual review and HALT automated processing.

### Phase 2: Extract Fields

Based on the classified form type, extract the following fields:

- **All form types:** patient name, date of birth, policy number, date of service, provider name, provider NPI, diagnosis codes (ICD-10), total billed amount
- **CMS-1500 additionally:** place of service, CPT/HCPCS codes, modifier codes, referring provider
- **UB-04 additionally:** admission date, discharge date, revenue codes, DRG code, occurrence codes
- **ADA-J400 additionally:** tooth numbers, surface codes, area of oral cavity
- **Pharmacy claims additionally:** NDC codes, quantity dispensed, days supply, DAW code

For EACH extracted field, record the extraction confidence score. If ANY field has a confidence score below `$config.extraction_confidence_threshold`, flag that field for manual verification.

### Phase 3: Validate

Apply these validations to the extracted data:

1. **Required fields** — ALL common fields listed above MUST be present. If ANY are missing, flag the claim as incomplete.
2. **Date consistency** — the date of service MUST NOT be in the future. For UB-04 forms, the discharge date MUST be on or after the admission date.
3. **Code validity** — ALL diagnosis codes MUST be valid ICD-10 codes. ALL procedure codes MUST be valid for the form type (CPT for CMS-1500, revenue codes for UB-04).
4. **Policy lookup** — the policy number MUST match an active policy in the system. If no match is found, flag as "policy not found."
5. **Amount reasonableness** — the total billed amount SHOULD be within 3 standard deviations of the average for that procedure code. If it exceeds this, flag as "amount outlier."

### Phase 4: Output

Generate a structured claim record in `$config.output_format` containing:

- All extracted fields with confidence scores
- Classification result and confidence
- Validation results (pass/fail for each check)
- List of flags requiring manual review (if any)
- Processing timestamp

## Rules

### Cross-Cutting Rules

- **Audit trail:** EVERY processing decision MUST be logged with a timestamp, the rule that triggered it, and the input values that matched.
- **No data modification:** The processor MUST NOT alter extracted values. If a value appears incorrect, flag it — do not correct it.
- **Confidence transparency:** ALL confidence scores MUST be included in the output, even for high-confidence extractions.

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| unsupported_format | critical | HALT: "Document format not supported. Expected PDF, TIFF, PNG, or JPEG." |
| exceeds_page_limit | critical | HALT: "Document has {pages} pages, exceeds limit of {max}." |
| unclassified_document | warning | Route to manual review queue. Do not proceed with extraction. |
| low_confidence_field | warning | Flag field for manual verification. Continue processing remaining fields. |
| missing_required_field | warning | Flag claim as incomplete. Include list of missing fields in output. |
| invalid_diagnosis_code | warning | Flag code as invalid. Include the code value and position in output. |
| policy_not_found | warning | Flag as "policy not found." Continue processing but mark for review. |
| amount_outlier | info | Include flag in output. Do not block processing. |

## Examples

unclassified_with_partial_match: document has CMS-1500-like fields but no header → classified as "unclassified" (partial matches are not sufficient)
future_date_of_service: date_of_service="2027-01-15", today="2026-03-13" → validation fails with "date of service is in the future"
confidence_at_threshold: field confidence=0.85 exactly → passes threshold (threshold is "below 0.85", not "at or below")
dual_diagnosis_one_invalid: codes=["M54.5", "Z99.99"] → M54.5 passes, Z99.99 flagged as invalid, claim still processed with flag
```

### Complex Example: Competitive Intelligence Analysis System (~350 lines)

```markdown
---
title: Competitive Intelligence Analyzer
description: "Multi-phase analysis of competitor earnings calls and filings."
---

# Competitive Intelligence Analyzer

Analyze competitor earnings call transcripts and SEC filings to produce
a structured competitive intelligence report. Extract strategic signals,
assess competitive positioning, and generate actionable recommendations
for the executive team.

## Scope

**In scope:**
- Earnings call transcript analysis (10-Q commentary, guidance statements)
- Strategic signal extraction (market moves, product launches, investment priorities)
- Competitive positioning assessment (relative strengths, vulnerabilities)
- Recommendation generation (defensive and offensive strategic options)

**Not in scope:**
- Financial modeling or valuation
- Stock price prediction
- Legal analysis of SEC compliance
- Real-time market data integration

## Inputs

- `transcripts`: list of string — one or more earnings call transcripts (required)
- `company_profile`: object — our company's product lines, market segments, and strategic priorities (required)
- `previous_report`: string — the last competitive intelligence report, if any (optional)
- `focus_areas`: list of string — specific competitive dimensions to prioritize (optional)

## Outputs

- `intelligence_report`: markdown file — structured competitive intelligence report
- `signal_database`: JSON file — machine-readable extracted signals with metadata
- `executive_summary`: markdown file — 1-page summary for leadership team

## Configuration

@config
  max_signals_per_transcript: 50
  confidence_levels: [high, medium, low]
  signal_categories: [product, market, financial, operational, strategic, talent]
  lookback_quarters: 4
  output_dir: /tmp/competitive-intel/
  recommendation_limit: 10

## Routing Logic

@route transcript_processing [first_match_wins]
  transcript ≤ 25,000 tokens    → direct processing (single pass)
  transcript ≤ 175,000 tokens   → chunked processing (section by section)
  transcript > 175,000 tokens   → summary-first processing (executive summary, then deep dive on flagged sections)

@route signal_priority [first_match_wins]
  signal matches a focus_area AND confidence = high      → priority 1 (lead the report)
  signal matches a focus_area AND confidence = medium    → priority 2 (include with analysis)
  signal is a new market entry or product launch         → priority 1 (always lead-worthy)
  confidence = high                                      → priority 2
  confidence = medium                                    → priority 3 (supporting evidence)
  *                                                      → priority 4 (appendix only)

## Instructions

### Phase 1: Setup → $scratchpad

Create the output directory: `mkdir -p $config.output_dir`.

If a `previous_report` is provided, read it and extract:
- Previously identified signals (for trend tracking)
- Open questions from the last report (to check if any are now answered)
- Strategic recommendations that were made (to assess if competitors acted on them)

Store this context → $scratchpad

### Phase 2: Signal Extraction → $raw_signals

For EACH transcript, process according to the transcript routing table above.

Read the transcript thoroughly — no skimming. For EACH section (prepared remarks, Q&A, guidance), extract:

1. **Product signals** — new launches, deprecations, roadmap hints, feature comparisons
2. **Market signals** — geographic expansion, segment entry/exit, customer wins/losses mentioned by name
3. **Financial signals** — margin commentary, investment priorities, cost structure changes, guidance revisions
4. **Operational signals** — hiring plans, restructuring, supply chain changes, technology migrations
5. **Strategic signals** — partnership announcements, M&A hints, competitive positioning statements
6. **Talent signals** — key hires, departures, organizational changes

For EACH extracted signal, record:
- A unique label (S1, S2, S3...)
- The verbatim quote from the transcript
- The speaker and their role
- The signal category (from `$config.signal_categories`)
- A confidence level (from `$config.confidence_levels`)
- Whether this confirms, contradicts, or is new relative to $scratchpad

Produce AT MOST `$config.max_signals_per_transcript` signals per transcript. If extraction yields more, keep only the highest-confidence signals → $raw_signals

### Phase 3: Cross-Transcript Analysis → $analyzed_signals

Compare signals across all transcripts and against $scratchpad:

1. **Identify convergent signals** — EACH signal that appears in 2+ transcripts MUST be flagged as a convergent theme. Convergent signals are inherently higher confidence.
2. **Identify contradictions** — when two competitors make opposing claims about the same market, document both with analysis of which is more credible.
3. **Track trend evolution** — for signals that appeared in the previous report ($scratchpad), note whether the signal has strengthened, weakened, or remained stable.
4. **Map competitive dimensions** — for EACH signal category, rank competitors by apparent strength or investment level.

Apply the signal priority routing table to assign priority levels → $analyzed_signals

### Phase 4: Competitive Positioning Assessment → $positioning

Using $analyzed_signals and `company_profile`:

1. **Strength mapping** — for EACH product line in our portfolio, identify where competitors are investing more, less, or comparably. Use only evidence from the transcripts.
2. **Vulnerability identification** — identify areas where competitors have announced capabilities or investments that could threaten our market position. EACH vulnerability MUST cite specific signals.
3. **Opportunity identification** — identify areas competitors are deprioritizing or struggling with that represent potential opportunities for us.
4. **Blind spot detection** — compare focus_areas against what competitors are actually discussing. If competitors are heavily investing in an area we did not list as a focus area, flag it as a potential blind spot.

All assessments MUST be grounded in specific signals. Do not speculate beyond what the transcripts support. If making an inference, label it explicitly as `[inferred from S4, S12]` → $positioning

### Phase 5: Recommendations → $recommendations

Generate AT MOST `$config.recommendation_limit` strategic recommendations:

For EACH recommendation:
1. State the recommendation in one sentence
2. Cite the supporting signals (by label)
3. Classify as **defensive** (protecting existing position) or **offensive** (exploiting competitor weakness)
4. Assess urgency: IMMEDIATE (act within 30 days), NEAR-TERM (this quarter), STRATEGIC (this year)
5. Identify the specific team or function that should own the action

Recommendations MUST be specific and actionable. "Monitor the situation" is not a recommendation — state what to monitor, what threshold triggers action, and what the action would be → $recommendations

### Phase 6: Report Assembly

Produce three output files in `$config.output_dir`:

**`intelligence_report.md`** — the full report containing:
- Executive summary (2-3 paragraphs)
- Signal summary table (all signals with priority, category, confidence)
- Cross-transcript themes (from $analyzed_signals)
- Competitive positioning assessment (from $positioning)
- Strategic recommendations (from $recommendations)
- Appendix: all extracted signals with full quotes

**`signal_database.json`** — structured data containing EVERY extracted signal with all metadata fields, suitable for programmatic analysis.

**`executive_summary.md`** — a 1-page summary containing:
- Top 3 competitive threats (with evidence)
- Top 3 strategic opportunities (with evidence)
- Recommended immediate actions (urgency = IMMEDIATE only)

EACH output file MUST be self-contained. A reader of the executive summary MUST NOT need to read the full report to understand the recommendations.

## Rules

### Analytical Rigor

- **Professional skepticism:** When a CEO claims something is easy, growing fast, or industry-leading — ask: what evidence supports this? What could go wrong? Document both the claim and the counter-scenario.
- **No fabrication:** The analysis MUST NOT introduce competitive intelligence not present in the provided transcripts. If external knowledge would be relevant, note it as `[analyst context, not from source]` but do not present it as extracted intelligence.
- **Balanced representation:** EACH competitor SHOULD receive proportional analytical depth. If one transcript is 3x longer than others, normalize the analysis by depth of insight, not volume of text.
- **Confidence calibration:** Do not present low-confidence signals with the same certainty as high-confidence ones. ALWAYS include the confidence level when citing a signal.

### Output Quality

- **Artifact isolation:** EACH output file MUST be independently readable. No cross-references that require reading another file.
- **Signal traceability:** EVERY claim in the report MUST trace to a specific signal label and transcript quote.
- **Recommendation specificity:** EVERY recommendation MUST name a specific team, a specific action, and a specific trigger or timeline. Generic advice is not acceptable.

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| empty_transcript | critical | HALT: "Transcript is empty or unreadable." |
| no_signals_extracted | critical | HALT: "No competitive signals found in transcript. Verify this is an earnings call." |
| company_profile_missing | critical | HALT: "Company profile is required for competitive positioning." |
| transcript_too_large | warning | Process using summary-first routing. Note in report: "Full transcript exceeded token limit; analysis based on executive summary + deep-dive sections." |
| low_signal_density | warning | Continue but note: "Transcript yielded fewer than 10 signals. Analysis may be incomplete." |
| contradictory_signals | info | Include both signals with analysis of credibility. Do not suppress contradictions. |
| no_previous_report | info | Skip trend analysis. Note: "No previous report available; all signals treated as new." |
| focus_area_mismatch | info | Note in blind spot section: "Competitors discussing {topic} heavily, but not listed in our focus areas." |

## Examples

earnings_call_vs_press_release: transcript is a press release, not an earnings call → low_signal_density warning, proceed but flag in report that source quality is lower than expected
contradictory_guidance: Company A says "cloud market growing 40% YoY", Company B says "cloud growth decelerating to 15%" → include both as S5 and S12, note contradiction, assess credibility based on each company's market position
signal_at_extraction_limit: transcript yields 55 signals, max is 50 → keep top 50 by confidence, note in report that 5 lower-confidence signals were excluded
previous_signal_disappeared: $scratchpad shows S3 ("AI investment doubling") from last quarter, current transcript does not mention AI → flag as "signal weakened or dropped" in trend analysis, do not assume the initiative was canceled
no_focus_area_blind_spot: focus_areas=["cloud", "security"], but 3 competitors discuss "edge computing" extensively → flag as blind spot in positioning assessment, include as a recommendation to evaluate
```
