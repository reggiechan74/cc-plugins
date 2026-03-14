---
description: "Generate clean paper artifact from a .math.md document (strips validation blocks)"
argument-hint: "<path-to-file.math.md>"
allowed-tools: ["Bash", "Read", "Write", "Glob"]
arguments:
  - name: "file"
    description: "Path to the .math.md file"
  - name: "depth"
    description: "Depth filter: executive, technical, or appendix"
  - name: "output"
    description: "Output file path (defaults to stdout)"
---

# Generate Paper Artifact

Compile a clean paper from a `.math.md` document. Strips all validation blocks, leaving only prose and math.

## Steps

1. **Locate the file:** Use the provided path argument. If no path is given, search with Glob for `**/*.math.md`.

2. **Build the command:**

   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && PYTHONPATH=src python3 -m meta_compiler.cli paper "<file_path>"
   ```

   Add `--depth <depth>` if a depth filter was specified.
   Add `--output <output_path>` if an output path was specified.

3. **Execute and report:** Run the command. If an output path was given, confirm the file was written. If no output path, display the paper content or write it to a sensible default location (e.g., `<basename>.paper.md`).
