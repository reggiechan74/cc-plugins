# HSF v5 Complete Examples

Three complete specifications demonstrating every Hybrid Specification Format tier. Example 1 is a micro-tier spec showing minimal structure with prose instructions. Example 2 is a standard-tier spec showing @route tables, @config blocks, and prose rules. Example 3 is a complex-tier spec demonstrating all hybrid features including $variable threading, multi-phase instructions, and worked edge-case examples. Each is a working spec with concrete data, suitable as a reference when writing new specifications.

---

## Example 1: Micro Tier -- Webhook Signature Validator

```
---
title: Webhook Signature Validator
description: "Validate HMAC-SHA256 signatures on incoming webhook payloads before processing."
version: 1.0.0
domain: API Security
tier: micro
---

# Webhook Signature Validator

Validate that incoming webhook requests carry a correct HMAC-SHA256 signature in the `X-Hub-Signature-256` header. Reject unsigned or incorrectly signed requests before any payload processing occurs.

**Not in scope:** Payload parsing, retry logic, response body formatting, IP allowlisting.

## Configuration

Signing secret: `whsec_K8e2pQ9xVn3bRtYm` (loaded from `WEBHOOK_SECRET` env var).
Signature tolerance window: 300 seconds.

## Instructions

1. **Extract the signature header.** Read the `X-Hub-Signature-256` header from the incoming request. If the header is missing entirely, reject the request immediately with `missing_signature`.

2. **Extract the timestamp.** Read the `X-Hub-Timestamp` header. Parse it as a Unix epoch integer. If absent or non-numeric, reject with `missing_timestamp`.

3. **Check timestamp freshness.** Compute the absolute difference between the request timestamp and the current server time. If the difference exceeds 300 seconds, reject with `stale_request`. This prevents replay attacks using captured payloads.

4. **Compute the expected signature.** Concatenate the timestamp, a literal period (`.`), and the raw request body as UTF-8. Compute HMAC-SHA256 over the concatenated string using the signing secret. Hex-encode the result and prepend `sha256=`.

5. **Compare signatures.** Use a constant-time comparison function to compare the computed signature against the provided header value. If they do not match, reject with `invalid_signature`. Constant-time comparison MUST be used to prevent timing side-channel attacks.

6. **Accept the request.** If all checks pass, forward the raw payload to the processing queue and return HTTP 200.

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| missing_signature | critical | Return HTTP 401, body: `{"error": "missing_signature", "message": "X-Hub-Signature-256 header required"}` |
| missing_timestamp | critical | Return HTTP 401, body: `{"error": "missing_timestamp", "message": "X-Hub-Timestamp header required"}` |
| stale_request | critical | Return HTTP 403, body: `{"error": "stale_request", "message": "Request timestamp outside tolerance window"}` |
| invalid_signature | critical | Return HTTP 403, body: `{"error": "invalid_signature", "message": "Signature verification failed"}`. Log the remote IP for monitoring. |
```

---

## Example 2: Standard Tier -- Document Processing Pipeline

