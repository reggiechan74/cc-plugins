"""Symbol record dataclasses — what gets stored in the registry."""

from __future__ import annotations

from dataclasses import dataclass, field

from meta_compiler.expr import ExprNode
from meta_compiler.units import Unit


@dataclass(frozen=True)
class SetSymbol:
    """An index set like W (workers), P (projects)."""
    name: str
    description: str


@dataclass(frozen=True)
class ParameterSymbol:
    """A parameter like cap_i (capacity of worker i)."""
    name: str
    index: tuple[str, ...]
    domain: str
    units: Unit
    description: str


@dataclass(frozen=True)
class VariableSymbol:
    """A decision variable like x_{ijp} (allocation fraction)."""
    name: str
    index: tuple[str, ...]
    domain: str
    bounds: tuple[float | None, float | None]
    units: Unit
    description: str


@dataclass(frozen=True)
class ExpressionSymbol:
    """A derived expression like load_i (total load on worker i)."""
    name: str
    index: tuple[str, ...]
    units: Unit
    description: str
    expr_tree: ExprNode


@dataclass(frozen=True)
class ConstraintSymbol:
    """A constraint like capacity_limit (no worker exceeds capacity)."""
    name: str
    over: tuple[str, ...]
    constraint_type: str  # "hard" or "soft"
    description: str
    expr_tree: ExprNode


@dataclass(frozen=True)
class ObjectiveSymbol:
    """An objective like maximize_utility."""
    name: str
    sense: str  # "maximize" or "minimize"
    description: str
    expr_tree: ExprNode


# Union of all symbol types
Symbol = SetSymbol | ParameterSymbol | VariableSymbol | ExpressionSymbol | ConstraintSymbol | ObjectiveSymbol
