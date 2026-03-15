# Changelog

All notable changes to the `structured-english` plugin are documented here.

---

## [8.0.0] — 2026-03-14 — HSF v6: XML Envelope + Output Schemas

### Breaking Changes
- **HSF upgraded from v5 to v6:** The LLM-facing specification format now uses XML tags and native JSON/XML notation instead of custom `@`-prefixed syntax
  - Top-level sections wrapped in XML tags (`<purpose>`, `<scope>`, `<config>`, `<instructions>`, `<rules>`, `<errors>`, `<examples>`, `<inputs>`, `<outputs>`) instead of `## Markdown Headers`
  - `@config` with YAML-like syntax replaced by `<config>` with JSON body
  - `@route name [mode]` with `→` rows replaced by `<route name="..." mode="...">` with `<case when="...">` and `<default>` XML elements
  - Config references changed from `$config.key` to `config.key` (no `$` prefix — reserved for `$variable` threading)
  - `## Section` markdown headers forbidden for top-level sections (use XML tags); `###` headers still used for sub-structure within sections

### New: `<output-schema>` Blocks
- Define exact structured output shape inline in instructions
- Uses descriptive type annotations (`"string"`, `"float 0.0-1.0"`, `"string | null"`) — not formal JSON Schema
- SHOULD for standard and complex tiers when producing structured output; MAY for micro
- Closes the biggest LLM compliance gap: LLMs guessing output shape

### Updated
- `skills/hsf/SKILL.md` — rewritten for v6 rules and examples
- `skills/hsf/assets/reference.md` — rewritten with XML envelope, JSON config, XML routes, output-schema documentation
- `skills/hsf/assets/template.md` — all tier templates rewritten in v6 format
- `skills/hsf/references/examples.md` — all three tier examples (Micro, Standard, Complex) rewritten in v6 format
- `commands/write-LLM-spec.md` — updated for v6 notation and output-schema guidance
- `commands/assess-LLM-doc.md` — updated assessment signals for XML envelope and output-schema benefits
- `commands/convert-human-to-llm.md` — updated conversion mapping table for SESF → HSF v6

### Validator
- `validate_sesf.py` now auto-detects HSF v6 (by XML section tags) alongside v5 and SESF v4
- New validation functions: `check_hsf_v6_structure`, `check_hsf_v6_config` (JSON parsing), `check_hsf_v6_routes` (XML element parsing), `check_hsf_v6_output_schema`
- 19 new v6 tests added (54 total, all passing)

### Unchanged
- SESF v4.1 (human-facing format) — no changes
- `$variable` threading, RFC 2119 keywords, tier system, line budgets, error table format, edge-case-only examples — all preserved
- `/write-human-spec`, `/assess-human-doc`, `/update-human-spec`, `/assess-inferred-intent` — unchanged

### Design Rationale
- XML tags provide unambiguous section boundaries that LLMs parse with near-perfect accuracy
- JSON config eliminates custom YAML-like syntax — LLMs already parse JSON natively
- XML route elements make branch boundaries explicit without custom `→` separator notation
- Output schemas close the most common LLM compliance failure: guessing output structure
- The approach matches how Anthropic's own system prompts work — XML envelopes with prose content

---

## [7.0.0] — 2026-03-13 — Dual-Audience Architecture (HSF + SESF)

### Breaking Changes
- **Two skills instead of one:** Plugin now contains two specification format skills under one package
  - `hsf` — Hybrid Specification Format v5, optimized for LLM execution (prose instructions, markdown headers)
  - `sesf` — Structured English Specification Format v4.1, optimized for human readers (formal BEHAVIOR/PROCEDURE/RULE/STEP blocks with WHEN/THEN syntax and rationale annotations)
- **Skill renamed:** `structured-english` skill renamed to `hsf`; all internal paths changed from `skills/structured-english/` to `skills/hsf/`
- **Commands replaced:** The 3 audience-agnostic commands (`/write-spec`, `/update-spec`, `/assess-doc`) are removed and replaced with 7 audience-specific commands

### New Commands
- `/write-LLM-spec` — write a spec optimized for LLM execution (uses `hsf` skill)
- `/write-human-spec` — write a spec optimized for human reading (uses `sesf` skill, produces formal blocks)
- `/assess-LLM-doc` — assess whether a document would benefit from LLM-facing HSF conversion
- `/assess-human-doc` — assess whether a document would benefit from human-facing SESF conversion
- `/update-LLM-spec` — upgrade an older spec to HSF v5 (LLM-optimized)
- `/update-human-spec` — upgrade an older SESF spec (v1/v2/v3/v4) to SESF v4.1
- `/convert-human-to-llm` — convert a SESF v4.1 spec to HSF v5 (the authoring pipeline bridge)

