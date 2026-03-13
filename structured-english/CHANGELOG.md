# Changelog

All notable changes to the `structured-english` plugin are documented here.

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
