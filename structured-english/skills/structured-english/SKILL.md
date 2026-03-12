---
name: structured-english
description: Write specifications using Structured English Specification Format (SESF v4), a natural-language format for defining declarative specifications (BEHAVIOR) and procedural pseudocode (PROCEDURE) for AI systems. Features 3-tier scaling (Micro/Standard/Complex), @config parameters, @route decision tables, $variable threading, compact error/example tables, and integrated validation. Use when you need clear, unambiguous, machine-readable specifications. Triggers include "write a spec", "create a specification", "define requirements", "specify the behavior", "write a procedure".
---

# Structured English Specification Format (SESF v4)

Meta
* Version: 4.0.0
* Date: 2026-03-03
* Domain: Specification Authoring
* Status: active
* Tier: standard

Notation
* $ -- references a variable or config value (e.g., $config.validator_path)
* @ -- marks a structured block (@config for parameters, @route for decision tables)
* -> -- means "produces", "routes to", or "yields"
* MUST/SHOULD/MAY/CAN -- requirement strength keywords

Purpose
Generate well-structured SESF v4 specifications from user requests. Given a domain, complexity indicators, and user intent, produce a specification that uses BEHAVIOR blocks for declarative rules, PROCEDURE blocks for step-by-step workflows, and hybrid notation (@config, @route, $variable threading, compact tables) where appropriate. Follows the correct tier format, groups rules/errors/examples by concern, and passes structural validation.

Scope
* IN SCOPE: tier selection, document structuring, behavior composition, procedure composition, hybrid notation placement, type and function placement, natural-English phrasing validation, quality assurance, reference extraction
* OUT OF SCOPE: executing the generated specs, providing domain expertise for spec content, maintaining the validator script, runtime interpretation of specs

Inputs
* user_request: string - what the user wants specified - required
* domain: string - subject area for the specification - required
* complexity_indicators: ComplexityIndicators - signals that inform tier selection - optional
* target_tier: enum [micro, standard, complex] - explicit tier override - optional

Outputs
* specification: string - the complete SESF v4 specification document
* validation_result: ValidationSummary - output from running the validator
* extracted_assets: string - reference material extracted to assets/ if applicable

@config
  validator_path: ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/scripts/validate_sesf.py
  reference_path: ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/reference.md
  template_path: ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/template.md
  examples_path: ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/references/examples.md
  line_budget:
    micro: [10, 100]
    standard: [80, 250]
    complex: [250, 500]
  tier_threshold:
    route_min_branches: 3

Types

ComplexityIndicators {
  behavior_count: integer, optional  -- number of distinct concerns
  has_shared_types: boolean, optional  -- behaviors reference common structures
  has_overlapping_rules: boolean, optional  -- rules from different behaviors can match same input
  has_state: boolean, optional  -- system maintains state across invocations
}

ValidationSummary {
  failures: integer, required
  warnings: integer, required
  passed: boolean, required
}

Functions
-- none: all logic is expressed directly in behavior rules

Behaviors


BEHAVIOR select_tier: Choose the correct complexity tier for the specification

  @route tier_selection [first_match_wins]
    single concern, <=5 rules, no shared types or functions  -> micro
    2-5 behaviors OR shared types/functions OR procedures     -> standard
    overlapping rules needing PRECEDENCE OR 5+ behaviors      -> complex
    *                                                         -> standard

  RULE user_override:
    WHEN the user explicitly requests a tier via target_tier
    THEN use that tier regardless of complexity indicators

  RULE promote_on_growth:
    WHEN a spec exceeds its tier's line budget ($config.line_budget)
    THEN suggest promotion to the next tier
    -- a micro spec that grows past 100 lines SHOULD become standard

  RULE demote_after_refactoring:
    WHEN a complex spec has only one behavior after refactoring
    THEN demote to micro tier

  ERROR no_tier_determinable: warning → default to standard tier and note the assumption, "Insufficient complexity signals. Defaulting to standard tier."

  EXAMPLES:
    single_concern: behavior_count=1, has_shared_types=false, has_overlapping_rules=false -> micro
    multi_behavior: behavior_count=3, has_shared_types=true, has_overlapping_rules=false -> standard
    overlapping: behavior_count=4, has_overlapping_rules=true -> complex
    user_override: target_tier=micro, behavior_count=3 -> micro (user override honored)


