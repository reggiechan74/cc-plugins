---
name: sesf
description: Write specifications using Structured English Specification Format (SESF v4.1), a human-readable format that uses formal BEHAVIOR/PROCEDURE/RULE/STEP blocks for visual scaffolding, WHEN/THEN conditionals for scannable rules, and explicit data flow with → $variable declarations. Features @route decision tables, @config parameters, consolidated error tables, and 3-tier scaling. Optimized for human authors and readers. Triggers include "write a human spec", "create a human-readable specification", "SESF spec", "human-facing spec".
---

# Structured English Specification Format (SESF v4.1)

Generate well-structured specifications from user requests using formal BEHAVIOR/PROCEDURE/RULE/STEP blocks. Given a domain, complexity indicators, and user intent, produce a specification that uses explicit block syntax for visual scaffolding, WHEN/THEN conditionals for scannable rules, STEP with → $variable for data flow tracking, @route tables for multi-branch decisions, @config for centralized parameters, and consolidated error tables. Follows the correct tier format and passes structural validation.

**Not in scope:** executing the generated specs, providing domain expertise for spec content, maintaining the validator script, runtime interpretation of specs

## Configuration

@config
  validator_path: ${CLAUDE_PLUGIN_ROOT}/skills/sesf/scripts/validate_sesf.py
  reference_path: ${CLAUDE_PLUGIN_ROOT}/skills/sesf/assets/reference.md
  template_path: ${CLAUDE_PLUGIN_ROOT}/skills/sesf/assets/template.md
  examples_path: ${CLAUDE_PLUGIN_ROOT}/skills/sesf/references/examples.md
  authoring_guide_path: ${CLAUDE_PLUGIN_ROOT}/skills/sesf/assets/authoring-guide.md
  line_budget:
    micro: [20, 80]
    standard: [80, 200]
    complex: [200, 400]
  tier_threshold:
    route_min_branches: 3

## Inputs

- `user_request`: string - what the user wants specified - required
- `domain`: string - subject area for the specification - required
- `complexity_indicators`: signals that inform tier selection (concern count, shared structures, overlapping rules, stateful behavior) - optional
- `target_tier`: enum [micro, standard, complex] - explicit tier override - optional

## Outputs

- `specification`: string - the complete SESF v4.1 specification document
- `validation_result`: pass/fail/warnings from the validator
- `extracted_assets`: reference material extracted to assets/ if applicable

## Tier Selection

@route tier_selection [first_match_wins]
  single concern, ≤5 rules, no shared types or functions        → micro
  2-5 concerns OR shared structures OR multi-phase procedures    → standard
  overlapping rules needing precedence OR 5+ concerns            → complex
  *                                                              → standard

When the user explicitly requests a tier via `target_tier`, use that tier regardless of complexity indicators. When a spec exceeds its tier's line budget, suggest promotion to the next tier.

## Instructions

### How to Select a Tier

Use the @route table above. Default to standard when signals are ambiguous. A micro spec that grows past 80 lines SHOULD become standard. A complex spec with only one concern after refactoring SHOULD demote to micro.

### How to Structure the Document

**Always required** (all tiers):

- **Purpose** (1-3 sentences, no heading needed for micro)
- **Scope** (IN/OUT as bullet lists, or a single "Not in scope" line for micro)
- **Configuration** (if any static params exist — use @config block for 3+ values, or inline for fewer)
- **BEHAVIOR and/or PROCEDURE blocks** (the core content — formal blocks with RULE and STEP entries)
- **Errors** (as a consolidated table: Error | Severity | Action)

**Required for Standard and Complex only:**

- **Inputs / Outputs** (typed parameter lists)
- **Rules** (cross-cutting only — rules that span ALL behaviors/procedures)
- **Examples** (edge cases only, with pass/fail)

**Optional (include only when they add value):**

- @route tables (only for 3+ branch decision logic)
- @config blocks (only when 3+ configuration values exist)
- $variable threading with STEP → $var (only when data flows between procedures are complex enough to need explicit tracking)
- Rationale annotations (parenthetical after non-obvious rules)

**Removed entirely — do NOT include:**

