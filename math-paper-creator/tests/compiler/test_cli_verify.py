import pytest
z3 = pytest.importorskip("z3")

from meta_compiler.cli import main


CONSISTENT_DOC = '''# Model

```python:validate
from z3 import Real
H = Real('H')
Axiom("A1", statement="H > 0", z3_expr=lambda: H > 0, description="Pos")
```
'''

CONTRADICTORY_DOC = '''# Model

```python:validate
from z3 import Real
H = Real('H')
Axiom("A1", statement="H > 0", z3_expr=lambda: H > 0, description="Pos")
Axiom("A2", statement="H < 0", z3_expr=lambda: H < 0, description="Neg")
```
'''


def test_cli_verify_consistent(tmp_path):
    f = tmp_path / "test.model.md"
    f.write_text(CONSISTENT_DOC)
    result = main(["verify", str(f)])
    assert result == 0


def test_cli_verify_contradictory(tmp_path):
    f = tmp_path / "test.model.md"
    f.write_text(CONTRADICTORY_DOC)
    result = main(["verify", str(f)])
    assert result == 1
