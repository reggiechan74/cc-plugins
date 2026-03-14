---
description: "Onboard an existing math paper — generate validation blocks section-by-section with interactive approval"
argument-hint: "<path-to-paper.md>"
allowed-tools: ["Bash", "Read", "Write", "Glob"]
arguments:
  - name: "file"
    description: "Path to the plain .md file containing the math paper"
---

# Onboard a Math Paper

Convert an existing markdown math paper into a fully validated `.math.md` document with working `python:validate` blocks. This is an interactive, section-by-section process — you will approve each validation block before moving on.

## Step 1: Locate the file

Use the provided path argument. If no path is given, search with Glob for `**/*.md` (excluding `*.math.md` files). If multiple results are found:
- Show at most 20 matches and ask the user which one to onboard.
- If more than 20 matches exist, ask the user to provide a path directly.

## Step 2: Guard rails

Before proceeding, check two conditions:

1. **Already a `.math.md` file?** If the file ends in `.math.md`, tell the user: "This file is already a `.math.md` document. Use `/model:check` to validate it or `/model:status` to see its current state." Stop here.

2. **No math blocks?** Read the file and check for `$$...$$` display math blocks. If none are found, tell the user: "No display math blocks (`$$...$$`) were found in this file. There is nothing to onboard." Stop here.

## Step 3: Read and analyze

Read the entire document. Identify:
- All sections (by heading level: `#`, `##`, `###`, etc.)
- All `$$...$$` display math blocks and which section each belongs to
- The mathematical model being described: sets, parameters, variables, expressions, constraints, objectives

Build a mental model of the paper's structure and mathematical content.

## Step 4: Present overview

Show the user a summary:
- Number of sections containing math blocks
- Total number of display math blocks
- A high-level interpretation of the model, e.g.: "This paper describes a linear program for workforce scheduling with 3 sets, 5 parameters, 2 variables, and 4 constraints."

Ask the user to confirm or correct this interpretation. The user may respond with free-form corrections. If they do, re-interpret and re-present until the user confirms.

**Do not proceed until the user explicitly confirms.**

## Step 5: Section-by-section conversion

For each section that contains `$$...$$` math blocks, in document order:

1. **Show context.** Display the section heading and the math block(s) it contains.

2. **Propose a validation block.** Write a `python:validate` block that registers the symbols and relationships defined in that section using the meta-compiler API:
   - `Set(name, description=...)` for sets
   - `Parameter(name, index=[...], domain=..., units=..., description=...)` for parameters
   - `Variable(name, index=[...], domain=..., bounds=(...), units=..., description=...)` for variables
   - `Expression(name, definition=lambda ...: ..., index=[...], units=..., description=...)` for derived expressions
   - `Constraint(name, expr=lambda ...: ..., over=[...], type=..., description=...)` for constraints
   - `Objective(name, expr=lambda ...: ..., sense=..., description=...)` for objectives
   - End each block with `registry.run_tests()` to validate incrementally.

3. **Clarify ambiguity.** If notation is ambiguous (implicit sets, unclear units or domains, undefined subscripts), ask the user to clarify **before** finalizing the block. Do not guess — wait for the user's answer.

4. **Get approval.** Present the proposed block and ask the user to approve it, request changes, or skip it. Do not move to the next section until the user explicitly approves.

### API reference for validation blocks

```python
from meta_compiler import Set, Parameter, Variable, Expression, Constraint, Objective, S, registry

# Sets
Set("W", description="Set of workers")

# Parameters (indexed, with units)
Parameter("cap", index=["W"], domain="nonneg_real", units="hours", description="Capacity per worker")

# Variables (indexed, with bounds)
Variable("x", index=["W", "T"], domain="continuous", bounds=(0, None), units="hours", description="Hours assigned")

# Expressions (lambda captures relationships via symbolic indexing)
Expression("load", definition=lambda i: sum(Variable("x")[i, t] for t in S("T")),
           index=["W"], units="hours", description="Total load per worker")

# Constraints (lambda returns comparison expression)
Constraint("capacity", expr=lambda i: Expression("load")[i] <= Parameter("cap")[i],
           over=["W"], description="Load cannot exceed capacity")

# Objectives
Objective("total_output", expr=lambda: sum(Expression("load")[i] for i in S("W")),
          sense="maximize", description="Maximize total productive hours")

# Always end with
registry.run_tests()
```

## Step 6: Write the output

Once all sections are approved, write the complete `.math.md` file:

- **Filename:** `<original-basename>.math.md` in the same directory as the original file. For example, `paper.md` becomes `paper.math.md`.
- **Content rules:**
  - All original prose preserved verbatim.
  - All original math blocks preserved verbatim.
  - One validation block inserted per section, placed immediately after the last `$$...$$` math block in that section.
- **Never modify the original file.**

Use the Write tool to create the file.

## Step 7: Validate

Run the meta-compiler check in authoring mode (no `--strict` flag — orphans are warnings, not errors):

```bash
cd ${CLAUDE_PLUGIN_ROOT} && PYTHONPATH=src python3 -m meta_compiler.cli check "<output_path>"
```

## Step 8: Report

Show the validation result and coverage metric to the user.

- **If validation passed:** Confirm success. List any warnings (e.g., orphan symbols that will be covered in later sections).
- **If validation failed:** Show the errors, fix them in the `.math.md` file, and re-run check. Repeat up to 3 times. If still failing after 3 attempts, show the remaining errors and ask the user for guidance.
