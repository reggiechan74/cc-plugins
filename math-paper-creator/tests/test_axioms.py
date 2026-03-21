from meta_compiler.symbols import AxiomSymbol, PropertySymbol


def test_axiom_symbol_fields():
    ax = AxiomSymbol(name="A1", statement="H > 0", z3_expr=None, description="Positivity")
    assert ax.name == "A1"
    assert ax.statement == "H > 0"
    assert ax.z3_expr is None
    assert ax.description == "Positivity"


def test_axiom_symbol_is_frozen():
    ax = AxiomSymbol(name="A1", statement="H > 0", z3_expr=None, description="Positivity")
    import pytest
    with pytest.raises(AttributeError):
        ax.name = "A2"


def test_property_symbol_fields():
    prop = PropertySymbol(
        name="P1", claim="t_eff >= 0",
        z3_expr=lambda: None, given=("A1", "A2"), description="Non-negative"
    )
    assert prop.name == "P1"
    assert prop.claim == "t_eff >= 0"
    assert prop.given == ("A1", "A2")
    assert prop.description == "Non-negative"
