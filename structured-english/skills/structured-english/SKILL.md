---
name: structured-english
description: Write specifications using Structured English Specification Format (SESF v3), a natural-language format for defining declarative specifications (BEHAVIOR) and procedural pseudocode (PROCEDURE) for AI systems. Features 3-tier scaling (Micro/Standard/Complex), rule precedence, ACTION/FUNCTION distinction, and integrated validation. Use when you need clear, unambiguous, machine-readable specifications. Triggers include "write a spec", "create a specification", "define requirements", "specify the behavior", "write a procedure".
---

# Structured English Specification Format (SESF v3)

Meta
* Version: 3.0.0
* Date: 2026-03-01
* Domain: Specification Authoring
* Status: active
* Tier: standard

Purpose
Generate well-structured SESF v3 specifications from user requests. Given a domain, complexity indicators, and user intent, produce a specification that uses BEHAVIOR blocks for declarative rules and PROCEDURE blocks for step-by-step workflows. Follows the correct tier format, groups rules/errors/examples by concern, and passes structural validation.

Scope
* IN SCOPE: tier selection, document structuring, behavior composition, PROCEDURE composition, ACTION placement, type and function placement, natural-English phrasing validation, quality assurance, reference extraction
* OUT OF SCOPE: executing the generated specs, providing domain expertise for spec content, maintaining the validator script, runtime interpretation of specs

Inputs
* user_request: string - what the user wants specified - required
* domain: string - subject area for the specification - required
* complexity_indicators: ComplexityIndicators - signals that inform tier selection - optional
* target_tier: enum [micro, standard, complex] - explicit tier override - optional

Outputs
* specification: string - the complete SESF v3 specification document
* validation_result: ValidationSummary - output from running the validator
* extracted_assets: string - reference material extracted to assets/ if applicable

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


BEHAVIOR select_tier: Determine the correct specification tier based on complexity signals and user intent

  RULE explicit_override:
    WHEN target_tier is provided by the user
    THEN use that tier
    ELSE evaluate complexity_indicators to select tier

  RULE micro_criteria:
    WHEN behavior_count = 1 AND has_shared_types = false AND has_overlapping_rules = false
    THEN select micro tier

  RULE standard_criteria:
    WHEN behavior_count > 1 AND has_overlapping_rules = false
    THEN select standard tier

  RULE complex_criteria:
    WHEN has_overlapping_rules = true OR has_state = true
    THEN select complex tier

  RULE promote_on_growth:
    WHEN writing reveals a second BEHAVIOR block in a micro spec
    THEN promote to standard tier
    ELSE WHEN writing reveals overlapping conditions across behaviors in a standard spec
    THEN promote to complex tier

  RULE demote_after_refactoring:
    WHEN a complex spec has only one behavior after refactoring
    THEN demote to micro tier

  ERROR no_tier_determinable:
    WHEN target_tier is not provided AND complexity_indicators are insufficient to select a tier
    SEVERITY warning
    ACTION default to standard tier and note the assumption
    MESSAGE "Insufficient complexity signals. Defaulting to standard tier."

  EXAMPLE single_concern:
    INPUT: { "behavior_count": 1, "has_shared_types": false, "has_overlapping_rules": false }
    EXPECTED: { "tier": "micro" }
    NOTES: One behavior, no shared types — micro is correct

  EXAMPLE multi_behavior_shared_types:
    INPUT: { "behavior_count": 3, "has_shared_types": true, "has_overlapping_rules": false }
    EXPECTED: { "tier": "standard" }
    NOTES: Multiple behaviors sharing types — standard tier

  EXAMPLE overlapping_rules:
    INPUT: { "behavior_count": 4, "has_overlapping_rules": true }
    EXPECTED: { "tier": "complex" }
    NOTES: Overlapping conditions require PRECEDENCE — complex tier

  EXAMPLE explicit_override_honored:
    INPUT: { "target_tier": "micro", "behavior_count": 3 }
    EXPECTED: { "tier": "micro" }
    NOTES: User override takes precedence over complexity signals


