import os
import subprocess
import sys
from pathlib import Path

from meta_compiler.compiler import check_document, compile_document

# Build env with src/ on the Python path so subprocess CLI calls can find meta_compiler
_SRC = str(Path(__file__).parent.parent.parent / "src")
_CLI_ENV = {**os.environ, "PYTHONPATH": _SRC}


def test_check_document_valid():
    """check_document returns passing result for valid document."""
    doc = '''### Sets

```python:validate
Set("W", description="Workers")
```
'''
    result = check_document(doc)
    assert result.passed


def test_check_document_invalid():
    """check_document returns failing result for invalid document."""
    doc = '''
```python:validate
Parameter("cap", index=["W"], description="Missing set")
```
'''
    result = check_document(doc)
    assert not result.passed


def test_compile_document_produces_artifacts():
    """compile_document returns paper, codebase, and report."""
    doc = '''### Sets

$$\\mathcal{W}$$

```python:validate
Set("W", description="Workers")
cap = Parameter("cap", index=["W"], description="Capacity")
x = Variable("x", index=["W"], domain="continuous",
             bounds=(0, 1), description="Allocation")
Constraint("limit", expr=lambda i: x[i] <= cap[i],
           over=["W"], description="Cap limit")
```
'''
    artifacts = compile_document(doc)
    assert "paper" in artifacts
    assert "codebase" in artifacts
    assert "report" in artifacts
    assert isinstance(artifacts["codebase"], dict)
    assert "Parameter(" not in artifacts["paper"]


def test_cli_check_valid_file(tmp_path):
    """CLI check command exits 0 for valid document."""
    doc_path = tmp_path / "test.math.md"
    doc_path.write_text('''
```python:validate
Set("W", description="Workers")
```
''')
    result = subprocess.run(
        [sys.executable, "-m", "meta_compiler.cli", "check", str(doc_path)],
        capture_output=True, text=True, env=_CLI_ENV,
    )
    assert result.returncode == 0
    assert "PASSED" in result.stdout


def test_cli_check_invalid_file(tmp_path):
    """CLI check command exits 1 for invalid document."""
    doc_path = tmp_path / "test.math.md"
    doc_path.write_text('''
```python:validate
Parameter("cap", index=["W"], description="Missing set")
```
''')
    result = subprocess.run(
        [sys.executable, "-m", "meta_compiler.cli", "check", str(doc_path)],
        capture_output=True, text=True, env=_CLI_ENV,
    )
    assert result.returncode == 1
    assert "FAILED" in result.stdout or "BLOCK" in result.stdout


def test_cli_compile_writes_artifacts(tmp_path):
    """CLI compile command writes artifact files."""
    doc_path = tmp_path / "test.math.md"
    doc_path.write_text('''### Sets

$$\\mathcal{W}$$

```python:validate
Set("W", description="Workers")
cap = Parameter("cap", index=["W"], description="Capacity")
x = Variable("x", index=["W"], domain="continuous",
             bounds=(0, 1), description="Allocation")
Constraint("limit", expr=lambda i: x[i] <= cap[i],
           over=["W"], description="Cap limit")
```
''')
    out_dir = tmp_path / "output"
    result = subprocess.run(
        [sys.executable, "-m", "meta_compiler.cli", "compile",
         str(doc_path), "--output", str(out_dir)],
        capture_output=True, text=True, env=_CLI_ENV,
    )
    assert result.returncode == 0
    assert (out_dir / "paper.md").exists()
    assert (out_dir / "model" / "sets.py").exists()
    assert (out_dir / "report.txt").exists()
