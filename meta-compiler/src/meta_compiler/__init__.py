"""Meta-compiler: Symbol registry and validation engine for mathematical models."""

from meta_compiler.registry import registry


def Set(name: str, *, description: str = "") -> "SymbolProxy":
    """Declare an index set."""
    return registry.register_set(name, description=description)


def Parameter(
    name: str,
    *,
    index=None,
    domain: str = "real",
    units: str = "dimensionless",
    description: str = "",
) -> "SymbolProxy":
    """Declare a parameter."""
    return registry.register_parameter(name, index=index, domain=domain, units=units, description=description)


def Variable(
    name: str,
    *,
    index=None,
    domain: str = "continuous",
    bounds: tuple[float | None, float | None] = (None, None),
    units: str = "dimensionless",
    description: str = "",
) -> "SymbolProxy":
    """Declare a decision variable."""
    return registry.register_variable(name, index=index, domain=domain, bounds=bounds, units=units, description=description)


def Expression(
    name: str,
    *,
    definition: object,
    index=None,
    units: str = "dimensionless",
    description: str = "",
) -> "SymbolProxy":
    """Declare a derived expression."""
    return registry.register_expression(name, definition=definition, index=index, units=units, description=description)


def Constraint(
    name: str,
    *,
    expr: object,
    over=None,
    type: str = "hard",
    description: str = "",
) -> None:
    """Declare a constraint."""
    registry.register_constraint(name, expr=expr, over=over, constraint_type=type, description=description)


def Objective(
    name: str,
    *,
    expr: object,
    sense: str = "maximize",
    description: str = "",
) -> None:
    """Declare an objective."""
    registry.register_objective(name, expr=expr, sense=sense, description=description)


def S(name: str):
    """Return the members of a registered set for iteration."""
    return registry.s(name)