BEHAVIOR structure_document: Assemble the specification with correct section ordering and required sections per tier

  RULE section_order:
    sections MUST appear in this order when present:
    Meta, Notation, Purpose, Audience, Scope, Inputs, Outputs, @config,
    Types, Functions, Behaviors/Procedures, Constraints, Precedence,
    Dependencies, Changelog

  @route required_sections [all_matches]
    tier is micro     -> Meta, Purpose, Behaviors OR Procedures, Constraints (optional)
    tier is standard  -> Meta, Notation, Purpose, Scope, Inputs, Outputs, @config (if needed), Behaviors/Procedures, Constraints, Dependencies
    tier is complex   -> all standard sections plus Precedence, Audience (optional), State/Flow (optional per block)
    *                 -> Meta, Purpose, Behaviors OR Procedures

  RULE meta_fields:
    Meta MUST contain: Version (semver), Date (YYYY-MM-DD), Domain,
    Status (draft|active|deprecated), Tier (micro|standard|complex)

  RULE meta_format:
    WHEN tier is micro
    THEN use pipe-delimited single-line Meta format
    ELSE use multi-line bullet Meta format

  RULE empty_section_stubs:
    WHEN a required section has no content
    THEN use a `-- none` stub with a brief reason
    -- applies only to sections required by the tier (e.g., Constraints at standard tier)
    -- optional sections (Types, Functions) MUST be omitted entirely rather than stubbed

  RULE purpose_length:
    Purpose MUST be 1-3 sentences describing what the spec accomplishes

  RULE scope_format:
    Scope MUST contain IN SCOPE and OUT OF SCOPE subsections

  RULE notation_requirement:
    WHEN tier is standard OR tier is complex
    THEN the spec MAY include a Notation section after Meta
    -- bridges readability for non-technical readers; LLMs do not require it

  ERROR missing_required_section: critical → add the missing section, "Missing required section: {section_name} for {tier} tier."
  ERROR extra_micro_section: warning → remove the extra section or promote to standard, "Micro tier MUST NOT include {section_name}."

  EXAMPLES:
    standard_valid: tier=standard, all 10 required sections present -> valid
    micro_with_extras: tier=micro, includes Inputs and Types -> invalid, micro MUST NOT include Inputs or Types


BEHAVIOR write_behaviors: Compose BEHAVIOR blocks with rules, errors, and examples grouped by concern

  RULE self_contained:
    each BEHAVIOR block MUST make sense on its own without reading other behaviors
    -- shared types and functions are defined outside behaviors; everything else lives inside

  RULE naming:
    behavior names MUST use snake_case and describe the concern, not the implementation
    -- "validate_payment" not "step_3"; "calculate_shipping" not "shipping_logic"

  RULE rule_forms:
    WHEN a rule depends on a condition
    THEN use WHEN/THEN/ELSE syntax
    ELSE use direct constraint syntax: "field MUST satisfy constraint"

  RULE consolidate_branches:
    WHEN multiple rules share the same subject and differ only in the condition value
    THEN combine them into one rule with WHEN/ELSE WHEN branches

  RULE route_usage:
    WHEN a conditional has $config.tier_threshold.route_min_branches or more branches
    THEN use an @route decision table instead of chained WHEN/THEN/ELSE WHEN
    ELSE use WHEN/THEN rules for binary constraints
    -- the form is determined by branch count, not author preference

  RULE inline_error_format:
    errors SHOULD use inline ERROR format: ERROR name: severity → action, "message"
    -- one ERROR per line; compact and scannable
    -- MAY use full ERROR block (WHEN/SEVERITY/ACTION/MESSAGE) for complex recovery logic
    -- MAY use compact ERRORS: table for backward compatibility
    -- omit ERROR declarations entirely when the failure mode is already fully specified by a RULE's WHEN/THEN/ELSE
    -- ERROR is for failure modes that rules don't cover

  RULE compact_examples:
    examples SHOULD use single-line format: name: input -> expected
    -- concise and sufficient for most cases
    MAY use full EXAMPLE blocks (INPUT/EXPECTED/NOTES) only when multi-line JSON or essential NOTES are needed
    -- omit examples entirely when the rules are self-explanatory
    -- an example that just restates a rule adds bytes without adding clarity

  RULE error_coverage:
    EXAMPLES SHOULD cover only non-obvious edge cases, borderline decisions, or behavior that is surprising or ambiguous
    -- happy-path examples that restate what the rules already say are bloat — omit them

  RULE error_structure:
    ERROR blocks MUST contain: WHEN, SEVERITY (critical|warning|info), ACTION, MESSAGE

  RULE example_concreteness:
    EXAMPLE blocks MUST use concrete values in INPUT and EXPECTED -- never placeholders
    AND MUST include both happy-path and error-triggering examples

  RULE explicit_outcomes:
    every conditional branch MUST have an explicit outcome
    (THEN and ELSE, or document that no action is taken)
    -- AI agents interpret literally; implicit "do nothing" is ambiguous

  RULE no_ambiguity:
    rules MUST NOT use vague language:
    "handle appropriately", "use common sense", "extract relevant fields"
    -- specify each case explicitly; name specific fields; define expected behavior

  RULE inline_comments:
    non-obvious rule logic SHOULD include a `-- comment` explaining the rationale

  RULE evaluation_order:
    rules within a behavior are evaluated in declaration order
    unless a PRIORITY tag overrides it

  ERROR vague_rule: critical → rewrite the rule with specific conditions and actions, "Rule '{rule_name}' is too vague. Specify each case explicitly."
  ERROR missing_error_block: warning → add ERROR blocks for each failure mode, "Behavior '{behavior_name}' has rules but no error handling."
  ERROR route_under_threshold: warning → convert to WHEN/THEN rules, "@route '{table_name}' has fewer than {route_min_branches} branches. Use WHEN/THEN instead."

  EXAMPLES:
    well_structured: behavior with 3 rules, 2 errors, 4 examples -> valid, self-contained
    vague_detected: rule_text="Handle errors appropriately" -> invalid, must specify each error case
    route_appropriate: 4-branch conditional -> use @route table
    route_inappropriate: 2-branch conditional -> use WHEN/THEN rule


