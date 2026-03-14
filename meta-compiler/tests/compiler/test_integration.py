"""End-to-end integration test: parse → execute → generate all artifacts."""

import subprocess
import sys
from pathlib import Path

from meta_compiler.compiler import check_document, compile_document
from meta_compiler.compiler.parser import parse_document

# Build env with src/ on the Python path so subprocess CLI calls can find meta_compiler
_SRC = str(Path(__file__).parent.parent.parent / "src")
_CLI_ENV = {**__import__("os").environ, "PYTHONPATH": _SRC}


WORKFORCE_DOC = '''
<!-- depth:executive -->
# Workforce Optimization Model

## Executive Summary

This model optimizes worker-project assignments.

<!-- depth:technical -->
## Technical Framework

### 2.1 Index Sets

$$\\mathcal{W} = \\{w_1, w_2, \\ldots\\}$$

```python:validate
Set("W", description="Workers")
Set("P", description="Project types")
Set("T", description="Time periods")
```

### 2.2 Parameters

$$cap_i \\in \\mathbb{R}^+, \\quad \\forall i \\in \\mathcal{W}$$

```python:validate
cap = Parameter("cap", index=["W"], domain="nonneg_real",
                units="hours", description="Maximum capacity of worker i")
h = Parameter("h", index=["P"], domain="nonneg_real",
              units="hours", description="Effort-hours required per project type")
```

### 2.3 Decision Variables

$$x_{ijt} \\in [0, 1], \\quad \\forall i \\in \\mathcal{W}, j \\in \\mathcal{P}, t \\in \\mathcal{T}$$

```python:validate
x = Variable("x", index=["W", "P", "T"], domain="continuous",
             bounds=(0, 1), description="Allocation fraction")
```

### 2.4 Derived Expressions

$$\\text{load}_i = \\sum_{j \\in \\mathcal{P}} \\sum_{t \\in \\mathcal{T}} x_{ijt} \\cdot h_j$$

```python:validate
load = Expression("load",
    definition=lambda i: sum(x[i, j, t] * h[j] for j in S("P") for t in S("T")),
    index=["W"], units="hours",
    description="Total load on worker i")
```

### 2.5 Utility

```python:validate
U = Parameter("U", index=["W", "P", "T"], domain="real",
              units="dimensionless", description="Utility score")
```

### 2.6 Constraints

$$\\text{load}_i \\leq cap_i, \\quad \\forall i \\in \\mathcal{W}$$

```python:validate
Constraint("capacity_limit",
    expr=lambda i: load[i] <= cap[i],
    over=["W"], type="hard",
    description="No worker exceeds their capacity")
```

### 2.7 Objective

$$\\max \\sum_{i,j,t} x_{ijt} \\cdot U_{ijt}$$

```python:validate
Objective("maximize_utility",
    expr=lambda: sum(x[i, j, t] * U[i, j, t]
                     for i in S("W") for j in S("P") for t in S("T")),
    sense="maximize",
    description="Maximize total weighted utility across assignments")
```
'''


def test_full_pipeline_check():
    """Full document passes validation."""
    result = check_document(WORKFORCE_DOC)
    assert result.passed, f"Errors: {result.errors}"


def test_full_pipeline_compile():
    """Full document compiles to all three artifacts."""
    artifacts = compile_document(WORKFORCE_DOC)

    # Paper artifact
    paper = artifacts["paper"]
    assert "Workforce Optimization Model" in paper
    assert "python:validate" not in paper
    assert "Parameter(" not in paper

    # Codebase artifact
    codebase = artifacts["codebase"]
    assert "sets.py" in codebase
    assert "parameters.py" in codebase
    assert "variables.py" in codebase
    assert "__main__.py" in codebase
    assert "Set(" in codebase["sets.py"] and "W" in codebase["sets.py"]
    assert "Parameter(" in codebase["parameters.py"] and "cap" in codebase["parameters.py"]

    # Report artifact
    report = artifacts["report"]
    assert report.test_passed
    assert len(report.symbol_table) == 10  # W, P, T, cap, h, x, load, U, capacity_limit, maximize_utility
    assert report.coverage["total_math"] > 0


def test_full_pipeline_paper_depth_executive():
    """Executive depth filter shows only executive content."""
    artifacts = compile_document(WORKFORCE_DOC, depth="executive")
    paper = artifacts["paper"]
    assert "Executive Summary" in paper
    assert "Technical Framework" not in paper


def test_full_pipeline_compile_to_disk(tmp_path):
    """Full compile writes files to disk via CLI."""
    doc_path = tmp_path / "model.math.md"
    doc_path.write_text(WORKFORCE_DOC)

    out_dir = tmp_path / "output"

    result = subprocess.run(
        [sys.executable, "-m", "meta_compiler.cli", "compile",
         str(doc_path), "--output", str(out_dir)],
        capture_output=True, text=True, env=_CLI_ENV,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}\nstdout: {result.stdout}"
    assert (out_dir / "paper.md").exists()
    assert (out_dir / "model" / "sets.py").exists()
    assert (out_dir / "model" / "parameters.py").exists()
    assert (out_dir / "report.txt").exists()

    # Verify paper content
    paper = (out_dir / "paper.md").read_text()
    assert "python:validate" not in paper


MODEL_DOC = '''# Workforce Model

```python:fixture
W = ["alice", "bob"]
cap = {"alice": 40, "bob": 35}
```

$$\\text{cap}_i \\leq 100$$

```python:validate
Set("W", description="Workers")
Parameter("cap", index="W", units="hours", description="Capacity")
Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
```
'''


def test_compile_produces_paper_report_runner():
    result = compile_document(MODEL_DOC)
    assert "paper" in result
    assert "report_text" in result
    assert "runner" in result
    assert "python:fixture" not in result["paper"]
    assert "python:validate" not in result["paper"]
    assert "check_document" in result["runner"]


def test_compile_no_codebase_key():
    result = compile_document(MODEL_DOC)
    assert "codebase" not in result
