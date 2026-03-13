---
description: Upgrade an existing specification to the latest format version (HSF v5)
argument-hint: <path to spec file>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Upgrade a Specification to HSF v5

Detect the format version of an existing specification and migrate it to Hybrid Specification Format v5, preserving all domain logic while upgrading notation, structure, and hybrid elements.

## Workflow

### Step 1: Load the Skill

Use the `structured-english` skill — it contains all the rules, formats, and validation requirements for HSF v5 specifications. Read it fully before proceeding. Also read the reference at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/reference.md`.

### Step 2: Read and Detect Version

If the user provided a file path in the arguments, read it. Otherwise, ask the user:

- "Which specification file should I upgrade?"

Read the full file content, then detect the format version using structural signals:

| Signal | Inferred Format |
|--------|-----------------|
| Has `**BEHAVIOR**`, `**PROCEDURE**`, `### Meta`, `### Notation` keywords | SESF v4 |
| Has `@route` or `@config` or `## Instructions` prose sections, no BEHAVIOR/PROCEDURE | Already HSF v5 |
| Has BEHAVIOR blocks only, no PROCEDURE/ACTION blocks, no hybrid notation | SESF v1/v2/v3 |
| No BEHAVIOR, PROCEDURE, or `## Instructions` sections found | Not a spec |

**If already HSF v5**: Report that the specification is already at the latest format version and stop.

**If not a spec**: Suggest using `/write-spec` to create a new specification or `/assess-doc` to evaluate whether HSF is a good fit, then stop.

Also detect the tier from context or infer it:

- **Micro**: Single concern, ≤80 lines
- **Standard**: Multiple concerns, ≤200 lines
- **Complex**: Many concerns, complex interactions, ≤400 lines

### Step 2.5: Determine Output Mode

Before analyzing gaps, detect whether the file is a self-contained executable (Claude Code command or skill) or a standalone specification document.

**Detection heuristic**: If the file has YAML frontmatter containing `allowed-tools` or `argument-hint`, it is a Claude Code command or skill — default-suggest "Self-contained" as the recommended option.

Use `AskUserQuestion` to ask:

"How should this specification be structured after the upgrade?"

With these options:

1. **Self-contained** (spec + executable in one file) — The document serves as both the specification and the executable command/skill. The agent prompt, examples, and all operational content stay inline. Only the format is upgraded. This is the correct choice when the file is a Claude Code command or skill that directly executes its own instructions. *(Recommended if the file has `allowed-tools` or `argument-hint` frontmatter)*
2. **Split into spec + executable** — Create a pure HSF v5 specification document (declarative, non-executable — defines rules and structure) and a separate executable document (the agent prompt, procedures, operational instructions). This is the correct choice when you want a clean separation between "what the system does" (spec) and "how to run it" (executable).

Store the user's choice as `$output_mode` ("self-contained" or "split") for use in Step 5.

### Step 3: Analyze Gaps

Compare the specification against HSF v5 requirements. Build two lists:

**Format migrations** (auto-apply without user approval):

When upgrading from SESF v4 → HSF v5:

1. **Delete** Meta, Notation, Types (unless types are genuinely complex), Functions, Precedence, Dependencies, Changelog sections
2. **Convert** each `**BEHAVIOR**` block:
   - Extract the rules into prose bullets under a `## Rules` section (or inline them into the relevant instruction phase)
   - Move inline ERROR declarations to the consolidated error table
   - Keep any @route tables — lift them out of the BEHAVIOR and place them in a `## Routing Logic` section or inline in Instructions
3. **Convert** each `**PROCEDURE**` block:
   - Rewrite as prose under `## Instructions` with `###` phase headers
   - Drop `**STEP**` and `→ $variable` syntax unless data flow is genuinely complex
   - Inline applicable rules from BEHAVIOR blocks directly into the phase where they apply
   - Eliminate duplicate constraint statements
4. **Consolidate** errors into a single `## Errors` table at the end
5. **Preserve** @config blocks, @route tables, worked examples, and RFC 2119 keywords
6. **Move** version to YAML frontmatter, remove inline version references

**v5 opportunity suggestions** (require user approval):

- **@config candidates**: Repeated literal values appearing in 2+ rules that could be centralized
- **@route candidates**: Conditional logic with 3+ branches that could use compact routing tables
- **$variable threading candidates**: Implicit result passing between phases where naming intermediate values would improve clarity
- **Rule inlining candidates**: Rules that apply to only one phase and could be moved inline

### Step 4: Present Migration Report

Show a report with:

- **Detected format**: The inferred version
- **Target format**: HSF v5
- **Format migrations**: List of automatic changes that will be applied
- **Suggestions**: List of optional enhancements with brief rationale for each

Use `AskUserQuestion` to ask the user how to proceed, with these options:

- "Migrate format only"
- "Migrate format + all suggestions"
- "Migrate format + selected suggestions"
- "Cancel"

If the user selects "selected suggestions", ask which suggestions to include.

### Step 5: Rewrite the Specification

Using the skill's HSF v5 rules, rewrite the specification:

1. Read the template at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/template.md`
2. Read the examples at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/references/examples.md` for reference
3. Apply all format migrations
4. Apply the user-approved suggestions (if any)

**Apply output mode** based on `$output_mode`:

- **self-contained**: Convert the existing content into HSF v5 prose format — markdown headers and bold list items replace BEHAVIOR/PROCEDURE blocks. Do NOT create a meta-specification layer on top of the existing prose. Do NOT produce formal blocks alongside original content. The result must be one layer: prose instructions with structured notation where it adds value, no parallel formal blocks.
- **split**: Extract operational content (agent prompt templates, code blocks, worked examples) into companion files. Have the main spec reference them. The main spec becomes a pure declarative HSF v5 document.

**Examples must be edge cases only**: Write or preserve only examples that demonstrate boundary conditions, error paths, or non-obvious behavior.

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
