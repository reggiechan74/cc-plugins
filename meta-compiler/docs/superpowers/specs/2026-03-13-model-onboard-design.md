# `/model:onboard` — Design Spec

## Purpose

Convert an existing markdown math paper into a fully validated `.math.md` document with working `python:validate` blocks. The command guides Claude through a section-by-section interactive process where the user approves each validation block before moving on.

## Deliverable

A single command file: `commands/onboard.md`

## Input / Output

- **Input:** A plain `.md` file containing prose and LaTeX math blocks (`$$...$$`).
- **Output:** A new `<original-name>.math.md` file alongside the original, containing the original prose and math plus inserted validation blocks. The original file is never modified.

## Workflow

1. **Locate the file.** Accept a path argument. If none given, search with `**/*.md` (excluding `*.math.md`). If multiple results, show at most 20 and ask the user which one. If more than 20, ask the user to provide a path directly.

2. **Guard rails.** Before proceeding:
   - If the file is already a `.math.md` file, tell the user this command is for onboarding plain `.md` papers and suggest using `/model:check` or `/model:status` instead.
   - If the file contains no `$$...$$` math blocks, tell the user no math was found and stop.

3. **Read and analyze.** Read the entire document. Identify all sections (by heading), math blocks, and the mathematical model being described — sets, parameters, variables, expressions, constraints, objectives.

4. **Present overview.** Show the user a summary: number of sections, number of math blocks, and a high-level interpretation of the model ("This paper describes a linear program for workforce scheduling with 3 sets, 5 parameters, 2 variables, and 4 constraints"). Ask the user to confirm or correct this interpretation before proceeding. The user may respond with free-form corrections; re-interpret and re-present until the user confirms.

5. **Section-by-section conversion.** For each section that contains math blocks:
   - Show the math block(s) in context.
   - Propose a `python:validate` block that registers the symbols and relationships defined in that section.
   - If notation is ambiguous (implicit sets, unclear units/domains), ask the user to clarify before finalizing the block. Do not guess — wait for the user's answer.
   - Get explicit approval before moving to the next section.

6. **Write the output.** Once all sections are approved, write the complete `.math.md` file:
   - All original prose preserved verbatim.
   - All original math blocks preserved verbatim.
   - One validation block inserted per section, placed after the last math block in that section.
   - File written to `<original-basename>.math.md` in the same directory as the original.

7. **Validate.** Run the meta-compiler check (without `--strict`, which is authoring mode — orphans are warnings, not errors):
   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && PYTHONPATH=src python3 -m meta_compiler.cli check "<output_path>"
   ```

8. **Report.** Show the validation result and coverage metric. If validation fails, show the errors, fix them, and re-run check. Repeat up to 3 times. If still failing after 3 attempts, show the remaining errors and ask the user for guidance.

## Command Frontmatter

The command file (`commands/onboard.md`) uses this frontmatter:

```yaml
description: "Onboard an existing math paper — generate validation blocks section-by-section with interactive approval"
argument-hint: "<path-to-paper.md>"
allowed-tools: ["Bash", "Read", "Write", "Glob"]
```

## Constraints

- Never modify the original file.
- Preserve all original prose and math verbatim — only add validation blocks.
- Each validation block must use the meta-compiler API (`Set`, `Parameter`, `Variable`, `Expression`, `Constraint`, `Objective`, `registry.run_tests()`).
- The final document must pass `check` without the `--strict` flag (authoring mode: orphans are warnings only).
