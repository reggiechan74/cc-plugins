"""Tests for numpy type compatibility (issue #9).

These tests verify that numpy scalar types (np.float64, np.int64, np.True_)
are handled correctly in constraint evaluation, scalar detection, and
objective numeric checks.
"""
import pytest

from meta_compiler.compiler.executor import _coerce_bool, _is_numeric


class TestCoerceBool:
    def test_python_true(self):
        assert _coerce_bool(True) is True

    def test_python_false(self):
        assert _coerce_bool(False) is False

    def test_numpy_true(self):
        np = pytest.importorskip("numpy")
        assert _coerce_bool(np.True_) is True

    def test_numpy_false(self):
        np = pytest.importorskip("numpy")
        assert _coerce_bool(np.False_) is False

    def test_numpy_bool_from_comparison(self):
        np = pytest.importorskip("numpy")
        result = np.float64(3.0) <= np.float64(5.0)
        assert _coerce_bool(result) is True

    def test_none_is_falsy(self):
        assert _coerce_bool(None) is False

    def test_zero_is_falsy(self):
        assert _coerce_bool(0) is False


class TestIsNumeric:
    def test_python_int(self):
        assert _is_numeric(42) is True

    def test_python_float(self):
        assert _is_numeric(3.14) is True

    def test_string_not_numeric(self):
        assert _is_numeric("42") is False

    def test_none_not_numeric(self):
        assert _is_numeric(None) is False

    def test_numpy_float64(self):
        np = pytest.importorskip("numpy")
        assert _is_numeric(np.float64(3.14)) is True

    def test_numpy_int64(self):
        np = pytest.importorskip("numpy")
        assert _is_numeric(np.int64(42)) is True

    def test_numpy_int32(self):
        np = pytest.importorskip("numpy")
        assert _is_numeric(np.int32(7)) is True


class TestRegistryIsScalar:
    def test_python_scalars(self):
        from meta_compiler.registry import Registry
        assert Registry._is_scalar(42) is True
        assert Registry._is_scalar(3.14) is True
        assert Registry._is_scalar("hello") is True

    def test_non_scalars(self):
        from meta_compiler.registry import Registry
        assert Registry._is_scalar([1, 2]) is False
        assert Registry._is_scalar({"a": 1}) is False
        assert Registry._is_scalar(None) is False

    def test_numpy_scalars(self):
        np = pytest.importorskip("numpy")
        from meta_compiler.registry import Registry
        assert Registry._is_scalar(np.float64(3.14)) is True
        assert Registry._is_scalar(np.int64(42)) is True

    def test_numpy_array_not_scalar(self):
        np = pytest.importorskip("numpy")
        from meta_compiler.registry import Registry
        assert Registry._is_scalar(np.array([1, 2, 3])) is False


class TestEndToEndNumpy:
    """Integration tests using numpy values in fixture blocks."""

    def test_numpy_constraint_passes(self):
        np = pytest.importorskip("numpy")
        from meta_compiler.compiler.parser import parse_document
        from meta_compiler.compiler.executor import execute_blocks

        doc = '''# Model

```python:fixture
import numpy as np
W = ["alice", "bob"]
cap = {"alice": np.float64(40.0), "bob": np.float64(35.0)}
```

```python:validate
Set("W", description="Workers")
Parameter("cap", index="W", units="hours", description="Capacity")
Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
```
'''
        blocks = parse_document(doc)
        result = execute_blocks(blocks)
        assert result.passed, f"Expected pass, got errors: {result.errors}"

    def test_numpy_scalar_parameter(self):
        np = pytest.importorskip("numpy")
        from meta_compiler.compiler.parser import parse_document
        from meta_compiler.compiler.executor import execute_blocks

        doc = '''# Model

```python:fixture
import numpy as np
n_workers = np.int64(5)
```

```python:validate
Parameter("n_workers", description="Number of workers")
```
'''
        blocks = parse_document(doc)
        result = execute_blocks(blocks)
        assert result.passed, f"Expected pass, got errors: {result.errors}"

    def test_numpy_objective_accepted(self):
        np = pytest.importorskip("numpy")
        from meta_compiler.compiler.parser import parse_document
        from meta_compiler.compiler.executor import execute_blocks

        doc = '''# Model

```python:fixture
import numpy as np
total = np.float64(100.0)
```

```python:validate
Parameter("total", description="Total value")
Objective("maximize_total", expr=lambda: total, sense="maximize", description="Maximize total")
```
'''
        blocks = parse_document(doc)
        result = execute_blocks(blocks)
        assert result.passed, f"Expected pass, got errors: {result.errors}"
