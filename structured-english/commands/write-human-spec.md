---
description: Write a human-readable specification using SESF v4.1 formal blocks
argument-hint: <domain or topic to specify>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Write a Human-Facing Specification

Generate a complete SESF v4.1 specification optimized for human readers and maintainers. The output uses formal BEHAVIOR/PROCEDURE/RULE/STEP blocks that provide visual scaffolding humans can scan, review, and modify. Includes rationale annotations explaining *why* rules exist.

## Audience

The primary reader of this spec is a human — an engineer, product manager, or domain expert who needs to understand, review, or modify the spec. Optimize for:

- **Comprehension** — formal blocks categorize concerns visually; rationale annotations explain the *why*
- **Scannability** — BEHAVIOR/PROCEDURE blocks create chapters; WHEN/THEN creates alignment points the eye locks onto
- **Maintainability** — explicit structure makes it obvious where to add, modify, or remove rules

## Workflow

### Step 1: Load the Skill and Authoring Guide

Use the `sesf` skill — it contains all the rules, formats, and validation requirements for SESF v4.1. Read it fully before proceeding. Also read:

- The format reference at `${CLAUDE_PLUGIN_ROOT}/skills/sesf/assets/reference.md`
- The authoring guide at `${CLAUDE_PLUGIN_ROOT}/skills/sesf/assets/authoring-guide.md` — this walks through the thinking process

### Step 2: Gather Requirements

Walk the user through the thinking process from the authoring guide:

1. **Domain**: "What system or process should this specification define?"
2. **Behaviors**: "What are the rules? What conditions produce different outcomes?" (These become `**BEHAVIOR**` blocks)
3. **Procedures**: "What are the ordered steps? What's the overall workflow?" (These become `**PROCEDURE**` blocks)
4. **Decision points**: "Where does the logic branch? How many branches per decision?" (2 branches → WHEN/THEN, 3+ → @route)
5. **Complexity**: "How many distinct concerns does this involve?" (helps determine tier)

### Step 3: Select Tier

Based on the requirements, select the appropriate tier:

- **Micro** (20-80 lines): Single concern, ≤5 rules. Single PROCEDURE block with STEPs.
- **Standard** (80-200 lines): Multiple concerns. BEHAVIOR blocks + PROCEDURE blocks + @route tables.
- **Complex** (200-400 lines): Many concerns with interactions. Multiple BEHAVIORs and PROCEDUREs, $variable threading, @config.

Present the plan to the user before writing:
- Tier (micro/standard/complex)
- Which concerns map to BEHAVIOR blocks
- Which workflows map to PROCEDURE blocks
- Which decision points will use @route tables vs WHEN/THEN
- Section outline

### Step 4: Write the Specification

1. Read the template at `${CLAUDE_PLUGIN_ROOT}/skills/sesf/assets/template.md`
2. Read the examples at `${CLAUDE_PLUGIN_ROOT}/skills/sesf/references/examples.md` for the selected tier
3. Follow the SESF v4.1 skill rules:
   - Wrap related rules in `**BEHAVIOR** name: description` blocks
   - Use `**RULE** name:` with `WHEN condition THEN action` syntax inside behaviors
   - Wrap ordered workflows in `**PROCEDURE** name: description` blocks
   - Use `**STEP** name: description` with optional `→ $variable` for data flow
   - Add rationale annotations (parenthetical) after non-obvious rules
   - Consolidate errors into a single `## Errors` table at the end
   - @route tables for 3+ branch decisions only
   - @config for 3+ configuration values only
   - Edge-case examples only — no happy-path examples
   - NO empty sections
4. Use concrete values in all examples — never placeholders
5. Include rationale for thresholds and non-obvious rules

### Step 5: Review

Present the finished specification to the user for review. Highlight design decisions (e.g., "I separated validation into its own BEHAVIOR block because those rules apply across multiple procedures").

### Step 6: Validate

Run the structural validator:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sesf/scripts/validate_sesf.py <output-file>
```

Show the validation results to the user. If there are failures, present each proposed fix and ask the user to approve before applying.

### Step 7: Save

Ask the user where to save the specification, or suggest a default based on the domain name (e.g., `<domain>-spec.md`). If the target file already exists, ask the user whether to overwrite it or save to a different path.
