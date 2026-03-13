import pytest
from meta_compiler import Set, Parameter, Variable, Expression, Constraint, S
from meta_compiler.symbols import ExpressionSymbol
from meta_compiler.expr import IndexExpr, ArithExpr
from meta_compiler.units import parse_unit


def test_symbol_conflict_message(fresh_registry):
    """Error message for symbol conflict matches spec format."""
    Set("W", description="Workers")
    Parameter("F", index=["W"], units="dimensionless",
              description="fragility decay rate (dimensionless)")
    with pytest.raises(ValueError) as exc_info:
        Parameter("F", index=["W"], units="points",
                  description="fragility-resilience rubric score (points)")
    msg = str(exc_info.value)
    assert 'Symbol "F" already registered' in msg
    assert "fragility decay rate" in msg


def test_undefined_reference_message(fresh_registry):
    """Error message for undefined set reference matches spec format."""
    with pytest.raises(ValueError) as exc_info:
        Parameter("cap", index=["W"], units="hours",
                  description="Capacity")
    msg = str(exc_info.value)
    assert 'references set "W"' in msg
    assert "not registered" in msg


def test_phantom_error_message(fresh_registry):
    """Phantom detection error names the exact symbol."""
    Set("W", description="Workers")
    x = Variable("x", index=["W"], domain="continuous",
                 bounds=(0, 1), description="Allocation")

    # Manually inject expression referencing unregistered "h"
    phantom_expr = ArithExpr(IndexExpr("x", ("i",)), "*", IndexExpr("h", ("i",)))
    sym = ExpressionSymbol(
        name="bad", index=("W",), units=parse_unit("hours"),
        description="Bad expression", expr_tree=phantom_expr,
    )
    fresh_registry.symbols["bad"] = sym
    fresh_registry._registration_order.append("bad")

    result = fresh_registry.run_tests()
    assert not result.passed
    assert any('"h"' in e and "not registered" in e for e in result.errors)


def test_dimensional_error_message(fresh_registry):
    """Dimensional inconsistency error names units on both sides."""
    Set("W", description="Workers")
    hours_param = Parameter("hours_val", index=["W"], units="hours",
                            description="Hours value")
    heads_param = Parameter("heads_val", index=["W"], units="headcount",
                            description="Headcount value")

    Constraint("bad",
        expr=lambda i: hours_param[i] <= heads_param[i],
        over=["W"], description="Comparing incompatible units")

    result = fresh_registry.run_tests()
    assert not result.passed
    dimensional_errors = [e for e in result.errors if "units" in e.lower()]
    assert len(dimensional_errors) >= 1
    assert "hours" in dimensional_errors[0]
    assert "headcount" in dimensional_errors[0]


def test_cycle_error_message(fresh_registry):
    """Cycle detection error shows the cycle path."""
    Set("W", description="Workers")

    sym_a = ExpressionSymbol(
        name="load", index=("W",), units=parse_unit("dimensionless"),
        description="Load", expr_tree=IndexExpr("utilization", ("i",)),
    )
    sym_b = ExpressionSymbol(
        name="utilization", index=("W",), units=parse_unit("dimensionless"),
        description="Utilization", expr_tree=IndexExpr("adjusted_cap", ("i",)),
    )
    sym_c = ExpressionSymbol(
        name="adjusted_cap", index=("W",), units=parse_unit("dimensionless"),
        description="Adjusted cap", expr_tree=IndexExpr("load", ("i",)),
    )
    for s in [sym_a, sym_b, sym_c]:
        fresh_registry.symbols[s.name] = s
        fresh_registry._registration_order.append(s.name)

    result = fresh_registry.run_tests()
    assert not result.passed
    cycle_errors = [e for e in result.errors if "circular" in e.lower() or "cycle" in e.lower()]
    assert len(cycle_errors) >= 1
    # Should contain the cycle path
    assert "load" in cycle_errors[0]


def test_orphan_error_message_strict(fresh_registry):
    """Orphan error names the unused symbol."""
    Set("W", description="Workers")
    Parameter("buildability", index=["W"], units="dimensionless",
              description="Buildability score")

    result = fresh_registry.run_tests(strict=True)
    assert not result.passed
    assert any('"buildability"' in e for e in result.errors)
    assert any("never referenced" in e for e in result.errors)
