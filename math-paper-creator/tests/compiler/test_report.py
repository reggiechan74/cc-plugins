from meta_compiler.compiler.report import generate_report, Report
from meta_compiler.compiler.parser import parse_document
from meta_compiler.compiler.executor import execute_blocks
from meta_compiler.registry import registry


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
    report = generate_report(blocks, registry=result.registry)

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
    report = generate_report(blocks, registry=result.registry)

    # In v2, dependency graph uses structural refs (index/over fields)
    # load has index=("W",), so it depends on W
    load_deps = [e for e in report.dependencies if e["from"] == "load"]
    dep_targets = [e["to"] for e in load_deps]
    assert "W" in dep_targets


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
    report = generate_report(blocks, registry=result.registry)
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
    report = generate_report(blocks, registry=result.registry)

    assert report.coverage["total_math"] == 2
    assert report.coverage["covered_math"] == 1


def test_report_generates_without_expr_tree():
    registry.reset()
    registry.data_store = {"W": ["a"], "cap": {"a": 40}}
    registry.register_set("W", description="Workers")
    registry.register_parameter("cap", index="W", units="hours", description="Cap")
    registry.register_constraint("check", over="W", constraint_type="hard",
                                 description="Check", expr=lambda i: True)
    blocks = parse_document("# test\n$$x$$\n```python:validate\nSet('W')\n```\n")
    report = generate_report(blocks, registry=registry)
    assert report.symbol_table is not None
    text = report.to_text()
    assert "cap" in text


def test_generate_report_blocks_first_signature(fresh_registry):
    """generate_report takes blocks as first positional arg, registry as keyword-only."""
    from meta_compiler.compiler.report import generate_report
    from meta_compiler.compiler.parser import parse_document
    from meta_compiler.registry import registry
    from meta_compiler import Set, Parameter

    Set("W", description="workers")
    registry.data_store["W"] = ["a", "b"]

    source = '''
Some prose.

```python:validate
Set("W", description="workers")
Parameter("cap", index="W", description="capacity")
```
'''
    blocks = parse_document(source)
    report = generate_report(blocks, registry=registry)
    assert report.test_passed is not None


def test_report_str_delegates_to_to_text():
    """str(report) should produce the same output as report.to_text()."""
    report = Report(
        symbol_table=[{"name": "x", "type": "Variable", "description": "test"}],
        dependencies=[],
        test_passed=True,
        test_errors=[],
        test_warnings=[],
        coverage={"total_math": 1, "covered_math": 1, "uncovered_sections": []},
    )
    assert str(report) == report.to_text()
    assert repr(report) != str(report)  # __str__ is not __repr__
