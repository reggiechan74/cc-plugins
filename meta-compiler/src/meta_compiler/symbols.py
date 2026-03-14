"""Symbol record dataclasses — what gets stored in the registry."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SetSymbol:
    """An index set like W (workers), P (projects)."""
    name: str
    description: str


@dataclass(frozen=True)
class ParameterSymbol:
    """A parameter like cap_i (capacity of worker i)."""
    name: str
    index: tuple[str, ...] | None
    domain: str
    units: str
    description: str


@dataclass(frozen=True)
class VariableSymbol:
    """A decision variable like x_{ijp} (allocation fraction)."""
    name: str
    index: tuple[str, ...] | None
    domain: str
    bounds: tuple[float | None, float | None]
    units: str
    description: str


@dataclass(frozen=True)
class ExpressionSymbol:
    """A derived expression like load_i (total load on worker i)."""
    name: str
    index: tuple[str, ...] | None
    units: str
    description: str
    expr: object  # callable in v2


@dataclass(frozen=True)
class ConstraintSymbol:
    """A constraint like capacity_limit (no worker exceeds capacity)."""
    name: str
    over: str | None
    constraint_type: str  # "hard" or "soft"
    description: str
    expr: object  # callable in v2


@dataclass(frozen=True)
class ObjectiveSymbol:
    """An objective like maximize_utility."""
    name: str
    sense: str  # "maximize" or "minimize"
    description: str
    expr: object  # callable in v2


# Union of all symbol types
Symbol = SetSymbol | ParameterSymbol | VariableSymbol | ExpressionSymbol | ConstraintSymbol | ObjectiveSymbol
