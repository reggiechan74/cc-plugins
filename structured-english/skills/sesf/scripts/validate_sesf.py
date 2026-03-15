#!/usr/bin/env python3
"""SESF/HSF Structural Validator — thin wrapper.

Delegates to the canonical validator at skills/hsf/scripts/validate_sesf.py,
which handles SESF v3/v4, HSF v5, and HSF v6 with auto-detection.

Usage:
    python3 validate_sesf.py <spec_file.md>
"""

import importlib.util
import runpy
import sys
from pathlib import Path

# Locate the canonical validator relative to this file
_CANONICAL = Path(__file__).resolve().parent.parent.parent / "hsf" / "scripts" / "validate_sesf.py"

if not _CANONICAL.exists():
    print(f"ERROR: Canonical validator not found at {_CANONICAL}", file=sys.stderr)
    sys.exit(1)

# Re-export all public names from the canonical module so that
# `from validate_sesf import parse_sesf` works for tests.
_spec = importlib.util.spec_from_file_location("_canonical_validate_sesf", _CANONICAL)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Populate this module's namespace with everything from the canonical module
for _name in dir(_mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_mod, _name)

if __name__ == "__main__":
    runpy.run_path(str(_CANONICAL), run_name="__main__")
