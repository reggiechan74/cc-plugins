import pytest
from meta_compiler import Set, Parameter, Variable, Expression, S
from meta_compiler.expr import (
    ArithExpr,
    CompareExpr,
    IndexExpr,
    SumExpr,
    collect_refs,
)
from meta_compiler.symbols import ExpressionSymbol


def test_simple_expression(fresh_registry):
    Set("W", description="Workers")
    Set("P", description="Projects")
    cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
    x = Variable("x", index=["W", "P"], domain="continuous",
                 bounds=(0, 1), description="Allocation")
    h = Parameter("h", index=["P"], units="hours", description="Effort")

    Expression("load",
        definition=lambda i: sum(x[i, j] * h[j] for j in S("P")),
        index=["W"], units="hours",
        description="Total load on worker i")

    sym = fresh_registry.symbols["load"]
    assert isinstance(sym, ExpressionSymbol)
    refs = collect_refs(sym.expr_tree)
    assert "x" in refs
    assert "h" in refs


def test_expression_undefined_symbol_raises(fresh_registry):
    Set("W", description="Workers")
    with pytest.raises(ValueError, match="not registered"):
        Expression("bad",
            definition=lambda i: S("NOPE"),
            index=["W"], description="References undefined set")


def test_expression_references_tracked(fresh_registry):
    Set("W", description="Workers")
    cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
    Expression("double_cap",
        definition=lambda i: cap[i] * 2,
        index=["W"], units="hours",
        description="Double capacity")

    sym = fresh_registry.symbols["double_cap"]
    assert collect_refs(sym.expr_tree) == {"cap", "2"}
