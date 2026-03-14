import pytest
from meta_compiler import Set, Parameter, Variable, Expression, Constraint, S
from meta_compiler.expr import collect_refs
from meta_compiler.symbols import ConstraintSymbol


def test_register_constraint(fresh_registry):
    Set("W", description="Workers")
    Set("P", description="Projects")
    cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
    x = Variable("x", index=["W", "P"], domain="continuous",
                 bounds=(0, 1), description="Allocation")
    h = Parameter("h", index=["P"], units="hours", description="Effort")
    load = Expression("load",
        definition=lambda i: sum(x[i, j] * h[j] for j in S("P")),
        index=["W"], units="hours", description="Total load")

    Constraint("capacity_limit",
        expr=lambda i: load[i] <= cap[i],
        over=["W"], type="hard",
        description="No worker exceeds capacity")

    sym = fresh_registry.symbols["capacity_limit"]
    assert isinstance(sym, ConstraintSymbol)
    refs = collect_refs(sym.expr_tree)
    assert "load" in refs
    assert "cap" in refs


def test_constraint_duplicate_raises(fresh_registry):
    Set("W", description="Workers")
    cap = Parameter("cap", index=["W"], units="hours", description="Capacity")
    Constraint("c1",
        expr=lambda i: cap[i] <= cap[i],
        over=["W"], description="First")
    with pytest.raises(ValueError, match="already registered"):
        Constraint("c1",
            expr=lambda i: cap[i] <= cap[i],
            over=["W"], description="Second")


def test_constraint_undefined_set_raises(fresh_registry):
    with pytest.raises(ValueError, match='references set "W"'):
        Constraint("bad", expr=lambda i: i, over=["W"], description="Bad")


from meta_compiler.registry import Registry

def test_register_constraint_stores_callable():
    reg = Registry()
    reg.register_set("W", description="Workers")
    fn = lambda i: True
    reg.register_constraint("cap_check", over="W", constraint_type="hard",
                            description="Check capacity", expr=fn)
    sym = reg.symbols["cap_check"]
    assert sym.expr is fn

def test_registry_with_data_store():
    reg = Registry()
    reg.data_store["cap"] = {"alice": 40, "bob": 35}
    reg.register_set("W", description="Workers")
    proxy = reg.register_parameter("cap", index="W", units="hours", description="Cap")
    # Proxy should be data-backed — returns real value, not RuntimeError
    assert proxy["alice"] == 40

def test_registry_access_log_exists():
    reg = Registry()
    assert hasattr(reg, "access_log")
    assert isinstance(reg.access_log, set)
