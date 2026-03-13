"""Cumulative validation checks: orphan, phantom, cycle, dimensional consistency."""

from __future__ import annotations

from typing import TYPE_CHECKING

from meta_compiler.expr import collect_refs
from meta_compiler.symbols import (
    ConstraintSymbol,
    ExpressionSymbol,
    ObjectiveSymbol,
    ParameterSymbol,
    SetSymbol,
    VariableSymbol,
)

if TYPE_CHECKING:
    from meta_compiler.registry import Registry, TestResult


def run_all_checks(registry: "Registry", *, strict: bool = False) -> "TestResult":
    """Run all cumulative integrity checks."""
    from meta_compiler.registry import TestResult

    errors: list[str] = []
    warnings: list[str] = []

    _check_phantoms(registry, errors)
    _check_cycles(registry, errors)
    _check_dimensions(registry, errors)
    _check_orphans(registry, errors, warnings, strict=strict)

    return TestResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def _get_all_referenced_symbols(registry: "Registry") -> set[str]:
    """Collect all symbols referenced in expressions, constraints, and objectives."""
    refs: set[str] = set()
    for sym in registry.symbols.values():
        if isinstance(sym, (ExpressionSymbol, ConstraintSymbol, ObjectiveSymbol)):
            refs |= collect_refs(sym.expr_tree)
    # Also count symbols used as indices (sets referenced by parameters/variables/expressions)
    for sym in registry.symbols.values():
        if isinstance(sym, (ParameterSymbol, VariableSymbol)):
            refs.update(sym.index)
        elif isinstance(sym, ExpressionSymbol):
            refs.update(sym.index)
        elif isinstance(sym, ConstraintSymbol):
            refs.update(sym.over)
    return refs


def _check_orphans(
    registry: "Registry",
    errors: list[str],
    warnings: list[str],
    *,
    strict: bool,
) -> None:
    """Check for symbols that are registered but never referenced."""
    all_refs = _get_all_referenced_symbols(registry)

    for name, sym in registry.symbols.items():
        # Sets are referenced via index declarations — already tracked
        if isinstance(sym, SetSymbol):
            continue
        # Constraints and objectives are consumers, not things that need to be referenced
        if isinstance(sym, (ConstraintSymbol, ObjectiveSymbol)):
            continue
        if name not in all_refs:
            msg = (
                f'BLOCK: Symbol "{name}" was registered as "{sym.description}" '
                f"but is never referenced by any Constraint, Objective, or Expression. "
                f"Either use it or remove it."
            )
            if strict:
                errors.append(msg)
            else:
                warnings.append(msg)


def _check_phantoms(registry: "Registry", errors: list[str]) -> None:
    """Check for symbols referenced in expressions but not registered."""
    registered = set(registry.symbols.keys())

    for name, sym in registry.symbols.items():
        if isinstance(sym, (ExpressionSymbol, ConstraintSymbol, ObjectiveSymbol)):
            refs = collect_refs(sym.expr_tree)
            for ref in refs:
                # Skip numeric literals (e.g., "2", "0.5")
                try:
                    float(ref)
                    continue
                except ValueError:
                    pass
                if ref not in registered:
                    defined = ", ".join(sorted(registered))
                    errors.append(
                        f'BLOCK: {type(sym).__name__.replace("Symbol", "")} "{name}" '
                        f'references symbol "{ref}" which is not registered. '
                        f"Defined symbols: {defined}"
                    )


def _check_cycles(registry: "Registry", errors: list[str]) -> None:
    """Check for circular dependencies between expressions."""
    # Build adjacency list: expression -> expressions it references
    expr_names = {
        name for name, sym in registry.symbols.items()
        if isinstance(sym, ExpressionSymbol)
    }

    adj: dict[str, set[str]] = {}
    for name in expr_names:
        sym = registry.symbols[name]
        assert isinstance(sym, ExpressionSymbol)
        refs = collect_refs(sym.expr_tree)
        adj[name] = refs & expr_names  # Only track expression-to-expression deps

    # DFS cycle detection
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {name: WHITE for name in expr_names}
    path: list[str] = []

    def dfs(node: str) -> bool:
        color[node] = GRAY
        path.append(node)
        for neighbor in adj.get(node, set()):
            if color[neighbor] == GRAY:
                # Found cycle — extract it
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                errors.append(
                    f"BLOCK: Circular dependency detected: "
                    f"{' -> '.join(cycle)}"
                )
                return True
            if color[neighbor] == WHITE:
                if dfs(neighbor):
                    return True
        path.pop()
        color[node] = BLACK
        return False

    for name in expr_names:
        if color[name] == WHITE:
            dfs(name)


def _check_dimensions(registry: "Registry", errors: list[str]) -> None:
    """Check dimensional consistency in constraints.

    For constraints with comparison operators, verify that left and right sides
    have compatible units. Objectives are exempt from cross-term unit checking.
    """
    from meta_compiler.expr import CompareExpr
    from meta_compiler.units import units_compatible

    for name, sym in registry.symbols.items():
        if not isinstance(sym, ConstraintSymbol):
            continue
        if not isinstance(sym.expr_tree, CompareExpr):
            continue

        left_unit = _infer_units(sym.expr_tree.left, registry)
        right_unit = _infer_units(sym.expr_tree.right, registry)

        if left_unit is not None and right_unit is not None:
            if not units_compatible(left_unit, right_unit):
                errors.append(
                    f'BLOCK: Constraint "{name}" compares left side '
                    f"(units: {left_unit}) with right side (units: {right_unit}). "
                    f"Cannot compare incompatible units."
                )


def _infer_units(node: object, registry: "Registry") -> "Unit | None":
    """Attempt to infer units for an expression tree node. Returns None if unknown."""
    from meta_compiler.expr import (
        ArithExpr,
        IndexExpr,
        NegExpr,
        SumExpr,
        SymbolRef,
    )
    from meta_compiler.units import Unit, units_multiply

    match node:
        case SymbolRef(name=name):
            sym = registry.symbols.get(name)
            if sym is None:
                return None
            if hasattr(sym, "units"):
                return sym.units  # type: ignore[return-value]
            return None
        case IndexExpr(symbol=symbol):
            sym = registry.symbols.get(symbol)
            if sym is None:
                return None
            if hasattr(sym, "units"):
                return sym.units  # type: ignore[return-value]
            return None
        case ArithExpr(left=left, op=op, right=right):
            lu = _infer_units(left, registry)
            ru = _infer_units(right, registry)
            if lu is None or ru is None:
                return None
            if op in ("+", "-"):
                # Addition/subtraction requires same units
                if not units_compatible(lu, ru):
                    return None  # Error will be caught elsewhere
                return lu
            if op == "*":
                return units_multiply(lu, ru)
            if op == "/":
                from meta_compiler.units import units_divide
                return units_divide(lu, ru)
            return None
        case SumExpr(body=body):
            return _infer_units(body, registry)
        case NegExpr(operand=operand):
            return _infer_units(operand, registry)
        case _:
            return None
