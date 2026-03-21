"""Tests for scalar auto-unwrap in registry."""
from meta_compiler.registry import registry
from meta_compiler import Parameter, Variable, Set


def test_scalar_parameter_returns_raw_float(fresh_registry):
    """Scalar fixture data should be injected as raw float, not SymbolProxy."""
    registry.data_store["M"] = 5.0
    registry._exec_namespace = {}
    result = Parameter("M", description="meeting hours")
    assert result == 5.0
    assert isinstance(result, float)


def test_scalar_arithmetic_works(fresh_registry):
    """Scalars should support arithmetic directly."""
    registry.data_store["M"] = 5.0
    registry.data_store["beta"] = 0.8
    registry._exec_namespace = {}
    M = Parameter("M", description="meeting hours")
    beta = Parameter("beta", description="productivity factor")
    assert M * beta == 4.0
    assert M + beta == 5.8
    assert M - beta == 4.2


def test_indexed_data_still_returns_proxy(fresh_registry):
    """Dict/list fixture data should still get a SymbolProxy."""
    from meta_compiler.proxy import SymbolProxy

    registry.data_store["W"] = ["alice", "bob"]
    registry.data_store["cap"] = {"alice": 10, "bob": 20}
    registry._exec_namespace = {}
    Set("W", description="workers")
    result = Parameter("cap", index="W", description="capacity")
    assert isinstance(result, SymbolProxy)


def test_no_fixture_data_returns_proxy(fresh_registry):
    """Missing fixture data should still get a SymbolProxy (helpful error on access)."""
    from meta_compiler.proxy import SymbolProxy

    # data_store does NOT have "M"
    registry._exec_namespace = {}
    result = Parameter("M", description="meeting hours")
    assert isinstance(result, SymbolProxy)


def test_scalar_names_tracked_on_registry(fresh_registry):
    """Registry should track which symbols were auto-unwrapped as scalars."""
    registry.data_store["M"] = 5.0
    registry._exec_namespace = {}
    Parameter("M", description="meeting hours")
    assert "M" in registry.scalar_names


def test_reset_clears_scalar_names(fresh_registry):
    """reset() should clear the scalar_names set."""
    registry.scalar_names.add("M")
    registry.reset()
    assert len(registry.scalar_names) == 0


def test_namespace_injection_uses_raw_value(fresh_registry):
    """Auto-unwrapped scalar should be injected as raw value in exec namespace."""
    registry.data_store["H"] = 8.0
    ns = {}
    registry._exec_namespace = ns
    Parameter("H", description="hours")
    assert ns["H"] == 8.0
    assert isinstance(ns["H"], float)


def test_bool_scalar_auto_unwrapped(fresh_registry):
    """bool is a subclass of int, so booleans should be auto-unwrapped."""
    registry.data_store["flag"] = True
    registry._exec_namespace = {}
    result = Parameter("flag", description="a boolean flag")
    assert result is True
    assert isinstance(result, bool)
    assert "flag" in registry.scalar_names


def test_str_scalar_auto_unwrapped(fresh_registry):
    """String scalars should be auto-unwrapped."""
    registry.data_store["mode"] = "fast"
    registry._exec_namespace = {}
    result = Parameter("mode", description="execution mode")
    assert result == "fast"
    assert isinstance(result, str)
    assert "mode" in registry.scalar_names
