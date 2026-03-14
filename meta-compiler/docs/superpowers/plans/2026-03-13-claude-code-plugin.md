# Claude Code Plugin — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Claude Code plugin that integrates the meta-compiler into the live authoring workflow via a PostToolUse validation hook and five slash commands.

**Architecture:** A thin integration layer over the existing compiler CLI (`meta_compiler.cli`). The PostToolUse hook runs a bash script that detects `.math.md` file edits, calls `python3 -m meta_compiler.cli check` on the file, and returns structured JSON feedback to Claude on validation failure. Five slash commands (`/model:check`, `/model:paper`, `/model:report`, `/model:status`, `/model:compile`) are markdown files that instruct Claude to invoke the CLI with the appropriate arguments.

**Tech Stack:** Claude Code plugin (plugin.json, hooks.json, markdown commands), Bash (hook script), Python 3.10+ (existing CLI).

---

## Scope

This is **Phase 3 of 3** from the [meta-compiler design spec](../specs/2026-03-13-meta-compiler-design.md).

- **Phase 1 (complete):** Symbol registry and validation engine
- **Phase 2 (complete):** Artifact compiler — parser, executor, paper/codebase/report generators, CLI
- **Phase 3 (this plan):** Claude Code plugin — hooks and commands for live authoring

This plan depends on the existing CLI at `src/meta_compiler/cli.py` which supports `check`, `paper`, `report`, and `compile` subcommands.

## File Structure

```
meta-compiler/
  .claude-plugin/
    plugin.json              # Plugin manifest — name "model", references hooks + commands
  hooks/
    hooks.json               # PostToolUse hook config for Write|Edit on .math.md files
  scripts/
    validate-math-md.sh      # Hook script — filters by extension, runs check, returns JSON
  commands/
    check.md                 # /model:check — run validation pipeline
    paper.md                 # /model:paper — generate paper artifact
    report.md                # /model:report — generate validation report
    status.md                # /model:status — show symbol table and coverage
    compile.md               # /model:compile — generate all three artifacts
  tests/
    plugin/
      test_hook_script.py    # Integration tests for the hook script
  README.md                  # Plugin README with badges and install instructions
```

---

## Chunk 1: Plugin Scaffold and Hook

### Task 1: Create plugin manifest and hooks config

**Files:**
- Create: `meta-compiler/.claude-plugin/plugin.json`
- Create: `meta-compiler/hooks/hooks.json`

- [ ] **Step 1: Create the plugin.json with hooks and commands references**

```json
{
  "name": "model",
  "version": "0.1.0",
  "description": "Live validation for mathematical model documents (.math.md). Auto-validates on every edit, hard blocks on inconsistency.",
  "author": {
    "name": "Reggie Chan"
  },
  "license": "MIT",
  "keywords": ["math", "validation", "meta-compiler", "optimization"],
  "hooks": "./hooks/hooks.json",
  "commands": [
    "./commands/"
  ]
}
```

- [ ] **Step 2: Create hooks.json**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate-math-md.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Verify plugin structure**

Run: `ls -la meta-compiler/.claude-plugin/plugin.json meta-compiler/hooks/hooks.json`
Expected: Both files exist.

- [ ] **Step 4: Commit**

```bash
git add meta-compiler/.claude-plugin/plugin.json meta-compiler/hooks/hooks.json
git commit -m "feat(plugin): add plugin manifest and hook config"
```

---

### Task 2: Create the hook validation script

**Files:**
- Create: `meta-compiler/scripts/validate-math-md.sh`

The hook script receives JSON on stdin from Claude Code's PostToolUse event. It:
1. Extracts `tool_input.file_path` from stdin JSON
2. Checks if the file ends with `.math.md` — exits 0 silently if not
3. Runs `python3 -m meta_compiler.cli check <file>` (authoring mode, no `--strict`)
4. Also runs coverage metric check
5. On validation failure (exit code 1): outputs JSON with `decision: "block"` and the error details as `reason`, exits 0
6. On validation pass: outputs JSON with any warnings as `additionalContext`, exits 0

- [ ] **Step 1: Write the failing test**

