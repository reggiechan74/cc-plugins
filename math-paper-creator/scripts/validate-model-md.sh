#!/usr/bin/env bash
# validate-model-md.sh — PostToolUse hook for .model.md live validation
#
# Reads PostToolUse JSON from stdin.
# If the edited file is .model.md, runs the meta-compiler check pipeline.
# Returns structured JSON feedback to Claude Code.

# Find the meta-compiler package relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Read stdin before the heredoc consumes it
HOOK_INPUT="$(cat)"

# Delegate everything to Python for safe JSON handling
HOOK_INPUT="$HOOK_INPUT" exec python3 - "$PROJECT_DIR" <<'PYTHON_SCRIPT'
import json
import os
import sys
from pathlib import Path

project_dir = Path(sys.argv[1])

# Read and parse hook input from environment variable
try:
    hook_input = json.loads(os.environ.get("HOOK_INPUT", ""))
except (json.JSONDecodeError, ValueError):
    sys.exit(0)

tool_name = hook_input.get("tool_name", "")
file_path = hook_input.get("tool_input", {}).get("file_path", "")

# Only process Write and Edit on .model.md files
if tool_name not in ("Write", "Edit"):
    sys.exit(0)

if not file_path.endswith(".model.md"):
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
