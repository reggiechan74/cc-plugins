---
description: "Generate full validation report (symbol table, dependencies, coverage, test results)"
argument-hint: "<path-to-file.math.md>"
allowed-tools: ["Bash", "Read", "Write", "Glob"]
arguments:
  - name: "file"
    description: "Path to the .math.md file"
  - name: "output"
    description: "Output file path (defaults to stdout)"
---

# Generate Validation Report

Produce a full validation report from a `.math.md` document including symbol table, dependency graph, test results, and coverage audit.

## Steps

1. **Locate the file:** Use the provided path argument. If no path is given, search with Glob for `**/*.math.md`.

2. **Run the report command:**

   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && PYTHONPATH=src python3 -m meta_compiler.cli report "<file_path>"
   ```

   Add `--output <output_path>` if an output path was specified.

3. **Present results:** Show the full report to the user. Highlight any errors, warnings, orphan symbols, or coverage gaps.
