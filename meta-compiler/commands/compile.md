---
description: "Compile all three artifacts: paper, codebase, and validation report"
argument-hint: "<path-to-file.model.md>"
allowed-tools: ["Bash", "Read", "Write", "Glob"]
arguments:
  - name: "file"
    description: "Path to the .model.md file"
  - name: "output"
    description: "Output directory (defaults to ./output)"
  - name: "depth"
    description: "Depth filter for paper: executive, technical, or appendix"
---

# Compile All Artifacts

Produce all three artifacts from a `.model.md` document:
1. **Paper** — clean Markdown with validation blocks stripped
2. **Codebase** — standalone Python package extracted from validation blocks
3. **Validation Report** — symbol table, dependencies, coverage, test results

This runs in **strict mode** — orphan symbols are hard errors. Use this when the document is complete.

## Steps

1. **Locate the file:** Use the provided path argument. If no path is given, search with Glob for `**/*.model.md`.

2. **Build the command:**

   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && PYTHONPATH=src python3 -m meta_compiler.cli compile "<file_path>" --output "<output_dir>"
   ```

   Add `--depth <depth>` if a depth filter was specified.
   Default output directory is `./output` relative to the document's location.

3. **Execute:** Run the command. If validation fails (strict mode), report the errors and offer to help fix them before retrying.

4. **Report:** Show the user what was generated:
   - `<output>/paper.md` — the clean paper
   - `<output>/model/` — the Python package (list files)
   - `<output>/report.txt` — the validation report

5. **Verify codebase:** Optionally run the generated codebase:

   ```bash
   cd <output> && python3 -m model
   ```

   Report pass/fail status.
