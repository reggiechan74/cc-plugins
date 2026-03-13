# SESF v4.1 Complete Examples

Three complete specifications demonstrating every Structured English Specification Format tier. Example 1 is a micro-tier spec showing a single PROCEDURE block with STEP entries. Example 2 is a standard-tier spec showing BEHAVIOR blocks with RULE entries, PROCEDURE blocks with STEP entries, @route tables, and @config. Example 3 is a complex-tier spec demonstrating multiple BEHAVIOR and PROCEDURE blocks, $variable threading with STEP → $var, @route tables, rationale annotations, and worked edge-case examples. Each is a working spec with concrete data, suitable as a reference when writing new specifications.

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

Validate that incoming webhook requests carry a correct HMAC-SHA256 signature
in the `X-Hub-Signature-256` header. Reject unsigned or incorrectly signed
requests before any payload processing occurs.

**Not in scope:** Payload parsing, retry logic, response body formatting, IP allowlisting.

## Configuration

Signing secret: `whsec_K8e2pQ9xVn3bRtYm` (loaded from `WEBHOOK_SECRET` env var).
Signature tolerance window: 300 seconds.

**PROCEDURE** validate_request: Authenticate and accept incoming webhook

  **STEP** extract_signature: Read signature from request header
    Read the `X-Hub-Signature-256` header from the incoming request.
    WHEN the header is missing THEN reject with missing_signature.

  **STEP** extract_timestamp: Read and parse request timestamp
    Read the `X-Hub-Timestamp` header. Parse as a Unix epoch integer.
    WHEN absent or non-numeric THEN reject with missing_timestamp.

  **STEP** check_freshness: Verify request is not stale
    Compute the absolute difference between request timestamp and current server time.
    WHEN difference exceeds 300 seconds THEN reject with stale_request.
    (Rationale: prevents replay attacks using captured payloads.)

  **STEP** compute_expected: Calculate the expected HMAC signature
    Concatenate the timestamp, a literal period (`.`), and the raw request body as UTF-8.
    Compute HMAC-SHA256 over the concatenated string using the signing secret.
    Hex-encode the result and prepend `sha256=`.

  **STEP** compare_signatures: Verify computed matches provided
    Use a constant-time comparison function to compare the computed signature
    against the provided header value.
    (Rationale: constant-time comparison prevents timing side-channel attacks.)
    WHEN signatures do not match THEN reject with invalid_signature.

  **STEP** accept: Forward payload for processing
    Forward the raw payload VERBATIM to the processing queue. Return HTTP 200.

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| missing_signature | critical | Return HTTP 401: `{"error": "missing_signature", "message": "X-Hub-Signature-256 header required"}` |
| missing_timestamp | critical | Return HTTP 401: `{"error": "missing_timestamp", "message": "X-Hub-Timestamp header required"}` |
| stale_request | critical | Return HTTP 403: `{"error": "stale_request", "message": "Request timestamp outside tolerance window"}` |
| invalid_signature | critical | Return HTTP 403: `{"error": "invalid_signature", "message": "Signature verification failed"}`. Log the remote IP for monitoring. |
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

Process uploaded business documents (PDFs and scanned images) through
classification, data extraction, and validation. Each document is classified
by type, routed to the appropriate extraction template, and validated
against business rules before storage.

**Not in scope:** Document storage/archival, user authentication, OCR engine selection, multi-language support (English-only), handwritten text recognition.

## Configuration

@config
  ocr_confidence_threshold: 0.85
  max_file_size_mb: 25
  supported_formats: [pdf, png, jpg, tiff]
  extraction_timeout_ms: 30000
  validation_strict_mode: true
  output_format: json

**BEHAVIOR** classify_document: Determine document type from OCR content

  @route document_type [first_match_wins]
    contains "Invoice" or "Bill To" or "Amount Due"      → invoice_extraction
    contains "Purchase Order" or "PO Number"              → purchase_order_extraction
    contains "Packing Slip" or "Shipping Label"           → shipping_doc_extraction
    contains "W-9" or "Taxpayer Identification"           → tax_form_extraction
    *                                                     → unclassified_review

  **RULE** classification_scope:
    Classification MUST use only the first 500 characters of OCR output.
    (Rationale: avoids misclassification from boilerplate text in footers.)

  **RULE** unclassified_handling:
    WHEN document is unclassified
    THEN halt automated processing and queue for human review
    (Rationale: automated extraction on misclassified documents produces garbage data.)