```
---
title: Document Processing Pipeline
description: "Classify, extract, and validate structured data from uploaded business documents."
version: 1.0.0
domain: Document Intelligence
tier: standard
---

# Document Processing Pipeline

Process uploaded business documents (PDFs and scanned images) through classification, data extraction, and validation. Each document is classified by type, routed to the appropriate extraction template, and validated against business rules before storage.

**Not in scope:** Document storage/archival, user authentication, OCR engine selection, multi-language support (English-only), handwritten text recognition.

## Configuration

@config
  ocr_confidence_threshold: 0.85
  max_file_size_mb: 25
  supported_formats: [pdf, png, jpg, tiff]
  extraction_timeout_ms: 30000
  validation_strict_mode: true
  output_format: json

## Document Classification

After OCR completes, classify the document to determine which extraction template to apply:

@route document_type [first_match_wins]
  contains "Invoice" or "Bill To" or "Amount Due"      → invoice_extraction
  contains "Purchase Order" or "PO Number"              → purchase_order_extraction
  contains "Packing Slip" or "Shipping Label"           → shipping_doc_extraction
  contains "W-9" or "Taxpayer Identification"           → tax_form_extraction
  none of the above                                     → unclassified_review

## Instructions

### Phase 1: Intake and Pre-processing

Receive the uploaded file and validate it before processing:

1. **Check file format.** Confirm the file extension is one of the `supported_formats`. If not, reject with `unsupported_format`.
2. **Check file size.** If the file exceeds `max_file_size_mb`, reject with `file_too_large`.
3. **Run OCR.** Submit the document to the OCR engine. For each extracted text block, record the text content, bounding box coordinates, and confidence score.
4. **Filter low-confidence blocks.** Any text block with a confidence score below `ocr_confidence_threshold` MUST be flagged as `low_confidence` in the extraction output. Do not discard these blocks — include them with the flag so downstream reviewers can assess them.

### Phase 2: Classification and Routing

Apply the `document_type` route table to the full extracted text. Use the first 500 characters of OCR output as the classification input — this avoids misclassification from boilerplate text in footers.

If the document matches `unclassified_review`, halt automated processing and queue the document for human review. Do not attempt extraction on unclassified documents.

### Phase 3: Field Extraction

Apply the matched extraction template to pull structured fields from the document. Each template defines its required and optional fields:

- **Invoice extraction:** `vendor_name`, `invoice_number`, `invoice_date`, `due_date`, `line_items[]` (description, quantity, unit_price, total), `subtotal`, `tax`, `total_due`, `payment_terms`.
- **Purchase order extraction:** `buyer_name`, `po_number`, `order_date`, `vendor_name`, `line_items[]` (sku, description, quantity, unit_price), `shipping_address`, `total`.
- **Shipping doc extraction:** `tracking_number`, `carrier`, `ship_date`, `origin_address`, `destination_address`, `package_count`, `weight_kg`.
- **Tax form extraction:** `taxpayer_name`, `tin`, `business_name`, `address`, `tax_classification`, `signature_date`.

For each extracted field, record the source text span (character offsets in the OCR output) to enable audit tracing.

### Phase 4: Validation

Validate the extracted fields against business rules. When `validation_strict_mode` is true, any validation failure rejects the document. When false, failures are flagged as warnings but the document proceeds.

1. **Required field check.** Every required field for the document type MUST have a non-empty value. Missing required fields trigger `missing_required_field`.
2. **Format validation.** Dates MUST parse as valid calendar dates. Currency amounts MUST be non-negative numbers. TINs MUST match the pattern `XX-XXXXXXX` or `XXX-XX-XXXX`.
3. **Cross-field consistency.** For invoices: the sum of `line_items[].total` MUST equal `subtotal` within a tolerance of $0.01. `subtotal` + `tax` MUST equal `total_due` within $0.01.
4. **Duplicate detection.** Check whether an identical `invoice_number` + `vendor_name` combination (or `po_number` + `buyer_name`) already exists in the system. If so, flag as `potential_duplicate`.

## Rules

### Data Quality

- **Source traceability:** Every extracted field value MUST include the character offset span from the OCR output. If a field is inferred rather than directly extracted, the `source` field MUST be set to `"inferred"` with a reason.
- **Confidence propagation:** If any field in an extracted record was sourced from a low-confidence OCR block, the entire record MUST carry a `requires_review: true` flag.
- **No silent defaults:** If a field cannot be extracted and no default is specified in the template, the field MUST be set to `null` — never to an empty string or zero.

### Processing Integrity

- **Idempotency:** Submitting the same file twice MUST produce identical extraction results. The pipeline MUST NOT incorporate randomness or time-dependent logic in extraction or validation.
- **Timeout enforcement:** If extraction for any single document exceeds `extraction_timeout_ms`, abort and report `extraction_timeout`. Do not return partial results.

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| unsupported_format | critical | Reject upload. Return the list of `supported_formats` in the error response. |
| file_too_large | critical | Reject upload. Return `max_file_size_mb` in the error response. |
| ocr_failure | critical | Log the OCR engine error. Queue document for manual processing. |
| extraction_timeout | critical | Abort extraction. Log elapsed time. Queue for retry with extended timeout (2x). |
| missing_required_field | critical (strict) / warning (lenient) | In strict mode, reject. In lenient mode, flag and continue. Include the field name and document type. |
| cross_field_mismatch | warning | Flag the discrepancy with both values. Route to human review. |
| potential_duplicate | warning | Flag with the existing record ID. Do not block processing. |
| unclassified_document | warning | Queue for human classification. Do not attempt extraction. |

## Examples

low_confidence_propagation: OCR extracts invoice_number="INV-2024-0892" from a text block with confidence 0.72 (below 0.85 threshold). The field is included but the entire record carries `requires_review: true`, even though all other fields had confidence above 0.95. → Pass: confidence flag propagates correctly.

cross_field_rounding: Invoice has line items totaling $1,249.995 (three items with unit prices that produce half-cent totals). Subtotal on document reads "$1,250.00". The $0.005 difference is within the $0.01 tolerance. → Pass: tolerance absorbs floating-point rounding.

cross_field_real_mismatch: Invoice line items total $4,200.00 but subtotal field reads "$4,800.00" — a $600.00 discrepancy. → Fail with `cross_field_mismatch`. The $600 gap far exceeds tolerance and likely indicates a missing line item.

duplicate_different_vendor: Invoice number "INV-001" from "Acme Corp" already exists. A new upload has invoice number "INV-001" from "Beta Industries". → Pass: no duplicate flagged, because the vendor_name differs. Duplicate detection keys on the combination, not the invoice number alone.

timeout_no_partial: A 200-page scanned PDF takes 45 seconds to extract (exceeds 30,000ms timeout). → Fail with `extraction_timeout`. No partial results are returned, even though 120 pages were already processed. Partial extractions create data integrity risks.
```

