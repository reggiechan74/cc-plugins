---
description: "Show current symbol table, defined/undefined/orphan status, and coverage"
argument-hint: "<path-to-file.math.md>"
allowed-tools: ["Bash", "Read", "Glob"]
arguments:
  - name: "file"
    description: "Path to the .math.md file to inspect"
---

# Show Model Status

Display the current symbol table, dependency status, and coverage metric for a `.math.md` document.

## Steps

1. **Locate the file:** Use the provided path argument. If no path is given, search with Glob for `**/*.math.md` and ask the user which one if multiple are found.

2. **Run the validation report:** Execute:

   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && PYTHONPATH=src python3 -m meta_compiler.cli report "<file_path>"
   ```

3. **Present the results:** Format the report output for the user, highlighting:
   - Total symbols defined by type (Sets, Parameters, Variables, Expressions, Constraints, Objectives)
   - Any orphan symbols (defined but never referenced)
   - Any phantom references (referenced but never defined)
   - Coverage ratio (math blocks with corresponding validation blocks)
   - Unvalidated sections (if any)
