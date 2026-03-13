import pytest
from meta_compiler import Set, Parameter, Variable, Expression, Constraint, Objective, S


def test_orphan_warning_in_authoring_mode(fresh_registry):
    """Unused symbols produce warnings in authoring mode (strict=False)."""
    Set("W", description="Workers")
    Parameter("cap", index=["W"], units="hours", description="Capacity")
    # cap is never referenced by any expression/constraint/objective

    result = fresh_registry.run_tests(strict=False)
    assert result.passed is True
    assert any("cap" in w for w in result.warnings)


def test_orphan_error_in_strict_mode(fresh_registry):
    """Unused symbols produce errors in strict/compilation mode."""
    Set("W", description="Workers")
    Parameter("cap", index=["W"], units="hours", description="Capacity")

    result = fresh_registry.run_tests(strict=True)
    assert result.passed is False
    assert any("cap" in e for e in result.errors)


def test_no_orphan_when_used(fresh_registry):
    """Symbol used in a constraint is not an orphan."""
    Set("W", description="Workers")
    cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
    x = Variable("x", index=["W"], domain="continuous",
                 bounds=(0, 1), description="Allocation")
    Constraint("limit",
        expr=lambda i: x[i] <= cap[i],
        over=["W"], description="Limit")

    result = fresh_registry.run_tests(strict=True)
    # x and cap are used in constraint — no orphan for them
    orphan_errors = [e for e in result.errors if "never referenced" in e.lower()
                     or "orphan" in e.lower()]
    # Only sets might be orphans if not used as index — but they're used as indices
    assert not orphan_errors or all("W" not in e and "cap" not in e and "x" not in e
                                     for e in orphan_errors)


def test_phantom_detection(fresh_registry):
    """Expression referencing unregistered symbol produces error."""
    Set("W", description="Workers")
    # Register x but NOT h
    x = Variable("x", index=["W"], domain="continuous",
                 bounds=(0, 1), description="Allocation")

    # Manually create an expression with a phantom reference
    from meta_compiler.symbols import ExpressionSymbol
    from meta_compiler.expr import ArithExpr, IndexExpr
    from meta_compiler.units import parse_unit

    phantom_expr = ArithExpr(IndexExpr("x", ("i",)), "*", IndexExpr("h", ("j",)))
    sym = ExpressionSymbol(
        name="bad_load", index=("W",), units=parse_unit("hours"),
        description="References phantom h", expr_tree=phantom_expr,
    )
    fresh_registry.symbols["bad_load"] = sym
    fresh_registry._registration_order.append("bad_load")

    result = fresh_registry.run_tests()
    assert result.passed is False
    assert any("h" in e for e in result.errors)


def test_cycle_detection(fresh_registry):
    """Circular dependency between expressions produces error."""
    Set("W", description="Workers")

    # Manually create circular expressions: a -> b -> a
    from meta_compiler.symbols import ExpressionSymbol
    from meta_compiler.expr import IndexExpr
    from meta_compiler.units import parse_unit

    expr_a = ExpressionSymbol(
        name="a", index=("W",), units=parse_unit("dimensionless"),
        description="Expr A", expr_tree=IndexExpr("b", ("i",)),
    )
    expr_b = ExpressionSymbol(
        name="b", index=("W",), units=parse_unit("dimensionless"),
        description="Expr B", expr_tree=IndexExpr("a", ("i",)),
    )
    fresh_registry.symbols["a"] = expr_a
    fresh_registry.symbols["b"] = expr_b
    fresh_registry._registration_order.extend(["a", "b"])

    result = fresh_registry.run_tests()
    assert result.passed is False
    assert any("circular" in e.lower() or "cycle" in e.lower() for e in result.errors)


def test_dimensional_inconsistency(fresh_registry):
    """Constraint comparing hours with headcount produces error."""
    Set("W", description="Workers")
    hours_param = Parameter("hours_val", index=["W"], units="hours", description="Hours")
    heads_param = Parameter("heads_val", index=["W"], units="headcount", description="Headcount")

    Constraint("bad_compare",
        expr=lambda i: hours_param[i] <= heads_param[i],
        over=["W"], description="Comparing incompatible units")

    result = fresh_registry.run_tests()
    assert result.passed is False
    assert any("unit" in e.lower() or "dimension" in e.lower() for e in result.errors)
