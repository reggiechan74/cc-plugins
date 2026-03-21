from meta_compiler.compiler.paper import generate_paper
from meta_compiler.compiler.parser import parse_document, FixtureBlock, ResultsBlock


def test_paper_strips_validation_blocks():
    """Paper output includes prose and math but not validation blocks."""
    doc = """### 2.1 Worker Capacity

Each worker has a maximum capacity:

$$cap_i \\in \\mathbb{R}^+$$

```python:validate
cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
registry.run_tests()
```

### 2.2 Next Section
"""
    blocks = parse_document(doc)
    paper = generate_paper(blocks)
    assert "Worker Capacity" in paper
    assert "$$cap_i" in paper
    assert "Parameter(" not in paper
    assert "registry.run_tests()" not in paper
    assert "python:validate" not in paper
    assert "Next Section" in paper


def test_paper_depth_executive():
    """Executive depth filter shows only executive content."""
    doc = """<!-- depth:executive -->
# Executive Summary

Key findings.

<!-- depth:technical -->
# Technical Details

$$x = 1$$

The math details.
"""
    blocks = parse_document(doc)
    paper = generate_paper(blocks, depth="executive")
    assert "Executive Summary" in paper
    assert "Key findings" in paper
    assert "Technical Details" not in paper


def test_paper_depth_technical():
    """Technical depth filter shows executive and technical content."""
    doc = """<!-- depth:executive -->
# Executive Summary

Key findings.

<!-- depth:technical -->
# Technical Details

$$x = 1$$

<!-- depth:appendix -->
# Appendix

Proofs and derivations.
"""
    blocks = parse_document(doc)
    paper = generate_paper(blocks, depth="technical")
    assert "Executive Summary" in paper
    assert "Technical Details" in paper
    assert "Appendix" not in paper


def test_paper_no_depth_filter():
    """No depth filter includes everything."""
    doc = """<!-- depth:executive -->
# Executive Summary

<!-- depth:appendix -->
# Appendix
"""
    blocks = parse_document(doc)
    paper = generate_paper(blocks)
    assert "Executive Summary" in paper
    assert "Appendix" in paper


def test_paper_strips_fixture_blocks():
    source = '''# Model

Some prose.

```python:fixture
cap = {"alice": 40}
```

$$x + y$$

```python:validate
Set("W")
```

More prose.
'''
    blocks = parse_document(source)
    paper = generate_paper(blocks)
    assert "python:fixture" not in paper
    assert "cap =" not in paper
    assert "Some prose" in paper
    assert "$$x + y$$" in paper
    assert "More prose" in paper
    assert "python:validate" not in paper


def test_paper_includes_results_output():
    """Results block output appears in paper, code does not."""
    source = '''# Model

Some prose.

```python:fixture
x = 42
```

```python:results
print(f"The answer is {x}.")
```

```python:validate
Parameter("x", description="the answer")
```

More prose.
'''
    from meta_compiler.compiler.executor import execute_blocks
    blocks = parse_document(source)
    execute_blocks(blocks)  # populates ResultsBlock.output
    paper = generate_paper(blocks)
    assert "The answer is 42." in paper
    assert "python:results" not in paper
    assert "python:fixture" not in paper
    assert "python:validate" not in paper
    assert "Some prose" in paper
    assert "More prose" in paper


def test_paper_empty_results_omitted():
    """A results block that prints nothing is silently omitted."""
    source = '''# Model

```python:results
pass  # no output
```

Some prose.
'''
    blocks = parse_document(source)
    from meta_compiler.compiler.executor import execute_blocks
    execute_blocks(blocks)
    rblocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    assert rblocks[0].output == ""
    paper = generate_paper(blocks)
    assert "python:results" not in paper
    assert "Some prose" in paper


def test_paper_results_with_depth_filter():
    """Results blocks respect depth filtering."""
    source = '''<!-- depth:executive -->
# Summary

Key findings.

<!-- depth:appendix -->
# Appendix

```python:results
print("Detailed computation log")
```
'''
    blocks = parse_document(source)
    from meta_compiler.compiler.executor import execute_blocks
    execute_blocks(blocks)
    paper = generate_paper(blocks, depth="executive")
    assert "Key findings" in paper
    assert "Detailed computation log" not in paper
