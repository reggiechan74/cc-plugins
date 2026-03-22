"""Tests for AST-based dimensional analysis in _check_unit_boundaries.

Covers the fix for GitHub issue #12: the unit checker should use dimensional
algebra (multiply/divide units) instead of pairwise string comparison.
"""

from meta_compiler import Set, Parameter, Variable, Constraint


def test_mixed_units_via_multiply_divide_no_error(fresh_registry):
    """Multiplying/dividing different units should NOT produce errors.

    This is the core bug from issue #12: an expression like
    gamma_v * H_0 / delta_v combines units algebraically and should
    not be flagged as a unit mismatch.
    """
    fresh_registry.data_store["W"] = ["alice"]
    fresh_registry.data_store["gamma_v"] = {"alice": 0.5}
    fresh_registry.data_store["H_0"] = {"alice": 8}
    fresh_registry.data_store["delta_v"] = {"alice": 2}

    Set("W", description="Workers")
    Parameter("gamma_v", index="W", units="dimensionless",
              description="Decay rate")
    Parameter("H_0", index="W", units="hours",
              description="Base hours")
    Parameter("delta_v", index="W", units="headcount",
              description="Delta headcount")

    Constraint("mixed_product",
        expr=lambda i: gamma_v[i] * H_0[i] / delta_v[i] <= 10,
        over="W", description="Mixed multiply/divide")

    result = fresh_registry.run_tests()
    unit_errors = [e for e in result.errors if "unit" in e.lower()]
    assert len(unit_errors) == 0, f"Unexpected unit errors: {unit_errors}"


def test_incompatible_addition_produces_error(fresh_registry):
    """Adding hours + headcount should produce an error."""
    fresh_registry.data_store["W"] = ["alice"]
    fresh_registry.data_store["hours_val"] = {"alice": 8}
    fresh_registry.data_store["heads_val"] = {"alice": 1}

    Set("W", description="Workers")
    Parameter("hours_val", index="W", units="hours",
              description="Hours value")
    Parameter("heads_val", index="W", units="headcount",
              description="Headcount value")

    Constraint("bad_add",
        expr=lambda i: hours_val[i] + heads_val[i] <= 10,
        over="W", description="Adding incompatible units")

    result = fresh_registry.run_tests()
    unit_errors = [e for e in result.errors if "unit" in e.lower()]
    assert len(unit_errors) >= 1
    assert "hours" in unit_errors[0]
    assert "headcount" in unit_errors[0]


def test_incompatible_subtraction_produces_error(fresh_registry):
    """Subtracting hours - headcount should produce an error."""
    fresh_registry.data_store["W"] = ["alice"]
    fresh_registry.data_store["hours_val"] = {"alice": 8}
    fresh_registry.data_store["heads_val"] = {"alice": 1}

    Set("W", description="Workers")
    Parameter("hours_val", index="W", units="hours",
              description="Hours value")
    Parameter("heads_val", index="W", units="headcount",
              description="Headcount value")

    Constraint("bad_sub",
        expr=lambda i: hours_val[i] - heads_val[i] >= 0,
        over="W", description="Subtracting incompatible units")

    result = fresh_registry.run_tests()
    unit_errors = [e for e in result.errors if "unit" in e.lower()]
    assert len(unit_errors) >= 1


def test_compatible_addition_no_error(fresh_registry):
    """Adding hours + hours should NOT produce errors."""
    fresh_registry.data_store["W"] = ["alice"]
    fresh_registry.data_store["hours_a"] = {"alice": 4}
    fresh_registry.data_store["hours_b"] = {"alice": 4}

    Set("W", description="Workers")
    Parameter("hours_a", index="W", units="hours",
              description="Hours A")
    Parameter("hours_b", index="W", units="hours",
              description="Hours B")

    Constraint("ok_add",
        expr=lambda i: hours_a[i] + hours_b[i] <= 10,
        over="W", description="Adding compatible units")

    result = fresh_registry.run_tests()
    unit_errors = [e for e in result.errors if "unit" in e.lower()]
    assert len(unit_errors) == 0


def test_comparison_incompatible_units_produces_error(fresh_registry):
    """Comparing hours <= headcount should produce an error."""
    fresh_registry.data_store["W"] = ["alice"]
    fresh_registry.data_store["hours_val"] = {"alice": 8}
    fresh_registry.data_store["heads_val"] = {"alice": 1}

    Set("W", description="Workers")
    Parameter("hours_val", index="W", units="hours",
              description="Hours value")
    Parameter("heads_val", index="W", units="headcount",
              description="Headcount value")

    Constraint("bad_cmp",
        expr=lambda i: hours_val[i] <= heads_val[i],
        over="W", description="Comparing incompatible units")

    result = fresh_registry.run_tests()
    unit_errors = [e for e in result.errors if "unit" in e.lower()]
    assert len(unit_errors) >= 1
    assert "hours" in unit_errors[0]
    assert "headcount" in unit_errors[0]


def test_multiply_then_compare_compatible(fresh_registry):
    """rate (hours/headcount) * count (headcount) compared to hours: OK."""
    fresh_registry.data_store["W"] = ["alice"]
    fresh_registry.data_store["rate"] = {"alice": 2.0}
    fresh_registry.data_store["count"] = {"alice": 3}
    fresh_registry.data_store["cap"] = {"alice": 8}

    Set("W", description="Workers")
    Parameter("rate", index="W", units="hours/headcount",
              description="Rate")
    Parameter("count", index="W", units="headcount",
              description="Count")
    Parameter("cap", index="W", units="hours",
              description="Capacity")

    Constraint("product_cmp",
        expr=lambda i: rate[i] * count[i] <= cap[i],
        over="W", description="Product vs cap")

    result = fresh_registry.run_tests()
    unit_errors = [e for e in result.errors if "unit" in e.lower()]
    assert len(unit_errors) == 0, f"Unexpected unit errors: {unit_errors}"
