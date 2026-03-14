# `/model:onboard` — Design Spec

## Purpose

Convert an existing markdown math paper into a fully validated `.math.md` document with working `python:validate` blocks. The command guides Claude through a section-by-section interactive process where the user approves each validation block before moving on.

## Input / Output

- **Input:** A plain `.md` file containing prose and LaTeX math blocks (`$$...$$`).
- **Output:** A new `<original-name>.math.md` file alongside the original, containing the original prose and math plus inserted validation blocks. The original file is never modified.

## Workflow

1. **Locate the file.** Accept a path argument. If none given, search with `**/*.md` (excluding `*.math.md`) and ask the user which one.

2. **Read and analyze.** Read the entire document. Identify all sections (by heading), math blocks, and the mathematical model being described — sets, parameters, variables, expressions, constraints, objectives.

3. **Present overview.** Show the user a summary: number of sections, number of math blocks, and a high-level interpretation of the model ("This paper describes a linear program for workforce scheduling with 3 sets, 5 parameters, 2 variables, and 4 constraints"). Ask the user to confirm or correct this interpretation before proceeding.

4. **Section-by-section conversion.** For each section that contains math blocks:
   - Show the math block(s) in context.
   - Propose a `python:validate` block that registers the symbols and relationships defined in that section.
   - Discuss any ambiguous notation, implicit set definitions, or unclear units/domains with the user.
   - Get explicit approval before moving to the next section.

5. **Write the output.** Once all sections are approved, write the complete `.math.md` file:
   - All original prose preserved verbatim.
   - All original math blocks preserved verbatim.
   - Validation blocks inserted after each math block (or group of related math blocks within a section).
   - File written to `<original-basename>.math.md` in the same directory as the original.

6. **Validate.** Run the meta-compiler check on the new file:
   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && PYTHONPATH=src python3 -m meta_compiler.cli check "<output_path>"
   ```

7. **Report.** Show the validation result and coverage metric. If validation fails, offer to fix the errors interactively.

## Command Frontmatter

```yaml
description: "Onboard an existing math paper — generate validation blocks section-by-section with interactive approval"
argument-hint: "<path-to-paper.md>"
allowed-tools: ["Bash", "Read", "Write", "Glob"]
arguments:
  - name: "file"
    description: "Path to the existing .md math paper"
```

## Constraints

- Never modify the original file.
- Preserve all original prose and math verbatim — only add validation blocks.
- Each validation block must use the meta-compiler API (`Set`, `Parameter`, `Variable`, `Expression`, `Constraint`, `Objective`, `registry.run_tests()`).
- The final document must pass `check` in authoring mode (non-strict).