### Updated
- `/assess-inferred-intent` — after resolving ambiguity/contradictions, now asks whether to output as SESF v4.1 (human), HSF v5 (LLM), or keep current format

### New: SESF v4.1 Skill
- `skills/sesf/SKILL.md` — full skill definition with formal block syntax rules
- `skills/sesf/assets/reference.md` — SESF v4.1 format specification with syntax docs and tier examples
- `skills/sesf/assets/template.md` — fill-in-the-blank templates for all tiers using formal blocks
- `skills/sesf/assets/authoring-guide.md` — 6-step thinking process guide for human spec authors
- `skills/sesf/references/examples.md` — 3 complete SESF v4.1 examples (Micro, Standard, Complex)
- `skills/sesf/scripts/validate_sesf.py` — validator (shared codebase, auto-detects format)

### SESF v4.1 Format (What's New vs v4)
- **Kept from v4:** BEHAVIOR/PROCEDURE/RULE/STEP blocks, WHEN/THEN/ELSE syntax, → $variable declarations, @route, @config
- **Added:** Consolidated `## Errors` table (no more scattered inline ERROR declarations), rationale annotations (parenthetical after rules explaining *why*)
- **Removed:** Meta, Notation, Types, Functions, Precedence, Dependencies, Changelog boilerplate sections

### Design Rationale
- LLMs follow prose better (65% more synthesis, 55% fewer tokens in A/B testing)
- Humans benefit from formal blocks (visual scaffolding, explicit categorization, scannable WHEN/THEN alignment)
- One format cannot serve both audiences well — the dual-skill architecture lets each optimize for its reader

---

## [6.0.0] — 2026-03-13 — Hybrid Format (HSF v5.0.0)

### Breaking Changes
- **New output format:** Hybrid Specification Format replaces SESF v4
  - BEHAVIOR/RULE/PROCEDURE/STEP keywords removed
  - Instructions written in natural language prose with markdown headers
  - Rules stated inline where they apply, not in separate blocks
  - Errors consolidated into a single table
  - Meta/Notation/Types/Functions/Precedence/Dependencies/Changelog sections removed
- **Line budgets reduced:** Micro ≤80, Standard ≤200, Complex ≤400
- **Validator updated:** Auto-detects v4 vs v5 format, applies appropriate rules

### What's Preserved from SESF v4
- @route decision tables (3+ branch logic)
- @config blocks (3+ static parameters)
- $variable threading (complex data flows)
- Named error taxonomy
- Edge-case-only examples
- RFC 2119 keyword precision (MUST/SHOULD/MAY)

### Migration
- `/update-spec` now handles SESF v4 → Hybrid v5 conversion
- SESF v4 specs remain valid and validator-compatible (backward compat)

### Evidence
- A/B test on 130KB meeting transcript:
  - Hybrid spec (336 lines) vs SESF spec (586 lines)
  - Hybrid produced 65% more synthesis items (48 vs 29)
  - Hybrid extracted nearly 2x ideas (35 vs 20)
  - Both maintained identical rule compliance
  - Hybrid consumed 55% fewer spec tokens

---

## [5.2.5] — 2026-03-13

### Fixed
- `update-spec.md`: Self-contained mode now explicitly requires converting prose workflow into SESF notation rather than wrapping SESF around existing prose. Guards against producing a SESF meta-layer alongside original operational content (one layer: SESF blocks only, no parallel prose).

---

## [5.2.4] — 2026-03-13

### Changed
- `update-spec.md`: Added Step 2.5 — output mode selection (self-contained vs. split) before rewriting; prevents command/skill files from being incorrectly split when operational content must stay inline. Includes auto-detection heuristic for `allowed-tools`/`argument-hint` frontmatter.
- `update-spec.md`: Step 3 EXAMPLE migration now explicitly removes happy-path examples (edge cases only). Step 5 adds edge-case-only constraint to rewriting.
- `write-spec.md`: Step 1 now reads `reference.md` in addition to loading the skill (aligned with `update-spec.md`)
- `write-spec.md`: Step 4 examples rule updated to edge cases only — boundary conditions, error paths, non-obvious behavior; happy-path constraint removed
- `write-spec.md`: Removed "Warnings about example count are acceptable" from Step 6 validator note
- `assess-doc.md`: Added Step 1 to load the skill and `reference.md` (was missing entirely); renumbered subsequent steps
- `assess-doc.md`: Added output mode selection (self-contained vs. split) before conversion, matching `update-spec.md` Step 2.5
- `SKILL.md`: `example_concreteness` rule — removed "MUST include both happy-path and error-triggering examples"; replaced with "MUST cover edge cases, boundary conditions, or error-triggering scenarios only". Resolves contradiction with `error_coverage` rule.
- `SKILL.md`: Meta date updated to 2026-03-13
- `reference.md`: Example Syntax section — replaced happy-path `valid_gold_discount` and `standard_pricing_fallback` examples with boundary-condition examples (`boundary_at_threshold`, `tier_mismatch_at_boundary`)
- `reference.md`: Compact Examples section — removed happy-path `valid_email`; replaced with `at_sign_only` edge case

