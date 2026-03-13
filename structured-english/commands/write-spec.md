---
description: Write a specification or procedural pseudocode using Structured English Specification Format (SESF v4)
argument-hint: <domain or topic to specify>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Write a Structured English Specification

Generate a complete SESF v4 specification from a user request. SESF v4 supports both declarative rules (BEHAVIOR blocks) and step-by-step workflows (PROCEDURE blocks), with hybrid elements for configuration, routing, variable threading, and compact notation.

## Workflow

### Step 1: Load the Skill

Use the `structured-english` skill — it contains all the rules, formats, and validation requirements for SESF v4 specifications. Read it fully before proceeding. Also read the reference at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/reference.md`.

### Step 2: Gather Requirements

Always ask all three questions, even if the user provided a domain/topic in the arguments (use it as a starting point but confirm):

1. **Domain**: "What system or process should this specification define?"
2. **Nature**: "Is this primarily declarative rules (conditions that produce different outcomes) or a step-by-step workflow (do this, then this), or a mix of both?"
3. **Complexity**: "How many distinct concerns does this involve?" (helps determine tier)

### Step 3: Select Tier and Block Types

Based on the requirements, select the appropriate SESF tier:

- **Micro**: Single BEHAVIOR or single PROCEDURE containing 1-2 rules/steps within it, 20-40 lines
- **Standard**: Multiple BEHAVIORs and/or PROCEDUREs sharing types, 100-300 lines. Requires a Notation section defining any symbols used.
- **Complex**: Overlapping rules, state machines, mixed declarative+procedural, 300-600 lines. Requires a Notation section defining any symbols used.

Choose block types based on the nature of each concern:

- **BEHAVIOR** — for declarative rules where conditions produce different outcomes (validation, classification, routing)
- **PROCEDURE** — for ordered steps with decisions, loops, or side effects (workflows, pipelines, onboarding). Use `$variable` threading to pass intermediate results between steps.
- **FUNCTION** — for pure calculations (no side effects)
- **ACTION** — for reusable operations with side effects (sending emails, writing files, calling APIs)

Also consider hybrid elements that reduce boilerplate:

- **@config** — use for centralized parameters (thresholds, limits, feature flags) that are referenced across multiple blocks, rather than scattering magic values throughout rules
- **@route** — use for conditionals with 3 or more branches as a compact alternative to deeply nested IF/ELSE IF chains
- **$variable threading** — use in PROCEDURE steps to name intermediate results and pass them to subsequent steps (e.g., `$validated_input`, `$api_response`)
- **Compact ERRORS** — default to `| Condition | Severity | Message |` table format for error definitions within blocks
- **Compact EXAMPLES** — default to `| Input | Expected | Why |` table format for examples within blocks

A spec can use any combination of these. If unsure about tier, default to standard.

Present the selected tier and block types to the user for confirmation before proceeding to write the specification.

### Step 4: Write the Specification

1. Read the template at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/template.md`
2. Read the examples at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/references/examples.md` for the selected tier
3. Follow the SESF v4 skill rules exactly — group rules/steps, errors, and examples by concern
4. Use concrete values in all examples — never placeholders. Write edge cases only — boundary conditions, error paths, and non-obvious behavior. Do not write happy-path or obvious examples.
5. Use natural English throughout — every line should read like an instruction to a human assistant, not programming syntax

### Step 5: Review

Present the finished specification to the user for review before saving. Allow them to request changes before proceeding.

### Step 6: Validate

Run the structural validator:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/scripts/validate_sesf.py <output-file>
```

Show the validation results to the user. If there are failures, present each proposed fix and ask the user to approve before applying — especially when a fix would change something the user explicitly requested.

### Step 7: Save

Ask the user where to save the specification, or suggest a default based on the domain name (e.g., `<domain>-spec.md`). If the target file already exists, ask the user whether to overwrite it or save to a different path.