**BEHAVIOR** validate_extracted_data: Ensure extracted fields meet business rules

  **RULE** required_fields:
    EVERY required field for the document type MUST have a non-empty value.
    WHEN ANY required field is missing THEN trigger missing_required_field.

  **RULE** format_validation:
    Dates MUST parse as valid calendar dates.
    Currency amounts MUST be non-negative numbers.
    TINs MUST match the pattern `XX-XXXXXXX` or `XXX-XX-XXXX`.

  **RULE** cross_field_consistency:
    WHEN document is an invoice
    THEN the sum of line_items[].total MUST equal subtotal within $0.01 tolerance
    AND subtotal + tax MUST equal total_due within $0.01 tolerance.

  **RULE** duplicate_detection:
    WHEN an identical invoice_number + vendor_name combination already exists
    THEN flag as potential_duplicate
    (Rationale: duplicates may be legitimate resubmissions — flag but do not block.)

**BEHAVIOR** data_quality: Maintain extraction integrity

  **RULE** source_traceability:
    EVERY extracted field value MUST include the character offset span from OCR output.
    WHEN a field is inferred rather than directly extracted
    THEN set source to "inferred" with a reason.

  **RULE** confidence_propagation:
    WHEN ANY field was sourced from a low-confidence OCR block
    THEN the entire record MUST carry `requires_review: true`.

  **RULE** no_silent_defaults:
    WHEN a field cannot be extracted and no default is specified
    THEN set to null — NEVER to empty string or zero.

  **RULE** idempotency:
    Submitting the same file twice MUST produce identical extraction results.
    The pipeline MUST NOT incorporate randomness or time-dependent logic.

**PROCEDURE** process_document: Full document processing pipeline

  **STEP** intake: Receive and validate upload → $raw_file
    Confirm file extension is one of $config.supported_formats.
    WHEN format is unsupported THEN reject with unsupported_format.
    WHEN file exceeds $config.max_file_size_mb THEN reject with file_too_large.

  **STEP** ocr: Extract text from document → $ocr_output
    Submit $raw_file to the OCR engine. For EACH extracted text block,
    record the text content, bounding box coordinates, and confidence score.
    WHEN ANY block has confidence below $config.ocr_confidence_threshold
    THEN flag that block as low_confidence. Do not discard — include with flag.

  **STEP** classify: Determine document type → $doc_type
    Apply the document_type @route table to the first 500 characters of $ocr_output.
    WHEN document is unclassified THEN queue for human review and HALT.

  **STEP** extract: Pull structured fields → $extracted_data
    Using $doc_type, apply the matching extraction template:

    - **Invoice:** vendor_name, invoice_number, invoice_date, due_date,
      line_items[] (description, quantity, unit_price, total), subtotal, tax, total_due
    - **Purchase order:** buyer_name, po_number, order_date, vendor_name,
      line_items[] (sku, description, quantity, unit_price), shipping_address, total
    - **Shipping doc:** tracking_number, carrier, ship_date, origin_address,
      destination_address, package_count, weight_kg
    - **Tax form:** taxpayer_name, tin, business_name, address,
      tax_classification, signature_date

    For EACH extracted field, record the source text span (character offsets).

  **STEP** validate: Check extracted data against business rules
    Apply ALL rules from validate_extracted_data to $extracted_data.
    WHEN $config.validation_strict_mode is true THEN reject on ANY failure.
    ELSE flag failures as warnings and continue.

  **STEP** output: Generate structured record
    Produce a $config.output_format record containing: all extracted fields
    with confidence scores, classification result, validation results
    (pass/fail for each check), list of flags, and processing timestamp.

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| unsupported_format | critical | Reject upload. Return the list of $config.supported_formats. |
| file_too_large | critical | Reject upload. Return $config.max_file_size_mb in error. |
| ocr_failure | critical | Log the OCR engine error. Queue document for manual processing. |
| extraction_timeout | critical | Abort extraction. Log elapsed time. Queue for retry with 2x timeout. |
| missing_required_field | critical (strict) / warning (lenient) | In strict mode, reject. In lenient mode, flag and continue. Include field name and document type. |
| cross_field_mismatch | warning | Flag the discrepancy with both values. Route to human review. |
| potential_duplicate | warning | Flag with the existing record ID. Do not block processing. |
| unclassified_document | warning | Queue for human classification. Do not attempt extraction. |

