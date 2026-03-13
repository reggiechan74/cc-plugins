"""Expression tree nodes for symbolic math validation.

These are pure data structures — no registry dependency. Lambdas in
Expression/Constraint/Objective build trees of these nodes via operator
overloading on proxy objects.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SymbolRef:
    """Direct reference to a symbol by name (not indexed)."""
    name: str


@dataclass(frozen=True)
class IndexExpr:
    """Symbol indexed by placeholder variables, e.g. x[i, j, t]."""
    symbol: str
    indices: tuple[str, ...]


@dataclass(frozen=True)
class ArithExpr:
    """Binary arithmetic: left op right."""
    left: ExprNode
    op: str  # "+", "-", "*", "/"
    right: ExprNode


@dataclass(frozen=True)
class CompareExpr:
    """Comparison: left op right."""
    left: ExprNode
    op: str  # "<=", ">=", "=="
    right: ExprNode


@dataclass(frozen=True)
class SumExpr:
    """Summation over a set: sum(body for _ in S(over_set))."""
    body: ExprNode
    over_set: str


@dataclass(frozen=True)
class NegExpr:
    """Unary negation: -operand."""
    operand: ExprNode


@dataclass(frozen=True)
class SetIterator:
    """Symbolic placeholder for iterating over a set via S("name")."""
    set_name: str


# Union type for expression tree nodes
ExprNode = SymbolRef | IndexExpr | ArithExpr | CompareExpr | SumExpr | NegExpr | SetIterator


def collect_refs(node: ExprNode) -> set[str]:
    """Walk an expression tree and collect all symbol names referenced."""
    match node:
        case SymbolRef(name=name):
            return {name}
        case IndexExpr(symbol=symbol):
            return {symbol}
        case ArithExpr(left=left, right=right):
            return collect_refs(left) | collect_refs(right)
        case CompareExpr(left=left, right=right):
            return collect_refs(left) | collect_refs(right)
        case SumExpr(body=body):
            return collect_refs(body)
        case NegExpr(operand=operand):
            return collect_refs(operand)
        case SetIterator():
            return set()
        case _:
            raise TypeError(f"Unknown expression node: {type(node)}")
