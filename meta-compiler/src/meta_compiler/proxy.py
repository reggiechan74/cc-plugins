"""Proxy objects returned by symbol constructors.

Support __getitem__ for indexing (x[i,j,t]) and arithmetic/comparison operators
for building expression trees in lambdas.
"""

from __future__ import annotations

from meta_compiler.expr import (
    ArithExpr,
    CompareExpr,
    ExprNode,
    IndexExpr,
    NegExpr,
    SymbolRef,
    SumExpr,
    SetIterator,
)


class SymbolProxy:
    """Proxy object for a registered symbol. Builds expression tree nodes via operators."""

    def __init__(self, name: str) -> None:
        self._name = name

    def __getitem__(self, key: object) -> IndexExpr:
        if isinstance(key, tuple):
            indices = tuple(str(k) for k in key)
        else:
            indices = (str(key),)
        return IndexExpr(self._name, indices)

    def _as_node(self) -> ExprNode:
        return SymbolRef(self._name)

    # Arithmetic — returns ArithExpr nodes

    def __add__(self, other: object) -> ArithExpr:
        return ArithExpr(self._as_node(), "+", _to_node(other))

    def __radd__(self, other: object) -> ArithExpr:
        return ArithExpr(_to_node(other), "+", self._as_node())

    def __sub__(self, other: object) -> ArithExpr:
        return ArithExpr(self._as_node(), "-", _to_node(other))

    def __rsub__(self, other: object) -> ArithExpr:
        return ArithExpr(_to_node(other), "-", self._as_node())

    def __mul__(self, other: object) -> ArithExpr:
        return ArithExpr(self._as_node(), "*", _to_node(other))

    def __rmul__(self, other: object) -> ArithExpr:
        return ArithExpr(_to_node(other), "*", self._as_node())

    def __truediv__(self, other: object) -> ArithExpr:
        return ArithExpr(self._as_node(), "/", _to_node(other))

    def __rtruediv__(self, other: object) -> ArithExpr:
        return ArithExpr(_to_node(other), "/", self._as_node())

    def __neg__(self) -> NegExpr:
        return NegExpr(self._as_node())

    # Comparisons — returns CompareExpr nodes

    def __le__(self, other: object) -> CompareExpr:
        return CompareExpr(self._as_node(), "<=", _to_node(other))

    def __ge__(self, other: object) -> CompareExpr:
        return CompareExpr(self._as_node(), ">=", _to_node(other))

    def __eq__(self, other: object) -> CompareExpr:  # type: ignore[override]
        return CompareExpr(self._as_node(), "==", _to_node(other))

    def __repr__(self) -> str:
        return f"SymbolProxy({self._name!r})"

    def __str__(self) -> str:
        return self._name


def _to_node(value: object) -> ExprNode:
    """Convert a value to an expression node."""
    if isinstance(value, (SymbolRef, IndexExpr, ArithExpr, CompareExpr,
                          SumExpr, NegExpr, SetIterator)):
        return value
    if isinstance(value, SymbolProxy):
        return value._as_node()
    if isinstance(value, (int, float)):
        return SymbolRef(str(value))
    raise TypeError(f"Cannot convert {type(value).__name__} to expression node")
