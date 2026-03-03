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
    standard: [100, 300]
    complex: [300, 600]
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

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | no_tier_determinable | target_tier is not provided AND complexity_indicators are insufficient | warning | default to standard tier and note the assumption | "Insufficient complexity signals. Defaulting to standard tier." |

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
    tier is standard  -> Meta, Notation, Purpose, Scope, Inputs, Outputs, @config (if needed), Types, Functions, Behaviors/Procedures, Constraints, Dependencies
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
    WHEN a required section has no content (e.g., no shared types exist)
    THEN use a `-- none` stub with a brief reason

  RULE purpose_length:
    Purpose MUST be 1-3 sentences describing what the spec accomplishes

  RULE scope_format:
    Scope MUST contain IN SCOPE and OUT OF SCOPE subsections

  RULE notation_requirement:
    WHEN tier is standard OR tier is complex
    THEN the spec MUST include a Notation section after Meta
    -- bridges readability for non-technical readers

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | missing_required_section | a required section for the selected tier is absent | critical | add the missing section | "Missing required section: {section_name} for {tier} tier." |
  | extra_micro_section | a micro spec includes sections beyond Meta, Purpose, Behaviors/Procedures, Constraints | warning | remove the extra section or promote to standard | "Micro tier MUST NOT include {section_name}." |

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

  RULE compact_error_tables:
    WHEN a behavior has 2 or more error cases
    THEN use a compact ERRORS: table with 5 mandatory columns (name, when, severity, action, message)
    ELSE a single error case MAY use either compact or traditional ERROR block format

  RULE compact_examples:
    WHEN examples are simple and self-evident (no NOTES needed)
    THEN use compact EXAMPLES: format with -> syntax
    ELSE use full EXAMPLE blocks with INPUT/EXPECTED/NOTES

  RULE error_coverage:
    every RULE SHOULD have at least one EXAMPLE demonstrating it
    AND every ERROR SHOULD have at least one EXAMPLE triggering it

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

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | vague_rule | a rule uses vague language like "handle appropriately" or "validate the data" | critical | rewrite the rule with specific conditions and actions | "Rule '{rule_name}' is too vague. Specify each case explicitly." |
  | missing_error_block | a behavior has rules that can fail but no ERROR blocks | warning | add ERROR blocks for each failure mode | "Behavior '{behavior_name}' has rules but no error handling." |
  | route_under_threshold | an @route table has fewer than $config.tier_threshold.route_min_branches branches | warning | convert to WHEN/THEN rules | "@route '{table_name}' has fewer than {route_min_branches} branches. Use WHEN/THEN instead." |

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

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | programming_syntax | a step uses programming-style syntax (SET, FOR i=0, END IF, RETURN, assignment operators) | critical | rewrite the step in natural English | "Step '{step_name}' uses programming syntax. Rewrite in natural English." |
  | steps_out_of_order | a step references a result that has not been produced by a prior step | critical | reorder steps so each step has what it needs | "Step '{step_name}' references '{dependency}' which has not been produced yet." |
  | unproduced_variable | a $variable is referenced but no STEP declares it with -> $var | critical | add -> $var declaration to the producing step | "$variable '{var_name}' is referenced but never produced by any STEP." |

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
    AND every @route table MUST end with a * (wildcard) default row
    -- for fewer than 3 branches, use WHEN/THEN rules instead

  RULE route_modes:
    @route tables use one of two modes:
    first_match_wins -- stop at first matching row (default)
    all_matches -- apply all matching rows

  RULE variable_threading_syntax:
    $variable declarations use -> $var after STEP names and action lines
    AND $variables use $ prefix with snake_case naming
    AND $config.key references the @config block; $var references a step output
    -- variable threading is optional; steps without outputs omit the -> declaration

  RULE compact_error_syntax:
    compact error tables MUST have 5 mandatory columns: name, when, severity, action, message
    AND severity values MUST be: critical (halt), warning (continue with degradation), or info (log only)
    AND for complex recovery logic needing multiple sentences, use a traditional ERROR block instead

  RULE compact_example_syntax:
    compact examples use the format: name: input_description -> expected_outcome
    AND the -> symbol separates input from expected output
    AND for examples needing NOTES or multi-line INPUT/EXPECTED, use full EXAMPLE blocks

  RULE notation_section:
    WHEN tier is standard OR tier is complex
    THEN the spec MUST include a Notation section after Meta
    AND the Notation section MUST define at minimum: $, @, ->, and MUST/SHOULD/MAY/CAN
    -- micro tier MAY omit Notation or use an abbreviated form

  RULE mixed_usage:
    a BEHAVIOR or PROCEDURE block MAY contain both compact and traditional ERROR/EXAMPLE entries
    AND a BEHAVIOR block MAY contain both @route tables (for 3+ branch routing) AND individual RULE blocks (for binary constraints)

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | config_after_behavior | @config appears after a BEHAVIOR or PROCEDURE block | critical | move @config before all behavior/procedure blocks | "@config MUST appear before any BEHAVIOR or PROCEDURE block." |
  | route_outside_behavior | @route appears outside a BEHAVIOR block | critical | move @route inside a BEHAVIOR block | "@route tables belong inside BEHAVIOR blocks only." |
  | route_missing_wildcard | @route table has no * (wildcard) default row | critical | add a wildcard default row | "@route '{table_name}' is missing a wildcard (*) default row." |
  | route_too_few_branches | @route table has fewer than $config.tier_threshold.route_min_branches branches | warning | convert to WHEN/THEN rules | "@route '{table_name}' has fewer than {route_min_branches} branches." |
  | variable_never_produced | a $variable is referenced but never declared with -> $var | critical | add -> $var to the producing step | "$variable '{var_name}' is referenced but never produced." |
  | config_runtime_misuse | $config.key is used for a runtime value that changes between invocations | warning | use $variable threading instead of @config | "$config is for static values only. Use $variable threading for '{key}'." |
  | notation_missing | a standard or complex tier spec omits the Notation section | warning | add a Notation section after Meta | "Notation section is required for {tier} tier." |

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
    ELSE inline it within the single behavior or procedure that uses it

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

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | orphan_type | a Type is defined but no BEHAVIOR references it | warning | remove the type or add a reference | "Type '{type_name}' is defined but never referenced." |
  | orphan_function | a Function is defined but no BEHAVIOR or PROCEDURE references it | warning | remove the function or add a reference | "Function '{function_name}' is never referenced." |
  | orphan_action | an ACTION is defined but no BEHAVIOR or PROCEDURE references it | warning | remove the action or add a reference | "ACTION '{action_name}' is never referenced." |

  EXAMPLES:
    shared_type: type=Order, referenced_by=[validate_order, process_order] -> Types section, valid
    single_use_type: type=TempResult, referenced_by=[calculate_total] -> inline within calculate_total
    orphan_detected: type=LegacyRecord, referenced_by=[] -> invalid, remove or add reference


