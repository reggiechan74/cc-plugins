---
description: "Run full validation pipeline against a .math.md document"
argument-hint: "<path-to-file.math.md>"
allowed-tools: ["Bash", "Read", "Glob"]
arguments:
  - name: "file"
    description: "Path to the .math.md file to validate"
  - name: "strict"
    description: "If present, treat orphan symbols as errors (compilation mode)"
---

# Validate Mathematical Model Document

Run the meta-compiler validation pipeline against the specified `.math.md` file.

## Steps

1. **Locate the file:** Use the provided path argument. If no path is given, search the current directory for `.math.md` files using Glob with pattern `**/*.math.md` and ask the user which one to validate if multiple are found.

2. **Run validation:** Execute the check command:

   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && python3 -m meta_compiler.cli check "<file_path>"
   ```

   If the `--strict` flag was requested, add it:

   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && python3 -m meta_compiler.cli check --strict "<file_path>"
   ```

3. **Report results:** Show the output to the user. If validation passed, confirm success and list any warnings. If validation failed, show the errors and offer to help fix them.
