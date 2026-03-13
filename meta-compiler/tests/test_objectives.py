import pytest
from meta_compiler import Set, Parameter, Variable, Objective, S
from meta_compiler.expr import collect_refs
from meta_compiler.symbols import ObjectiveSymbol


def test_register_objective(fresh_registry):
    Set("W", description="Workers")
    Set("P", description="Projects")
    x = Variable("x", index=["W", "P"], domain="continuous",
                 bounds=(0, 1), description="Allocation")
    u = Parameter("U", index=["W", "P"], units="dimensionless",
                  description="Utility")

    Objective("maximize_utility",
        expr=lambda: sum(
            x[i, j] * u[i, j]
            for i in S("W") for j in S("P")
        ),
        sense="maximize",
        description="Maximize total utility")

    sym = fresh_registry.symbols["maximize_utility"]
    assert isinstance(sym, ObjectiveSymbol)
    assert sym.sense == "maximize"
    refs = collect_refs(sym.expr_tree)
    assert "x" in refs
    assert "U" in refs


def test_objective_minimize(fresh_registry):
    Set("W", description="Workers")
    cost = Parameter("cost", index=["W"], units="dollars", description="Cost")

    Objective("minimize_cost",
        expr=lambda: sum(cost[i] for i in S("W")),
        sense="minimize",
        description="Minimize total cost")

    assert fresh_registry.symbols["minimize_cost"].sense == "minimize"
