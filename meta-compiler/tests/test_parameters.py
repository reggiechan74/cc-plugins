import pytest
from meta_compiler import Set, Parameter
from meta_compiler.symbols import ParameterSymbol
from meta_compiler.units import parse_unit


def test_register_parameter(fresh_registry):
    Set("W", description="Workers")
    p = Parameter("cap", index=["W"], domain="nonneg_real",
                  units="hours", description="Max capacity")
    assert "cap" in fresh_registry.symbols
    sym = fresh_registry.symbols["cap"]
    assert isinstance(sym, ParameterSymbol)
    assert sym.index == ("W",)
    assert sym.units == parse_unit("hours")


def test_parameter_undefined_set_raises(fresh_registry):
    with pytest.raises(ValueError, match='references set "W"'):
        Parameter("cap", index=["W"], domain="nonneg_real",
                  units="hours", description="Max capacity")


def test_parameter_multi_index(fresh_registry):
    Set("W", description="Workers")
    Set("P", description="Projects")
    Parameter("d", index=["W", "P"], domain="nonneg_real",
              units="hours", description="Demand")
    sym = fresh_registry.symbols["d"]
    assert sym.index == ("W", "P")


def test_parameter_no_index(fresh_registry):
    Parameter("alpha", domain="nonneg_real",
              units="dimensionless", description="Coefficient")
    sym = fresh_registry.symbols["alpha"]
    assert sym.index == ()


def test_parameter_duplicate_raises(fresh_registry):
    Set("W", description="Workers")
    Parameter("cap", index=["W"], units="hours", description="Capacity")
    with pytest.raises(ValueError, match="already registered"):
        Parameter("cap", index=["W"], units="headcount", description="Different")


from meta_compiler.proxy import SymbolProxy

def test_proxy_getitem_returns_real_value():
    log = set()
    proxy = SymbolProxy("cap", data={"alice": 40, "bob": 35}, access_log=log)
    assert proxy["alice"] == 40
    assert proxy["bob"] == 35

def test_proxy_getitem_logs_access():
    log = set()
    proxy = SymbolProxy("cap", data={"alice": 40}, access_log=log)
    proxy["alice"]
    assert "cap" in log

def test_proxy_getitem_no_data_raises():
    log = set()
    proxy = SymbolProxy("cap", data=None, access_log=log)
    import pytest
    with pytest.raises(RuntimeError, match="No fixture data"):
        proxy["alice"]

def test_proxy_multi_index_tuple_key():
    log = set()
    data = {("alice", "projA"): 5, ("bob", "projB"): 10}
    proxy = SymbolProxy("x", data=data, access_log=log)
    assert proxy["alice", "projA"] == 5
    assert proxy["bob", "projB"] == 10
