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


RESULTS_DOC = '''# Model

```python:fixture
W = ["alice", "bob"]
cap = {"alice": 40, "bob": 35}
```

```python:results
for w in W:
    print(f"| {w} | {cap[w]} |")
```

```python:validate
Set("W", description="Workers")
Parameter("cap", index="W", units="hours", description="Capacity")
Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
```
'''

def test_results_block_captures_stdout():
    from meta_compiler.compiler.parser import ResultsBlock
    blocks = parse_document(RESULTS_DOC)
    result = execute_blocks(blocks)
    assert result.passed
    rblocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    assert len(rblocks) == 1
    assert "| alice | 40 |" in rblocks[0].output
    assert "| bob | 35 |" in rblocks[0].output


RESULTS_ERROR_DOC = '''# Model

```python:fixture
x = 1
```

```python:results
print(undefined_var)
```
'''

def test_results_block_error_fails_compilation():
    blocks = parse_document(RESULTS_ERROR_DOC)
    result = execute_blocks(blocks)
    assert not result.passed
    assert any("Results error" in e for e in result.errors)


RESULTS_NO_FIXTURE_DOC = '''# Model

```python:results
print("no fixtures needed for simple text")
```
'''

def test_results_block_without_fixtures():
    from meta_compiler.compiler.parser import ResultsBlock
    blocks = parse_document(RESULTS_NO_FIXTURE_DOC)
    result = execute_blocks(blocks)
    assert result.passed
    rblocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    assert rblocks[0].output == "no fixtures needed for simple text\n"


RESULTS_MULTI_DOC = '''# Model

```python:fixture
x = 10
y = 20
```

```python:results
print(f"x = {x}")
```

Some prose.

```python:results
print(f"y = {y}")
print(f"sum = {x + y}")
```
'''

def test_multiple_results_blocks():
    from meta_compiler.compiler.parser import ResultsBlock
    blocks = parse_document(RESULTS_MULTI_DOC)
    result = execute_blocks(blocks)
    assert result.passed
    rblocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    assert len(rblocks) == 2
    assert "x = 10" in rblocks[0].output
    assert "y = 20" in rblocks[1].output
    assert "sum = 30" in rblocks[1].output
