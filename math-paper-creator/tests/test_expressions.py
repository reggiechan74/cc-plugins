import pytest
from meta_compiler import Set, Parameter, Variable, Expression, S
from meta_compiler.symbols import ExpressionSymbol


def test_expression_symbol_stores_callable():
    fn = lambda: 42
    sym = ExpressionSymbol(
        name="total", index=None, units="hours",
        description="Total hours", expr=fn,
    )
    assert sym.expr is fn
    assert sym.name == "total"


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
    # v2: sym.expr is a callable, no expr_tree
    assert callable(sym.expr)
    assert sym.index == ("W",)


def test_expression_undefined_index_set_raises(fresh_registry):
    """Registering an expression with an undefined index set raises at registration time."""
    with pytest.raises(ValueError, match='references set "W"'):
        Expression("bad",
            definition=lambda i: i,
            index=["W"], description="References undefined index set")


def test_expression_references_tracked(fresh_registry):
    Set("W", description="Workers")
    cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
    Expression("double_cap",
        definition=lambda i: cap[i] * 2,
        index=["W"], units="hours",
        description="Double capacity")

    sym = fresh_registry.symbols["double_cap"]
    # v2: sym.expr is callable, index is stored correctly
    assert callable(sym.expr)
    assert sym.index == ("W",)