---

## Example 3: Complex Tier -- Multi-Phase Meeting Analysis

```
---
title: Multi-Phase Meeting Analysis
description: "Analyze meeting transcripts through structured phases to produce synthesis artifacts with ideas, second-order effects, frameworks, and actionable recommendations."
version: 2.0.0
domain: Knowledge Synthesis
tier: complex
---

# Multi-Phase Meeting Analysis

Analyze a meeting transcript through six sequential phases: extraction, second-order analysis, framework mapping, synthesis, contradiction resolution, and final deliverable assembly. Each phase produces a scratchpad artifact that the next phase consumes. The goal is to surface not just what was said, but what it implies — including ideas the speakers gestured toward but never stated explicitly.

**Not in scope:** Real-time transcription, speaker diarization, sentiment analysis, meeting scheduling, action-item tracking (use a task manager for that), translation.

## Inputs

- `transcript`: string - The full meeting transcript, including speaker labels. Timestamps are optional but preserved if present. - required
- `meeting_context`: string - A 1-3 sentence description of the meeting purpose and participants. - required
- `focus_areas`: string[] - Optional list of topics to prioritize during extraction. If empty, all topics are weighted equally. - optional
- `output_format`: enum [markdown, json] - Format for the final deliverable. Default: markdown. - optional

## Outputs

- `deliverable`: file - The final synthesis document containing all findings, organized by theme. - required
- `scratchpad/`: directory - Working artifacts from each phase, preserved for audit. - required
- `metadata.json`: file - Processing statistics: token counts, phase durations, idea counts, confidence scores. - required

## Configuration

@config
  scratchpad_dir: /tmp/meeting-analysis/scratchpad
  max_input_tokens: 200000
  min_ideas_per_phase1: 15
  min_second_order_per_idea: 2
  framework_match_threshold: 0.7
  contradiction_severity_levels: [minor, moderate, critical]
  final_deliverable_max_sections: 8

## Input Routing

Before starting Phase 1, determine the processing strategy based on transcript length:

@route token_routing [first_match_wins]
  ≤ 25,000 tokens    → direct: process the full transcript in a single context window
  ≤ 100,000 tokens   → chunked: split into 20,000-token overlapping chunks (2,000-token overlap), process each, then merge
  ≤ 200,000 tokens   → delegated: create sub-agent tasks for each chunk, aggregate results
  > 200,000 tokens   → reject with input_too_large

For chunked and delegated strategies, the merge step MUST deduplicate ideas that appear in overlapping regions. Use the idea label and a text-similarity check (Jaccard similarity on the idea description, threshold 0.6) to identify duplicates.

## Instructions

### Setup

Run `mkdir -p /tmp/meeting-analysis/scratchpad/`. Create all six phase tasks upfront, each blocking on the previous:

1. Extract ideas
2. Generate second-order effects
3. Map to frameworks
4. Synthesize themes
5. Resolve contradictions
6. Assemble deliverable

Record the transcript token count in `$token_count` and apply the `token_routing` table to select the processing strategy. Record the selected strategy in `$processing_strategy`.

### Phase 1: Idea Extraction → `phase1_extraction.md`

Read the entire transcript without skimming. For chunked/delegated strategies, process each chunk fully before moving to the next. Produce a scratchpad artifact containing:

- **Explicit ideas (E1, E2, E3...).** Statements where a speaker directly proposes, claims, or asserts something. Quote the relevant passage and attribute it to the speaker.
- **Implicit ideas (I1, I2, I3...).** Ideas that are implied by the conversation but never stated outright. For example, if a speaker says "we tried that last quarter and it didn't work," the implicit idea is that the approach has a known failure mode. Each implicit idea MUST include a 1-sentence justification explaining the inference.
- **Frameworks and mental models (F1, F2, F3...).** Any reasoning framework, analogy, or mental model a speaker employs. For example, if someone says "this is a classic chicken-and-egg problem," label that as a framework reference.
- **Critical observations (C1, C2, C3...).** Claims that deserve scrutiny. For each, note what evidence supports it, what evidence contradicts it, and what information is missing.

When a `focus_areas` list is provided, extraction MUST cover all focus areas. If a focus area has no relevant content in the transcript, explicitly state "No relevant content found for [area]" rather than omitting it silently.

Examine every claim with equal skepticism. When a speaker asserts something is easy, obvious, or inevitable, ask: what evidence supports this? What could go wrong? Document both the claim and the counter-scenario.

The extraction artifact MUST contain at least `min_ideas_per_phase1` labeled items across all categories. If the transcript genuinely contains fewer extractable ideas, include a note explaining why (e.g., "Transcript is a brief 5-minute standup with only procedural updates").

Store the extraction artifact as `$phase1_output`.

### Phase 2: Second-Order Effects → `phase2_effects.md`

Read only `$phase1_output` — do not re-read the transcript. For every explicit and implicit idea, generate at least `min_second_order_per_idea` downstream effects:

- **Direct consequences (D-E1.1, D-E1.2...).** What happens next if this idea is implemented or proves true?
- **Indirect consequences (N-E1.1, N-E1.2...).** What happens two or three steps downstream? Who else is affected? What systems break or benefit?
- **Interaction effects (X-E1-I3, X-E2-F1...).** Where do ideas from different speakers or categories interact? For instance, if E1 contradicts I3, or if F1 provides a framework for evaluating E2, label these connections.

Every second-order effect MUST cite its source idea by label (e.g., "D-E1.1: If the API migration proposed in E1 proceeds..."). Effects without source citations are invalid.

Store the result as `$phase2_output`.

### Phase 3: Framework Mapping → `phase3_frameworks.md`

Read `$phase1_output` and `$phase2_output`. Map each idea and effect to known analytical frameworks where the match confidence exceeds `framework_match_threshold`. Use these categories:

1. **Strategic frameworks:** Porter's Five Forces, SWOT, Jobs-to-be-Done, Blue Ocean, Wardley Mapping.
2. **Systems frameworks:** Feedback loops, stock-and-flow, leverage points, Cynefin domains.
3. **Decision frameworks:** Expected value, reversibility test, regret minimization, opportunity cost.
4. **Risk frameworks:** Pre-mortem, failure modes, Black Swan exposure, antifragility assessment.

For each mapping, record: the idea/effect label, the framework name, the match confidence (0.0-1.0), and a 1-2 sentence explanation of why the framework applies. Mappings below `framework_match_threshold` SHOULD be omitted unless they reveal a non-obvious insight.

Do not force-fit. If an idea does not map well to any standard framework, say so and move on. Spurious framework mappings degrade synthesis quality.

Store the result as `$phase3_output`.

### Phase 4: Theme Synthesis → `phase4_synthesis.md`

Read `$phase1_output`, `$phase2_output`, and `$phase3_output`. Cluster the ideas, effects, and framework mappings into coherent themes. Each theme MUST:

1. Have a descriptive title (not a generic label like "Theme A").
2. Reference at least 2 source items by label.
3. Include a 2-4 sentence narrative explaining why these items form a theme.
4. Include a "so what?" statement explaining why this theme matters for the participants.

Limit themes to `final_deliverable_max_sections` or fewer. If natural clustering produces more themes, merge the least distinct ones. If it produces fewer, that is fine — do not pad.

Store the result as `$phase4_output`.

### Phase 5: Contradiction Resolution → `phase5_contradictions.md`

Read all prior phase outputs (`$phase1_output` through `$phase4_output`). Identify contradictions at three levels:

- **Speaker-to-speaker contradictions.** Two speakers assert incompatible claims. Cite both by label. Assess which has stronger evidence. If neither does, state that explicitly.
- **Idea-to-effect contradictions.** An idea's second-order effects undermine the idea itself. For example, E3 proposes cost reduction but D-E3.2 shows it increases support costs. Label these as paradoxes.
- **Theme-to-theme tensions.** Two synthesized themes pull in opposite directions. Propose a resolution path or acknowledge the genuine tension.

Classify each contradiction by severity: `minor` (cosmetic disagreement, easily resolved), `moderate` (substantive disagreement requiring discussion), `critical` (fundamental conflict that blocks action).

Store the result as `$phase5_output`.

### Phase 6: Deliverable Assembly → `deliverable.md`

Read all phase outputs (`$phase1_output` through `$phase5_output`). Assemble the final deliverable:

1. **Executive summary** (3-5 sentences). State the meeting's key outcome, the most important theme, and the most critical contradiction or risk.
2. **Themes** (one section per theme from Phase 4). For each, include the narrative, supporting evidence with labels, second-order effects, and relevant framework mappings.
3. **Contradictions and tensions** (from Phase 5). Present unresolved conflicts with recommended next steps.
4. **Ideas not captured by themes** (orphan ideas from Phase 1 that did not cluster into any theme). These are often the most novel items.
5. **Appendix: Full idea index** (all labeled items from Phase 1 with their downstream effects).

Every claim in the deliverable MUST cite its source label. Unsourced assertions are forbidden — if you synthesized an insight that does not trace back to a labeled item, go back and label the source first.

The deliverable MUST be in the format specified by `output_format`.

## Rules

### Intellectual Rigor

- **No sycophantic synthesis:** The deliverable MUST NOT validate participants' ideas without challenge. If an idea has weaknesses, state them. If a claim lacks evidence, say so. Synthesis that only praises is incomplete.
- **Equal scrutiny:** Apply the same level of critical analysis to every speaker's contributions, regardless of their apparent seniority or confidence. A CEO's assertion gets the same evidence check as an intern's suggestion.
- **Inference transparency:** Every implicit idea (I-series) MUST include a justification. The reader MUST be able to evaluate whether the inference is reasonable without re-reading the transcript.
- **Proportional confidence:** Strength of language MUST match strength of evidence. Use "suggests" for single-source inferences, "indicates" for multi-source, "demonstrates" only when evidence is direct and unambiguous.

### Artifact Integrity

- **Phase isolation:** Each phase reads only the outputs specified in its instructions. Phase 2 MUST NOT re-read the transcript. Phase 4 MUST NOT skip ahead to contradiction analysis. Violating phase boundaries produces circular reasoning.
- **Label consistency:** Once an item is labeled (E1, I3, D-E1.2, etc.), that label MUST refer to the same item throughout all phases. Do not relabel or renumber between phases.
- **Scratchpad preservation:** All intermediate artifacts MUST be preserved in `scratchpad_dir`. Do not delete or overwrite phase outputs during processing.

### Citation Rules

- **Derivation chains:** The final deliverable MUST support full derivation tracing: any claim in the deliverable → theme → source ideas/effects → transcript passage. If any link in this chain is broken, the claim is invalid.
- **Cross-phase references:** When Phase N references an item from Phase M, use the original label. Do not summarize or paraphrase without citing. "As noted in E3" is acceptable; restating E3's content without attribution is not.

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| input_too_large | critical | Reject the transcript. Return the `max_input_tokens` limit and the actual token count. Suggest splitting the meeting recording. |
| insufficient_extraction | warning | Phase 1 produced fewer than `min_ideas_per_phase1` items. Continue processing but include a note in the deliverable explaining the low yield. |
| missing_source_citation | critical | A claim in the deliverable cannot be traced to a labeled source. Halt assembly and backfill the citation before proceeding. |
| broken_derivation_chain | critical | A derivation chain has a gap (e.g., theme references D-E5.1 but no such label exists). Halt assembly and repair the chain. |
| phase_boundary_violation | critical | A phase accessed an input it should not have (e.g., Phase 2 re-read the transcript). Discard that phase's output and re-run from the correct inputs. |
| low_framework_confidence | warning | A framework mapping scored below `framework_match_threshold` but was included anyway. Flag it in the deliverable with a confidence disclaimer. |
| duplicate_idea_merge_conflict | warning | During chunk merging, two ideas had Jaccard similarity above 0.6 but substantively different content. Keep both with a note flagging the potential overlap. |
| empty_focus_area | warning | A requested focus area produced no extraction results. Include in the deliverable: "No relevant content found for [area]." |
| contradiction_deadlock | warning | A critical contradiction could not be resolved because both sides have equal evidence. Present both positions and recommend the specific additional information needed to break the tie. |

## Examples

implicit_idea_requires_justification:
  Transcript contains: "Alice: We tried microservices last year. Bob: Right, and we ended up reverting after three months."
  Extraction labels I4: "The team's microservices migration failed due to unspecified issues."
  But I4 has no justification sentence.
  → Fail with `missing_source_citation` rationale: implicit ideas MUST include a justification. Correct version: I4: "The team's microservices migration failed due to unspecified issues. Justification: Alice's 'tried' (past tense) and Bob's 'reverting after three months' together imply an unsuccessful attempt."

orphan_idea_not_silently_dropped:
  Phase 1 extracts E12: "The office lease expires in Q3 and has not been discussed."
  Phase 4 synthesis produces 6 themes, none of which relate to real estate.
  E12 does not appear in any theme section.
  → Fail if E12 is absent from the deliverable. It MUST appear in section 4 ("Ideas not captured by themes"). Orphan ideas are often the most actionable items a meeting overlooked.

chunked_deduplication:
  A 90,000-token transcript is split into 5 overlapping chunks. Chunk 2 and Chunk 3 both extract: "The Q4 revenue target of $2.3M requires 40% growth."
  Chunk 2 labels it E7. Chunk 3 labels it E14.
  Jaccard similarity on the description text is 0.82 (above 0.6 threshold).
  → Pass: E14 is merged into E7. All references to E14 in Chunk 3's output are relabeled to E7 during the merge step. Only E7 appears in the final extraction.

contradiction_with_equal_evidence:
  E2 (CTO): "Migrating to Kubernetes will reduce infrastructure costs by 30%."
  E8 (VP Eng): "Our last container migration increased operational costs by 25% due to tooling and training."
  Both cite concrete numbers. Neither has stronger evidence than the other.
  Phase 5 classifies this as a `critical` contradiction.
  → Pass: the deliverable presents both positions, notes the evidence stalemate, and recommends: "Request the finance team's actual cost comparison from the previous container migration before making a decision." This is a `contradiction_deadlock`.

phase_boundary_violation_during_synthesis:
  During Phase 4 (synthesis), the agent re-reads the original transcript to "check a quote" rather than relying on $phase1_output.
  → Fail with `phase_boundary_violation`. Phase 4 reads $phase1_output through $phase3_output only. Re-reading the transcript introduces the risk of extracting new ideas during synthesis, which breaks derivation chains. The correct action is to discard Phase 4's output and re-run it using only the specified inputs.

focus_area_with_no_content:
  focus_areas includes "supply chain resilience" but the meeting transcript discusses only software architecture and hiring.
  Phase 1 finds zero ideas related to supply chain.
  → Pass only if the extraction artifact explicitly states: "No relevant content found for: supply chain resilience." Silently omitting the focus area is a fail — the requestor chose that focus area for a reason and needs to know it was not covered.
```