BEHAVIOR write_procedures: Compose PROCEDURE blocks with ordered steps written in natural English

  RULE procedure_naming:
    procedure names MUST use snake_case and describe the workflow, not the implementation
    -- "onboard_new_customer" not "step_sequence_1"; "generate_monthly_report" not "report_proc"

  RULE step_ordering:
    each STEP MUST have what it needs from prior steps
    -- a step that uses a result MUST come after the step that produces it
    AND steps MUST be ordered so a reader CAN follow the workflow top to bottom

  RULE natural_english_phrasing:
    steps MUST be written in natural English, not programming syntax
    -- "Look up the customer record by email" not "SET customer = db.query(email)"
    -- "For each item in the order" not "FOR i = 0 TO items.length"
    AND steps SHOULD read as instructions a non-programmer CAN follow

  RULE variable_threading:
    WHEN a step produces data used by later steps
    THEN declare outputs using -> $var syntax on the STEP line
    AND show which action produces which variable with -> $var on the action line
    -- $variable threading replaces prose like "record the result" with explicit declarations

  RULE variable_scope:
    all $variables have document-global scope
    -- once produced by any STEP in any PROCEDURE, a $variable is visible everywhere in the spec

  RULE side_effect_placement:
    side effects (sending emails, writing files, updating databases) belong in PROCEDURE STEPs or ACTION blocks
    AND side effects MUST NOT appear in FUNCTION bodies
    -- FUNCTIONs are pure: inputs in, outputs out, no side effects

  RULE error_recovery_pattern:
    WHEN a step CAN fail
    THEN use the pattern: "Attempt to <action>. If it fails, <recovery>."

  RULE state_transitions:
    WHEN a step changes the state of an entity
    THEN use the pattern: "Move <entity> from <old_state> to <new_state>"

  ERROR programming_syntax: critical → rewrite the step in natural English, "Step '{step_name}' uses programming syntax. Rewrite in natural English."
  ERROR steps_out_of_order: critical → reorder steps so each step has what it needs, "Step '{step_name}' references '{dependency}' which has not been produced yet."
  ERROR unproduced_variable: critical → add -> $var declaration to the producing step, "$variable '{var_name}' is referenced but never produced by any STEP."

  EXAMPLES:
    well_ordered: steps=[lookup, calculate, act, transition, notify] -> valid, each builds on previous
    programming_rejected: step_text="SET total = SUM(line_items)" -> invalid, use natural English
    natural_accepted: step_text="For each line item, verify quantity matches shipment" -> valid
    variable_threaded: STEP gather -> $raw_data, STEP process uses $raw_data -> valid threading


