import os
import subprocess
from pathlib import Path

_SRC = str(Path(__file__).parent.parent.parent / "src")
_CLI_ENV = {**os.environ, "PYTHONPATH": _SRC}


def test_reconcile_cli_flags_directional_claims():
    """reconcile command flags directional keywords in prose."""
    doc = """## Setup

```python:validate
Set("W", description="Workers")
```

## Analysis

As sigma increases, the outside option widens.

```python:validate
Parameter("sigma", index="W", description="Volatility")
```
"""
    tmp = Path("/tmp/test_reconcile.model.md")
    tmp.write_text(doc)
    result = subprocess.run(
        ["python3", "-m", "meta_compiler.cli", "reconcile", str(tmp), "--section", "Analysis"],
        capture_output=True, text=True, env=_CLI_ENV,
    )
    assert result.returncode == 2
    assert "increases" in result.stdout.lower()
    assert "widens" in result.stdout.lower()
    tmp.unlink()


def test_reconcile_cli_clean_section():
    """reconcile command returns 0 for clean section."""
    doc = """## Setup

```python:validate
Set("W", description="Workers")
```

## Analysis

We define a parameter for the worker set.

```python:validate
Parameter("cap", index="W", description="Cap")
```
"""
    tmp = Path("/tmp/test_reconcile_clean.model.md")
    tmp.write_text(doc)
    result = subprocess.run(
        ["python3", "-m", "meta_compiler.cli", "reconcile", str(tmp), "--section", "Analysis"],
        capture_output=True, text=True, env=_CLI_ENV,
    )
    assert result.returncode == 0
    assert "Reconciliation: OK" in result.stdout
    tmp.unlink()


def test_reconcile_cli_scopes_to_section():
    """reconcile command does not flag issues in other sections."""
    doc = """## Setup

The value increases over time.

```python:validate
Set("W", description="Workers")
```

## Analysis

We define a parameter.

```python:validate
Parameter("cap", index="W", description="Cap")
```
"""
    tmp = Path("/tmp/test_reconcile_scope.model.md")
    tmp.write_text(doc)
    result = subprocess.run(
        ["python3", "-m", "meta_compiler.cli", "reconcile", str(tmp), "--section", "Analysis"],
        capture_output=True, text=True, env=_CLI_ENV,
    )
    # "increases" is in Setup, not Analysis — should not be flagged
    assert result.returncode == 0
    assert "increases" not in result.stdout.lower()
    tmp.unlink()
