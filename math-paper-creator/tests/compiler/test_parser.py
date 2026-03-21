"""Tests for the document parser module."""

from meta_compiler.compiler.parser import (
    parse_document,
    ProseBlock,
    MathBlock,
    ValidationBlock,
    coverage_metric,
    CoverageResult,
)


def test_parse_prose_only():
    """Plain markdown produces a single prose block."""
    doc = "# Hello\n\nSome text here.\n"
    blocks = parse_document(doc)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ProseBlock)
    assert blocks[0].content == "# Hello\n\nSome text here.\n"


def test_parse_display_math_single_line():
    """Single-line $$...$$ produces a MathBlock."""
    doc = "$$x^2 + y^2 = r^2$$\n"
    blocks = parse_document(doc)
    assert len(blocks) == 1
    assert isinstance(blocks[0], MathBlock)
    assert blocks[0].content == "x^2 + y^2 = r^2"


def test_parse_display_math_multi_line():
    """Multi-line $$...$$ produces a MathBlock."""
    doc = "$$\nx^2 + y^2\n= r^2\n$$\n"
    blocks = parse_document(doc)
    assert len(blocks) == 1
    assert isinstance(blocks[0], MathBlock)
    assert "x^2 + y^2" in blocks[0].content


def test_parse_validation_block():
    doc = '```python:validate\ncap = Parameter("cap")\nregistry.run_tests()\n```\n'
    blocks = parse_document(doc)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ValidationBlock)
    assert 'Parameter("cap")' in blocks[0].code
    assert "registry.run_tests()" in blocks[0].code


def test_parse_validation_block_tracks_line_number():
    doc = "# Title\n\nSome prose.\n\n```python:validate\ncode_here()\n```\n"
    blocks = parse_document(doc)
    vblocks = [b for b in blocks if isinstance(b, ValidationBlock)]
    assert len(vblocks) == 1
    assert vblocks[0].line_number == 5  # 0-indexed: line after the fence


def test_parse_mixed_document():
    doc = """### 2.1 Worker Capacity

Each worker $i \\in \\mathcal{W}$ has a maximum available capacity:

$$cap_i \\in \\mathbb{R}^+, \\quad \\forall i \\in \\mathcal{W}$$

```python:validate
cap = Parameter("cap", index=["W"], domain="nonneg_real",
                units="hours", description="Maximum capacity of worker i")
registry.run_tests()
```

### 2.2 Next Section

More prose here.
"""
    blocks = parse_document(doc)
    types = [type(b).__name__ for b in blocks]
    assert "ProseBlock" in types
    assert "MathBlock" in types
    assert "ValidationBlock" in types
    assert isinstance(blocks[0], ProseBlock)
    assert "Worker Capacity" in blocks[0].content


def test_regular_code_fence_not_captured():
    doc = "```python\nprint('hello')\n```\n"
    blocks = parse_document(doc)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ProseBlock)


def test_depth_markers_in_prose():
    doc = "<!-- depth:executive -->\n# Executive Summary\n\nKey findings.\n<!-- depth:technical -->\n# Details\n\nThe math.\n"
    blocks = parse_document(doc)
    full_text = "".join(b.content for b in blocks if isinstance(b, ProseBlock))
    assert "<!-- depth:executive -->" in full_text
    assert "<!-- depth:technical -->" in full_text


def test_coverage_metric_all_covered():
    doc = "$$x = 1$$\n\n```python:validate\ncode()\n```\n"
    result = coverage_metric(parse_document(doc))
    assert result.total_math == 1
    assert result.covered_math == 1
    assert result.uncovered_sections == []


def test_coverage_metric_uncovered():
    doc = "### 2.1\n\n$$x = 1$$\n\n### 2.2\n\n$$y = 2$$\n\n```python:validate\ncode()\n```\n"
    result = coverage_metric(parse_document(doc))
    assert result.total_math == 2
    assert result.covered_math == 1
    assert len(result.uncovered_sections) == 1


from meta_compiler.compiler.parser import parse_document, FixtureBlock, ResultsBlock

def test_parse_fixture_block():
    source = '''# Model

```python:fixture
sets = {"W": ["alice", "bob"]}
cap = {"alice": 40, "bob": 35}
```
'''
    blocks = parse_document(source)
    fixture_blocks = [b for b in blocks if isinstance(b, FixtureBlock)]
    assert len(fixture_blocks) == 1
    assert 'sets = {"W":' in fixture_blocks[0].code

def test_parse_mixed_blocks():
    source = '''# Model

```python:fixture
cap = {"alice": 40}
```

$$x + y = z$$

```python:validate
Set("W", description="Workers")
```
'''
    blocks = parse_document(source)
    from meta_compiler.compiler.parser import FixtureBlock, MathBlock, ValidationBlock, ProseBlock
    types = [type(b).__name__ for b in blocks]
    assert "FixtureBlock" in types
    assert "MathBlock" in types
    assert "ValidationBlock" in types

def test_parse_results_block():
    source = '''# Model

```python:fixture
x = 42
```

```python:results
print(f"x = {x}")
```
'''
    blocks = parse_document(source)
    results_blocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    assert len(results_blocks) == 1
    assert 'print(f"x = {x}")' in results_blocks[0].code


def test_parse_results_block_tracks_line_number():
    source = "# Title\n\n```python:results\nprint('hi')\n```\n"
    blocks = parse_document(source)
    rblocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    assert len(rblocks) == 1
    assert rblocks[0].line_number == 3  # 1-indexed line of the fence (matches FixtureBlock/ValidationBlock pattern)


def test_coverage_results_does_not_interrupt():
    """A results block between math and validate doesn't break coverage."""
    source = '''# Model

$$x = 1$$

```python:results
print("x is 1")
```

```python:validate
Parameter("x", description="x value")
```
'''
    from meta_compiler.compiler.parser import coverage_metric
    blocks = parse_document(source)
    result = coverage_metric(blocks)
    assert result.covered_math == 1


def test_coverage_fixture_does_not_interrupt():
    """A math block followed by fixture then validate counts as covered."""
    source = '''# Model

$$x = 1$$

```python:fixture
x_val = {"a": 1}
```

```python:validate
Parameter("x", description="x value")
```
'''
    from meta_compiler.compiler.parser import coverage_metric
    blocks = parse_document(source)
    result = coverage_metric(blocks)
    assert result.covered_math == 1
