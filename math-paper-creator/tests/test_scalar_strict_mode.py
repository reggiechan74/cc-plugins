"""Tests for scalar model auto-detection in strict mode."""
from meta_compiler.registry import registry
from meta_compiler import Parameter, Expression, Set
from meta_compiler.compiler import check_document


def test_strict_no_sets_suppresses_orphans(fresh_registry):
    """With strict=True but no Sets, orphan checking is skipped entirely."""
    Parameter("M", description="meeting hours")
    result = registry.run_tests(strict=True)
    # M is an orphan (never referenced), but no sets → skip orphan check
    orphan_errors = [e for e in result.errors if "Orphan" in e]
    orphan_warnings = [w for w in result.warnings if "Orphan" in w]
    assert len(orphan_errors) == 0, f"Orphans should not be errors: {orphan_errors}"
    assert len(orphan_warnings) == 0, f"Orphans should be suppressed: {orphan_warnings}"


def test_strict_with_sets_keeps_orphans_as_errors(fresh_registry):
    """With strict=True and Sets present, orphans remain errors."""
    Set("W", description="workers")
    Parameter("M", description="unused")
    registry.data_store["W"] = ["a"]
    result = registry.run_tests(strict=True)
    orphan_errors = [e for e in result.errors if "Orphan" in e]
    assert any("M" in e for e in orphan_errors), "M should be an orphan error"


def test_non_orphan_errors_unaffected_by_scalar_heuristic(fresh_registry):
    """Phantom errors should remain errors even in scalar models."""
    registry.access_log.add("nonexistent")
    result = registry.run_tests(strict=True)
    phantom_errors = [e for e in result.errors if "Phantom" in e]
    assert len(phantom_errors) > 0, "Phantoms should still be errors"


SCALAR_MODEL_STRICT = '''
```python:fixture
M = 5.0
H = 8.0
```

```python:validate
Parameter("M", description="meeting hours")
Parameter("H", description="total hours")
Expression("t_eff", definition=lambda: H - M, description="effective time")
```
'''


def test_check_document_strict_scalar_passes(fresh_registry):
    """check_document with strict=True on scalar model should pass (orphans demoted)."""
    result = check_document(SCALAR_MODEL_STRICT, strict=True)
    assert result.passed, f"Should pass but got errors: {result.errors}"