```python
# tests/plugin/test_hook_script.py
"""Integration tests for the validate-math-md.sh hook script."""

import json
import subprocess
from pathlib import Path
import tempfile

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate-math-md.sh"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_hook(tool_name: str, file_path: str, content: str = "") -> subprocess.CompletedProcess:
    """Simulate a PostToolUse hook invocation."""
    hook_input = json.dumps({
        "hook_event_name": "PostToolUse",
        "tool_name": tool_name,
        "tool_input": {
            "file_path": file_path,
            "content": content,
        },
        "tool_response": {"success": True},
    })
    return subprocess.run(
        ["bash", str(SCRIPT)],
        input=hook_input,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        timeout=30,
    )


class TestHookFiltering:
    """Hook should only process .math.md files."""

    def test_ignores_regular_md_files(self):
        result = run_hook("Write", "/tmp/notes.md")
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_ignores_python_files(self):
        result = run_hook("Write", "/tmp/code.py")
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_ignores_non_write_tools(self):
        result = run_hook("Read", "/tmp/model.math.md")
        assert result.returncode == 0
        assert result.stdout.strip() == ""


class TestHookValidation:
    """Hook should validate .math.md files and return structured feedback."""

    def test_valid_document_passes(self, tmp_path):
        doc = tmp_path / "valid.math.md"
        doc.write_text(
            '# Test\n\n$$x \\in \\mathbb{R}$$\n\n'
            '```python:validate\n'
            'Set("W", description="Workers")\n'
            'registry.run_tests()\n'
            '```\n'
        )
        result = run_hook("Write", str(doc))
        assert result.returncode == 0
        if result.stdout.strip():
            output = json.loads(result.stdout)
            assert output.get("decision") != "block"

    def test_invalid_document_blocks(self, tmp_path):
        doc = tmp_path / "invalid.math.md"
        doc.write_text(
            '# Test\n\n'
            '```python:validate\n'
            'Parameter("cap", index=["W"], domain="nonneg_real",\n'
            '          units="hours", description="Capacity")\n'
            'registry.run_tests()\n'
            '```\n'
        )
        result = run_hook("Write", str(doc))
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["decision"] == "block"
        assert "BLOCK" in output["reason"] or "not registered" in output["reason"]

    def test_coverage_warning_reported(self, tmp_path):
        """Document has 2 math blocks but only 1 validation block — must warn."""
        doc = tmp_path / "uncovered.math.md"
        doc.write_text(
            '# Test\n\n'
            '## Section A\n\n'
            '$$x \\in \\mathbb{R}$$\n\n'
            '```python:validate\n'
            'Set("W", description="Workers")\n'
            'registry.run_tests()\n'
            '```\n\n'
            '## Section B\n\n'
            '$$y \\in \\mathbb{R}$$\n\n'
        )
        result = run_hook("Write", str(doc))
        assert result.returncode == 0
        assert result.stdout.strip(), "Expected coverage warning output, got nothing"
        output = json.loads(result.stdout)
        context = output.get("hookSpecificOutput", {}).get("additionalContext", "")
        assert "math block" in context.lower() or "unvalidated" in context.lower() or "coverage" in context.lower()
```

- [ ] **Step 2: Create empty test directory and run tests to verify failure**

```bash
mkdir -p meta-compiler/tests/plugin
touch meta-compiler/tests/plugin/__init__.py
```

Run: `cd meta-compiler && python3 -m pytest tests/plugin/test_hook_script.py -v`
Expected: FAIL — script does not exist yet.

- [ ] **Step 3: Write the hook script**

The script does all JSON parsing, validation, and JSON output construction in a single
Python call to avoid shell interpolation bugs and ensure valid JSON output.

```bash
#!/usr/bin/env bash
# validate-math-md.sh — PostToolUse hook for .math.md live validation
#
# Reads PostToolUse JSON from stdin.
# If the edited file is .math.md, runs the meta-compiler check pipeline.
# Returns structured JSON feedback to Claude Code.

# Find the meta-compiler package relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Delegate everything to Python for safe JSON handling
exec python3 - "$PROJECT_DIR" <<'PYTHON_SCRIPT'
import json
import sys
from pathlib import Path

project_dir = Path(sys.argv[1])

# Read and parse hook input from stdin
try:
    hook_input = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

tool_name = hook_input.get("tool_name", "")
file_path = hook_input.get("tool_input", {}).get("file_path", "")

# Only process Write and Edit on .math.md files
if tool_name not in ("Write", "Edit"):
    sys.exit(0)

if not file_path.endswith(".math.md"):
    sys.exit(0)

file_path_obj = Path(file_path)
if not file_path_obj.is_file():
    sys.exit(0)

# Add meta-compiler src to path
sys.path.insert(0, str(project_dir / "src"))

from meta_compiler.compiler import check_document
from meta_compiler.compiler.parser import parse_document, coverage_metric

source = file_path_obj.read_text()

# Run validation in authoring mode (orphans are warnings, not errors)
result = check_document(source, strict=False)

# Check coverage
blocks = parse_document(source)
cov = coverage_metric(blocks)

if not result.passed:
    # Validation failed — block with error details
    errors = "; ".join(result.errors)
    output = {
        "decision": "block",
        "reason": f"Validation failed for {file_path}: {errors}",
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "Fix the validation errors before continuing. Re-run all validation blocks from the top of the document after your fix.",
        },
    }
    print(json.dumps(output))
