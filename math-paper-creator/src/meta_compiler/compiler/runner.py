"""Generate a standalone runner script from .model.md fixture + validate blocks.

The runner contains all fixture data and validation code extracted from the
document, concatenated in document order. It is self-contained — it does not
require the .model.md file or re-parse it at runtime.
"""

from __future__ import annotations

from meta_compiler.compiler.parser import Block, FixtureBlock, ValidationBlock


def generate_runner(blocks: list[Block], *, model_path: str = "model.model.md") -> str:
    """Generate a standalone Python script from extracted blocks.

    If blocks are provided, the runner contains all fixture and validate code
    inlined. If blocks are not provided (backward compat), falls back to a
    thin wrapper that re-parses the .model.md file.
    """
    if not blocks:
        return _generate_legacy_runner(model_path)

    fixture_blocks = [b for b in blocks if isinstance(b, FixtureBlock)]
    validate_blocks = [b for b in blocks if isinstance(b, ValidationBlock)]

    if not fixture_blocks and not validate_blocks:
        return _generate_legacy_runner(model_path)

    # Build the standalone script
    parts: list[str] = [
        '#!/usr/bin/env python3',
        f'"""Standalone validation runner extracted from {model_path}.',
        '',
        'This script contains all fixture data and validation logic from the',
        '.model.md document. It can be run independently without the paper.',
        '',
        'Usage:',
        '    python3 runner.py',
        '    python3 runner.py --strict   # treat orphans as errors',
        '"""',
        '',
        'import sys',
        '',
        'from meta_compiler import Set, Parameter, Variable, Expression, Constraint, Objective, S',
        'from meta_compiler import registry',
        '',
        '',
        'def main():',
        '    strict = "--strict" in sys.argv',
        '    registry.reset()',
        '',
    ]

    # Emit fixture blocks — build data store
    if fixture_blocks:
        parts.append('    # ── Fixture data ─────────────────────────────────────')
        parts.append('    _fixture_ns = {}')
        for i, fb in enumerate(fixture_blocks):
            parts.append(f'    # Fixture block {i + 1} (source line {fb.line_number})')
            # Indent each line of fixture code
            for line in fb.code.splitlines():
                if line.strip():
                    parts.append(f'    {line}')
                else:
                    parts.append('')
            parts.append('')

        # Populate data store from locals
        parts.append('    # Populate registry data store from fixture variables')
        parts.append('    _frame_locals = {k: v for k, v in locals().items()')
        parts.append('                     if not k.startswith("_") and k not in ("strict", "sys")}')
        parts.append('    for _name, _value in _frame_locals.items():')
        parts.append('        registry.data_store[_name] = _value')
        parts.append('')

    # Set up execution namespace for auto-injection
    parts.append('    # ── Validation blocks ──────────────────────────────')
    parts.append('    _ns = locals()')
    parts.append('    registry._exec_namespace = _ns')
    parts.append('')

    for i, vb in enumerate(validate_blocks):
        parts.append(f'    # Validate block {i + 1} (source line {vb.line_number})')
        for line in vb.code.splitlines():
            stripped = line.strip()
            # Skip imports (already at top level) and registry.run_tests() calls
            if stripped.startswith('from meta_compiler import'):
                continue
            if stripped == 'registry.run_tests()':
                continue
            if stripped.startswith('import ') and 'meta_compiler' in stripped:
                continue
            if line.strip():
                parts.append(f'    {line}')
            else:
                parts.append('')
        parts.append('')

    # Final validation
    parts.append('    registry._exec_namespace = None')
    parts.append('')
    parts.append('    # ── Run checks ─────────────────────────────────────')
    parts.append('    result = registry.run_tests(strict=strict)')
    parts.append('')
    parts.append('    if result.errors:')
    parts.append('        for error in result.errors:')
    parts.append('            print(f"ERROR: {error}", file=sys.stderr)')
    parts.append('    for warning in result.warnings:')
    parts.append('        print(f"WARNING: {warning}", file=sys.stderr)')
    parts.append('')
    parts.append('    if result.passed:')
    parts.append('        print("All checks passed.")')
    parts.append('    else:')
    parts.append('        print(f"{len(result.errors)} error(s) found.", file=sys.stderr)')
    parts.append('        sys.exit(1)')
    parts.append('')
    parts.append('')
    parts.append('if __name__ == "__main__":')
    parts.append('    main()')
    parts.append('')

    return '\n'.join(parts)


def _generate_legacy_runner(model_path: str) -> str:
    """Fallback: thin wrapper that re-parses .model.md at runtime."""
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
