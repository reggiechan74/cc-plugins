# HSF v6 Design: XML Envelope + Output Schemas

## Summary

HSF v6 replaces custom `@config`/`@route` notation with native XML/JSON that LLMs already parse perfectly, adds `<output-schema>` blocks to close the biggest compliance gap (LLMs guessing output shape), and wraps all top-level sections in XML tags for unambiguous section boundaries. Prose instructions inside sections are unchanged — XML is for structure, prose is for content.

## What Changes from v5

| v5 | v6 | Why |
|---|---|---|
| `## Section` markdown headers for top-level sections | `<section>` XML tags | LLMs parse XML boundaries with near-perfect accuracy; markdown headers require inference |
| `@config` with custom YAML-like syntax | `<config>` with JSON body | JSON parsing is native to LLMs; eliminates custom syntax |
| `@route name [mode]` with `→` rows | `<route name="..." mode="...">` with `<case>`/`<default>` | XML structure makes branch boundaries unambiguous |
| `$config.key` references | `config.key` references (drop the `$` prefix for config) | `$variable` is reserved for runtime data flow; config refs shouldn't look like variables |
| No output structure specification | `<output-schema>` blocks inline in instructions | Closes the biggest compliance gap — LLMs guessing output shape |
| `## Instructions` / `### Phase N` | `<instructions>` / `### Phase N` | XML for section boundary, markdown for sub-structure within |

**Unchanged:** prose instruction style, `$variable` threading, RFC 2119 keywords, tier system (micro/standard/complex), line budgets, edge-case-only examples, error table format, bold list items for rules, numbered lists for sequences.

## Document Structure

Every HSF v6 spec follows this skeleton. XML tags define section boundaries. Content inside tags is prose markdown (with `###` for sub-structure). Sections MUST appear in this order. Omit any section that would be empty.

```
<purpose>
  [1-3 sentence prose — what this spec does and why]
</purpose>

<scope>
  [IN/OUT bullet lists, or single "Not in scope" line for micro]
</scope>

<inputs>                          ← standard + complex only, when spec has clear data boundaries
  [typed parameter list: `name`: type — description - required/optional]
</inputs>

<outputs>                         ← standard + complex only, when spec has clear data boundaries
  [typed parameter list: `name`: type — description - required/optional]
</outputs>

<config>                          ← only when 3+ config values exist
  { JSON object }
</config>

<instructions>
  ### Phase 1: Name

  [prose instructions, numbered lists, bold terms]
  [inline rules that apply to this phase only]
  [<route> tables inline where decisions happen]
  [<output-schema> inline where output is produced]

  ### Phase 2: Name

  [...]
</instructions>

<rules>                           ← standard + complex only, cross-cutting only
  [bold list items with RFC 2119 keywords]
</rules>

<errors>
  [consolidated markdown table: Error | Severity | Action]
</errors>

<examples>                        ← standard + complex only, edge cases only
  [compact or worked examples]
</examples>
```

**Key structural rules:**

- **XML for sections, `###` for phases.** No `##` markdown headers for top-level sections — the XML tag IS the section marker.
- **No nesting of section tags.** `<config>` is never inside `<instructions>`. But `<route>` and `<output-schema>` ARE inside `<instructions>` because they're part of the instruction flow, not standalone sections.
- **Omit empty sections.** If there are no cross-cutting rules, omit `<rules>` entirely. Don't write `<rules></rules>`.
- **`<inputs>`/`<outputs>` are optional at all tiers.** Include them when the spec has clear data boundaries (receives specific typed parameters, produces specific typed artifacts). Omit when the inputs/outputs are obvious from context or the spec operates on implicit data. Format: `- \`name\`: type — description - required/optional`
- **YAML frontmatter is optional.** When present, it MAY include `title`, `description`, and `tier` fields. Omit the `---` block if tooling does not need it.

## `<config>` — JSON Configuration

Replaces `@config`. Static configuration values in a JSON object.

