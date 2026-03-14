import pytest
from meta_compiler import Set, Parameter, Variable, Objective, S
from meta_compiler.symbols import ObjectiveSymbol


def test_register_objective(fresh_registry):
    fresh_registry.data_store["W"] = ["alice", "bob"]
    fresh_registry.data_store["P"] = ["projA", "projB"]
    fresh_registry.data_store["x"] = {("alice", "projA"): 0.5, ("alice", "projB"): 0.3,
                                       ("bob", "projA"): 0.4, ("bob", "projB"): 0.2}
    fresh_registry.data_store["U"] = {("alice", "projA"): 1, ("alice", "projB"): 2,
                                       ("bob", "projA"): 3, ("bob", "projB"): 4}
    Set("W", description="Workers")
    Set("P", description="Projects")
    x = Variable("x", index=("W", "P"), domain="continuous",
                 bounds=(0, 1), description="Allocation")
    U = Parameter("U", index=("W", "P"), units="dimensionless",
                  description="Utility")
    Objective("maximize_utility",
        expr=lambda: sum(
            x[i, j] * U[i, j]
            for i in S("W") for j in S("P")
        ),
        sense="maximize",
        description="Maximize total utility")
    sym = fresh_registry.symbols["maximize_utility"]
    assert isinstance(sym, ObjectiveSymbol)
    assert sym.sense == "maximize"
    assert callable(sym.expr)


def test_objective_minimize(fresh_registry):
    fresh_registry.data_store["W"] = ["alice"]
    fresh_registry.data_store["cost"] = {"alice": 100}
    Set("W", description="Workers")
    cost = Parameter("cost", index="W", units="dollars", description="Cost")
    Objective("minimize_cost",
        expr=lambda: sum(cost[i] for i in S("W")),
        sense="minimize",
        description="Minimize total cost")
    assert fresh_registry.symbols["minimize_cost"].sense == "minimize"
