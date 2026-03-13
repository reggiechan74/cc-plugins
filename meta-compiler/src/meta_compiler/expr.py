"""Expression tree nodes for symbolic math validation.

These are pure data structures with operator overloading — no registry dependency.
Lambdas in Expression/Constraint/Objective build trees of these nodes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Union


class _ExprOps:
    """Mixin providing arithmetic and comparison operators for expression nodes.

    Enables expressions like: x[i,j] * h[j] + cap[i], load[i] <= cap[i]
    Python's sum() starts with 0, so __radd__ handles the 0 + expr case.
    """

    def __add__(self, other: object) -> ArithExpr:
        return ArithExpr(self, "+", _expr_to_node(other))  # type: ignore[arg-type]

    def __radd__(self, other: object) -> _ExprOps:
        if isinstance(other, int) and other == 0:
            return self  # type: ignore[return-value]
        return ArithExpr(_expr_to_node(other), "+", self)  # type: ignore[arg-type]

    def __mul__(self, other: object) -> ArithExpr:
        return ArithExpr(self, "*", _expr_to_node(other))  # type: ignore[arg-type]

    def __rmul__(self, other: object) -> ArithExpr:
        return ArithExpr(_expr_to_node(other), "*", self)  # type: ignore[arg-type]

    def __sub__(self, other: object) -> ArithExpr:
        return ArithExpr(self, "-", _expr_to_node(other))  # type: ignore[arg-type]

    def __rsub__(self, other: object) -> ArithExpr:
        return ArithExpr(_expr_to_node(other), "-", self)  # type: ignore[arg-type]

    def __truediv__(self, other: object) -> ArithExpr:
        return ArithExpr(self, "/", _expr_to_node(other))  # type: ignore[arg-type]

    def __rtruediv__(self, other: object) -> ArithExpr:
        return ArithExpr(_expr_to_node(other), "/", self)  # type: ignore[arg-type]

    def __neg__(self) -> NegExpr:
        return NegExpr(self)  # type: ignore[arg-type]

    def __le__(self, other: object) -> CompareExpr:
        return CompareExpr(self, "<=", _expr_to_node(other))  # type: ignore[arg-type]

    def __ge__(self, other: object) -> CompareExpr:
        return CompareExpr(self, ">=", _expr_to_node(other))  # type: ignore[arg-type]

    def __eq__(self, other: object) -> CompareExpr:  # type: ignore[override]
        return CompareExpr(self, "==", _expr_to_node(other))  # type: ignore[arg-type]


@dataclass(frozen=True)
class SymbolRef(_ExprOps):
    """Direct reference to a symbol by name (not indexed)."""
    name: str


@dataclass(frozen=True)
class IndexExpr(_ExprOps):
    """Symbol indexed by placeholder variables, e.g. x[i, j, t]."""
    symbol: str
    indices: tuple[str, ...]


@dataclass(frozen=True)
class ArithExpr(_ExprOps):
    """Binary arithmetic: left op right."""
    left: object  # ExprNode — typed as object to avoid forward-ref issues at runtime
    op: str  # "+", "-", "*", "/"
    right: object  # ExprNode


@dataclass(frozen=True)
class CompareExpr:
    """Comparison: left op right. Leaf node — not used in further arithmetic."""
    left: object  # ExprNode
    op: str  # "<=", ">=", "=="
    right: object  # ExprNode


@dataclass(frozen=True)
class SumExpr(_ExprOps):
    """Summation over a set: sum(body for _ in S(over_set))."""
    body: object  # ExprNode
    over_set: str


@dataclass(frozen=True)
class NegExpr(_ExprOps):
    """Unary negation: -operand."""
    operand: object  # ExprNode


@dataclass(frozen=True)
class SetIterator:
    """Symbolic placeholder for iterating over a set via S('name').

    When used in a for-loop, yields a single _SetElement placeholder.
    This captures 'sum over set P' in the expression tree.
    """
    set_name: str

    def __iter__(self):
        """Yield a single symbolic element tagged with this set."""
        yield _SetElement(self.set_name)


class _SetElement:
    """Symbolic element yielded by iterating over a SetIterator.

    Used as an index in expressions like x[i, j] where j comes from
    `for j in S("P")`. Converts to its set name when used as a string
    (for IndexExpr indices).
    """

    def __init__(self, set_name: str) -> None:
        self.set_name = set_name

    def __str__(self) -> str:
        return self.set_name

    def __repr__(self) -> str:
        return f"_SetElement({self.set_name!r})"


# Union type for expression tree nodes — defined after all classes so isinstance() works
ExprNode = Union[
    SymbolRef, IndexExpr, ArithExpr, CompareExpr, SumExpr, NegExpr, SetIterator
]

# Concrete tuple for isinstance() checks at runtime
_EXPR_NODE_TYPES = (
    SymbolRef, IndexExpr, ArithExpr, CompareExpr, SumExpr, NegExpr, SetIterator
)


def _expr_to_node(value: object) -> ExprNode:
    """Convert a value to an expression node for use in operator overloading."""
    if isinstance(value, _EXPR_NODE_TYPES):
        return value  # type: ignore[return-value]
    if isinstance(value, (int, float)):
        return SymbolRef(str(value))
    raise TypeError(f"Cannot convert {type(value).__name__} to expression node")


def collect_refs(node: ExprNode) -> set[str]:
    """Walk an expression tree and collect all symbol names referenced."""
    match node:
        case SymbolRef(name=name):
            return {name}
        case IndexExpr(symbol=symbol):
            return {symbol}
        case ArithExpr(left=left, right=right):
            return collect_refs(left) | collect_refs(right)  # type: ignore[arg-type]
        case CompareExpr(left=left, right=right):
            return collect_refs(left) | collect_refs(right)  # type: ignore[arg-type]
        case SumExpr(body=body):
            return collect_refs(body)  # type: ignore[arg-type]
        case NegExpr(operand=operand):
            return collect_refs(operand)  # type: ignore[arg-type]
        case SetIterator():
            return set()
        case _:
            raise TypeError(f"Unknown expression node: {type(node)}")