BEHAVIOR structure_document: Assemble the specification with correct section ordering and required sections per tier

  RULE section_order:
    sections MUST appear in this order:
    Meta, Purpose, Scope, Inputs, Outputs, Types, Functions,
    Behaviors, Precedence, Constraints, Dependencies, Changelog

  RULE micro_sections:
    WHEN tier = micro
    THEN include Meta, Purpose, Behaviors
    AND  Constraints is optional
    AND  all other sections MUST be omitted

  RULE standard_sections:
    WHEN tier = standard
    THEN include Meta, Purpose, Scope, Inputs, Outputs, Types,
         Functions, Behaviors, Constraints, Dependencies
    AND  Changelog is optional

  RULE complex_sections:
    WHEN tier = complex
    THEN include all standard sections plus Precedence
    AND  behaviors MAY include State/Flow and Audience notes subsections

  RULE meta_fields:
    Meta MUST contain:
    Version (semver), Date (YYYY-MM-DD), Domain,
    Status (draft|active|deprecated), Tier

  RULE empty_section_stubs:
    WHEN a required section has no content (e.g., no shared types exist)
    THEN use a `-- none` stub with a brief reason
    -- example: "Types\n-- none: all data structures are inline within behavior rules"

  RULE purpose_length:
    Purpose MUST be 1-3 sentences describing what the spec accomplishes

  RULE scope_format:
    Scope MUST contain IN SCOPE and OUT OF SCOPE subsections

  ERROR missing_required_section:
    WHEN a required section for the selected tier is absent
    SEVERITY critical
    ACTION add the missing section
    MESSAGE "Missing required section: <section_name> for <tier> tier"

  EXAMPLE standard_structure:
    INPUT: { "tier": "standard", "sections_present": ["Meta", "Purpose", "Scope", "Inputs", "Outputs", "Types", "Functions", "Behaviors", "Constraints", "Dependencies"] }
    EXPECTED: { "valid": true }
    NOTES: All 10 required standard sections present

  EXAMPLE micro_with_extras:
    INPUT: { "tier": "micro", "sections_present": ["Meta", "Purpose", "Behaviors", "Inputs", "Types"] }
    EXPECTED: { "valid": false, "error": "Micro tier MUST NOT include Inputs or Types sections" }


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

  ERROR vague_rule:
    WHEN a rule uses vague language like "handle appropriately" or "validate the data"
    SEVERITY critical
    ACTION rewrite the rule with specific conditions and actions
    MESSAGE "Rule '<rule_name>' is too vague. Specify each case explicitly."

  ERROR missing_error_block:
    WHEN a behavior has rules that can fail but no ERROR blocks
    SEVERITY warning
    ACTION add ERROR blocks for each failure mode
    MESSAGE "Behavior '<behavior_name>' has rules but no error handling."

  EXAMPLE well_structured_behavior:
    INPUT: { "behavior": "validate_payment", "rules": 3, "errors": 2, "examples": 4 }
    EXPECTED: { "valid": true }
    NOTES: Rules, errors, and examples grouped together — self-contained

  EXAMPLE vague_rule_detected:
    INPUT: { "rule_text": "Handle errors appropriately" }
    EXPECTED: { "valid": false, "error": "Rule is too vague" }
    NOTES: Must specify each error case explicitly


BEHAVIOR write_procedures: Compose PROCEDURE blocks with ordered steps written in natural English

  RULE procedure_naming:
    procedure names MUST use snake_case and describe the workflow, not the implementation
    -- "onboard_new_customer" not "step_sequence_1"; "generate_monthly_report" not "report_proc"

  RULE step_ordering:
    each STEP MUST have what it needs from prior steps
    -- a step that uses a result MUST come after the step that produces it
    AND steps MUST be ordered so a reader CAN follow the workflow top to bottom without jumping ahead

  RULE natural_english_phrasing:
    steps MUST be written in natural English, not programming syntax
    -- "Look up the customer record by email" not "SET customer = db.query(email)"
    -- "For each item in the order" not "FOR i = 0 TO items.length"
    -- "If the payment succeeds" not "IF result == SUCCESS THEN"
    AND steps SHOULD read as instructions a non-programmer CAN follow

  RULE side_effect_placement:
    side effects (sending emails, writing files, updating databases) belong in PROCEDURE STEPs or ACTION blocks
    AND side effects MUST NOT appear in FUNCTION bodies
    -- FUNCTIONs are pure: inputs in, outputs out, no side effects

  RULE error_recovery_pattern:
    WHEN a step CAN fail
    THEN use the pattern: "Attempt to <action>. If it fails, <recovery>."
    -- "Attempt to charge the card. If it fails, notify the customer and pause the order."

  RULE state_transitions:
    WHEN a step changes the state of an entity
    THEN use the pattern: "Move <entity> from <old_state> to <new_state>"
    -- "Move the order from pending to confirmed"

  ERROR programming_syntax_detected:
    WHEN a step uses programming-style syntax (SET, FOR i=0, END IF, RETURN, assignment operators)
    SEVERITY critical
    ACTION rewrite the step in natural English
    MESSAGE "Step '<step_name>' uses programming syntax. Rewrite in natural English."

  ERROR steps_out_of_order:
    WHEN a step references a result that has not been produced by a prior step
    SEVERITY critical
    ACTION reorder steps so each step has what it needs from prior steps
    MESSAGE "Step '<step_name>' references '<dependency>' which has not been produced yet."

  EXAMPLE well_ordered_procedure:
    INPUT: { "procedure": "process_refund", "steps": ["Look up the original transaction by order ID", "Calculate the refund amount based on the return policy", "Attempt to credit the customer account. If it fails, escalate to finance.", "Move the order from active to refunded", "Send a confirmation email to the customer"] }
    EXPECTED: { "valid": true }
    NOTES: Each step builds on the previous -- lookup, calculate, act, transition, notify

  EXAMPLE programming_syntax_rejected:
    INPUT: { "step_text": "SET total = SUM(line_items) * (1 + tax_rate)" }
    EXPECTED: { "valid": false, "error": "Uses programming syntax" }
    NOTES: Should be "Calculate the total by summing all line items and adding the applicable tax"

  EXAMPLE natural_english_accepted:
    INPUT: { "step_text": "For each line item in the invoice, verify that the quantity matches the shipment record" }
    EXPECTED: { "valid": true }
    NOTES: Natural English iteration -- no index variables or loop syntax


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

  ERROR orphan_type:
    WHEN a Type is defined but no BEHAVIOR references it
    SEVERITY warning
    ACTION remove the type or add a reference in a behavior rule
    MESSAGE "Type '<type_name>' is defined but never referenced by any behavior."

  ERROR orphan_function:
    WHEN a Function is defined but no BEHAVIOR or PROCEDURE references it
    SEVERITY warning
    ACTION remove the function or add a reference in a behavior or procedure
    MESSAGE "Function '<function_name>' is defined but never referenced by any behavior or procedure."

  ERROR orphan_action:
    WHEN an ACTION is defined but no BEHAVIOR or PROCEDURE references it
    SEVERITY warning
    ACTION remove the action or add a reference in a behavior or procedure
    MESSAGE "ACTION '<action_name>' is defined but never referenced by any behavior or procedure."

  EXAMPLE shared_type_correct:
    INPUT: { "type": "Order", "referenced_by": ["validate_order", "process_order"] }
    EXPECTED: { "placement": "Types section", "valid": true }
    NOTES: Used by two behaviors — belongs in shared Types section

  EXAMPLE single_use_type:
    INPUT: { "type": "TempResult", "referenced_by": ["calculate_total"] }
    EXPECTED: { "placement": "inline within calculate_total behavior" }
    NOTES: Only one behavior uses it — inline rather than promote to shared Types


