"""Meta-compiler: Symbol registry and validation engine for mathematical models."""

from meta_compiler.registry import registry


def Set(name: str, *, description: str = "") -> "SymbolProxy":
    """Declare an index set."""
    return registry.register_set(name, description)


def Parameter(
    name: str,
    *,
    index: list[str] | None = None,
    domain: str = "real",
    units: str = "dimensionless",
    description: str = "",
) -> "SymbolProxy":
    """Declare a parameter."""
    return registry.register_parameter(name, index or [], domain, units, description)


def Variable(
    name: str,
    *,
    index: list[str] | None = None,
    domain: str = "continuous",
    bounds: tuple[float | None, float | None] = (None, None),
    units: str = "dimensionless",
    description: str = "",
) -> "SymbolProxy":
    """Declare a decision variable."""
    return registry.register_variable(name, index or [], domain, bounds, units, description)


def Expression(
    name: str,
    *,
    definition: object,
    index: list[str] | None = None,
    units: str = "dimensionless",
    description: str = "",
) -> "SymbolProxy":
    """Declare a derived expression."""
    return registry.register_expression(name, index or [], units, description, definition)


def Constraint(
    name: str,
    *,
    expr: object,
    over: list[str] | None = None,
    type: str = "hard",
    description: str = "",
) -> None:
    """Declare a constraint."""
    registry.register_constraint(name, over or [], type, description, expr)


def Objective(
    name: str,
    *,
    expr: object,
    sense: str = "maximize",
    description: str = "",
) -> None:
    """Declare an objective."""
    registry.register_objective(name, sense, description, expr)


def S(name: str) -> "SetIterator":
    """Return a symbolic set iterator for use in lambda for-loops."""
    return registry.s(name)
