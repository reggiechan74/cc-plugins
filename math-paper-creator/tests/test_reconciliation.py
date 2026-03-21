import pytest
from meta_compiler.compiler.parser import ProseBlock
from meta_compiler.checks import check_directional_claims, check_value_reporting, check_constraint_tolerance
from meta_compiler.registry import registry


class TestCheckDirectionalClaims:
    def test_flags_increases(self):
        blocks = [ProseBlock(content="The σ parameter increases the outside option.\n")]
        warnings = check_directional_claims(blocks)
        assert len(warnings) == 1
        assert "increases" in warnings[0].lower()

    def test_flags_multiple_keywords(self):
        blocks = [ProseBlock(content="As x increases, y decreases and is monotone.\n")]
        warnings = check_directional_claims(blocks)
        # Should flag "increases", "decreases", and "monotone"
        assert len(warnings) == 3

    def test_no_warnings_for_clean_prose(self):
        blocks = [ProseBlock(content="The model defines a set of workers.\n")]
        warnings = check_directional_claims(blocks)
        assert warnings == []

    def test_ignores_non_prose_blocks(self):
        """Only ProseBlock content is scanned."""
        from meta_compiler.compiler.parser import ValidationBlock
        blocks = [ValidationBlock(code="# value increases here", line_number=1)]
        warnings = check_directional_claims(blocks)
        assert warnings == []


class TestCheckValueReporting:
    def setup_method(self):
        registry.reset()

    def test_warns_when_values_computed_but_not_reported(self):
        registry.register_set("W", description="Workers")
        registry.register_parameter("cap", index="W", description="Cap")
        registry.data_store = {"W": ["a"], "cap": {"a": 40}}
        blocks = [ProseBlock(content="The model defines capacity constraints.\n")]
        warnings = check_value_reporting(blocks, registry)
        assert len(warnings) == 1
        assert "computes" in warnings[0].lower()

    def test_no_warning_when_values_reported_in_prose(self):
        registry.register_set("W", description="Workers")
        registry.register_parameter("cap", index="W", description="Cap")
        registry.data_store = {"W": ["a"], "cap": {"a": 40}}
        blocks = [ProseBlock(content="The capacity is 40 hours per worker.\n")]
        warnings = check_value_reporting(blocks, registry)
        assert warnings == []

    def test_no_warning_when_no_computed_values(self):
        registry.register_set("W", description="Workers")
        blocks = [ProseBlock(content="We define a set of workers.\n")]
        warnings = check_value_reporting(blocks, registry)
        assert warnings == []


class TestCheckConstraintTolerance:
    def setup_method(self):
        registry.reset()

    def test_flags_large_arithmetic_offset(self):
        registry.register_set("W", description="Workers")
        registry.register_parameter("V_W", index="W", description="Value")
        registry.register_constraint(
            "participation", over="W", constraint_type="hard",
            description="Participation",
            expr=lambda i: V_W[i] >= 2750 - 50,
        )
        warnings = check_constraint_tolerance(registry)
        assert len(warnings) == 1
        assert "50" in warnings[0]
        assert "participation" in warnings[0].lower()

    def test_ignores_small_offset(self):
        registry.register_set("W", description="Workers")
        registry.register_constraint(
            "tight", over="W", constraint_type="hard",
            description="Tight",
            expr=lambda i: x[i] >= 100 - 1e-6,
        )
        warnings = check_constraint_tolerance(registry)
        assert warnings == []

    def test_ignores_no_comparison(self):
        registry.register_set("W", description="Workers")
        registry.register_constraint(
            "simple", over="W", constraint_type="hard",
            description="Simple",
            expr=lambda i: True,
        )
        warnings = check_constraint_tolerance(registry)
        assert warnings == []

    def test_flags_addition_offset(self):
        registry.register_set("W", description="Workers")
        registry.register_constraint(
            "slack", over="W", constraint_type="hard",
            description="Slack",
            expr=lambda i: x[i] <= 100 + 25,
        )
        warnings = check_constraint_tolerance(registry)
        assert len(warnings) == 1
        assert "25" in warnings[0]
