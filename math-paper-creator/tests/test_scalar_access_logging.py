"""Tests that scalar symbols are correctly logged during execution."""
from meta_compiler.compiler import check_document


SCALAR_MODEL = '''
```python:fixture
M = 5.0
beta = 0.8
H = 8.0
```

```python:validate
Parameter("M", description="meeting hours")
Parameter("beta", description="productivity factor")
Parameter("H", description="total hours")
Expression("t_eff", definition=lambda: H - M * beta, description="effective time")
```
'''


def test_scalar_refs_not_flagged_as_orphans(fresh_registry):
    """Scalar symbols used in expressions should not be orphans."""
    result = check_document(SCALAR_MODEL, strict=True)
    orphan_warnings = [w for w in result.warnings if "Orphan" in w]
    orphan_errors = [e for e in result.errors if "Orphan" in e]
    # M, beta, H are all referenced in the expression — none should be orphans
    assert not any("M" in w for w in orphan_warnings), f"M flagged as orphan: {orphan_warnings}"
    assert not any("M" in e for e in orphan_errors), f"M flagged as orphan error: {orphan_errors}"
    assert not any("beta" in w for w in orphan_warnings)
    assert not any("H" in w for w in orphan_warnings)


MIXED_MODEL = '''
```python:fixture
W = ["alice", "bob"]
cap = {"alice": 10, "bob": 20}
overhead = 5.0
```

```python:validate
Set("W", description="workers")
Parameter("cap", index="W", description="capacity")
Parameter("overhead", description="fixed overhead")
Expression("total", definition=lambda: cap[S("W")[0]] + overhead, description="total")
```
'''


def test_mixed_model_scalar_refs_logged(fresh_registry):
    """In mixed models, scalar refs should still be logged correctly."""
    result = check_document(MIXED_MODEL, strict=True)
    # overhead is scalar but referenced in expression — should not be orphan
    orphan_msgs = result.errors + result.warnings
    assert not any("overhead" in m for m in orphan_msgs if "Orphan" in m)
