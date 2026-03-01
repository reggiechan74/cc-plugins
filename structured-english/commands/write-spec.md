---
description: Write a specification or procedural pseudocode using Structured English Specification Format (SESF v3)
argument-hint: <domain or topic to specify>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Write a Structured English Specification

Generate a complete SESF v3 specification from a user request. SESF v3 supports both declarative rules (BEHAVIOR blocks) and step-by-step workflows (PROCEDURE blocks).

## Workflow

### Step 1: Load the Skill

Use the `structured-english` skill — it contains all the rules, formats, and validation requirements for SESF v3 specifications. Read it fully before proceeding.

### Step 2: Gather Requirements

If the user provided a domain/topic in the arguments, use that. Otherwise, ask:

1. **Domain**: "What system or process should this specification define?"
2. **Nature**: "Is this primarily declarative rules (conditions that produce different outcomes) or a step-by-step workflow (do this, then this), or a mix of both?"
3. **Complexity**: "How many distinct concerns does this involve?" (helps determine tier)

### Step 3: Select Tier and Block Types

Based on the requirements, select the appropriate SESF tier:

- **Micro**: Single BEHAVIOR or single PROCEDURE, 1-2 rules/steps, 20-40 lines
- **Standard**: Multiple BEHAVIORs and/or PROCEDUREs sharing types, 100-300 lines
- **Complex**: Overlapping rules, state machines, mixed declarative+procedural, 300-600 lines

Choose block types based on the nature of each concern:

- **BEHAVIOR** — for declarative rules where conditions produce different outcomes (validation, classification, routing)
- **PROCEDURE** — for ordered steps with decisions, loops, or side effects (workflows, pipelines, onboarding)
- **FUNCTION** — for pure calculations (no side effects)
- **ACTION** — for reusable operations with side effects (sending emails, writing files, calling APIs)

A spec can use any combination of these. If unsure about tier, default to standard.

### Step 4: Write the Specification

1. Read the template at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/template.md`
2. Read the examples at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/references/examples.md` for the selected tier
3. Follow the SESF v3 skill rules exactly — group rules/steps, errors, and examples by concern
4. Use concrete values in all examples — never placeholders
5. Use natural English throughout — every line should read like an instruction to a human assistant, not programming syntax

### Step 5: Validate

Run the structural validator:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/scripts/validate_sesf.py <output-file>
```

Fix any failures. Warnings about example count are acceptable.

### Step 6: Save

Ask the user where to save the specification, or use a sensible default based on the domain name (e.g., `<domain>-spec.md`).
