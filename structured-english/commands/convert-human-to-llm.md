---
description: Convert a human-facing SESF spec to LLM-facing HSF v5 format
argument-hint: <path to SESF spec file>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Convert SESF → HSF (Human Spec → LLM Spec)

Take a human-facing SESF v4.1 specification (with formal BEHAVIOR/PROCEDURE/RULE/STEP blocks) and convert it to an LLM-facing HSF v5 specification (prose instructions with markdown headers). Preserves all domain logic — only the format changes.

## When to Use

Use this when:

- A human authored a spec in SESF v4.1 and now an LLM agent needs to execute it
- You want to maintain a human-readable source (SESF) and generate an LLM-optimized derivative (HSF)
- You're bridging the dual-audience gap: humans think and author in formal blocks, LLMs execute prose

## Workflow

### Step 1: Load Both Skills

Read both skills fully:

- The `sesf` skill at `${CLAUDE_PLUGIN_ROOT}/skills/sesf/SKILL.md` — to understand the source format
- The `hsf` skill at `${CLAUDE_PLUGIN_ROOT}/skills/hsf/SKILL.md` — to understand the target format

Also read the HSF reference at `${CLAUDE_PLUGIN_ROOT}/skills/hsf/assets/reference.md`.

### Step 2: Read the Source Spec

If the user provided a file path in the arguments, read it. Otherwise, ask the user:

- "Which SESF specification file should I convert?"

Read the full file content. Verify it is a SESF spec by checking for `**BEHAVIOR**` or `**PROCEDURE**` keywords. If not found:

- If it looks like HSF v5 (prose with `## Instructions`), tell the user: "This is already in HSF v5 format. Use `/update-LLM-spec` if you want to optimize it further."
- If it's not a spec at all, suggest `/write-LLM-spec` or `/assess-LLM-doc`.

### Step 3: Analyze and Map

Build a conversion plan by mapping SESF structures to HSF equivalents:

| SESF v4.1 Source | HSF v5 Target |
|------------------|---------------|
| `**BEHAVIOR** name:` block | `## Rules` section with bold list items, OR inline in the relevant `### Phase` |
| `**RULE** name:` with `WHEN/THEN` | Bold list item: `- **Rule name:** Natural sentence with MUST/SHOULD.` |
| `**PROCEDURE** name:` block | `## Instructions` with `### Phase` headers |
| `**STEP** name: desc → $var` | Phase header or numbered list item, $variable only if flow is complex |
| Rationale annotations `(why)` | Strip unless the rationale prevents a common LLM misapplication |
| Inline `@route` inside BEHAVIOR | Move to `## Routing Logic` section or inline in Instructions |
| `@config` block | Unchanged |
| `## Errors` table | Unchanged |
| Edge-case examples | Unchanged |

**Key decisions to make during mapping:**

1. **Rule placement**: For each BEHAVIOR block, decide whether its rules belong in a cross-cutting `## Rules` section (if they apply across all phases) or inline in a specific instruction phase (if they apply to one phase only). Default to inline — fewer cross-references means better LLM compliance.

2. **$variable threading**: For each STEP → $var, decide whether the data flow is complex enough to keep explicit $variable names, or whether prose ("use the output from Phase 1") is sufficient. Default to prose.

3. **Rationale stripping**: Remove parenthetical rationale annotations. Keep only rationale that prevents a specific misapplication the LLM would likely make.

### Step 4: Present Conversion Plan

Show the user:

- **Source format**: SESF v4.1
- **Target format**: HSF v5 (LLM-optimized)
- **BEHAVIOR blocks → target**: Where each behavior's rules will land
- **PROCEDURE blocks → target**: How each procedure maps to instruction phases
- **Rationale**: Which annotations will be kept vs stripped (and why)
- **$variable threading**: Which variables will be kept vs converted to prose

Use `AskUserQuestion` to confirm:

- "Proceed with conversion"
- "Adjust the plan" (then ask what to change)
- "Cancel"

### Step 5: Convert

Rewrite the specification following the HSF v5 skill rules:

1. Read the HSF template at `${CLAUDE_PLUGIN_ROOT}/skills/hsf/assets/template.md`
2. Read the HSF examples at `${CLAUDE_PLUGIN_ROOT}/skills/hsf/references/examples.md`
3. Apply the conversion plan:
   - Strip all `**BEHAVIOR**`, `**RULE**`, `**PROCEDURE**`, `**STEP**` keywords
   - Convert WHEN/THEN to natural prose sentences
   - Reorganize into `## Instructions` with `### Phase` headers
   - Inline phase-specific rules
   - Consolidate cross-cutting rules into `## Rules` with bold list items
   - Strip rationale per the plan
   - Preserve @config, @route, error table, examples verbatim

**LLM optimizations** (apply automatically):

- Imperative mood throughout
- No preamble or explanatory paragraphs that don't contain instructions
- Explicit enumeration over references

**CRITICAL**: Preserve ALL domain logic exactly. Every RULE must appear as a prose constraint. Every STEP must appear as an instruction. No business logic added or removed.

### Step 6: Validate

Run the HSF validator:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/hsf/scripts/validate_sesf.py <output-file>
```

Fix failures and re-validate.

### Step 7: Save

Use `AskUserQuestion` to ask:

- "How should I save the converted specification?"
- Options:
  - "Overwrite the original file" — replaces the SESF source with HSF output
  - "Save alongside the original" — write to `<original-name>-hsf.md` next to the source
  - "Save to a specific path" — ask for the path

Report: conversion summary (blocks converted, rationale stripped, variables simplified).
