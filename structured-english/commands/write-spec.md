---
description: Write a specification using Structured English Specification Format (SESF)
argument-hint: <domain or topic to specify>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Write a Structured English Specification

Generate a complete SESF v2 specification from a user request.

## Workflow

### Step 1: Load the Skill

Use the `structured-english` skill — it contains all the rules, formats, and validation requirements for SESF v2 specifications. Read it fully before proceeding.

### Step 2: Gather Requirements

If the user provided a domain/topic in the arguments, use that. Otherwise, ask:

1. **Domain**: "What system or process should this specification define?"
2. **Complexity**: "How many distinct behaviors or concerns does this involve?" (helps determine tier)

### Step 3: Select Tier

Based on the requirements, select the appropriate SESF tier:

- **Micro**: Single behavior, 1-2 rules, 20-40 lines
- **Standard**: Multiple behaviors sharing types, 100-300 lines
- **Complex**: Interacting behaviors with overlapping rules or state, 300-600 lines

If unsure, default to standard.

### Step 4: Write the Specification

1. Read the template at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/template.md`
2. Read the examples at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/references/examples.md` for the selected tier
3. Follow the SESF v2 skill rules exactly — behavior-centric format with rules, errors, and examples grouped by behavior
4. Use concrete values in all examples — never placeholders

### Step 5: Validate

Run the structural validator:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/scripts/validate_sesf.py <output-file>
```

Fix any failures. Warnings about example count are acceptable.

### Step 6: Save

Ask the user where to save the specification, or use a sensible default based on the domain name (e.g., `<domain>-spec.md`).
