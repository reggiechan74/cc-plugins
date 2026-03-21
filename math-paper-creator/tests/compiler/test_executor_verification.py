import pytest
z3 = pytest.importorskip("z3")

from meta_compiler.compiler.parser import parse_document
from meta_compiler.compiler.executor import execute_blocks


CONSISTENT_AXIOM_DOC = '''# Model

```python:validate
from z3 import Real
H = Real('H')
M = Real('M')
Axiom("A1", statement="H is positive", z3_expr=lambda: H > 0, description="Positivity")
Axiom("A2", statement="M bounded by H", z3_expr=lambda: M <= H, description="Bound")
```
'''


def test_consistent_axioms_pass():
    blocks = parse_document(CONSISTENT_AXIOM_DOC)
    result = execute_blocks(blocks)
    assert result.passed, f"Errors: {result.errors}"


CONTRADICTORY_AXIOM_DOC = '''# Model

```python:validate
from z3 import Real
H = Real('H')
Axiom("A1", statement="H is positive", z3_expr=lambda: H > 0, description="Pos")
Axiom("A2", statement="H is negative", z3_expr=lambda: H < 0, description="Neg")
```
'''


def test_contradictory_axioms_fail():
    blocks = parse_document(CONTRADICTORY_AXIOM_DOC)
    result = execute_blocks(blocks)
    assert not result.passed
    assert any("contradictory" in e.lower() for e in result.errors)


PROPERTY_HOLDS_DOC = '''# Model

```python:validate
from z3 import Real
H = Real('H')
M = Real('M')
Axiom("A1", statement="H positive", z3_expr=lambda: H > 0, description="Pos")
Axiom("A2", statement="M non-negative", z3_expr=lambda: M >= 0, description="Non-neg")
Axiom("A3", statement="M bounded by H", z3_expr=lambda: M <= H, description="Bound")
Property("P1", claim="H - M >= 0", z3_expr=lambda: H - M >= 0, given=["A1", "A2", "A3"], description="Non-neg effective")
```
'''


def test_property_holds_passes():
    blocks = parse_document(PROPERTY_HOLDS_DOC)
    result = execute_blocks(blocks)
    assert result.passed, f"Errors: {result.errors}"


PROPERTY_FAILS_DOC = '''# Model

```python:validate
from z3 import Real
H = Real('H')
M = Real('M')
Axiom("A1", statement="H positive", z3_expr=lambda: H > 0, description="Pos")
Axiom("A2", statement="M non-negative", z3_expr=lambda: M >= 0, description="Non-neg")
Property("P1", claim="H - M >= 0", z3_expr=lambda: H - M >= 0, given=["A1", "A2"], description="Non-neg effective")
```
'''


def test_property_fails_with_counterexample():
    blocks = parse_document(PROPERTY_FAILS_DOC)
    result = execute_blocks(blocks)
    assert not result.passed
    assert any("P1" in e and "does NOT follow" in e for e in result.errors)


NO_Z3_EXPR_DOC = '''# Model

```python:validate
Axiom("A1", statement="H is positive", description="Positivity")
```
'''


def test_axiom_without_z3_expr_skips_verification():
    """Axioms without z3_expr should register fine and skip verification."""
    blocks = parse_document(NO_Z3_EXPR_DOC)
    result = execute_blocks(blocks)
    assert result.passed