---

## [5.2.3] — 2026-03-12

### Changed
- Template (standard + complex): removed boilerplate Types and Functions sections; replaced with opt-in guidance
- Template (standard + complex): removed boilerplate ERROR and EXAMPLES lines from BEHAVIOR/PROCEDURE blocks; replaced with opt-in comments
- Template (standard + complex): removed wildcard `*` row from @route; now conditional on whether a meaningful default exists
- SKILL.md: `error_coverage` rule — EXAMPLES now SHOULD cover only non-obvious edge cases, not happy-path restatements
- SKILL.md: `compact_examples` rule — omit examples entirely when rules are self-explanatory
- SKILL.md: `inline_error_format` rule — omit ERROR when failure mode already covered by a RULE
- SKILL.md: `route_threshold` rule — wildcard row changed from MUST to SHOULD; MAY be omitted when all cases are explicitly enumerated
- SKILL.md: `route_missing_wildcard` error — downgraded from critical to warning
- SKILL.md: `type_placement` rule — strengthened inline-first guidance for single-use types
- SKILL.md: `required_sections` route — Types and Functions removed from standard tier requirements
- SKILL.md: `empty_section_stubs` rule — scoped to required sections only; optional sections must be omitted entirely
- SKILL.md: `line_budget` @config — standard `[100, 300]` → `[80, 250]`; complex `[300, 600]` → `[250, 500]`
- reference.md: tier table target lengths updated (standard 100-300 → 80-250, complex 300-600 → 250-500)
- reference.md: Standard required sections — Types and Functions moved to optional
- reference.md: @route wildcard rule changed from MUST to SHOULD with explicit opt-out condition
- reference.md: completeness checklist aligned with new ERROR/EXAMPLES and wildcard rules

### Added
- SKILL.md: new rule `omit_empty_sections` — omit optional sections that would only contain a `-- none` stub
- SKILL.md: new rule `no_duplication_across_layers` — ERROR must not duplicate failure modes already covered by RULE blocks
- SKILL.md: new rule `inline_single_use_config` — @config values referenced exactly once should be inlined

---

## [5.2.2] — 2026-03-12

### Added
- Validator: `check_markdown_formatting` — new check that fails on plain section headers and unbolded block keywords
- Validator: `_normalize_for_matching` helper — strips `**BOLD**` and `###` heading markers before all keyword/section detection, allowing the parser to accept both plain and formatted forms

### Changed
- SKILL.md + reference.md: `markdown_formatting` rule — backtick identifiers, `###` section headers, and `**bold**` block keywords upgraded from SHOULD to MUST

---

## [5.2.1] — 2026-03-12

### Fixed
- Validator: indented `---` lines inside BEHAVIOR/PROCEDURE blocks (e.g. markdown horizontal rules in output templates) no longer terminate parsing; only unindented `---` lines act as spec separators
- Validator: multi-output STEP declarations (`STEP name -> $a, $b, $c:`) now correctly register all output variables; previously only single-output STEPs were detected, causing false "referenced but not produced" warnings

---

## [5.2.0] — 2026-03-01

Initial public release of SESF v4 plugin.

### Included
- SESF v4 authoring skill with 7 behaviors covering tier selection, document structuring, BEHAVIOR/PROCEDURE composition, hybrid notation, shared definitions, and quality assurance
- Commands: `/write-spec`, `/assess-doc`, `/assess-inferred-intent`, `/update-spec`
- Structural validator (`validate_sesf.py`) with checks for section completeness, behavior/procedure structure, @config/@route correctness, $variable threading, and tier compliance
- Templates for micro, standard, and complex tiers
- 7 complete example specs covering all tiers and styles
- Reference guide (Part 1–6): shared foundations, declarative syntax, procedural syntax, function syntax, quality anti-patterns, hybrid notation