## Examples

low_confidence_propagation: OCR extracts invoice_number="INV-2024-0892" from a text block with confidence 0.72 (below 0.85 threshold). The field is included but the entire record carries `requires_review: true`, even though all other fields had confidence above 0.95. → Pass: confidence flag propagates correctly.

cross_field_rounding: Invoice has line items totaling $1,249.995 (three items with half-cent totals). Subtotal on document reads "$1,250.00". The $0.005 difference is within the $0.01 tolerance. → Pass: tolerance absorbs floating-point rounding.

cross_field_real_mismatch: Invoice line items total $4,200.00 but subtotal field reads "$4,800.00" — a $600.00 discrepancy. → Fail with cross_field_mismatch. The $600 gap exceeds tolerance and likely indicates a missing line item.

duplicate_different_vendor: Invoice number "INV-001" from "Acme Corp" already exists. A new upload has invoice number "INV-001" from "Beta Industries". → Pass: no duplicate flagged, because the vendor_name differs. Detection keys on the combination, not the invoice number alone.

timeout_no_partial: A 200-page scanned PDF takes 45 seconds to extract (exceeds 30,000ms timeout). → Fail with extraction_timeout. No partial results returned, even though 120 pages were processed. Partial extractions create data integrity risks.
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

Analyze a meeting transcript through six sequential phases: extraction,
second-order analysis, framework mapping, synthesis, contradiction resolution,
and final deliverable assembly. Each phase produces a scratchpad artifact
that the next phase consumes. The goal is to surface not just what was said,
but what it implies — including ideas the speakers gestured toward but never
stated explicitly.

**Not in scope:** Real-time transcription, speaker diarization, sentiment analysis, meeting scheduling, action-item tracking (use a task manager for that), translation.

## Inputs

- `transcript`: string — full meeting transcript with speaker labels (required)
- `meeting_context`: string — 1-3 sentence description of meeting purpose and participants (required)
- `focus_areas`: list of string — topics to prioritize during extraction (optional)
- `output_format`: enum [markdown, json] — format for final deliverable (optional, default: markdown)

## Outputs

- `deliverable`: file — final synthesis document containing all findings, organized by theme
- `scratchpad/`: directory — working artifacts from each phase, preserved for audit
- `metadata.json`: file — processing statistics: token counts, phase durations, idea counts, confidence scores

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

For chunked and delegated strategies, the merge step MUST deduplicate ideas that appear in overlapping regions. Use Jaccard similarity on idea descriptions (threshold 0.6) to identify duplicates.

**BEHAVIOR** analytical_rigor: Maintain intellectual standards throughout all phases

  **RULE** professional_skepticism:
    WHEN a speaker claims something is easy, obvious, or inevitable
    THEN document both the claim AND a counter-scenario with evidence
    (Rationale: unchallenged optimism is the most common failure mode in meeting analysis)

  **RULE** no_fabrication:
    The analysis MUST NOT introduce intelligence not present in the transcripts.
    WHEN external knowledge would be relevant
    THEN note as "[analyst context, not from source]"

  **RULE** balanced_representation:
    EACH speaker SHOULD receive proportional analytical depth.
    WHEN one transcript is 3x longer than others
    THEN normalize by depth of insight, not volume of text.

  **RULE** confidence_calibration:
    Low-confidence signals MUST NOT be presented with the same certainty as high-confidence ones.
    ALWAYS include the confidence level when citing a signal.

  **RULE** proportional_language:
    Use "suggests" for single-source inferences.
    Use "indicates" for multi-source corroboration.
    Use "demonstrates" ONLY when evidence is direct and unambiguous.

