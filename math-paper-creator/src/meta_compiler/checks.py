"""Structural integrity checks for the symbol registry.

v2 checks use:
- Access logs (numeric mode) or tokenized source scanning (structural mode)
  for orphan/phantom detection
- Registration-order dependency graph for cycle detection
- Declared unit comparison at constraint boundaries for unit checks
"""

from __future__ import annotations

import io
import inspect
import re
import tokenize
from typing import TYPE_CHECKING

from meta_compiler.compiler.parser import Block, ProseBlock

from meta_compiler.symbols import (
    ConstraintSymbol, ExpressionSymbol, ObjectiveSymbol,
    SetSymbol, ParameterSymbol, VariableSymbol,
)

if TYPE_CHECKING:
    from meta_compiler.registry import Registry


def run_all_checks(
    registry: "Registry", *, strict: bool = False
) -> "TestResult":
    """Run all integrity checks. Returns TestResult."""
    from meta_compiler.registry import TestResult

    errors: list[str] = []
    warnings: list[str] = []

    # Augment access_log with names from source text scanning.
    source_refs = _collect_source_refs(registry)
    all_accessed = registry.access_log | source_refs

    _check_phantoms(registry, all_accessed, errors)

    # Auto-detect scalar models: if no Sets registered, skip orphan
    # checking entirely — scalar models have no indexed cross-references,
    # so every symbol would be flagged as an orphan (pure noise).
    has_sets = any(isinstance(s, SetSymbol) for s in registry.symbols.values())
    if has_sets:
        _check_orphans(registry, all_accessed, errors, warnings, strict)
    _check_cycles(registry, errors)
    _check_unit_boundaries(registry, errors)

    return TestResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def _collect_source_refs(registry: "Registry") -> set[str]:
    """Collect all symbol names referenced in expr source text."""
    refs: set[str] = set()
    for sym in registry.symbols.values():
        expr_fn = getattr(sym, "expr", None)
        if expr_fn is not None:
            refs |= _extract_names_from_source(expr_fn, registry)
    return refs


def _check_phantoms(registry: "Registry", all_accessed: set[str], errors: list[str]):
    """Symbols accessed but never registered."""
    registered = set(registry.symbols.keys())
    phantoms = all_accessed - registered
    for name in sorted(phantoms):
        errors.append(f'Phantom: symbol "{name}" referenced but never declared')


def _check_orphans(
    registry: "Registry", all_accessed: set[str], errors: list[str],
    warnings: list[str], strict: bool
):
    """Symbols registered but never accessed."""
    registered = set(registry.symbols.keys())

    # Symbols referenced in 'over' or 'index' fields count as accessed
    implicit_refs: set[str] = set()
    for sym in registry.symbols.values():
        if isinstance(sym, ConstraintSymbol) and sym.over:
            implicit_refs.add(sym.over)
        if hasattr(sym, "index") and sym.index:
            for idx_set in (sym.index if isinstance(sym.index, tuple) else (sym.index,)):
                implicit_refs.add(idx_set)

    # Constraints and objectives are consumers, not things that need to be referenced
    consumer_names = {
        name for name, sym in registry.symbols.items()
        if isinstance(sym, (ConstraintSymbol, ObjectiveSymbol))
    }

    combined = all_accessed | implicit_refs | consumer_names
    orphans = registered - combined

    for name in sorted(orphans):
        msg = f'Orphan: symbol "{name}" declared but never referenced'
        if strict:
            errors.append(msg)
        else:
            warnings.append(msg)