else:
    # Validation passed — collect warnings and coverage info
    context_parts = []

    if cov.total_math > 0 and cov.covered_math < cov.total_math:
        uncovered = cov.total_math - cov.covered_math
        sections = ", ".join(cov.uncovered_sections) if cov.uncovered_sections else "unknown"
        context_parts.append(
            f"WARNING: {uncovered} math blocks have no validation block. "
            f"Unvalidated sections: {sections}"
        )

    if result.warnings:
        context_parts.extend(result.warnings)

    if context_parts:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "; ".join(context_parts),
            }
        }
        print(json.dumps(output))
PYTHON_SCRIPT
```

- [ ] **Step 4: Make script executable**

Run: `chmod +x meta-compiler/scripts/validate-math-md.sh`

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd meta-compiler && python3 -m pytest tests/plugin/test_hook_script.py -v`
Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add meta-compiler/scripts/validate-math-md.sh meta-compiler/tests/plugin/
git commit -m "feat(plugin): add PostToolUse hook script for .math.md live validation"
```

---

## Chunk 2: Slash Commands

### Task 3: Create /model:check command

**Files:**
- Create: `meta-compiler/commands/check.md`

- [ ] **Step 1: Write the command file**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add meta-compiler/commands/check.md
git commit -m "feat(plugin): add /model:check command"
```

---

### Task 4: Create /model:status command

**Files:**
- Create: `meta-compiler/commands/status.md`

- [ ] **Step 1: Write the command file**

```markdown
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
   cd ${CLAUDE_PLUGIN_ROOT} && python3 -m meta_compiler.cli report "<file_path>"
   ```

3. **Present the results:** Format the report output for the user, highlighting:
   - Total symbols defined by type (Sets, Parameters, Variables, Expressions, Constraints, Objectives)
   - Any orphan symbols (defined but never referenced)
   - Any phantom references (referenced but never defined)
   - Coverage ratio (math blocks with corresponding validation blocks)
   - Unvalidated sections (if any)
```

- [ ] **Step 2: Commit**

```bash
git add meta-compiler/commands/status.md
git commit -m "feat(plugin): add /model:status command"
```

---

### Task 5: Create /model:paper command

**Files:**
- Create: `meta-compiler/commands/paper.md`

- [ ] **Step 1: Write the command file**

```markdown
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
   cd ${CLAUDE_PLUGIN_ROOT} && python3 -m meta_compiler.cli paper "<file_path>"
   ```

   Add `--depth <depth>` if a depth filter was specified.
   Add `--output <output_path>` if an output path was specified.

3. **Execute and report:** Run the command. If an output path was given, confirm the file was written. If no output path, display the paper content or write it to a sensible default location (e.g., `<basename>.paper.md`).
```

- [ ] **Step 2: Commit**

```bash
git add meta-compiler/commands/paper.md
git commit -m "feat(plugin): add /model:paper command"
```

---

### Task 6: Create /model:report command

**Files:**
- Create: `meta-compiler/commands/report.md`

- [ ] **Step 1: Write the command file**

```markdown
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
   cd ${CLAUDE_PLUGIN_ROOT} && python3 -m meta_compiler.cli report "<file_path>"
   ```

   Add `--output <output_path>` if an output path was specified.

3. **Present results:** Show the full report to the user. Highlight any errors, warnings, orphan symbols, or coverage gaps.
```

- [ ] **Step 2: Commit**

```bash
git add meta-compiler/commands/report.md
git commit -m "feat(plugin): add /model:report command"
```

---

### Task 7: Create /model:compile command

**Files:**
- Create: `meta-compiler/commands/compile.md`

- [ ] **Step 1: Write the command file**

```markdown
---
description: "Compile all three artifacts: paper, codebase, and validation report"
argument-hint: "<path-to-file.math.md>"
allowed-tools: ["Bash", "Read", "Write", "Glob"]
arguments:
  - name: "file"
    description: "Path to the .math.md file"
  - name: "output"
    description: "Output directory (defaults to ./output)"
  - name: "depth"
    description: "Depth filter for paper: executive, technical, or appendix"
---

# Compile All Artifacts

Produce all three artifacts from a `.math.md` document:
1. **Paper** — clean Markdown with validation blocks stripped
2. **Codebase** — standalone Python package extracted from validation blocks
3. **Validation Report** — symbol table, dependencies, coverage, test results

This runs in **strict mode** — orphan symbols are hard errors. Use this when the document is complete.

## Steps

1. **Locate the file:** Use the provided path argument. If no path is given, search with Glob for `**/*.math.md`.