- Meta section (version goes in YAML frontmatter if needed)
- Notation section (symbols are self-evident or explained inline on first use)
- Types section (inline field descriptions where they're used)
- Functions section (logic goes in BEHAVIOR or PROCEDURE blocks)
- Precedence section (resolve conflicts in the rules directly)
- Dependencies section (agent discovers these from context)
- Changelog section (use git history; version in frontmatter is sufficient)

### How to Write BEHAVIOR Blocks

BEHAVIOR blocks group related declarative rules. Each BEHAVIOR contains one or more RULE entries that describe *what should be true* — not *when to check it*.

**Syntax:**

```
**BEHAVIOR** name: One-line description

  **RULE** rule_name:
    WHEN condition
    THEN action
    ELSE alternative
    (Rationale: why this rule exists)

  **RULE** simple_rule:
    constraint MUST be true
    (Rationale: explanation)
```

**Guidelines:**

- Every BEHAVIOR MUST have a one-line summary after the colon
- RULE entries inside a BEHAVIOR use WHEN/THEN/ELSE for conditional logic
- Simple constraints that are always true use a declarative MUST/SHOULD/MAY statement
- Rationale annotations are parenthetical and SHOULD follow non-obvious rules
- BEHAVIOR blocks are for *declarative* logic — use PROCEDURE for *sequential* logic

**Example:**

```
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
```

### How to Write PROCEDURE Blocks

PROCEDURE blocks define ordered workflows. Each PROCEDURE contains STEP entries that execute sequentially.

**Syntax:**

```
**PROCEDURE** name: One-line description

  **STEP** step_name: Description → $output_var
    Detailed instructions for this step.

  **STEP** next_step: Description
    Uses $output_var from previous step.
```

**Guidelines:**

- Every PROCEDURE MUST have a one-line summary after the colon
- STEP entries execute in the order listed
- Use → $variable after a STEP description to declare output variables
- $variable threading tracks data flow between steps and across procedures
- Keep each STEP focused on a single logical action

**Example:**

```
**PROCEDURE** process_invoice: Validate and route incoming invoice

  **STEP** validate_fields: Check all required fields are present → $validated_invoice
    Verify vendor_name, invoice_number, invoice_date, amount, and currency
    are present and non-empty. If ANY field is missing, reject with
    missing_required_field.

  **STEP** classify: Determine invoice type → $invoice_type
    Apply the invoice_classification @route table to $validated_invoice.

  **STEP** route: Send to appropriate team
    Using $invoice_type, apply the team_assignment @route table.
    WHEN amount > $config.high_value_threshold THEN add VP approval flag.
```

### How to Write RULE with WHEN/THEN

Inside BEHAVIOR blocks, use WHEN/THEN/ELSE for conditional rules:

- **WHEN** introduces the condition
- **THEN** introduces the action when the condition is true
- **ELSE** introduces the alternative (optional)
- For simple always-true constraints, use a MUST/SHOULD/MAY statement without WHEN/THEN

Use WHEN/THEN for 1-2 branch conditions. For 3+ branches, use an @route table instead.

### How to Use @route and @config

These are **identical** to HSF v5 — they are the strongest parts of the format.

**@route decision tables:**
- Use ONLY for 3+ branch decision logic
- Fewer branches → use WHEN/THEN/ELSE inside a RULE
- Must specify mode: `[first_match_wins]` or `[all_matches]`
- SHOULD end with `*` wildcard default when a meaningful default exists

**@config blocks:**
- Use ONLY when 3+ configuration values exist
- Keys MUST use snake_case
- Values MUST be literals (strings, numbers, lists, nested objects)
- Reference with `$config.key` or `$config.nested.key`
- @config is for static values only — use $variable threading for runtime data

### How to Write Examples

Edge cases only — boundary conditions, error paths, non-obvious behavior. If the happy path is obvious from the rules, do not exemplify it. Use the compact single-line format or multi-line worked examples.

**Compact format:** `example_name: input_description → expected_outcome`

**Worked examples** (for specs where derivation chain integrity matters):

```markdown
[good_example]:
  Input: [concrete values]
  Expected: [concrete outcome]
  Why: [explain which rule applies and the reasoning]
```

### How to Write Errors

Consolidate ALL errors into a single `## Errors` table at the end of the spec:

```markdown
## Errors

| Error | Severity | Action |
|-------|----------|--------|
| missing_field | critical | halt and report which field is missing |
| over_budget | warning | review for redundancy, suggest promotion |
| empty_result | info | generate empty report, log the date range |
```

Severity values: `critical` (halt processing), `warning` (continue with degradation), `info` (log only).

Do NOT scatter error declarations inline after individual rules. This is a key improvement over SESF v4.

### How to Add Rationale Annotations

Rationale annotations explain *why* a rule exists. They are parenthetical and follow the rule they annotate:

```
**RULE** constant_time_compare:
  Signature comparison MUST use a constant-time function.
  (Rationale: prevents timing side-channel attacks that could leak signature bytes)
```

Add rationale to rules where the *why* is not obvious from the *what*. Skip rationale on self-evident rules like "amount MUST be positive."

## Rules

### Format Compliance

- **Formal blocks required:** Declarative rules MUST be wrapped in `**BEHAVIOR**` blocks. Sequential workflows MUST be wrapped in `**PROCEDURE**` blocks. Do not use prose headers and bold list items — use the formal block syntax.
- **RULE syntax required:** Conditional logic inside BEHAVIOR blocks MUST use WHEN/THEN/ELSE syntax, not prose "if/then" sentences.
- **STEP syntax required:** Sequential actions inside PROCEDURE blocks MUST use `**STEP**` entries, not numbered lists.
- **No empty sections:** If a section would say "none" or be blank, omit it entirely. Do not template the absence of content.
- **No duplicate constraints:** Each rule MUST be stated once, in the BEHAVIOR or PROCEDURE where it applies. No separate "define" then "reference" pattern.
- **No notation legend:** Symbols ($, @, →) are self-evident. Explain inline on first use only if genuinely non-obvious for the target audience.
- **Errors as consolidated table:** All errors MUST appear in a single `## Errors` table, not scattered inline after rules.
- **RFC 2119 keywords preserved:** MUST, SHOULD, MAY MUST be capitalized when used with their operative meanings.
- **Section-level summaries:** Each BEHAVIOR and PROCEDURE block MUST have a one-line description after the colon.

### Notation Usage

- **@route only for 3+ branches:** Fewer branches → WHEN/THEN/ELSE in a RULE. The form is determined by branch count, not author preference.
- **@config only for 3+ values:** Fewer values → inline in the text.
- **$variable threading for data flow:** Use STEP → $var syntax to declare outputs. Reference $var in subsequent steps. Most micro specs do not need it.
- **No @route outside BEHAVIOR/PROCEDURE blocks:** @route tables belong inline in the relevant block or in a dedicated routing section — not floating unattached.

### Line Budget

- **Micro** specs SHOULD stay within 20-80 lines
- **Standard** specs SHOULD stay within 80-200 lines
- **Complex** specs SHOULD stay within 200-400 lines

### Quality Assurance

- **Run the validator** when the spec is complete: `python3 $config.validator_path <spec.md>` and fix all failures
- **Concrete examples only:** EXAMPLE blocks MUST use concrete values — never placeholders. Cover edge cases and boundary conditions only.
- **No ambiguity:** Rules MUST NOT use vague language like "handle appropriately", "use common sense", or "extract relevant fields". Specify each case explicitly.
- **Reference extraction:** When reference/lookup data exceeds 10 lines, extract to `assets/` and add a one-line pointer.
- **YAML frontmatter:** When the specification is a Claude Code skill, it MUST include YAML frontmatter with `name` and `description` fields.

## Quality Checklist

| Check | Rule |
|-------|------|
| **Every behavior has a block** | Rules grouped under `**BEHAVIOR** name:` |
| **Every procedure has steps** | Steps under `**PROCEDURE** name:` |
| **WHEN/THEN for conditionals** | Not prose "if/then" inside rules |
| **@route only for 3+ branches** | Fewer branches use WHEN/THEN/ELSE |
| **@config only for 3+ values** | Fewer values stated inline in the text |
| **Errors consolidated** | All errors in a single `## Errors` table, not scattered inline |
| **Rationale on non-obvious rules** | Parenthetical after the rule |
| **No empty sections** | Omit unused sections entirely |
| **RFC 2119 keywords preserved** | MUST, SHOULD, MAY capitalized for precision |
| **Line budget compliance** | Micro ≤80, Standard ≤200, Complex ≤400 |
| **Edge-case examples only** | No happy-path examples |
| **Section-level summaries** | Each BEHAVIOR/PROCEDURE has a one-line description |

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| missing_behavior_block | critical | Wrap declarative rules in a `**BEHAVIOR** name:` block |
| missing_procedure_block | critical | Wrap sequential steps in a `**PROCEDURE** name:` block |
| prose_conditional_in_rule | warning | Convert "if/then" prose to WHEN/THEN/ELSE syntax |
| numbered_list_in_procedure | warning | Convert numbered list items to `**STEP** name:` entries |
| empty_section | critical | Delete the empty section entirely |
| duplicate_constraint | warning | Remove the duplicate; keep only the instance in the block where it applies |
| route_under_threshold | warning | Convert @route with fewer than 3 branches to WHEN/THEN/ELSE in a RULE |
| config_under_threshold | warning | Inline @config values referenced fewer than 3 times |
| scattered_errors | critical | Move all inline error declarations to the consolidated `## Errors` table |
| over_budget | warning | Review for redundancy, extract reference material, consolidate rules |
| vague_rule | critical | Rewrite with specific conditions and actions |
| missing_error_table | warning | Add consolidated error table at end of spec |
| validation_failure | critical | Fix structural issues identified by the validator |
| config_key_mismatch | critical | Add key to @config or fix the reference |
| missing_block_summary | warning | Add a one-line description after the BEHAVIOR/PROCEDURE name |
| missing_rationale | info | Consider adding a rationale annotation to non-obvious rules |