**BEHAVIOR** artifact_integrity: Ensure phase outputs are consistent and traceable

  **RULE** phase_isolation:
    EACH phase MUST read only the outputs specified in its PROCEDURE instructions.
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
    (Rationale: unsourced assertions undermine the entire analysis)

  **RULE** cross_phase_references:
    WHEN Phase N references an item from Phase M
    THEN use the original label. MUST NOT summarize without citing.

**BEHAVIOR** no_sycophancy: Challenge ideas rather than validating them

  **RULE** critical_synthesis:
    The deliverable MUST NOT validate participants' ideas without challenge.
    WHEN an idea has weaknesses THEN state them.
    WHEN a claim lacks evidence THEN say so.

  **RULE** equal_scrutiny:
    Apply the same level of critical analysis to EVERY speaker's contributions,
    regardless of apparent seniority or confidence.
    (Rationale: a CEO's assertion gets the same evidence check as an intern's suggestion)

  **RULE** inference_transparency:
    EVERY implicit idea (I-series) MUST include a justification.
    The reader MUST be able to evaluate whether the inference is reasonable
    without re-reading the transcript.

**PROCEDURE** setup: Initialize workspace and determine processing strategy

  **STEP** create_workspace: Prepare output directories
    Run `mkdir -p $config.scratchpad_dir`. Create all six phase tasks upfront,
    each blocking on the previous.

  **STEP** determine_strategy: Select processing mode → $processing_strategy
    Record transcript token count → $token_count.
    Apply token_routing @route table to select strategy.

**PROCEDURE** extract_ideas: Phase 1 — pull all ideas from transcript → $phase1_output

  **STEP** read_transcript: Process full transcript content
    Read the entire transcript without skimming. For chunked/delegated strategies,
    process EACH chunk fully before moving to next.

  **STEP** extract_explicit: Label explicit ideas → E1, E2, E3...
    Statements where a speaker directly proposes, claims, or asserts something.
    Quote the relevant passage and attribute it to the speaker.

  **STEP** extract_implicit: Label implicit ideas → I1, I2, I3...
    Ideas implied by the conversation but never stated outright. For example,
    if a speaker says "we tried that last quarter and it didn't work," the implicit
    idea is that the approach has a known failure mode.
    EACH implicit idea MUST include a 1-sentence justification explaining the inference.

  **STEP** extract_frameworks: Label frameworks and mental models → F1, F2, F3...
    Any reasoning framework, analogy, or mental model a speaker employs.

  **STEP** extract_critical: Label critical observations → C1, C2, C3...
    Claims that deserve scrutiny. For each, note supporting evidence,
    contradicting evidence, and missing information.

  **STEP** check_focus_areas: Verify coverage of requested topics
    WHEN focus_areas list is provided THEN extraction MUST cover ALL focus areas.
    WHEN a focus area has no relevant content
    THEN explicitly state "No relevant content found for [area]."
    MUST NOT omit silently.

  **STEP** validate_count: Ensure minimum extraction yield
    Artifact MUST contain AT LEAST $config.min_ideas_per_phase1 labeled items.
    WHEN transcript yields fewer THEN include a note explaining why.

  Store as $phase1_output in $config.scratchpad_dir/phase1_extraction.md.

**PROCEDURE** analyze_effects: Phase 2 — generate second-order effects → $phase2_output

  **STEP** read_phase1: Load extraction results
    Read ONLY $phase1_output. MUST NOT re-read the transcript.

  **STEP** generate_direct: Direct consequences → D-E1.1, D-E1.2...
    For EVERY explicit and implicit idea: what happens next if this is implemented or true?

  **STEP** generate_indirect: Indirect consequences → N-E1.1, N-E1.2...
    Two or three steps downstream. Who else is affected? What systems break or benefit?

  **STEP** generate_interactions: Interaction effects → X-E1-I3, X-E2-F1...
    Where do ideas from different speakers or categories interact?
    EVERY effect MUST cite its source idea by label.

  EACH idea MUST have AT LEAST $config.min_second_order_per_idea effects.
  Store as $phase2_output.