2. **Build the command:**

   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && python3 -m meta_compiler.cli compile "<file_path>" --output "<output_dir>"
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
```

- [ ] **Step 2: Commit**

```bash
git add meta-compiler/commands/compile.md
git commit -m "feat(plugin): add /model:compile command"
```

---

## Chunk 3: Integration Testing and README

### Task 8: Add hook integration tests for edge cases

**Files:**
- Modify: `meta-compiler/tests/plugin/test_hook_script.py`

- [ ] **Step 1: Add edge case tests**

Append to the existing test file:

```python
class TestHookEdgeCases:
    """Edge cases for the hook script."""

    def test_handles_edit_tool(self, tmp_path):
        """Hook should trigger on Edit tool, not just Write."""
        doc = tmp_path / "test.math.md"
        doc.write_text(
            '```python:validate\n'
            'Parameter("x", index=["MISSING"], domain="real",\n'
            '          units="hours", description="Bad param")\n'
            'registry.run_tests()\n'
            '```\n'
        )
        result = run_hook("Edit", str(doc))
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["decision"] == "block", "Edit tool should trigger validation, not be ignored"

    def test_nonexistent_file_exits_cleanly(self):
        """Hook should exit 0 when the .math.md file doesn't exist."""
        result = run_hook("Write", "/tmp/nonexistent.math.md")
        assert result.returncode == 0

    def test_empty_document(self, tmp_path):
        """Hook should handle an empty .math.md file gracefully."""
        doc = tmp_path / "empty.math.md"
        doc.write_text("")
        result = run_hook("Write", str(doc))
        assert result.returncode == 0

    def test_document_with_only_prose(self, tmp_path):
        """Hook should pass on a document with prose but no validation blocks."""
        doc = tmp_path / "prose.math.md"
        doc.write_text("# Title\n\nSome prose about math.\n")
        result = run_hook("Write", str(doc))
        assert result.returncode == 0

    def test_valid_json_output_on_block(self, tmp_path):
        """Block response must be valid JSON."""
        doc = tmp_path / "bad.math.md"
        doc.write_text(
            '```python:validate\n'
            'Parameter("x", index=["NONEXISTENT"], domain="real",\n'
            '          units="hours", description="Bad param")\n'
            'registry.run_tests()\n'
            '```\n'
        )
        result = run_hook("Write", str(doc))
        assert result.returncode == 0
        output = json.loads(result.stdout)  # Must be valid JSON
        assert output["decision"] == "block"
```

- [ ] **Step 2: Run full test suite**

Run: `cd meta-compiler && python3 -m pytest tests/plugin/ -v`
Expected: All tests PASS.

- [ ] **Step 3: Run the complete test suite (all phases)**

Run: `cd meta-compiler && python3 -m pytest tests/ -v`
Expected: All tests PASS (94 existing + 11 new plugin tests = 105 total).

- [ ] **Step 4: Commit**

```bash
git add meta-compiler/tests/plugin/test_hook_script.py
git commit -m "test(plugin): add edge case tests for hook script"
```

---

### Task 9: Create README with badges and install instructions

**Files:**
- Create: `meta-compiler/README.md`

- [ ] **Step 1: Write the full README**

```markdown
# model

<!-- badges-start -->
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-plugin-blueviolet)
<!-- badges-end -->

Live validation for mathematical model documents (`.math.md`). Auto-validates on every edit, hard blocks on inconsistency.

## Installation

```
/plugin marketplace add reggiechan74/cc-plugins
/plugin install model@cc-plugins
```

## Commands

| Command | Description |
|---------|-------------|
| `/model:check <file>` | Run validation pipeline against a `.math.md` document |
| `/model:status <file>` | Show symbol table, coverage, and orphan/phantom status |
| `/model:paper <file>` | Generate clean paper artifact (strips validation blocks) |
| `/model:report <file>` | Generate full validation report |
| `/model:compile <file>` | Produce all three artifacts (paper, codebase, report) |

## Live Validation

When installed, the plugin automatically validates `.math.md` files every time Claude writes or edits one. Validation errors are hard blocks — Claude must fix them before continuing.

The hook runs in **authoring mode**: symbol conflicts, undefined references, index mismatches, and dimensional errors are hard blocks. Orphan symbols produce warnings only (the symbol may be used in a later section).

Coverage gaps (math blocks without corresponding validation blocks) are reported as warnings.

## Requirements

Python 3.10+ with the `meta_compiler` package available on the Python path. The package is included in this plugin directory.
```

- [ ] **Step 2: Commit**

```bash
git add meta-compiler/README.md
git commit -m "docs(plugin): add README with badges and install instructions"
```

---

### Task 10: Add plugin to marketplace.json

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Read the current marketplace.json**

Read: `.claude-plugin/marketplace.json`

- [ ] **Step 2: Add the model plugin entry to the plugins array**

Add this entry to the `plugins` array in alphabetical order (after `mississauga-permits`, before `nano-banana`):

```json
{
  "name": "model",
  "source": "./meta-compiler",
  "description": "Live validation for mathematical model documents (.math.md). Auto-validates on every edit, hard blocks on inconsistency.",
  "version": "0.1.0"
}
```

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "chore: add model plugin to marketplace registry"
```
