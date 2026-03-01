---
description: Write a specification using Structured English Specification Format (SESF)
argument-hint: <domain or topic to specify>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Write Specification Command

Meta
* Version: 1.0.0
* Date: 2026-03-01
* Domain: Specification Authoring
* Status: active
* Tier: standard

Purpose
Guide the creation of a complete SESF v2 specification from a user request. Collect requirements, select the correct tier, write the specification following SESF v2 rules, validate it, and save the output file.

Scope
* IN SCOPE: requirements gathering, tier selection, specification authoring, structural validation, file output
* OUT OF SCOPE: executing the generated specification, providing domain expertise, modifying the validator script

Inputs
* command_arguments: string - domain or topic provided after `/write-spec` - optional
* user_request: string - what the user wants specified, gathered interactively if not in arguments - required

Outputs
* specification_file: file - the complete SESF v2 specification saved to disk
* validation_result: string - output from the structural validator confirming zero failures

Types
-- none: all data is passed as simple strings; resource paths are listed in Dependencies

Functions
-- none: all logic is expressed directly in behavior rules

Behaviors

BEHAVIOR gather_requirements: Collect domain, scope, and complexity signals from the user

  RULE use_arguments_first:
    WHEN command_arguments is not empty
    THEN treat command_arguments as the domain/topic
    ELSE ask the user: "What system or process should this specification define?"

  RULE load_skill:
    Read `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/SKILL.md` before proceeding
    -- the skill contains all SESF v2 authoring rules; follow them exactly

  RULE probe_complexity:
    WHEN domain is known
    THEN ask the user: "How many distinct behaviors or concerns does this involve? (1 = micro, 2-5 = standard, 5+ with overlapping rules = complex)"
    -- if the user says "you decide" or is unsure, infer from the domain description

  RULE confirm_scope:
    WHEN domain and complexity are known
    THEN summarize the planned specification (domain, estimated tier, key behaviors) and ask: "Does this look right, or should I adjust anything?"

  ERROR no_domain:
    WHEN command_arguments is empty AND user does not provide a domain after being asked
    SEVERITY critical
    ACTION ask again with a concrete prompt: "I need a topic to write a spec for. For example: 'email classification agent' or 'invoice validation rules'."
    MESSAGE "Cannot proceed without a domain or topic."

  EXAMPLE domain_from_arguments:
    INPUT: { "command_arguments": "payment webhook handler" }
    EXPECTED: { "domain": "payment webhook handler", "next": "probe_complexity" }
    NOTES: Domain extracted directly from arguments — no need to ask

  EXAMPLE domain_from_conversation:
    INPUT: { "command_arguments": "" }
    EXPECTED: { "action": "ask user for domain" }
    NOTES: No arguments provided — must ask interactively

BEHAVIOR select_tier: Determine the correct SESF tier based on gathered complexity signals

  RULE micro_selection:
    WHEN behavior_count = 1 AND no shared types AND no overlapping rules
    THEN select micro tier
    -- 20-40 lines, sections: Meta, Purpose, Behaviors, Constraints (optional)

  RULE standard_selection:
    WHEN behavior_count > 1 AND no overlapping rules
    THEN select standard tier
    -- 100-300 lines, sections: Meta, Purpose, Scope, Inputs, Outputs, Types, Functions, Behaviors, Constraints, Dependencies

  RULE complex_selection:
    WHEN overlapping rules exist OR system maintains state across invocations
    THEN select complex tier
    -- 300-600 lines, all standard sections plus Precedence

  RULE default_to_standard:
    WHEN complexity signals are ambiguous
    THEN default to standard tier and note the assumption to the user

  EXAMPLE single_validator:
    INPUT: { "domain": "email address validator", "behavior_count": 1 }
    EXPECTED: { "tier": "micro" }

  EXAMPLE multi_behavior_extraction:
    INPUT: { "domain": "lease abstraction from PDFs", "behavior_count": 5, "has_shared_types": true }
    EXPECTED: { "tier": "standard" }

  EXAMPLE stateful_workflow:
    INPUT: { "domain": "purchase order approval workflow", "has_state": true, "has_overlapping_rules": true }
    EXPECTED: { "tier": "complex" }

