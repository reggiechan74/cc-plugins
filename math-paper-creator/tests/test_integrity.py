import pytest
from meta_compiler.registry import registry
from meta_compiler.checks import run_all_checks

def setup_function():
    registry.reset()

def test_phantom_detected_via_access_log():
    """Symbol accessed but never registered -> phantom error."""
    registry.register_set("W", description="Workers")
    registry.access_log.add("cap")  # accessed but not registered
    result = run_all_checks(registry, strict=False)
    assert any("cap" in e and "phantom" in e.lower() for e in result.errors)

def test_orphan_warning_in_authoring_mode():
    """Symbol registered but never accessed -> orphan warning."""
    registry.register_set("W", description="Workers")
    registry.register_parameter("cap", index="W", units="hours", description="Cap")
    registry.access_log.add("W")  # W accessed, cap not
    result = run_all_checks(registry, strict=False)
    assert any("cap" in w for w in result.warnings)
    assert len(result.errors) == 0  # warning, not error

def test_orphan_error_in_strict_mode():
    """Symbol registered but never accessed -> orphan error in strict mode."""
    registry.register_set("W", description="Workers")
    registry.register_parameter("cap", index="W", units="hours", description="Cap")
    registry.access_log.add("W")
    result = run_all_checks(registry, strict=True)
    assert any("cap" in e for e in result.errors)

def test_no_false_positives_clean_model():
    """A clean model with all symbols used should have no errors."""
    registry.data_store = {"W": ["a"], "cap": {"a": 40}}
    registry.register_set("W", description="Workers")
    registry.register_parameter("cap", index="W", units="hours", description="Cap")
    registry.register_constraint("check", over="W", constraint_type="hard",
                                 description="Check", expr=lambda i: True)
    registry.access_log.update(["W", "cap"])
    result = run_all_checks(registry, strict=False)
    assert len(result.errors) == 0
