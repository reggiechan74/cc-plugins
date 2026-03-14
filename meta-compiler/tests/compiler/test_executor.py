from meta_compiler.compiler.executor import execute_blocks, ExecutionResult
from meta_compiler.compiler.parser import parse_document


def test_execute_valid_blocks():
    """Executing valid validation blocks returns success."""
    doc = '''
```python:validate
Set("W", description="Workers")
```

```python:validate
cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
registry.run_tests()
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    assert result.passed
    assert len(result.errors) == 0


def test_execute_duplicate_symbol_error():
    """Re-registering a symbol produces a clear error."""
    doc = '''
```python:validate
Set("W", description="Workers")
```

```python:validate
Set("W", description="Something else")
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    assert not result.passed
    assert any("already registered" in e for e in result.errors)


def test_execute_undefined_reference_error():
    """Referencing an undefined set produces an error."""
    doc = '''
```python:validate
Parameter("cap", index=["W"], units="hours", description="Capacity")
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    assert not result.passed
    assert any("not registered" in e for e in result.errors)


def test_execute_syntax_error():
    """Syntax errors in validation blocks produce clear errors."""
    doc = '''
```python:validate
def this is bad syntax +++
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    assert not result.passed
    assert len(result.errors) > 0


def test_execute_strict_mode_orphan():
    """Strict mode catches orphan symbols."""
    doc = '''
```python:validate
Set("W", description="Workers")
cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks, strict=True)
    assert not result.passed
    assert any("cap" in e for e in result.errors)


def test_execute_cross_block_references():
    """Variables defined in one block are accessible in later blocks."""
    doc = '''
```python:validate
Set("W", description="Workers")
Set("P", description="Projects")
```

```python:validate
cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
h = Parameter("h", index=["P"], units="hours", description="Effort")
```

```python:validate
x = Variable("x", index=["W", "P"], domain="continuous",
             bounds=(0, 1), description="Allocation")
```

```python:validate
Constraint("capacity_limit",
    expr=lambda i: sum(x[i, j] * h[j] for j in S("P")) <= cap[i],
    over=["W"], description="No worker exceeds capacity")
registry.run_tests()
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    assert result.passed, f"Errors: {result.errors}"
    assert len(result.registry.symbols) == 6  # W, P, cap, h, x, capacity_limit