BEHAVIOR ensure_quality: Validate the completed specification against SESF v4 standards

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
    WHEN tier is standard or complex
    THEN the Notation section MUST define all symbols used in the spec ($, @, ->)
    AND MUST define requirement strength keywords

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | validation_failure | validator reports failures > 0 | critical | fix the structural issues identified by the validator | "Specification has {n} validation failures. Fix before delivery." |
  | over_budget | line count exceeds the tier's $config.line_budget range by more than 20% | warning | review for redundancy, extract reference material, consolidate related rules | "Specification is {n} lines, exceeding the {tier} tier target of {range}." |
  | config_key_mismatch | a $config.key reference does not match any @config entry | critical | add the key to @config or fix the reference | "$config.{key} does not match any @config entry." |
  | missing_notation | a standard/complex spec omits the Notation section | warning | add Notation section after Meta | "Notation section is required for {tier} tier." |

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
* @route tables MUST have AT LEAST $config.tier_threshold.route_min_branches branches and a wildcard default
* $config values are static only -- use $variable threading for runtime data

Dependencies
* Template: $config.template_path -- fill-in-the-blank templates for all three tiers
* Examples: $config.examples_path -- one complete example per tier
* Reference: $config.reference_path -- syntax examples, keyword definitions, anti-patterns, completeness checklist
* Validator: `python3 $config.validator_path <spec.md>` -- structural validation including hybrid notation checks
