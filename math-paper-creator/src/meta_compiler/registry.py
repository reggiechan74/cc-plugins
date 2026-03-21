"""Global symbol registry — the heart of the validation system.

Accumulates symbol declarations and runs cumulative integrity checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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
from meta_compiler.units import parse_unit


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
        self.data_store: dict[str, Any] = {}
        self.access_log: set[str] = set()
        self.scalar_names: set[str] = set()
        self._exec_namespace: dict | None = None  # set by executor
        self._current_block_source: str | None = None  # set by executor per block

    def reset(self) -> None:
        """Clear all symbols — used between tests."""
        self.symbols.clear()
        self._registration_order.clear()
        self.data_store.clear()
        self.access_log.clear()
        self.scalar_names = set()
        self._exec_namespace = None
        self._current_block_source = None

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

    def _require_sets(self, *set_names: str, context: str = "") -> None:
        """Verify that all named sets exist."""
        for set_name in set_names:
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

    def _make_proxy(self, name: str) -> "SymbolProxy | int | float | str":
        """Create a data-backed proxy and auto-inject into exec namespace."""
        if name in self.data_store and isinstance(
            self.data_store[name], (int, float, str)
        ):
            # Scalar value — inject raw value, not a proxy
            value = self.data_store[name]
            self.scalar_names.add(name)
            if self._exec_namespace is not None:
                self._exec_namespace[name] = value
            return value
        proxy = SymbolProxy(name, data=self.data_store.get(name), access_log=self.access_log)
        if self._exec_namespace is not None:
            self._exec_namespace[name] = proxy
        return proxy

    def _normalize_index(self, index) -> tuple[str, ...] | None:
        """Normalize index argument to tuple or None."""
        if index is None:
            return None
        if isinstance(index, str):
            return (index,)
        if isinstance(index, (list, tuple)):
            return tuple(index)
        raise TypeError(f"index must be str, list, tuple, or None, got {type(index).__name__}")

    def register_set(self, name: str, *, description: str = "") -> SymbolProxy:
        """Register an index set."""
        symbol = SetSymbol(name=name, description=description)
        self._register(name, symbol)
        return self._make_proxy(name)

    def register_parameter(
        self,
        name: str,
        *,
        index=None,
        domain: str = "real",
        units: str = "dimensionless",
        description: str = "",
    ) -> SymbolProxy:
        """Register a parameter with index and unit validation."""
        idx = self._normalize_index(index)
        if idx:
            self._require_sets(*idx, context=f'Parameter "{name}"')
        symbol = ParameterSymbol(
            name=name, index=idx, domain=domain,
            units=units, description=description,
        )
        self._register(name, symbol)
        return self._make_proxy(name)

    def register_variable(
        self,
        name: str,
        *,
        index=None,
        domain: str = "continuous",
        bounds: tuple[float | None, float | None] = (None, None),
        units: str = "dimensionless",
        description: str = "",
    ) -> SymbolProxy:
        """Register a decision variable with index validation."""
        idx = self._normalize_index(index)
        if idx:
            self._require_sets(*idx, context=f'Variable "{name}"')
        symbol = VariableSymbol(
            name=name, index=idx, domain=domain, bounds=bounds,
            units=units, description=description,
        )
        self._register(name, symbol)
        return self._make_proxy(name)

    def register_expression(
        self,
        name: str,
        *,
        definition: object,
        index=None,
        units: str = "dimensionless",
        description: str = "",
    ) -> SymbolProxy:
        """Register a derived expression by storing its callable directly."""
        idx = self._normalize_index(index)
        if idx:
            self._require_sets(*idx, context=f'Expression "{name}"')
        if self._current_block_source and not hasattr(definition, "_source_text"):
            definition._source_text = self._current_block_source
        sym = ExpressionSymbol(
            name=name, index=idx, units=units,
            description=description, expr=definition,
        )
        self._register(name, sym)
        return self._make_proxy(name)

    def register_constraint(
        self,
        name: str,
        *,
        expr: object,
        over=None,
        constraint_type: str = "hard",
        description: str = "",
    ) -> None:
        """Register a constraint by storing its callable directly."""
        over_str = over if isinstance(over, str) or over is None else over[0] if over else None
        if over_str:
            self._require_sets(over_str, context=f'Constraint "{name}"')
        if self._current_block_source and not hasattr(expr, "_source_text"):
            expr._source_text = self._current_block_source
        sym = ConstraintSymbol(
            name=name, over=over_str, constraint_type=constraint_type,
            description=description, expr=expr,
        )
        self._register(name, sym)

    def register_objective(
        self,
        name: str,
        *,
        expr: object,
        sense: str = "maximize",
        description: str = "",
    ) -> None:
        """Register an objective by storing its callable directly."""
        if self._current_block_source and not hasattr(expr, "_source_text"):
            expr._source_text = self._current_block_source
        sym = ObjectiveSymbol(
            name=name, sense=sense, description=description, expr=expr,
        )
        self._register(name, sym)

    def s(self, name: str):
        """Return the members of a registered set for iteration."""
        self.access_log.add(name)
        if name not in self.symbols:
            defined = ", ".join(sorted(self.symbols.keys()))
            raise ValueError(
                f'BLOCK: S("{name}") references set "{name}" '
                f"which is not registered. Defined symbols: {defined}"
            )
        if not isinstance(self.symbols[name], SetSymbol):
            raise ValueError(
                f'BLOCK: S("{name}") — "{name}" is not a Set'
            )
        if name in self.data_store:
            data = self.data_store[name]
            if isinstance(data, list):
                return data
            raise RuntimeError(f"Set '{name}' fixture data must be a list, got {type(data).__name__}")
        raise RuntimeError(f"No fixture data for set '{name}'. Add a python:fixture block.")

    def run_tests(self, *, strict: bool = False) -> TestResult:
        """Run cumulative integrity checks."""
        from meta_compiler.checks import run_all_checks
        return run_all_checks(self, strict=strict)


# Global registry instance
registry = Registry()
