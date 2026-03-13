"""Global symbol registry — the heart of the validation system.

Accumulates symbol declarations and runs cumulative integrity checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from meta_compiler.expr import SetIterator
from meta_compiler.proxy import SymbolProxy
from meta_compiler.symbols import (
    ConstraintSymbol,
    ExpressionSymbol,
    ObjectiveSymbol,
    ParameterSymbol,
    SetSymbol,
    Symbol,
    VariableSymbol,
)
from meta_compiler.units import Unit, parse_unit


@dataclass
class TestResult:
    """Result from registry.run_tests()."""
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class Registry:
    """Global symbol registry that accumulates state as the document grows."""

    def __init__(self) -> None:
        self.symbols: dict[str, Symbol] = {}
        self._registration_order: list[str] = []

    def reset(self) -> None:
        """Clear all symbols — used between tests."""
        self.symbols.clear()
        self._registration_order.clear()

    def _register(self, name: str, symbol: Symbol) -> None:
        """Register a symbol, raising on conflicts."""
        if name in self.symbols:
            existing = self.symbols[name]
            raise ValueError(
                f'BLOCK: Symbol "{name}" already registered as '
                f'"{existing.description}". '
                f'Cannot redefine as "{symbol.description}"'
            )
        self.symbols[name] = symbol
        self._registration_order.append(name)

    def _require_sets(self, index: tuple[str, ...], context: str) -> None:
        """Verify that all index sets exist."""
        for set_name in index:
            if set_name not in self.symbols:
                defined = ", ".join(sorted(self.symbols.keys()))
                raise ValueError(
                    f'BLOCK: {context} references set "{set_name}" which is not registered. '
                    f"Defined symbols: {defined}"
                )
            if not isinstance(self.symbols[set_name], SetSymbol):
                raise ValueError(
                    f'BLOCK: {context} references "{set_name}" as an index set, '
                    f"but it is registered as {type(self.symbols[set_name]).__name__}"
                )

    def register_set(self, name: str, description: str) -> SymbolProxy:
        """Register an index set."""
        symbol = SetSymbol(name=name, description=description)
        self._register(name, symbol)
        return SymbolProxy(name)

    def register_parameter(
        self,
        name: str,
        index: list[str],
        domain: str,
        units: str,
        description: str,
    ) -> SymbolProxy:
        """Register a parameter with index and unit validation."""
        idx = tuple(index)
        self._require_sets(idx, f'Parameter "{name}"')
        symbol = ParameterSymbol(
            name=name, index=idx, domain=domain,
            units=parse_unit(units), description=description,
        )
        self._register(name, symbol)
        return SymbolProxy(name)

    def register_variable(
        self,
        name: str,
        index: list[str],
        domain: str,
        bounds: tuple[float | None, float | None],
        units: str,
        description: str,
    ) -> SymbolProxy:
        """Register a decision variable with index validation."""
        idx = tuple(index)
        self._require_sets(idx, f'Variable "{name}"')
        symbol = VariableSymbol(
            name=name, index=idx, domain=domain, bounds=bounds,
            units=parse_unit(units), description=description,
        )
        self._register(name, symbol)
        return SymbolProxy(name)

    def register_expression(
        self,
        name: str,
        index: list[str],
        units: str,
        description: str,
        definition: object,
    ) -> SymbolProxy:
        """Register a derived expression by capturing its lambda."""
        idx = tuple(index)
        self._require_sets(idx, f'Expression "{name}"')
        expr_tree = self._capture_lambda(definition, idx, f'Expression "{name}"')
        symbol = ExpressionSymbol(
            name=name, index=idx, units=parse_unit(units),
            description=description, expr_tree=expr_tree,
        )
        self._register(name, symbol)
        return SymbolProxy(name)

    def register_constraint(
        self,
        name: str,
        over: list[str],
        constraint_type: str,
        description: str,
        expr: object,
    ) -> None:
        """Register a constraint by capturing its lambda."""
        over_tuple = tuple(over)
        self._require_sets(over_tuple, f'Constraint "{name}"')
        expr_tree = self._capture_lambda(expr, over_tuple, f'Constraint "{name}"')
        symbol = ConstraintSymbol(
            name=name, over=over_tuple, constraint_type=constraint_type,
            description=description, expr_tree=expr_tree,
        )
        self._register(name, symbol)

    def register_objective(
        self,
        name: str,
        sense: str,
        description: str,
        expr: object,
    ) -> None:
        """Register an objective by capturing its lambda."""
        expr_tree = self._capture_lambda(expr, (), f'Objective "{name}"')
        symbol = ObjectiveSymbol(
            name=name, sense=sense, description=description,
            expr_tree=expr_tree,
        )
        self._register(name, symbol)

    def _capture_lambda(
        self, fn: object, index: tuple[str, ...], context: str
    ) -> "ExprNode":
        """Call a lambda with symbolic placeholders to capture its expression tree."""
        from meta_compiler.expr import ExprNode

        if not callable(fn):
            raise TypeError(f"{context}: definition must be callable, got {type(fn).__name__}")

        # Create symbolic placeholder arguments bound positionally to index sets
        placeholders = [_Placeholder(set_name) for set_name in index]
        try:
            result = fn(*placeholders)
        except Exception as e:
            raise ValueError(
                f"{context}: failed to capture lambda expression: {e}"
            ) from e

        if not isinstance(result, ExprNode):
            raise TypeError(
                f"{context}: lambda must return an expression tree node, "
                f"got {type(result).__name__}"
            )
        return result

    def s(self, set_name: str) -> SetIterator:
        """Return a symbolic set iterator for use in for-loops within lambdas."""
        if set_name not in self.symbols:
            defined = ", ".join(sorted(self.symbols.keys()))
            raise ValueError(
                f'BLOCK: S("{set_name}") references set "{set_name}" '
                f"which is not registered. Defined symbols: {defined}"
            )
        if not isinstance(self.symbols[set_name], SetSymbol):
            raise ValueError(
                f'BLOCK: S("{set_name}") — "{set_name}" is not a Set'
            )
        return SetIterator(set_name)

    def run_tests(self, *, strict: bool = False) -> TestResult:
        """Run cumulative integrity checks.

        Args:
            strict: If True, orphans are errors (compilation mode).
                    If False, orphans are warnings (authoring mode).
        """
        from meta_compiler.checks import run_all_checks
        return run_all_checks(self, strict=strict)


class _Placeholder:
    """Symbolic placeholder for a lambda parameter bound to an index set.

    Converts to its set name when used as a string (for IndexExpr indices).
    """

    def __init__(self, set_name: str) -> None:
        self._set_name = set_name

    def __str__(self) -> str:
        return self._set_name

    def __repr__(self) -> str:
        return f"_Placeholder({self._set_name!r})"


# Global registry instance
registry = Registry()
