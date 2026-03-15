---
description: Upgrade an existing specification to LLM-optimized HSF v6 format
argument-hint: <path to spec file>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Upgrade a Specification to LLM-Facing HSF v6

Detect the format version of an existing specification and migrate it to HSF v6, optimized for LLM execution. Preserves all domain logic while upgrading notation and structure for maximum LLM compliance and token efficiency.

## Audience Context

The upgraded spec will be consumed by an LLM agent. Optimize the migration for:

- **Compliance** — clear, unambiguous instructions with RFC 2119 keywords
- **Token efficiency** — remove boilerplate sections, strip rationale that doesn't prevent misapplication
- **XML envelope** — use XML section tags for unambiguous structure that LLMs parse with near-perfect accuracy

## Workflow

### Step 1: Load the Skill

Use the `hsf` skill — it contains all the rules, formats, and validation requirements for HSF v6. Read it fully before proceeding. Also read the reference at `${CLAUDE_PLUGIN_ROOT}/skills/hsf/assets/reference.md`.

### Step 2: Read and Detect Version

If the user provided a file path in the arguments, read it. Otherwise, ask the user:

- "Which specification file should I upgrade?"

Read the full file content, then detect the format version:

| Signal | Inferred Format |
|--------|-----------------|
| Has `**BEHAVIOR**`, `**PROCEDURE**`, `**RULE**`, `**STEP**` keywords | SESF v4 / v4.1 |
| Has `@route` or `@config` or `## Instructions` prose, no BEHAVIOR/PROCEDURE and no XML section tags | HSF v5 (needs v6 upgrade) |
| Has XML section tags (`<purpose>`, `<instructions>`, `<config>`, `<errors>`) | Already HSF v6 |
| No BEHAVIOR, PROCEDURE, `## Instructions`, or XML section tags found | Not a spec |

**If already HSF v6**: Report that the specification is already at the latest LLM-facing format and stop.

**If HSF v5**: Proceed with migration to HSF v6. The main changes are: replace `##` section headers with XML tags, convert `@config` to `<config>` with JSON body, convert `@route` to `<route>` with `<case>` elements, change `$config.key` references to `config.key`.

**If not a spec**: Suggest using `/write-LLM-spec` to create a new specification or `/assess-LLM-doc` to evaluate suitability, then stop.

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

Compare the specification against HSF v6 requirements. Build two lists:

**Format migrations** (auto-apply):

When upgrading from SESF v4/v4.1 → HSF v6:

1. **Delete** Meta, Notation, Types, Functions, Precedence, Dependencies, Changelog sections
2. **Convert** each `**BEHAVIOR**` block:
   - Extract rules into prose bullets under `<rules>` or inline in the relevant instruction phase
   - Convert WHEN/THEN/ELSE to natural prose sentences with bold list items
   - Move inline ERROR declarations to the consolidated error table
   - Convert `@route` tables to `<route name="..." mode="...">` with `<case>` elements
3. **Convert** each `**PROCEDURE**` block:
   - Rewrite as prose under `<instructions>` with `###` phase headers
   - Drop `**STEP**` keywords; convert to numbered lists or phase headers
   - Drop `→ $variable` syntax unless data flow is genuinely complex
   - Inline applicable rules directly into the phase where they apply
4. **Strip rationale annotations** — remove parenthetical explanations unless the rationale prevents a common LLM misapplication
5. **Consolidate** errors into a single table inside `<errors>`
6. **Convert** `@config` blocks to `<config>` with JSON body (reference as `config.key`, not `$config.key`)
7. **Wrap** top-level sections in XML tags (`<purpose>`, `<scope>`, `<instructions>`, `<rules>`, `<errors>`, `<examples>`)
8. **Move** version to YAML frontmatter

When upgrading from HSF v5 → HSF v6:

1. **Replace** `## Section` headers with XML tags (`<purpose>`, `<scope>`, `<instructions>`, `<rules>`, `<errors>`, `<examples>`)
2. **Convert** `@config` blocks to `<config>` with JSON body
3. **Convert** `@route name [mode]` with `→` rows to `<route name="..." mode="...">` with `<case when="...">` and `<default>` elements
4. **Change** `$config.key` references to `config.key` (drop `$` prefix)
5. **Wrap** error table in `<errors>` tags
6. **Add** `<output-schema>` blocks for phases producing structured output
7. **Preserve** prose instructions, $variable threading, RFC 2119 keywords, examples

**LLM-specific optimizations** (apply automatically):

- Convert passive voice to imperative mood
- Replace references to other sections with inline repetition where it improves compliance

**v6 opportunity suggestions** (require user approval):

- **`<config>` candidates**: Repeated literal values (3+)
- **`<route>` candidates**: Conditional logic with 3+ branches
- **`<output-schema>` candidates**: Phases producing structured output
- **Rule inlining candidates**: Rules that apply to only one phase

### Step 4: Present Migration Report

Show:

- **Detected format**: The inferred version
- **Target format**: HSF v6 (LLM-optimized, XML envelope)
- **Format migrations**: Automatic changes
- **Suggestions**: Optional enhancements

Use `AskUserQuestion`:

- "Migrate format only"
- "Migrate format + all suggestions"
- "Migrate format + selected suggestions"
- "Cancel"

### Step 5: Rewrite the Specification

1. Read the template at `${CLAUDE_PLUGIN_ROOT}/skills/hsf/assets/template.md`
2. Read the examples at `${CLAUDE_PLUGIN_ROOT}/skills/hsf/references/examples.md`
3. Apply all migrations and optimizations
4. Apply user-approved suggestions

**Apply output mode** based on `$output_mode`:

- **self-contained**: Convert into HSF v6 format with XML envelope. No meta-specification layer.
- **split**: Extract operational content into companion files.

**CRITICAL**: Preserve ALL domain logic exactly. Only change format and notation.

### Step 6: Validate and Save

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/hsf/scripts/validate_sesf.py <output-file>
```

Fix failures and re-validate. Overwrite the original file.

Report: original format, changes applied, validation result.
