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


def test_s_function_returns_set_iterator(fresh_registry):
    from meta_compiler import Set, S
    Set("P", description="Projects")
    it = S("P")
    from meta_compiler.expr import SetIterator
    assert isinstance(it, SetIterator)
    assert it.set_name == "P"


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