BEHAVIOR write_hybrid_elements: Apply v4 hybrid notation correctly across the specification

  RULE config_placement:
    @config MUST appear after Outputs and before Types (or before Behaviors in micro tier)
    AND @config MUST appear before any BEHAVIOR or PROCEDURE block

  RULE config_syntax:
    @config keys MUST use snake_case
    AND values MUST be literals: strings, numbers, lists [a, b, c], or nested objects
    AND references use $config.key or $config.nested.key syntax
    -- @config is for static values only; runtime values use $variable threading

  RULE route_placement:
    @route tables MUST appear inside BEHAVIOR blocks only
    -- @route replaces RULE chains for multi-branch routing; it does not belong outside BEHAVIORs

  RULE route_threshold:
    @route tables MUST have AT LEAST $config.tier_threshold.route_min_branches branches
    -- for fewer than 3 branches, use WHEN/THEN rules instead
    AND @route tables SHOULD end with a * (wildcard) default row WHEN a meaningful default action exists
    -- WHEN all cases are explicitly enumerated, the wildcard MAY be omitted

  RULE route_modes:
    @route tables use one of two modes:
    first_match_wins -- stop at first matching row (default)
    all_matches -- apply all matching rows

  RULE variable_threading_syntax:
    $variable declarations use -> $var after STEP names and action lines
    AND $variables use $ prefix with snake_case naming
    AND $config.key references the @config block; $var references a step output
    -- variable threading is optional; steps without outputs omit the -> declaration

  RULE inline_error_syntax:
    inline errors use the format: ERROR name: severity → action, "message"
    AND severity values MUST be: critical (halt), warning (continue with degradation), or info (log only)
    AND for complex recovery logic needing multiple sentences, MAY use a full ERROR block instead
    AND compact ERRORS: tables (5-column markdown) are accepted for backward compatibility

  RULE compact_example_syntax:
    examples SHOULD use single-line format: name: input_description -> expected_outcome
    AND the -> symbol separates input from expected output
    AND MAY use full EXAMPLE blocks (INPUT/EXPECTED/NOTES) only when multi-line JSON or essential NOTES are needed

  RULE notation_section:
    the spec MAY include a Notation section after Meta
    -- bridges readability for non-technical or human readers
    -- LLM consumers do not require it
    WHEN a Notation section is included
    THEN it MUST define at minimum: $, @, ->, and MUST/SHOULD/MAY/CAN

  RULE mixed_usage:
    a BEHAVIOR or PROCEDURE block MAY contain both compact and traditional ERROR/EXAMPLE entries
    AND a BEHAVIOR block MAY contain both @route tables (for 3+ branch routing) AND individual RULE blocks (for binary constraints)

  ERROR config_after_behavior: critical → move @config before all behavior/procedure blocks, "@config MUST appear before any BEHAVIOR or PROCEDURE block."
  ERROR route_outside_behavior: critical → move @route inside a BEHAVIOR block, "@route tables belong inside BEHAVIOR blocks only."
  ERROR route_missing_wildcard: warning → consider whether a wildcard default is needed, "@route '{table_name}' has no wildcard (*) default row. Omit if all cases are explicitly covered."
  ERROR route_too_few_branches: warning → convert to WHEN/THEN rules, "@route '{table_name}' has fewer than {route_min_branches} branches."
  ERROR variable_never_produced: critical → add -> $var to the producing step, "$variable '{var_name}' is referenced but never produced."
  ERROR config_runtime_misuse: warning → use $variable threading instead of @config, "$config is for static values only. Use $variable threading for '{key}'."

  EXAMPLES:
    config_valid: @config after Outputs, before Types, keys in snake_case -> valid
    route_valid: @route with 4 branches inside BEHAVIOR, ends with wildcard -> valid
    route_invalid_2_branches: @route with 2 branches -> invalid, use WHEN/THEN instead
    variable_valid: STEP produce -> $data, later STEP uses $data -> valid threading
    notation_present: standard tier with Notation after Meta -> valid


