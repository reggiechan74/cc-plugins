"""End-to-end test using the exact API example from the spec."""

from meta_compiler import (
    Set, Parameter, Variable, Expression, Constraint, Objective, S,
)
from meta_compiler.registry import registry


def test_spec_example(fresh_registry):
    """The full example from the spec should register and validate cleanly."""
    # Declare index sets
    Set("W", description="Workers")
    Set("P", description="Project types")
    Set("T", description="Time periods")

    # Declare parameters
    cap = Parameter("cap", index=["W"], domain="nonneg_real",
                    units="hours", description="Maximum capacity of worker i")
    h = Parameter("h", index=["P"], domain="nonneg_real",
                  units="hours", description="Effort-hours required per project type")

    # Declare decision variables
    x = Variable("x", index=["W", "P", "T"], domain="continuous",
                 bounds=(0, 1), description="Allocation fraction")

    # Declare derived expressions
    load = Expression("load",
        definition=lambda i: sum(x[i, j, t] * h[j] for j in S("P") for t in S("T")),
        index=["W"], units="hours",
        description="Total load on worker i")

    # Declare utility parameter (needed for objective)
    U = Parameter("U", index=["W", "P", "T"], domain="real",
                  units="dimensionless", description="Utility score")

    # Declare constraints
    Constraint("capacity_limit",
        expr=lambda i: load[i] <= cap[i],
        over=["W"], type="hard",
        description="No worker exceeds their capacity")

    # Declare objectives
    Objective("maximize_utility",
        expr=lambda: sum(x[i, j, t] * U[i, j, t]
                         for i in S("W") for j in S("P") for t in S("T")),
        sense="maximize",
        description="Maximize total weighted utility across assignments")

    # Run tests
    result = fresh_registry.run_tests()
    assert result.passed, f"Errors: {result.errors}"
    assert len(result.errors) == 0

    # Verify symbol table completeness
    # W, P, T, cap, h, x, load, U, capacity_limit, maximize_utility = 10
    assert len(fresh_registry.symbols) == 10


def test_spec_example_strict_mode(fresh_registry):
    """Same example in strict mode — all symbols are used, so should pass."""
    Set("W", description="Workers")
    Set("P", description="Project types")
    Set("T", description="Time periods")

    cap = Parameter("cap", index=["W"], domain="nonneg_real",
                    units="hours", description="Maximum capacity of worker i")
    h = Parameter("h", index=["P"], domain="nonneg_real",
                  units="hours", description="Effort-hours required per project type")
    x = Variable("x", index=["W", "P", "T"], domain="continuous",
                 bounds=(0, 1), description="Allocation fraction")
    load = Expression("load",
        definition=lambda i: sum(x[i, j, t] * h[j] for j in S("P") for t in S("T")),
        index=["W"], units="hours",
        description="Total load on worker i")
    U = Parameter("U", index=["W", "P", "T"], domain="real",
                  units="dimensionless", description="Utility score")
    Constraint("capacity_limit",
        expr=lambda i: load[i] <= cap[i],
        over=["W"], type="hard",
        description="No worker exceeds their capacity")
    Objective("maximize_utility",
        expr=lambda: sum(x[i, j, t] * U[i, j, t]
                         for i in S("W") for j in S("P") for t in S("T")),
        sense="maximize",
        description="Maximize total weighted utility across assignments")

    result = fresh_registry.run_tests(strict=True)
    assert result.passed, f"Errors: {result.errors}"