**PROCEDURE** map_frameworks: Phase 3 — map to analytical frameworks → $phase3_output

  **STEP** read_inputs: Load phase 1 and phase 2 outputs
    Read $phase1_output and $phase2_output.

  **STEP** apply_frameworks: Match ideas to known frameworks
    Map EACH idea and effect to frameworks where match confidence exceeds
    $config.framework_match_threshold.

    Categories:
    - Strategic: Porter's Five Forces, SWOT, JTBD, Blue Ocean, Wardley Mapping
    - Systems: feedback loops, stock-and-flow, leverage points, Cynefin domains
    - Decision: expected value, reversibility test, regret minimization, opportunity cost
    - Risk: pre-mortem, failure modes, Black Swan exposure, antifragility assessment

  **STEP** record_mappings: Document each framework mapping
    For EACH mapping, record: idea/effect label, framework name,
    match confidence (0.0-1.0), and 1-2 sentence explanation.
    WHEN confidence is below threshold THEN omit UNLESS it reveals a non-obvious insight.
    (Rationale: spurious framework mappings degrade synthesis quality)

  Store as $phase3_output.

**PROCEDURE** synthesize_themes: Phase 4 — cluster into coherent themes → $phase4_output

  **STEP** read_all_prior: Load phases 1-3
    Read $phase1_output, $phase2_output, $phase3_output.

  **STEP** cluster: Group items into themes
    EACH theme MUST:
    1. Have a descriptive title (not generic like "Theme A")
    2. Reference AT LEAST 2 source items by label
    3. Include a 2-4 sentence narrative explaining why these items form a theme
    4. Include a "so what?" statement explaining why this theme matters

  **STEP** limit_themes: Enforce maximum section count
    Limit to $config.final_deliverable_max_sections or fewer.
    WHEN clustering produces more THEN merge the least distinct ones.
    WHEN clustering produces fewer THEN that is fine — do not pad.

  Store as $phase4_output.

**PROCEDURE** resolve_contradictions: Phase 5 — identify and assess contradictions → $phase5_output

  **STEP** read_all: Load all prior phase outputs ($phase1_output through $phase4_output)

  **STEP** find_speaker_contradictions: Two speakers assert incompatible claims
    Cite both by label. Assess which has stronger evidence.
    WHEN neither has stronger evidence THEN state that explicitly.

  **STEP** find_idea_effect_contradictions: Idea undermined by its own effects
    Label as paradoxes. Example: E3 proposes cost reduction but D-E3.2
    shows it increases support costs.

  **STEP** find_theme_tensions: Two synthesized themes pull in opposite directions
    Propose a resolution path or acknowledge the genuine tension.

  **STEP** classify_severity: Assign severity to each contradiction
    Use $config.contradiction_severity_levels:
    minor (cosmetic disagreement), moderate (substantive, requires discussion),
    critical (fundamental conflict that blocks action).

  Store as $phase5_output.

