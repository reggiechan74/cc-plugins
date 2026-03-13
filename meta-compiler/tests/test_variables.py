import pytest
from meta_compiler import Set, Variable
from meta_compiler.symbols import VariableSymbol


def test_register_variable(fresh_registry):
    Set("W", description="Workers")
    Set("P", description="Projects")
    Set("T", description="Time periods")
    Variable("x", index=["W", "P", "T"], domain="continuous",
             bounds=(0, 1), description="Allocation fraction")
    sym = fresh_registry.symbols["x"]
    assert isinstance(sym, VariableSymbol)
    assert sym.index == ("W", "P", "T")
    assert sym.bounds == (0, 1)


def test_variable_undefined_set_raises(fresh_registry):
    with pytest.raises(ValueError, match='references set "W"'):
        Variable("x", index=["W"], description="Bad")


def test_variable_binary_domain(fresh_registry):
    Set("W", description="Workers")
    Variable("y", index=["W"], domain="binary",
             bounds=(0, 1), description="Assignment flag")
    assert fresh_registry.symbols["y"].domain == "binary"
