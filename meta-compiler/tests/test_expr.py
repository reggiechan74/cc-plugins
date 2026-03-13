from meta_compiler.expr import (
    SymbolRef,
    IndexExpr,
    ArithExpr,
    CompareExpr,
    SumExpr,
    NegExpr,
    SetIterator,
    collect_refs,
)


def test_symbol_ref():
    ref = SymbolRef("cap")
    assert ref.name == "cap"
    assert collect_refs(ref) == {"cap"}


def test_index_expr():
    expr = IndexExpr("x", ("i", "j", "t"))
    assert expr.symbol == "x"
    assert expr.indices == ("i", "j", "t")
    assert collect_refs(expr) == {"x"}


def test_arith_expr():
    left = IndexExpr("x", ("i", "j"))
    right = IndexExpr("h", ("j",))
    expr = ArithExpr(left, "*", right)
    assert expr.op == "*"
    assert collect_refs(expr) == {"x", "h"}


def test_compare_expr():
    left = SymbolRef("load")
    right = SymbolRef("cap")
    expr = CompareExpr(left, "<=", right)
    assert expr.op == "<="
    assert collect_refs(expr) == {"load", "cap"}


def test_sum_expr():
    body = IndexExpr("x", ("i", "j"))
    expr = SumExpr(body, over_set="P")
    assert expr.over_set == "P"
    assert collect_refs(expr) == {"x"}


def test_nested_collect_refs():
    """Deeply nested expression tree collects all symbol references."""
    # sum(x[i,j] * h[j] for j in P)
    product = ArithExpr(IndexExpr("x", ("i", "j")), "*", IndexExpr("h", ("j",)))
    total = SumExpr(product, over_set="P")
    compare = CompareExpr(total, "<=", IndexExpr("cap", ("i",)))
    assert collect_refs(compare) == {"x", "h", "cap"}


def test_neg_expr():
    operand = IndexExpr("cost", ("i",))
    expr = NegExpr(operand)
    assert collect_refs(expr) == {"cost"}


def test_set_iterator():
    it = SetIterator("P")
    assert it.set_name == "P"