def _check_cycles(registry: "Registry", errors: list[str]):
    """Circular dependencies in expression definitions via DFS."""
    expr_names = {
        name for name, sym in registry.symbols.items()
        if isinstance(sym, ExpressionSymbol)
    }
    if not expr_names:
        return

    adj: dict[str, set[str]] = {name: set() for name in expr_names}
    for name in expr_names:
        sym = registry.symbols[name]
        if sym.expr is not None:
            refs = _extract_names_from_source(sym.expr, registry)
            adj[name] = (refs & expr_names) - {name}  # exclude self-references

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {name: WHITE for name in expr_names}
    path: list[str] = []

    def dfs(node: str) -> bool:
        color[node] = GRAY
        path.append(node)
        for neighbor in adj[node]:
            if color[neighbor] == GRAY:
                cycle = path[path.index(neighbor):]
                errors.append(
                    f"Cycle detected: {' -> '.join(cycle)} -> {neighbor}"
                )
                return True
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        path.pop()
        color[node] = BLACK
        return False

    for name in expr_names:
        if color[name] == WHITE:
            dfs(name)


def _extract_names_from_source(fn, registry: "Registry") -> set[str]:
    """Extract symbol names from a callable's source using tokenize."""
    try:
        source = inspect.getsource(fn)
    except (OSError, TypeError):
        source = getattr(fn, "_source_text", "")
        if not source:
            return set()

    registered = set(registry.symbols.keys())
    found: set[str] = set()

    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for tok_type, tok_string, _, _, _ in tokens:
            if tok_type == tokenize.NAME and tok_string in registered:
                found.add(tok_string)
    except tokenize.TokenizeError:
        pass

    return found


def collect_scalar_refs(
    block_source: str, scalar_names: set[str], access_log: set[str]
) -> None:
    """Add scalar symbol names found in block_source to access_log.

    Uses Python's tokenizer to avoid substring false positives.
    """
    if not scalar_names:
        return
    try:
        tokens = tokenize.generate_tokens(io.StringIO(block_source).readline)
        for tok_type, tok_string, *_ in tokens:
            if tok_type == tokenize.NAME and tok_string in scalar_names:
                access_log.add(tok_string)
    except tokenize.TokenError:
        pass  # partial source is OK — best-effort


def _check_unit_boundaries(registry: "Registry", errors: list[str]):
    """Check unit compatibility at constraint boundaries."""
    from meta_compiler.units import parse_unit, units_compatible

    for name, sym in registry.symbols.items():
        if not isinstance(sym, ConstraintSymbol):
            continue
        if sym.expr is None:
            continue

        refs = _extract_names_from_source(sym.expr, registry)

        unit_map: dict[str, str] = {}
        for ref_name in refs:
            ref_sym = registry.symbols.get(ref_name)
            if ref_sym is None:
                continue
            if isinstance(ref_sym, (ParameterSymbol, VariableSymbol)):
                unit_map[ref_name] = ref_sym.units

        units_seen: list[tuple[str, str]] = list(unit_map.items())
        for i, (name_a, unit_a) in enumerate(units_seen):
            for name_b, unit_b in units_seen[i + 1:]:
                if unit_a != "dimensionless" and unit_b != "dimensionless":
                    if not units_compatible(parse_unit(unit_a), parse_unit(unit_b)):
                        errors.append(
                            f'Constraint "{name}": "{name_a}" has unit '
                            f'"{unit_a}" but "{name_b}" has unit "{unit_b}"'
                        )


# ---------------------------------------------------------------------------
# Prose-math reconciliation checks
# ---------------------------------------------------------------------------

_DIRECTIONAL_KEYWORDS = re.compile(
    r'\b(increases|decreases|widens|narrows|higher|lower'
    r'|maximizes|minimizes|monotone|non-monotone)\b',
    re.IGNORECASE,
)


def check_directional_claims(blocks: list[Block]) -> list[str]:
    """Flag directional keywords in prose for manual verification."""
    warnings: list[str] = []
    for block in blocks:
        if not isinstance(block, ProseBlock):
            continue
        for line in block.content.split("\n"):
            for match in _DIRECTIONAL_KEYWORDS.finditer(line):
                keyword = match.group()
                # Show ~40 chars of context around the match
                start = max(0, match.start() - 20)
                end = min(len(line), match.end() + 20)
                context = line[start:end].strip()
                warnings.append(
                    f'Directional claim "{keyword}": "...{context}..." '
                    f"— verify against computed values"
                )
    return warnings