**PROCEDURE** assemble_deliverable: Phase 6 — produce final output

  **STEP** read_all: Load all phase outputs ($phase1_output through $phase5_output)

  **STEP** write_executive_summary: State key findings in 3-5 sentences
    Include meeting's key outcome, most important theme, most critical
    contradiction or risk.

  **STEP** write_themes: One section per theme from Phase 4
    Include narrative, supporting evidence with labels, second-order effects,
    and relevant framework mappings.

  **STEP** write_contradictions: Present unresolved conflicts from Phase 5
    Include recommended next steps for each.

  **STEP** write_orphans: Ideas not captured by any theme
    These are often the most novel items a meeting overlooked.
    (Rationale: orphan ideas frequently represent blind spots the group failed to discuss)

  **STEP** write_appendix: Full idea index
    ALL labeled items from Phase 1 with their downstream effects.

  **STEP** validate_citations: Verify all claims are sourced
    EVERY claim in the deliverable MUST cite its source label.
    WHEN an unsourced assertion is found THEN HALT and backfill the citation.

  Produce deliverable in format specified by output_format.
  Produce signal_database.json with ALL extracted items and metadata.
  Produce executive_summary.md: top 3 threats, top 3 opportunities, immediate actions.
  EACH output file MUST be self-contained — no cross-references requiring another file.

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| input_too_large | critical | Reject transcript. Return $config.max_input_tokens limit and actual token count. Suggest splitting the recording. |
| insufficient_extraction | warning | Phase 1 produced fewer than $config.min_ideas_per_phase1 items. Continue but note in deliverable. |
| missing_source_citation | critical | Claim in deliverable cannot be traced to a labeled source. HALT assembly, backfill citation. |
| broken_derivation_chain | critical | A chain has a gap (e.g., theme references D-E5.1 but no such label exists). HALT and repair. |
| phase_boundary_violation | critical | A phase accessed an input it should not have. Discard output and re-run from correct inputs. |
| low_framework_confidence | warning | Mapping below $config.framework_match_threshold included anyway. Flag with confidence disclaimer. |
| duplicate_idea_merge_conflict | warning | Two ideas with Jaccard similarity > 0.6 but substantively different content. Keep both with overlap note. |
| empty_focus_area | warning | Focus area produced no extraction results. Include: "No relevant content found for [area]." |
| contradiction_deadlock | warning | Critical contradiction with equal evidence on both sides. Present both, recommend what info would break tie. |

## Examples

implicit_idea_requires_justification:
  Transcript contains: "Alice: We tried microservices last year. Bob: Right, and we ended up reverting after three months."
  Extraction labels I4: "The team's microservices migration failed due to unspecified issues."
  But I4 has no justification sentence.
  → Fail with missing_source_citation rationale: implicit ideas MUST include a justification. Correct version: I4 with justification citing "tried" (past tense) and "reverting after three months."

orphan_idea_not_silently_dropped:
  Phase 1 extracts E12: "The office lease expires in Q3 and has not been discussed."
  Phase 4 synthesis produces 6 themes, none related to real estate.
  E12 does not appear in any theme section.
  → Fail if E12 is absent from the deliverable. It MUST appear in the "Ideas not captured by themes" section. Orphan ideas are often the most actionable items a meeting overlooked.

chunked_deduplication:
  A 90,000-token transcript is split into 5 overlapping chunks. Chunk 2 and Chunk 3 both extract: "The Q4 revenue target of $2.3M requires 40% growth."
  Chunk 2 labels it E7. Chunk 3 labels it E14.
  Jaccard similarity on the description text is 0.82 (above 0.6 threshold).
  → Pass: E14 is merged into E7. All references to E14 in Chunk 3 relabeled to E7. Only E7 appears in final extraction.

contradiction_with_equal_evidence:
  E2 (CTO): "Migrating to Kubernetes will reduce infrastructure costs by 30%."
  E8 (VP Eng): "Our last container migration increased operational costs by 25%."
  Both cite concrete numbers. Neither has stronger evidence.
  Phase 5 classifies as `critical` contradiction.
  → Pass: deliverable presents both positions, notes evidence stalemate, recommends: "Request finance team's actual cost comparison from previous migration." This is a contradiction_deadlock.

phase_boundary_violation_during_synthesis:
  During Phase 4 (synthesis), the agent re-reads the original transcript to "check a quote."
  → Fail with phase_boundary_violation. Phase 4 reads $phase1_output through $phase3_output only. Re-reading the transcript introduces risk of extracting new ideas during synthesis, breaking derivation chains. Discard Phase 4 output and re-run.

focus_area_with_no_content:
  focus_areas includes "supply chain resilience" but transcript discusses only software and hiring.
  Phase 1 finds zero ideas related to supply chain.
  → Pass ONLY if extraction artifact explicitly states: "No relevant content found for: supply chain resilience." Silently omitting the focus area is a fail.
```
