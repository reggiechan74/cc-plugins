from meta_compiler.registry import registry
from meta_compiler.symbols import SetSymbol


def test_register_set(fresh_registry):
    from meta_compiler import Set
    s = Set("W", description="Workers")
    assert "W" in fresh_registry.symbols
    assert isinstance(fresh_registry.symbols["W"], SetSymbol)
    assert fresh_registry.symbols["W"].description == "Workers"


def test_duplicate_set_raises(fresh_registry):
    from meta_compiler import Set
    import pytest
    Set("W", description="Workers")
    with pytest.raises(ValueError, match="already registered"):
        Set("W", description="Different meaning")



def test_s_undefined_set_raises(fresh_registry):
    from meta_compiler import S
    import pytest
    with pytest.raises(ValueError, match="not registered"):
        S("X")


def test_set_returns_proxy(fresh_registry):
    from meta_compiler import Set
    from meta_compiler.proxy import SymbolProxy
    result = Set("W", description="Workers")
    assert isinstance(result, SymbolProxy)


def test_s_returns_real_set_members():
    from meta_compiler import S
    from meta_compiler.registry import registry
    registry.reset()
    registry.data_store["W"] = ["alice", "bob"]
    registry.register_set("W", description="Workers")
    members = S("W")
    assert members == ["alice", "bob"]
