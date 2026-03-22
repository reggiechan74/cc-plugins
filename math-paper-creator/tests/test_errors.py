import pytest
from meta_compiler import Set, Parameter, Variable, Expression, Constraint, S
from meta_compiler.symbols import ExpressionSymbol


def test_symbol_conflict_message(fresh_registry):
    """Error message for symbol conflict matches spec format."""
    Set("W", description="Workers")
    Parameter("F", index="W", units="dimensionless",
              description="fragility decay rate (dimensionless)")
    with pytest.raises(ValueError) as exc_info:
        Parameter("F", index="W", units="points",
                  description="fragility-resilience rubric score (points)")
    msg = str(exc_info.value)
    assert 'Symbol "F" already registered' in msg
    assert "fragility decay rate" in msg


def test_undefined_reference_message(fresh_registry):
    """Error message for undefined set reference matches spec format."""
    with pytest.raises(ValueError) as exc_info:
        Parameter("cap", index="W", units="hours",
                  description="Capacity")
    msg = str(exc_info.value)
    assert 'references set "W"' in msg
    assert "not registered" in msg


def test_phantom_error_message(fresh_registry):
    """Phantom detection error names the exact symbol."""
    Set("W", description="Workers")
    Variable("x", index="W", domain="continuous",
             bounds=(0, 1), description="Allocation")
    # Access a symbol that was never registered
    fresh_registry.access_log.add("h")
    result = fresh_registry.run_tests()
    assert not result.passed
    assert any('"h"' in e and "never declared" in e for e in result.errors)


def test_dimensional_error_message(fresh_registry):
    """Dimensional inconsistency error names units on both sides."""
    fresh_registry.data_store["W"] = ["alice"]
    fresh_registry.data_store["hours_val"] = {"alice": 8}
    fresh_registry.data_store["heads_val"] = {"alice": 1}
    Set("W", description="Workers")
    hours_param = Parameter("hours_val", index="W", units="hours",
                            description="Hours value")
    heads_param = Parameter("heads_val", index="W", units="headcount",
                            description="Headcount value")
    Constraint("bad",
        expr=lambda i: hours_val[i] <= heads_val[i],
        over="W", description="Comparing incompatible units")
    result = fresh_registry.run_tests()
    assert not result.passed
    dimensional_errors = [e for e in result.errors if "unit" in e.lower()]
    assert len(dimensional_errors) >= 1
    assert "hours" in dimensional_errors[0]
    assert "headcount" in dimensional_errors[0]


def test_cycle_error_message(fresh_registry):
    """Cycle detection error shows the cycle path."""
    Set("W", description="Workers")
    # Create expression symbols with circular references via source text
    fn_load = lambda i: utilization[i]
    fn_load._source_text = "lambda i: utilization[i]"
    fn_util = lambda i: adjusted_cap[i]
    fn_util._source_text = "lambda i: adjusted_cap[i]"
    fn_adj = lambda i: load[i]
    fn_adj._source_text = "lambda i: load[i]"
    sym_a = ExpressionSymbol(name="load", index=("W",), units="dimensionless",
                             description="Load", expr=fn_load)
    sym_b = ExpressionSymbol(name="utilization", index=("W",), units="dimensionless",
                             description="Utilization", expr=fn_util)
    sym_c = ExpressionSymbol(name="adjusted_cap", index=("W",), units="dimensionless",
                             description="Adjusted cap", expr=fn_adj)
    for s in [sym_a, sym_b, sym_c]:
        fresh_registry.symbols[s.name] = s
        fresh_registry._registration_order.append(s.name)
    result = fresh_registry.run_tests()
    assert not result.passed
    cycle_errors = [e for e in result.errors if "cycle" in e.lower()]
    assert len(cycle_errors) >= 1
    assert "load" in cycle_errors[0]


def test_orphan_error_message_strict(fresh_registry):
    """Orphan error names the unused symbol."""
    Set("W", description="Workers")
    Parameter("buildability", index="W", units="dimensionless",
              description="Buildability score")
    result = fresh_registry.run_tests(strict=True)
    assert not result.passed
    assert any('"buildability"' in e for e in result.errors)
    assert any("never referenced" in e for e in result.errors)


def test_unregistered_fixture_variable_helpful_message(fresh_registry):
    """Constraint referencing fixture var not registered as Parameter gives helpful error."""
    from meta_compiler.compiler.parser import parse_document
    from meta_compiler.compiler.executor import execute_blocks

    doc = '''# Model

```python:fixture
Hf_C0 = 42.0
```

```python:validate
Constraint("C0_recovers_base_Hf", expr=lambda: Hf_C0 > 0, description="Check base enthalpy")
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    assert not result.passed
    msgs = [e for e in result.errors if "Hf_C0" in e]
    assert len(msgs) >= 1
    assert "computed in fixture" in msgs[0]
    assert 'add Parameter("Hf_C0"' in msgs[0]


def test_truly_undefined_variable_generic_error(fresh_registry):
    """Constraint referencing a truly undefined name gives the generic NameError."""
    from meta_compiler.compiler.parser import parse_document
    from meta_compiler.compiler.executor import execute_blocks

    doc = '''# Model

```python:fixture
dummy = 1
```

```python:validate
Constraint("uses_nonexistent", expr=lambda: totally_bogus_var > 0, description="References nothing")
```
'''
    blocks = parse_document(doc)
    result = execute_blocks(blocks)
    assert not result.passed
    msgs = [e for e in result.errors if "totally_bogus_var" in e]
    assert len(msgs) >= 1
    assert "computed in fixture" not in msgs[0]
    assert "Error in constraint" in msgs[0]
