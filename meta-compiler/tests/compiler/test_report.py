from meta_compiler.compiler.report import generate_report, Report
from meta_compiler.compiler.parser import parse_document
from meta_compiler.compiler.executor import execute_blocks


def test_report_symbol_table():
    """Report includes a symbol table with all registered symbols."""
    doc = '''
```python:validate
Set("W", description="Workers")
cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
x = Variable("x", index=["W"], domain="continuous",
             bounds=(0, 1), description="Allocation")
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    report = generate_report(result.registry, blocks)

    assert len(report.symbol_table) == 3
    names = [s["name"] for s in report.symbol_table]
    assert "W" in names
    assert "cap" in names
    assert "x" in names


def test_report_dependency_graph():
    """Report includes dependency edges."""
    doc = '''
```python:validate
Set("W", description="Workers")
Set("P", description="Projects")
cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
h = Parameter("h", index=["P"], units="hours", description="Effort")
x = Variable("x", index=["W", "P"], domain="continuous",
             bounds=(0, 1), description="Allocation")
```

```python:validate
load = Expression("load",
    definition=lambda i: sum(x[i, j] * h[j] for j in S("P")),
    index=["W"], units="hours", description="Total load")
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    report = generate_report(result.registry, blocks)

    # load depends on x and h
    load_deps = [e for e in report.dependencies if e["from"] == "load"]
    dep_targets = [e["to"] for e in load_deps]
    assert "x" in dep_targets
    assert "h" in dep_targets


def test_report_to_text():
    """Report renders as readable text."""
    doc = '''
```python:validate
Set("W", description="Workers")
cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
x = Variable("x", index=["W"], domain="continuous",
             bounds=(0, 1), description="Allocation")
Constraint("limit", expr=lambda i: x[i] <= cap[i],
           over=["W"], description="Cap limit")
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    report = generate_report(result.registry, blocks)
    text = report.to_text()

    assert "VALIDATION REPORT" in text
    assert "Symbol Table" in text
    assert "cap" in text
    assert "Workers" in text


def test_report_coverage_section():
    """Report includes coverage information."""
    doc = '''
$$x = 1$$

```python:validate
Set("W", description="Workers")
```

$$y = 2$$
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    report = generate_report(result.registry, blocks)

    assert report.coverage["total_math"] == 2
    assert report.coverage["covered_math"] == 1