BEHAVIOR ensure_quality: Validate the completed specification against SESF standards

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
    micro specs SHOULD stay within 20-40 lines
    AND standard specs SHOULD stay within 100-300 lines
    AND complex specs SHOULD stay within 300-600 lines
    -- PROCEDURE blocks count the same as BEHAVIOR blocks for line budgeting

  RULE keyword_capitalization:
    requirement keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY, CAN)
    MUST be capitalized when used with their RFC 2119 meanings
    -- CAN indicates ability or permission in natural-English phrasing

  RULE run_validator:
    WHEN specification is complete
    THEN run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/scripts/validate_sesf.py <spec.md>`
         and fix all failures
    -- the SESF v3 validator checks BEHAVIOR blocks, PROCEDURE blocks, ACTION declarations, and section structure
    -- warnings are acceptable when example count < rule count in some behaviors

  RULE yaml_frontmatter:
    WHEN the specification is a Claude Code skill
    THEN it MUST include YAML frontmatter with `name` and `description` fields
         before the title

  ERROR validation_failure:
    WHEN validator reports failures > 0
    SEVERITY critical
    ACTION fix the structural issues identified by the validator
    MESSAGE "Specification has <n> validation failures. Fix before delivery."

  ERROR over_budget:
    WHEN line count exceeds the tier's target range by more than 20%
    SEVERITY warning
    ACTION review for redundancy, extract reference material, consolidate related rules
    MESSAGE "Specification is <n> lines, exceeding the <tier> tier target of <range>."

  EXAMPLE clean_validation:
    INPUT: { "validator_output": { "failures": 0, "warnings": 2 } }
    EXPECTED: { "passed": true }
    NOTES: Zero failures — warnings about example count are acceptable

  EXAMPLE bloated_spec:
    INPUT: { "tier": "standard", "line_count": 380 }
    EXPECTED: { "warning": "over_budget", "action": "review for redundancy and extract reference material" }
    NOTES: Standard tier target is 100-300 lines; 380 exceeds by 27%

Constraints
* Clarity over brevity: explicit is better than clever
* One idea per statement: break complex rules into simple parts
* Concrete over abstract: use examples, not just descriptions
* Consistent structure: same format across all specs
* Behavior-centric: group rules, errors, and examples by behavior, not by type
* Tight over bloated: say each thing once, in the right place -- completeness does not mean repetition
* specifications MUST pass `python3 ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/scripts/validate_sesf.py` with zero failures before delivery
* YAML frontmatter (name + description) is required for Claude Code skills

Dependencies
* Template: `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/template.md` -- fill-in-the-blank templates for all three tiers
* Examples: `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/references/examples.md` -- one complete example per tier
* Reference: `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/reference.md` -- syntax examples, keyword definitions, anti-patterns, completeness checklist
* Validator: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/scripts/validate_sesf.py <spec.md>` -- structural validation

## Reference

See `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/reference.md` for keyword definitions, syntax examples, anti-patterns, and the completeness checklist.