BEHAVIOR author_specification: Write the specification following SESF v2 format rules

  RULE load_template:
    Read the template at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/template.md`
    AND use the template matching the selected tier as the starting structure

  RULE study_examples:
    Read the examples at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/references/examples.md`
    AND study the example matching the selected tier for style, structure, and level of detail

  RULE follow_sesf_rules:
    Follow every rule in the `structured-english` skill exactly:
    -- behavior-centric grouping: rules, errors, and examples together per behavior
    -- snake_case behavior names describing the concern, not the implementation
    -- WHEN/THEN/ELSE for conditional rules; direct constraint syntax for unconditional rules
    -- ERROR blocks with WHEN, SEVERITY, ACTION, MESSAGE
    -- EXAMPLE blocks with concrete INPUT and EXPECTED values — never placeholders

  RULE section_completeness:
    WHEN tier = micro THEN include only Meta, Purpose, Behaviors, and optionally Constraints
    ELSE WHEN tier = standard THEN include Meta, Purpose, Scope, Inputs, Outputs, Types, Functions, Behaviors, Constraints, Dependencies
    ELSE WHEN tier = complex THEN include all standard sections plus Precedence

  RULE meta_fields:
    Meta MUST contain Version (1.0.0), Date (today's date), Domain, Status (draft), and Tier

  RULE empty_section_stubs:
    WHEN a required section has no content
    THEN use a `-- none` stub with a brief reason
    -- example: "Functions\n-- none: all logic is expressed directly in behavior rules"

  RULE no_vague_language:
    rules MUST NOT use phrases like "handle appropriately", "validate the data", "extract relevant fields"
    -- specify each case explicitly

  ERROR missing_section:
    WHEN a required section for the selected tier is absent from the draft
    SEVERITY critical
    ACTION add the missing section before proceeding to validation
    MESSAGE "Missing required section: <section_name> for <tier> tier."

  EXAMPLE standard_spec_authored:
    INPUT: { "domain": "invoice line item validation", "tier": "standard" }
    EXPECTED: { "sections": ["Meta", "Purpose", "Scope", "Inputs", "Outputs", "Types", "Functions", "Behaviors", "Constraints", "Dependencies"], "behaviors_have_rules_errors_examples": true }

BEHAVIOR validate_and_deliver: Run the structural validator, fix failures, and save the output file

  RULE write_to_temp_first:
    WHEN specification draft is complete
    THEN save it to a temporary file before running the validator
    -- allows the validator to read the file and report line numbers

  RULE run_validator:
    run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/scripts/validate_sesf.py <temp_file>`
    AND inspect the output for failures and warnings

  RULE fix_failures:
    WHEN validator reports failures > 0
    THEN fix each failure in the specification and re-run the validator
    AND repeat until failures = 0
    -- warnings about example count are acceptable; failures are not

  RULE ask_save_location:
    WHEN validation passes (failures = 0)
    THEN ask the user: "Where should I save this specification?"
    AND suggest a default path based on the domain name (e.g., `<domain-kebab-case>-spec.md`)

  RULE save_final:
    WHEN user confirms save location
    THEN write the specification to that path
    AND report the validation summary (passed count, warning count) and file path

  ERROR validator_unavailable:
    WHEN `python3` is not available OR the validator script cannot be found
    SEVERITY warning
    ACTION skip automated validation and note that manual review is needed
    MESSAGE "Validator unavailable. Specification written but not automatically validated."

  EXAMPLE clean_pass:
    INPUT: { "validator_output": "34 passed, 3 warnings, 0 failures" }
    EXPECTED: { "action": "ask save location", "passed": true }
    NOTES: Zero failures — proceed to save

  EXAMPLE failures_found:
    INPUT: { "validator_output": "28 passed, 2 warnings, 3 failures" }
    EXPECTED: { "action": "fix 3 failures and re-run validator" }
    NOTES: Must reach zero failures before saving

Constraints
* Follow the `structured-english` skill rules exactly — do not deviate from SESF v2 format
* Use concrete values in all EXAMPLE blocks — never use placeholders like `[value]`
* Present the specification to the user for review before final save
* MUST NOT save the file without running the validator first (unless validator is unavailable)

Dependencies
* Skill: `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/SKILL.md` -- full SESF v2 authoring rules
* Template: `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/template.md` -- tier-specific starting points
* Examples: `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/references/examples.md` -- complete working specs per tier
* Reference: `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/reference.md` -- syntax, keywords, anti-patterns, checklist
* Validator: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/scripts/validate_sesf.py <file>` -- structural validation