BEHAVIOR write_shared_definitions: Place types, functions, actions, and precedence rules correctly

  RULE type_placement:
    WHEN a data structure is referenced by multiple behaviors or procedures
    THEN define it in the Types section
    ELSE inline its fields directly in the single behavior or procedure that uses it
    -- only extract to Types when 2+ blocks share the same structure
    -- single-use types in the Types section are dead weight; inline them

  RULE function_purity:
    functions MUST be pure -- inputs in, outputs out, no side effects

  RULE action_side_effects:
    ACTIONs are the counterpart to FUNCTIONs for operations with side effects
    -- ACTION for sending emails, writing files, calling APIs
    -- FUNCTION for calculations, transformations, lookups
    AND ACTIONs MUST be named with a verb phrase describing the side effect

  RULE function_placement:
    WHEN a calculation is used by multiple behaviors or procedures
    THEN define it in the Functions section
    ELSE inline it within the single behavior or procedure that uses it

  RULE omit_empty_sections:
    WHEN a section would contain only a `-- none` stub
    THEN omit the section entirely
    -- do not template the absence of content
    -- applies to optional sections: Types, Functions, Notation, Audience, Changelog

  RULE no_orphan_definitions:
    every Type, Function, and ACTION defined in the shared sections
    MUST be referenced by at least one BEHAVIOR or PROCEDURE
    -- unreferenced definitions are dead weight; remove them or add references

  RULE precedence_required:
    WHEN tier = complex AND rules from different behaviors can match the same input
    THEN a PRECEDENCE block MUST be defined
    ELSE WHEN no overlapping conditions exist
    THEN PRECEDENCE block MUST be omitted -- even at complex tier

  RULE priority_consistency:
    inline PRIORITY tags within behaviors
    MUST NOT contradict the global PRECEDENCE block

  ERROR orphan_type: warning → remove the type or add a reference, "Type '{type_name}' is defined but never referenced."
  ERROR orphan_function: warning → remove the function or add a reference, "Function '{function_name}' is never referenced."
  ERROR orphan_action: warning → remove the action or add a reference, "ACTION '{action_name}' is never referenced."

  EXAMPLES:
    shared_type: type=Order, referenced_by=[validate_order, process_order] -> Types section, valid
    single_use_type: type=TempResult, referenced_by=[calculate_total] -> inline within calculate_total
    orphan_detected: type=LegacyRecord, referenced_by=[] -> invalid, remove or add reference