```markdown
<config>
{
  "supported_form_types": ["CMS-1500", "UB-04", "ADA-J400", "pharmacy_claim"],
  "max_document_pages": 50,
  "extraction_confidence_threshold": 0.85,
  "output_format": "JSON",
  "thresholds": {
    "warning": 80,
    "critical": 95
  }
}
</config>
```

**Rules:**
- JSON MUST be valid (parseable)
- Keys use snake_case
- Reference values as `config.key` or `config.nested.key` in prose (no `$` prefix — that's reserved for `$variable` threading)
- `<config>` is for static values only — runtime data uses `$variable`
- Use `<config>` only when 3+ values exist; fewer values go inline in prose

## `<route>` — Decision Tables

Replaces `@route`. Lives inline within `<instructions>` where the decision happens.

```markdown
<route name="form_classifier" mode="first_match_wins">
  <case when="has CMS-1500 header or NPI in Box 33">CMS-1500 (professional claim)</case>
  <case when="has UB-04 header or revenue codes in FL 42">UB-04 (institutional claim)</case>
  <case when="has ADA claim form header or tooth numbers">ADA-J400 (dental claim)</case>
  <default>unclassified (route to manual review)</default>
</route>
```

**Rules:**
- Use `<route>` only for 3+ branch decision logic. Fewer branches use a prose conditional.
- `mode` attribute: `first_match_wins` (stop at first matching case) or `all_matches` (apply all matching cases — collects outcomes into a list)
- `<case when="...">outcome</case>` for each branch
- `<default>outcome</default>` for the fallback — SHOULD be present when a meaningful default exists; MAY be omitted when all cases are explicitly enumerated
- Conditions in `when` are natural English predicates, not code
- `<route>` lives inside `<instructions>`, inline at the point where the decision is made

## `<output-schema>` — Structured Output Specification

New in v6. Defines the exact shape of structured output an LLM must produce. Lives inline in `<instructions>` at the phase that produces the output.

```markdown
### Phase 4: Generate Output

Assemble the claim record from the validated fields. The output MUST conform to:

<output-schema format="json">
{
  "claim_id": "string — unique identifier for this processing run",
  "form_type": "CMS-1500 | UB-04 | ADA-J400 | pharmacy_claim",
  "fields": {
    "[field_name]": {
      "value": "string | number | null",
      "confidence": "float 0.0-1.0",
      "source_span": "array of two integers [start_offset, end_offset]"
    }
  },
  "validation": {
    "required_fields": "pass | fail",
    "date_consistency": "pass | fail",
    "code_validity": "pass | fail"
  },
  "flags": ["string — human-readable flag descriptions"],
  "requires_review": "boolean",
  "processed_at": "ISO 8601 timestamp"
}
</output-schema>
```

**Rules:**
- `format` attribute: `json` (required — only supported format for now)
- The schema uses descriptive type annotations (`"string"`, `"float 0.0-1.0"`, `"ISO 8601 timestamp"`) rather than formal JSON Schema — LLMs understand natural descriptions better than `{"type": "string", "format": "date-time"}`
- Union types use `|`: `"string | null"`
- Array types use `[]`: `["string"]`
- Object templates with variable keys use `"[key_name]"`: `{"[field_name]": {...}}`
- `<output-schema>` is placed inline immediately after the prose instruction that says "produce the output"
- **Tier rules:** SHOULD for standard and complex tiers when producing structured output. MAY for micro tier. Not required when the output is unstructured prose (e.g., a markdown report).

## Unchanged Features

**`$variable` threading** — still uses `$` prefix, still document-global scope, still optional and used only for complex multi-phase data flows:

```markdown
### Phase 1: Gather Data → $raw_sales, $date_range

Query the sales database for the current week → $raw_sales
Determine the reporting period → $date_range

### Phase 2: Analyze

Compare $raw_sales against industry benchmarks.
Include $date_range in the report header.
```

**RFC 2119 keywords** — MUST, SHOULD, MAY, etc. still capitalized with operative meanings.

**Error table format** — same markdown table inside `<errors>`:

```markdown
<errors>
| Error | Severity | Action |
|-------|----------|--------|
| unsupported_format | critical | Reject. Return supported formats list. |
| file_too_large | critical | Reject. Return max size in error. |
</errors>
```

**Example format** — same compact and worked formats inside `<examples>`:

```markdown
<examples>
cross_field_rounding: line items total $1,249.995, subtotal reads $1,250.00 → Pass (within $0.01 tolerance)

confidence_at_threshold:
  Input: field confidence = 0.85 exactly
  Expected: passes threshold (threshold is "below 0.85", not "at or below")
  Notes: boundary condition — exact threshold value is a pass
</examples>
```

**Tier system** — micro (20-80 lines), standard (80-200), complex (200-400). Same thresholds, same promotion/demotion rules.

**Prose instruction style** — imperative mood, numbered lists for sequences, bullet lists for parallel concerns, bold key terms, `###` phase headers.

## Impact on Files

All files update to v6 with no backward compatibility:

**Skill files:**
- `skills/hsf/SKILL.md` — rewrite for v6 rules
- `skills/hsf/assets/reference.md` — rewrite with XML envelope, JSON config, XML route, output-schema
- `skills/hsf/assets/template.md` — rewrite all tier templates with XML structure
- `skills/hsf/references/examples.md` — rewrite all three examples in v6 format

**Command files:**
- `commands/write-LLM-spec.md` — update to v6 format, add output-schema guidance
- `commands/assess-LLM-doc.md` — update signals to include XML envelope benefits, add output-schema signal
- `commands/convert-human-to-llm.md` — update conversion mapping table:

| SESF v4.1 Source | HSF v6 Target |
|---|---|
| `**BEHAVIOR** name:` block | Bold list items inside `<rules>` or inline in `<instructions>` phase |
| `**RULE** name:` with `WHEN/THEN` | Bold list item with MUST/SHOULD |
| `**PROCEDURE** name:` block | `### Phase` headers inside `<instructions>` |
| `**STEP** name: → $var` | Numbered list item, `$variable` only if complex flow |
| `@config` block | `<config>` with JSON body |
| `@route` table | `<route>` with `<case>`/`<default>` elements |
| `## Section` headers | XML section tags |
| Rationale annotations | Strip unless prevents common LLM misapplication |

**Validator:**
- `skills/hsf/scripts/validate_sesf.py` — rewrite to validate v6 XML structure, JSON config validity, route element structure, output-schema presence for standard+ tiers
- `skills/hsf/scripts/test_validate_sesf.py` — rewrite tests for v6

## Full Example: Standard Tier in v6

```markdown
---
title: Insurance Claim Document Processor
description: "Classify, extract, and validate insurance claim documents."
tier: standard
---

<purpose>
Process incoming insurance claim documents by classifying them, extracting
structured data, and validating the extracted data against policy rules.
Output a structured claim record ready for adjudication.
</purpose>

<scope>
**In scope:**
- Document classification (form type identification)
- Field extraction from PDFs and scanned images
- Cross-field validation against policy rules
- Structured output generation

**Not in scope:**
- Claim adjudication or payment decisions
- Fraud detection (separate pipeline)
- Customer communication
</scope>

<config>
{
  "supported_form_types": ["CMS-1500", "UB-04", "ADA-J400", "pharmacy_claim"],
  "max_document_pages": 50,
  "extraction_confidence_threshold": 0.85,
  "output_format": "JSON"
}
</config>

<instructions>
### Phase 1: Receive and Classify

1. Verify the document is a PDF or supported image format (TIFF, PNG, JPEG).
2. If the document exceeds `config.max_document_pages`, reject it.
3. Classify the document:

<route name="form_classifier" mode="first_match_wins">
  <case when="has CMS-1500 header or NPI in Box 33">CMS-1500 (professional claim)</case>
  <case when="has UB-04 header or revenue codes in FL 42">UB-04 (institutional claim)</case>
  <case when="has ADA claim form header or tooth numbers">ADA-J400 (dental claim)</case>
  <case when="has NDC codes and pharmacy identifiers">pharmacy_claim</case>
  <default>unclassified (route to manual review)</default>
</route>

4. If the document is unclassified, route to manual review and HALT automated processing.

### Phase 2: Extract Fields

Based on the classified form type, extract:

- **All form types:** patient name, date of birth, policy number, date of service, provider name, provider NPI, diagnosis codes (ICD-10), total billed amount
- **CMS-1500 additionally:** place of service, CPT/HCPCS codes, modifier codes, referring provider
- **UB-04 additionally:** admission date, discharge date, revenue codes, DRG code
- **ADA-J400 additionally:** tooth numbers, surface codes, area of oral cavity
- **Pharmacy claims additionally:** NDC codes, quantity dispensed, days supply, DAW code

For EACH extracted field, record the extraction confidence score. If ANY field has a confidence below `config.extraction_confidence_threshold`, flag that field for manual verification.

### Phase 3: Validate

1. **Required fields** — ALL common fields MUST be present. If ANY are missing, flag as incomplete.
2. **Date consistency** — date of service MUST NOT be in the future. For UB-04, discharge date MUST be on or after admission date.
3. **Code validity** — ALL diagnosis codes MUST be valid ICD-10 codes. ALL procedure codes MUST be valid for the form type.
4. **Policy lookup** — policy number MUST match an active policy. If no match, flag as "policy not found."
5. **Amount reasonableness** — total billed amount SHOULD be within 3 standard deviations of the average for that procedure code. If exceeded, flag as "amount outlier."

### Phase 4: Output

Generate a structured claim record:

<output-schema format="json">
{
  "claim_id": "string",
  "form_type": "CMS-1500 | UB-04 | ADA-J400 | pharmacy_claim",
  "fields": {
    "[field_name]": {
      "value": "string | number | null",
      "confidence": "float 0.0-1.0",
      "source_span": "array of two integers [start_offset, end_offset]"
    }
  },
  "classification": {
    "form_type": "string",
    "confidence": "float 0.0-1.0"
  },
  "validation": {
    "[check_name]": "pass | fail"
  },
  "flags": ["string"],
  "requires_review": "boolean",
  "processed_at": "ISO 8601 timestamp"
}
</output-schema>
</instructions>

<rules>
- **Audit trail:** EVERY processing decision MUST be logged with timestamp, triggering rule, and input values.
- **No data modification:** MUST NOT alter extracted values. If a value appears incorrect, flag it — do not correct it.
- **Confidence transparency:** ALL confidence scores MUST be included in output, even for high-confidence extractions.
</rules>

<errors>
| Error | Severity | Action |
|-------|----------|--------|
| unsupported_format | critical | HALT: "Document format not supported. Expected PDF, TIFF, PNG, or JPEG." |
| exceeds_page_limit | critical | HALT: "Document has {pages} pages, exceeds limit of {max}." |
| unclassified_document | warning | Route to manual review. Do not proceed with extraction. |
| low_confidence_field | warning | Flag field for manual verification. Continue processing. |
| missing_required_field | warning | Flag claim as incomplete. Include missing field list. |
| invalid_diagnosis_code | warning | Flag code as invalid. Include code value and position. |
| policy_not_found | warning | Flag as "policy not found." Continue but mark for review. |
| amount_outlier | info | Include flag in output. Do not block processing. |
</errors>

<examples>
unclassified_with_partial_match: document has CMS-1500-like fields but no header → classified as "unclassified" (partial matches not sufficient)
future_date_of_service: date_of_service="2027-01-15", today="2026-03-14" → validation fails with "date of service is in the future"
confidence_at_threshold: field confidence=0.85 exactly → passes threshold (threshold is "below 0.85", not "at or below")
dual_diagnosis_one_invalid: codes=["M54.5", "Z99.99"] → M54.5 passes, Z99.99 flagged as invalid, claim still processed with flag
</examples>
```
