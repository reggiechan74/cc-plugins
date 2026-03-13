---
description: Upgrade an older SESF specification to the current SESF v4.1 format
argument-hint: <path to spec file>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Upgrade a Specification to SESF v4.1

Detect the version of an existing SESF specification and migrate it to SESF v4.1. Preserves all domain logic while applying v4.1 improvements: consolidated error tables, removed boilerplate sections, and rationale annotations.

## Workflow

### Step 1: Load the Skill

Use the `sesf` skill — it contains all the rules, formats, and validation requirements for SESF v4.1. Read it fully before proceeding. Also read:

- The format reference at `${CLAUDE_PLUGIN_ROOT}/skills/sesf/assets/reference.md`
- The authoring guide at `${CLAUDE_PLUGIN_ROOT}/skills/sesf/assets/authoring-guide.md`

### Step 2: Read and Detect Version

If the user provided a file path in the arguments, read it. Otherwise, ask the user:

- "Which SESF specification file should I upgrade?"

Read the full file content, then detect the format version:

| Signal | Inferred Format |
|--------|-----------------|
| Has `**BEHAVIOR**`/`**PROCEDURE**` blocks AND `### Meta`, `### Notation`, inline `ERROR` declarations | SESF v4 (needs v4.1 upgrade) |
| Has `**BEHAVIOR**`/`**PROCEDURE**` blocks, consolidated `## Errors` table, no Meta/Notation sections | Already SESF v4.1 |
| Has BEHAVIOR blocks only, no PROCEDURE/ACTION blocks, no @route/@config | SESF v1/v2/v3 (needs full upgrade) |
| Has `## Instructions` prose, no BEHAVIOR/PROCEDURE blocks | HSF v5 — not a SESF spec. Suggest `/convert-human-to-llm` (wrong direction) or `/write-human-spec` to create a fresh SESF spec. Stop. |
| No BEHAVIOR, PROCEDURE, or Instructions sections | Not a spec. Suggest `/write-human-spec` or `/assess-human-doc`. Stop. |

**If already SESF v4.1**: Report that the spec is current and stop.

Also detect the tier from context.

### Step 2.5: Determine Output Mode

Detect whether the file is a self-contained executable (Claude Code command or skill) or a standalone specification.

Use `AskUserQuestion` to ask:

"How should this specification be structured after the upgrade?"

Options:

1. **Self-contained** (spec + executable in one file) *(Recommended if the file has `allowed-tools` or `argument-hint` frontmatter)*
2. **Split into spec + executable**

Store the user's choice as `$output_mode`.

### Step 3: Analyze Gaps

**When upgrading from SESF v4 → v4.1:**

1. **Consolidate errors** — gather all scattered inline `ERROR name: severity → action, "message"` declarations into a single `## Errors` table at the end
2. **Delete boilerplate sections** — remove Meta, Notation, Types, Functions, Precedence, Dependencies, Changelog sections
3. **Add rationale annotations** — for each non-obvious rule, add a parenthetical explaining *why* the rule exists
4. **Preserve** all BEHAVIOR/PROCEDURE/RULE/STEP blocks, @config, @route, examples, RFC 2119 keywords

**When upgrading from SESF v1/v2/v3 → v4.1:**

1. **Wrap rules in BEHAVIOR blocks** — if rules exist outside of `**BEHAVIOR**` wrappers, group related rules into named BEHAVIOR blocks
2. **Add WHEN/THEN syntax** — convert informal conditional rules to explicit `WHEN condition THEN action` format
3. **Wrap procedures in PROCEDURE blocks** — if ordered steps exist outside of `**PROCEDURE**` wrappers, group them into named PROCEDURE blocks with `**STEP**` entries
4. **Add → $variable declarations** — where data flows between steps and the flow is non-trivial, add explicit output variable declarations
5. **Consolidate errors** into a single `## Errors` table
6. **Delete boilerplate sections** (Meta, Notation, Types, etc.)
7. **Add rationale annotations** after non-obvious rules
8. **Add @route tables** where conditional logic has 3+ branches
9. **Add @config blocks** where 3+ configuration values exist

**Suggestions** (require user approval):

- **@config candidates**: Repeated literal values appearing in 2+ rules
- **@route candidates**: Conditional logic with 3+ branches currently in WHEN/THEN chains
- **BEHAVIOR split candidates**: Large blocks that mix unrelated concerns
- **Rationale candidates**: Rules where adding a *why* would help maintainability

### Step 4: Present Migration Report

Show:

- **Detected format**: The inferred version (v1/v2/v3 or v4)
- **Target format**: SESF v4.1
- **Migrations**: Automatic changes (error consolidation, section cleanup, block wrapping)
- **Rationale additions**: Rules that will get *why* annotations
- **Suggestions**: Optional enhancements

Use `AskUserQuestion`:

- "Migrate format only"
- "Migrate format + all suggestions"
- "Migrate format + selected suggestions"
- "Cancel"

### Step 5: Rewrite the Specification

1. Read the template at `${CLAUDE_PLUGIN_ROOT}/skills/sesf/assets/template.md`
2. Read the examples at `${CLAUDE_PLUGIN_ROOT}/skills/sesf/references/examples.md`
3. Apply all migrations and rationale additions
4. Apply user-approved suggestions

**Apply output mode** based on `$output_mode`:

- **self-contained**: Upgrade with formal blocks inline. No meta-specification layer.
- **split**: Extract operational content into companion files.

**CRITICAL**: Preserve ALL domain logic exactly. Only change format, consolidate errors, remove boilerplate, and add rationale.

### Step 6: Validate and Save

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sesf/scripts/validate_sesf.py <output-file>
```

Fix failures and re-validate. Overwrite the original file.

Report: original format version, changes applied, validation result.
