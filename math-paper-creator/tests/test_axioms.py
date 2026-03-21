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


def test_register_axiom(fresh_registry):
    fresh_registry.register_axiom("A1", statement="H > 0", description="Positivity")
    assert "A1" in fresh_registry.symbols
    assert isinstance(fresh_registry.symbols["A1"], AxiomSymbol)
    assert fresh_registry.symbols["A1"].statement == "H > 0"

def test_register_axiom_duplicate_raises(fresh_registry):
    fresh_registry.register_axiom("A1", statement="H > 0", description="Positivity")
    import pytest
    with pytest.raises(ValueError, match="already registered"):
        fresh_registry.register_axiom("A1", statement="M > 0", description="Other")

def test_register_axiom_with_z3_expr(fresh_registry):
    expr = lambda: "fake_z3_expr"
    fresh_registry.register_axiom("A1", statement="H > 0", z3_expr=expr, description="Positivity")
    assert fresh_registry.symbols["A1"].z3_expr is expr


from meta_compiler.symbols import PropertySymbol

def test_register_property(fresh_registry):
    fresh_registry.register_axiom("A1", statement="H > 0", description="Pos")
    fresh_registry.register_axiom("A2", statement="M <= H", description="Bound")
    fresh_registry.register_property(
        "P1", claim="t_eff >= 0", z3_expr=lambda: None,
        given=["A1", "A2"], description="Non-neg"
    )
    assert "P1" in fresh_registry.symbols
    assert isinstance(fresh_registry.symbols["P1"], PropertySymbol)
    assert fresh_registry.symbols["P1"].given == ("A1", "A2")

def test_register_property_missing_axiom_raises(fresh_registry):
    import pytest
    with pytest.raises(ValueError, match="references axiom.*not registered"):
        fresh_registry.register_property(
            "P1", claim="t_eff >= 0", z3_expr=lambda: None,
            given=["A1"], description="Non-neg"
        )

def test_register_property_given_not_axiom_raises(fresh_registry):
    from meta_compiler import Set
    Set("W", description="Workers")
    import pytest
    with pytest.raises(ValueError, match="not an Axiom"):
        fresh_registry.register_property(
            "P1", claim="t_eff >= 0", z3_expr=lambda: None,
            given=["W"], description="Non-neg"
        )