BEHAVIOR ensure_quality: Validate the completed specification against SESF v4 standards

  RULE no_duplication_across_layers:
    ERROR declarations MUST NOT duplicate failure modes already fully specified by RULE blocks
    -- if a RULE's WHEN/THEN covers the failure case, an ERROR restating it is redundant
    -- ERROR adds value only for failure modes that rules don't cover

  RULE inline_single_use_config:
    WHEN a @config value is referenced exactly once in the spec
    THEN consider inlining it at the point of use rather than declaring it in @config
    -- @config earns its bytes when the same value appears in multiple locations or is likely to change

  RULE deduplicate:
    no rule MUST be restated in Constraints that already appears as a RULE inside a BEHAVIOR
    -- Constraints are for cross-cutting limits not naturally part of any single behavior

  RULE input_coverage:
    every input enum value MUST map to at least one rule in a behavior
    -- if an input option has no corresponding rule, either add the rule or remove the option

  RULE reference_extraction:
    WHEN reference/lookup data (flag tables, model lists, keyword catalogs) exceeds 10 lines
    THEN extract it to `assets/` and add a one-line pointer in the spec
    -- keeps the spec focused on what the agent DOES, not what it LOOKS UP

  RULE line_budget:
    micro specs SHOULD stay within $config.line_budget.micro lines
    AND standard specs SHOULD stay within $config.line_budget.standard lines
    AND complex specs SHOULD stay within $config.line_budget.complex lines
    -- PROCEDURE blocks count the same as BEHAVIOR blocks for line budgeting

  RULE keyword_capitalization:
    requirement keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY, CAN)
    MUST be capitalized when used with their RFC 2119 meanings
    -- CAN indicates ability or permission in natural-English phrasing

  RULE markdown_formatting:
    identifiers MUST use backtick formatting: `$variable` names, `@config` keys,
    `behavior_name` and `procedure_name` references, and literal values like `"error message"`
    -- backticks distinguish system tokens from surrounding prose in both raw and rendered markdown
    AND section headers (Meta, Purpose, Behaviors, etc.) MUST use markdown `###` heading syntax
    AND block keywords (BEHAVIOR, PROCEDURE, RULE, STEP) MUST use markdown `**bold**` syntax
    -- heading and bold formatting improve readability in rendered markdown editors
    -- SESF specs MUST remain readable as plain text without rendering

  RULE run_validator:
    WHEN specification is complete
    THEN run `python3 $config.validator_path <spec.md>` and fix all failures
    -- the SESF v4 validator checks BEHAVIOR blocks, PROCEDURE blocks, ACTION declarations,
    -- section structure, @config references, @route tables, and $variable threading

  RULE yaml_frontmatter:
    WHEN the specification is a Claude Code skill
    THEN it MUST include YAML frontmatter with `name` and `description` fields before the title

  RULE hybrid_quality_checks:
    WHEN the specification uses @config
    THEN every $config.key reference MUST match an entry in the @config block
    AND WHEN the specification uses @route
    THEN every @route table MUST have a wildcard default row
    AND WHEN the specification uses $variable threading
    THEN every $variable MUST be produced before it is referenced

  RULE notation_completeness:
    WHEN a Notation section is included
    THEN it MUST define all symbols used in the spec ($, @, ->)
    AND MUST define requirement strength keywords

  ERROR validation_failure: critical → fix the structural issues identified by the validator, "Specification has {n} validation failures. Fix before delivery."
  ERROR over_budget: warning → review for redundancy, extract reference material, consolidate related rules, "Specification is {n} lines, exceeding the {tier} tier target of {range}."
  ERROR config_key_mismatch: critical → add the key to @config or fix the reference, "$config.{key} does not match any @config entry."

  EXAMPLES:
    clean_validation: validator_output={failures: 0, warnings: 2} -> passed (warnings acceptable)
    bloated_spec: tier=standard, line_count=380 -> warning, exceeds $config.line_budget.standard by 27%
    config_valid: all $config.key references match @config entries -> passed
    notation_present: standard tier, Notation section after Meta -> passed

Constraints
* Clarity over brevity: explicit is better than clever
* One idea per statement: break complex rules into simple parts
* Concrete over abstract: use examples, not just descriptions
* Consistent structure: same format across all specs
* Behavior-centric: group rules, errors, and examples by behavior, not by type
* Tight over bloated: say each thing once, in the right place -- completeness does not mean repetition
* specifications MUST pass `python3 $config.validator_path` with zero failures before delivery
* YAML frontmatter (name + description) is required for Claude Code skills
* @route tables MUST have AT LEAST $config.tier_threshold.route_min_branches branches; wildcard default row is recommended but MAY be omitted when all cases are explicitly covered
* $config values are static only -- use $variable threading for runtime data

Syntax Quick Reference
-- Essential syntax skeletons; see $config.reference_path for full details

BEHAVIOR block:
  BEHAVIOR behavior_name: Brief description
    RULE rule_name:
      WHEN condition
      THEN action
      ELSE alternative
    ERROR error_name: severity → action, "message"
    EXAMPLES:
      name: input -> expected

PROCEDURE block:
  PROCEDURE procedure_name: Brief description
    STEP step_name → $output_var:
      action description → $output_var
    ERROR error_name: severity → action, "message"
    EXAMPLES:
      name: input -> expected

@config block:
  @config
    key: value
    nested:
      key: value
  -- reference with $config.key or $config.nested.key

@route table:
  @route table_name [first_match_wins]
    condition_1  → outcome_1
    condition_2  → outcome_2
    *            → default_outcome
  -- 3+ branches required; wildcard * recommended when a meaningful default exists

Inline ERROR format:
  ERROR name: severity → action, "message"
  -- severity: critical (halt), warning (continue), info (log only)

Single-line EXAMPLE format:
  name: input_description -> expected_outcome

Dependencies
* Template: $config.template_path -- fill-in-the-blank templates for all three tiers
* Examples: $config.examples_path -- one complete example per tier
* Reference: $config.reference_path -- syntax examples, keyword definitions, anti-patterns, completeness checklist
* Validator: `python3 $config.validator_path <spec.md>` -- structural validation including hybrid notation checks
