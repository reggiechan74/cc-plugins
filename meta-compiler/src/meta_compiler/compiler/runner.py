"""Generate a thin runner script for .model.md files."""

from __future__ import annotations


def generate_runner(model_path: str) -> str:
    """Generate a standalone Python script that validates a .model.md file."""
    return f'''#!/usr/bin/env python3
"""Auto-generated runner for {model_path}."""

import sys
from pathlib import Path

from meta_compiler.compiler import check_document


def main():
    path = Path(__file__).parent / "{model_path}"
    if not path.exists():
        print(f"Error: {{path}} not found", file=sys.stderr)
        sys.exit(1)

    result = check_document(path.read_text(), strict=True)

    if result.errors:
        for error in result.errors:
            print(f"ERROR: {{error}}", file=sys.stderr)
    for warning in result.warnings:
        print(f"WARNING: {{warning}}", file=sys.stderr)

    if result.passed:
        print("All checks passed.")
    else:
        print(f"{{len(result.errors)}} error(s) found.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
