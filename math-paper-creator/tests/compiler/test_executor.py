import pytest
from meta_compiler.compiler.parser import parse_document
from meta_compiler.compiler.executor import execute_blocks

STRUCTURAL_DOC = '''# Model

```python:validate
Set("W", description="Workers")
Parameter("cap", index="W", units="hours", description="Capacity")
Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
```
'''

NUMERIC_DOC = '''# Model

```python:fixture
W = ["alice", "bob"]
cap = {"alice": 40, "bob": 35}
```

```python:validate
Set("W", description="Workers")
Parameter("cap", index="W", units="hours", description="Capacity")
Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
```
'''

NUMERIC_FAIL_DOC = '''# Model

```python:fixture
W = ["alice", "bob"]
cap = {"alice": 40, "bob": 150}
```

```python:validate
Set("W", description="Workers")
Parameter("cap", index="W", units="hours", description="Capacity")
Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
```
'''

def test_structural_mode_no_fixture():
    blocks = parse_document(STRUCTURAL_DOC)
    result = execute_blocks(blocks)
    assert result.passed

def test_numeric_mode_with_fixture_pass():
    blocks = parse_document(NUMERIC_DOC)
    result = execute_blocks(blocks)
    assert result.passed

def test_numeric_mode_constraint_failure():
    blocks = parse_document(NUMERIC_FAIL_DOC)
    result = execute_blocks(blocks)
    assert not result.passed
    assert any("check" in e and "bob" in e for e in result.errors)
