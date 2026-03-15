---
name: hsf
description: Write specifications using Hybrid Specification Format (HSF v6), a prose-based format optimized for LLM consumption. Uses natural-language instructions within an XML envelope (<purpose>, <scope>, <config>, <instructions>, <rules>, <errors>, <examples>), JSON configuration blocks, XML <route> decision tables for multi-branch logic, <output-schema> for structured output specification, $variable threading for complex data flows, and consolidated error tables. Features 3-tier scaling (Micro/Standard/Complex) and integrated validation. Use when writing specs for LLM agents. Triggers include "write a spec", "write an LLM spec", "create an HSF specification", "write a specification for an agent".
---

# Hybrid Specification Format (HSF v6)

Generate well-structured hybrid specifications from user requests. Given a domain, complexity indicators, and user intent, produce a specification that uses prose instructions within an XML envelope (`<purpose>`, `<scope>`, `<config>`, `<instructions>`, `<rules>`, `<errors>`, `<examples>`), JSON configuration in `<config>` blocks, XML `<route>` decision tables for multi-branch logic, `<output-schema>` for structured output specification, `$variable` threading for complex data flows, and consolidated error tables. Follows the correct tier format and passes structural validation.

**Not in scope:** executing the generated specs, providing domain expertise for spec content, maintaining the validator script, runtime interpretation of specs

<config>
{
  "validator_path": "${CLAUDE_PLUGIN_ROOT}/skills/hsf/scripts/validate_sesf.py",
  "reference_path": "${CLAUDE_PLUGIN_ROOT}/skills/hsf/assets/reference.md",
  "template_path": "${CLAUDE_PLUGIN_ROOT}/skills/hsf/assets/template.md",
  "examples_path": "${CLAUDE_PLUGIN_ROOT}/skills/hsf/references/examples.md",
  "line_budget": {
    "micro": [20, 80],
    "standard": [80, 200],
    "complex": [200, 400]
  },
  "tier_threshold": {
    "route_min_branches": 3
  }
}
</config>

## Inputs

- `user_request`: string - what the user wants specified - required
- `domain`: string - subject area for the specification - required
- `complexity_indicators`: signals that inform tier selection (concern count, shared structures, overlapping rules, stateful behavior) - optional
- `target_tier`: enum [micro, standard, complex] - explicit tier override - optional

## Outputs

- `specification`: string - the complete HSF v6 specification document
- `validation_result`: pass/fail/warnings from the validator
- `extracted_assets`: reference material extracted to assets/ if applicable

## Tier Selection

<route name="tier_selection" mode="first_match_wins">
  <case when="single concern, ≤5 rules, no shared types or functions">micro</case>
  <case when="2-5 concerns OR shared structures OR multi-phase procedures">standard</case>
  <case when="overlapping rules needing precedence OR 5+ concerns">complex</case>
  <default>standard</default>
</route>

When the user explicitly requests a tier via `target_tier`, use that tier regardless of complexity indicators. When a spec exceeds its tier's line budget, suggest promotion to the next tier.

## Instructions

### How to Select a Tier

Use the `<route>` table above. Default to standard when signals are ambiguous. A micro spec that grows past 80 lines SHOULD become standard. A complex spec with only one concern after refactoring SHOULD demote to micro.

### How to Structure the Document

**Always required** (all tiers):

- **`<purpose>`** (1-3 sentences — the opening section of the spec)
- **`<scope>`** (IN/OUT as bullet lists, or a single "Not in scope" line for micro)
- **`<config>`** (if any static params exist — use `<config>` with JSON body for 3+ values, or inline in prose for fewer)
- **`<instructions>`** (the actual procedure — in prose, with clear `###` phase/step headers inside)
- **`<errors>`** (as a table: Error | Severity | Action)

**Required for Standard and Complex only:**

- **`<inputs>` / `<outputs>`** (typed parameter lists)
- **`<rules>`** (grouped by concern, as prose with bold headers — for cross-cutting rules that apply across ALL phases only)
- **`<examples>`** (edge cases only, with pass/fail)

**Optional (include only when they add value):**

- `<route>` tables (only for 3+ branch decision logic)
- `<config>` blocks (only when 3+ configuration values exist)
- `<output-schema>` blocks (for specifying structured output format)
- $variable threading (only when data flows between phases are complex enough to need explicit tracking)
- Worked examples with derivation chains (only for specs where chain integrity matters)

**Removed entirely — do NOT include:**

