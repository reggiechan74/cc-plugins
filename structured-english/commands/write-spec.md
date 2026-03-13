---
description: Write a specification using Hybrid Specification Format (HSF v5)
argument-hint: <domain or topic to specify>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Write a Hybrid Specification

Generate a complete HSF v5 specification from a user request. HSF v5 uses prose instructions with markdown headers, @route tables for multi-branch decisions, @config for centralized parameters, $variable threading for complex data flows, and consolidated error tables.

## Workflow

### Step 1: Load the Skill

Use the `structured-english` skill — it contains all the rules, formats, and validation requirements for HSF v5 specifications. Read it fully before proceeding. Also read the reference at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/reference.md`.

### Step 2: Gather Requirements

Always ask all three questions, even if the user provided a domain/topic in the arguments (use it as a starting point but confirm):

1. **Domain**: "What system or process should this specification define?"
2. **Nature**: "Is this primarily rules (conditions that produce different outcomes), a step-by-step workflow (do this, then this), or a mix of both?"
3. **Complexity**: "How many distinct concerns does this involve?" (helps determine tier)

### Step 3: Select Tier

Based on the requirements, select the appropriate tier:

- **Micro** (20-80 lines): Single concern, ≤5 rules. Configuration + prose instructions. No formal blocks needed.
- **Standard** (80-200 lines): Multiple concerns. Configuration + @route tables + prose rules + prose procedures. Named errors as table.
- **Complex** (200-400 lines): Many concerns with complex interactions. Everything in Standard, plus @config, $variable threading, worked examples, system dynamics sections.

Also determine which notation elements will be used:
- **@config** — only if 3+ configurable parameters
- **@route** — only if 3+ branch decision logic
- **$variable threading** — only if complex data flow between phases
- **Worked examples** — only if chain integrity matters

Present the plan to the user before writing:
- Tier (micro/standard/complex)
- Estimated line count
- Which notation elements will be used
- Section outline

### Step 4: Write the Specification

1. Read the template at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/template.md`
2. Read the examples at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/references/examples.md` for the selected tier
3. Follow the HSF v5 skill rules exactly:
   - Use prose instructions with markdown headers, NOT BEHAVIOR/PROCEDURE blocks
   - Include @route tables only for 3+ branch logic
   - Include @config only for 3+ configuration values
   - Consolidate errors into a single table at the end
   - State rules inline where they apply, with a cross-cutting Rules section only for rules that span all phases
   - Edge-case examples only — no happy-path examples
   - NO empty sections (do not stub "none")
4. Use concrete values in all examples — never placeholders
5. Use natural English throughout — every line should read as an instruction to a competent assistant

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
