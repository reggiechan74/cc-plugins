---
description: Upgrade an existing SESF specification to the latest format version (v4)
argument-hint: <path to SESF spec file>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Upgrade a Specification to SESF v4

Detect the format version of an existing SESF specification and migrate it to SESF v4, preserving all domain logic while upgrading notation, structure, and hybrid elements.

## Workflow

### Step 1: Load the Skill

Use the `structured-english` skill — it contains all the rules, formats, and validation requirements for SESF v4 specifications. Read it fully before proceeding. Also read the reference at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/reference.md`.

### Step 2: Read and Detect Version

If the user provided a file path in the arguments, read it. Otherwise, ask the user:

- "Which SESF specification file should I upgrade?"

Read the full file content, then detect the SESF format version using structural signals:

| Signal | Inferred Format |
|--------|-----------------|
| Has `@config`, `@route`, or `$variable` threading (`$`-prefixed variables in STEP declarations) | Already v4 |
| Has PROCEDURE or ACTION blocks, but no `@config`/`@route`/`$variable` threading | v3 |
| Has BEHAVIOR blocks only, no PROCEDURE/ACTION blocks, no hybrid notation | v1/v2 |
| No BEHAVIOR or PROCEDURE blocks found | Not an SESF spec |

**If already v4**: Report that the specification is already at the latest format version and stop.

**If not an SESF spec**: Suggest using `/write-spec` to create a new specification or `/assess-doc` to evaluate whether SESF is a good fit, then stop.

Also detect the tier from the Meta section or infer it:

- **Micro**: 1 block
- **Standard**: Multiple blocks
- **Complex**: Has PRECEDENCE, State, or Flow sections

### Step 3: Analyze Gaps

Compare the specification against v4 requirements. Build two lists:

**Format migrations** (auto-apply without user approval):

- Section ordering to match v4 template
- Verbose `ERROR` blocks → compact `ERRORS` tables (5 columns: name, when, severity, action, message)
- Verbose `EXAMPLE` blocks → compact table format
- Meta section `date` field update to today
- `-- none` stubs for any missing optional sections
- Notation section added for standard/complex tier specs

**v4 opportunity suggestions** (require user approval):

- **@config candidates**: Repeated literal values appearing in 2 or more rules (thresholds, limits, feature flags) that could be centralized
- **@route candidates**: Conditional logic with 3 or more branches in IF/ELSE IF chains that could use compact routing tables
- **$variable threading candidates**: Implicit result passing between PROCEDURE steps where naming intermediate values would improve clarity
- **PROCEDURE candidates** (for v1/v2 specs): Step-by-step logic written in prose within BEHAVIOR blocks that would be better expressed as PROCEDURE blocks

### Step 4: Present Migration Report

Show a report with:

- **Detected format**: The inferred version (v1/v2 or v3)
- **Target format**: v4
- **Format migrations**: List of automatic changes that will be applied
- **Suggestions**: List of optional v4 enhancements with brief rationale for each

Use `AskUserQuestion` to ask the user how to proceed, with these options:

- "Migrate format only"
- "Migrate format + all suggestions"
- "Migrate format + selected suggestions"
- "Cancel"

If the user selects "selected suggestions", ask which suggestions to include.

### Step 5: Rewrite the Specification

Using the skill's v4 rules, rewrite the specification:

1. Read the template at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/template.md`
2. Read the examples at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/references/examples.md` for reference
3. Apply all format migrations
4. Apply the user-approved suggestions (if any)

**CRITICAL**: Preserve ALL domain logic exactly as written. Only change format and notation. Do not add, remove, or alter any business rules, conditions, steps, or outcomes.

### Step 6: Validate and Save

Run the structural validator:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/scripts/validate_sesf.py <output-file>
```

Fix any failures and re-validate until the specification passes.

Overwrite the original file with the upgraded specification.

Report a result summary:

- Original format version
- Changes applied (format migrations and accepted suggestions)
- Validation result