- Meta section (version goes in YAML frontmatter if needed)
- Notation section (symbols are self-evident or explained inline on first use)
- Types section (inline field descriptions where they're used)
- Functions section (logic goes in Instructions or Rules)
- Precedence section (resolve conflicts in the prose directly)
- Dependencies section (agent discovers these from context)
- Changelog section (use git history; version in frontmatter is sufficient)

**Forbidden syntax — do NOT use:**

- `## Section` top-level headers (use XML tags: `<purpose>`, `<scope>`, etc.)
- `@config` blocks (use `<config>` with JSON body)
- `@route` tables (use `<route>` with XML `<case>` elements)
- `$config.key` references (use `config.key` without the `$` prefix)

### How to Write Rules

Write rules as prose with `###` sub-headers and bold list items inside `<rules>`. Use RFC 2119 keywords (MUST, SHOULD, MAY) for precision. State each constraint ONCE, in the section where it applies.

**Do NOT use:**
- `**BEHAVIOR**` or `**RULE**` keywords
- WHEN/THEN/ELSE syntax
- Scattered inline ERROR declarations after individual rules

**Do use:**
- `###` headers for rule groups (inside `<rules>`)
- Bold list items (`- **Rule name:**`) for individual rules
- Natural sentences that combine condition and action
- Consolidated error table inside `<errors>` at the end

Example of correct rule writing:

```markdown
<rules>

### Critical Thinking Rules

Apply throughout ALL phases:

- **Professional skepticism:** When a speaker claims something is easy, possible, or valuable — ask: what evidence supports this? What could go wrong? Document both scenarios.
- **Intellectual honesty:** Challenge claims. Identify logical flaws. Provide counterarguments not considered. Flag overconfidence.

</rules>
```

### How to Write Procedures / Instructions

Write procedures as prose inside `<instructions>` with `###` phase headers. Use numbered lists for ordered steps, bullet lists for parallel concerns. Bold key terms.

**Do NOT use:**
- `**PROCEDURE**` or `**STEP**` keywords
- `→ $variable` output declarations (unless data flow between phases is genuinely complex)
- References to BEHAVIOR blocks (inline the actual rules where they apply)

**Do use:**
- `###` headers for phases: `### Phase 1: Extraction`
- Numbered lists for sequences within a phase
- Inline constraints where they apply instead of referencing a separate rules section
- $variable threading only when explicit data flow tracking prevents bugs

Example of correct instruction writing:

```markdown
<instructions>

### Setup

Run `mkdir -p /tmp/scratchpad/`. Create all 6 tasks upfront using TaskCreate.

### Phase 1: Extraction → `phase1_extraction.md`

Read the entire transcript (no skimming). Produce a scratchpad artifact containing:

- **Labeled extracted ideas:** E1, E2, E3... (explicit and implicit)
- **Frameworks and philosophies** identified
- **Critical analysis** of at least 3 major claims

</instructions>
```

### How to Use `<route>` and `<config>`

These are the decision-table and configuration mechanisms of HSF.

**`<route>` decision tables:**
- Use ONLY for 3+ branch decision logic
- Fewer branches → use a prose conditional instead
- Must specify mode: `mode="first_match_wins"` or `mode="all_matches"`
- SHOULD include a `<default>` element when a meaningful default exists

**`<config>` blocks:**
- Use ONLY when 3+ configuration values exist
- Body MUST be valid JSON
- Keys MUST use snake_case
- Values MUST be literals (strings, numbers, arrays, nested objects)
- Reference with `config.key` or `config.nested.key` (no `$` prefix)
- `<config>` is for static values only — use $variable threading for runtime data

### How to Use `<output-schema>`

Use `<output-schema>` to specify structured output formats inline within `<instructions>`. This is useful when the spec produces JSON, structured objects, or machine-readable output.

**When to use:**
- SHOULD include for standard and complex tier specs that produce structured output
- MAY include for micro tier specs when output format clarity adds value
- Place inside `<instructions>`, in the phase that produces the output

**Syntax:**
```markdown
<output-schema format="json">
{
  "field_name": "string",
  "score": "float 0.0-1.0",
  "optional_field": "string | null",
  "items": ["string"]
}
</output-schema>
```

**Type annotations:** Use descriptive types like `"string"`, `"integer"`, `"float 0.0-1.0"`, `"boolean"`, `"string | null"`, `["string"]` (array of strings), or nested objects.

### How to Write Examples

Edge cases only — boundary conditions, error paths, non-obvious behavior. If the happy path is obvious from the rules, do not exemplify it. Use the compact single-line format or multi-line worked examples. Place inside `<examples>`.

**Compact format:** `example_name: input_description → expected_outcome`

**Worked examples** (for specs where derivation chain integrity matters):

```markdown
[good_example]:
  Input: [concrete values]
  Expected: [concrete outcome]
  Why: [explain which rule applies and the reasoning]
```

### How to Write Errors

Consolidate ALL errors into a single table inside `<errors>` at the end of the spec:

```markdown
<errors>

| Error | Severity | Action |
|-------|----------|--------|
| missing_field | critical | halt and report which field is missing |
| over_budget | warning | review for redundancy, suggest promotion |
| empty_result | info | generate empty report, log the date range |

</errors>
```

Severity values: `critical` (halt processing), `warning` (continue with degradation), `info` (log only).

Do NOT scatter error declarations inline after individual rules.

## Rules

### Format Compliance

- **XML envelope required:** MUST use XML tags (`<purpose>`, `<scope>`, `<config>`, `<instructions>`, `<rules>`, `<errors>`, `<examples>`) for top-level sections. MUST NOT use `## Section` markdown headers for top-level sections. `###` sub-headers are used for structure within sections.
- **No legacy syntax:** MUST NOT use `@config`, `@route`, or `$config.key` anywhere in the spec. Use `<config>` with JSON, `<route>` with XML cases, and `config.key` references instead.
- **No formal wrappers:** MUST NOT use `**BEHAVIOR**`, `**RULE**`, `**PROCEDURE**`, or `**STEP**` keywords anywhere in the spec. Use `###` headers and bold list items instead.
- **No empty sections:** If a section would say "none" or be blank, omit it entirely. Do not template the absence of content.
- **No duplicate constraints:** Each rule MUST be stated once, in the section where it applies. No separate "define" then "reference" pattern.
- **No notation legend:** Symbols ($, →) are self-evident. Explain inline on first use only if genuinely non-obvious for the target audience.
- **Errors as consolidated table:** All errors MUST appear in a single `<errors>` table, not scattered inline after rules.
- **RFC 2119 keywords preserved:** MUST, SHOULD, MAY MUST be capitalized when used with their operative meanings.

### Notation Usage

- **`<route>` only for 3+ branches:** Fewer branches → prose conditional. The form is determined by branch count, not author preference.
- **`<config>` only for 3+ values:** Fewer values → inline in the text.
- **$variable threading only for complex flows:** Most specs do not need it. "Phase 2 reads the output of Phase 1" is clear enough in prose.
- **No `<route>` outside instructions:** `<route>` tables belong inline in the `<instructions>` section or in a dedicated routing section — not in separate rule blocks.

### Line Budget

- **Micro** specs SHOULD stay within 20-80 lines
- **Standard** specs SHOULD stay within 80-200 lines
- **Complex** specs SHOULD stay within 200-400 lines

### Quality Assurance

- **Run the validator** when the spec is complete: `python3 config.validator_path <spec.md>` and fix all failures
- **Concrete examples only:** Examples MUST use concrete values — never placeholders. Cover edge cases and boundary conditions only.
- **No ambiguity:** Rules MUST NOT use vague language like "handle appropriately", "use common sense", or "extract relevant fields". Specify each case explicitly.
- **Reference extraction:** When reference/lookup data exceeds 10 lines, extract to `assets/` and add a one-line pointer.
- **YAML frontmatter:** When the specification is a Claude Code skill, it MUST include YAML frontmatter with `name` and `description` fields.

## Quality Checklist

| Check | Rule |
|-------|------|
| **XML envelope used** | Top-level sections use XML tags, not `##` headers |
| **No legacy syntax** | No `@config`, `@route`, or `$config.key` anywhere |
| **No empty sections** | If a section would say "none" or be blank, omit it entirely |
| **No duplicate constraints** | Each rule stated once, in the section where it applies |
| **No formal wrappers on prose** | No `**BEHAVIOR**`, `**RULE**`, `**PROCEDURE**`, `**STEP**` keywords. Use `###` headers and bold list items. |
| **`<route>` only for 3+ branches** | Fewer branches → prose conditional |
| **`<config>` only for 3+ values** | Fewer values → inline in the text |
| **Errors in `<errors>` table** | Not scattered inline after rules |
| **RFC 2119 keywords preserved** | MUST, SHOULD, MAY still capitalized for precision |
| **Line budget compliance** | Micro ≤80, Standard ≤200, Complex ≤400 |
| **Edge-case examples only** | No happy-path examples |
| **No notation legend** | Symbols explained inline on first use if non-obvious |

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| formal_wrapper_used | critical | Remove BEHAVIOR/RULE/PROCEDURE/STEP keywords; rewrite as prose with `###` headers |
| empty_section | critical | Delete the empty section entirely |
| legacy_syntax_used | critical | Replace `@config` with `<config>` JSON, `@route` with `<route>` XML, `$config.key` with `config.key` |
| missing_xml_envelope | critical | Wrap top-level sections in XML tags; remove `##` headers |
| duplicate_constraint | warning | Remove the duplicate; keep only the instance in the section where it applies |
| route_under_threshold | warning | Convert `<route>` with fewer than 3 branches to a prose conditional |
| config_under_threshold | warning | Inline `<config>` values referenced fewer than 3 times |
| over_budget | warning | Review for redundancy, extract reference material, consolidate rules |
| vague_rule | critical | Rewrite with specific conditions and actions |
| missing_error_table | warning | Add consolidated error table inside `<errors>` at end of spec |
| validation_failure | critical | Fix structural issues identified by the validator |
| config_key_mismatch | critical | Add key to `<config>` or fix the reference |
