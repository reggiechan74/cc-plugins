"""Generate validation report from registry state."""

from __future__ import annotations

from dataclasses import dataclass, field

from meta_compiler.compiler.parser import Block, coverage_metric
from meta_compiler.registry import Registry
from meta_compiler.symbols import (
    ConstraintSymbol,
    ExpressionSymbol,
    ObjectiveSymbol,
    ParameterSymbol,
    SetSymbol,
    VariableSymbol,
)


@dataclass
class Report:
    """Structured validation report."""
    symbol_table: list[dict]
    dependencies: list[dict]
    test_passed: bool
    test_errors: list[str]
    test_warnings: list[str]
    coverage: dict

    def to_text(self) -> str:
        """Render report as human-readable text."""
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("VALIDATION REPORT")
        lines.append("=" * 60)
        lines.append("")

        # Symbol table
        lines.append("## Symbol Table")
        lines.append("")
        for sym in self.symbol_table:
            lines.append(f"  {sym['type']:12s}  {sym['name']:20s}  {sym['description']}")
            if sym.get("index"):
                lines.append(f"{'':14s}  index: {sym['index']}")
            if sym.get("units") and sym["units"] != "dimensionless":
                lines.append(f"{'':14s}  units: {sym['units']}")
        lines.append("")

        # Dependencies
        lines.append("## Dependencies")
        lines.append("")
        if self.dependencies:
            for dep in self.dependencies:
                lines.append(f"  {dep['from']} -> {dep['to']}")
        else:
            lines.append("  (none)")
        lines.append("")

        # Coverage
        lines.append("## Coverage")
        lines.append("")
        lines.append(f"  Math blocks: {self.coverage['total_math']}")
        lines.append(f"  Covered:     {self.coverage['covered_math']}")
        if self.coverage["uncovered_sections"]:
            lines.append(f"  Uncovered:   {', '.join(self.coverage['uncovered_sections'])}")
        lines.append("")

        # Test results
        lines.append("## Test Results")
        lines.append("")
        lines.append(f"  Status: {'PASSED' if self.test_passed else 'FAILED'}")
        for error in self.test_errors:
            lines.append(f"  ERROR: {error}")
        for warning in self.test_warnings:
            lines.append(f"  WARNING: {warning}")
        lines.append("")

        return "\n".join(lines)


def generate_report(
    registry: Registry,
    blocks: list[Block],
    *,
    test_result: "TestResult | None" = None,
) -> Report:
    """Generate a validation report from registry state and parsed blocks."""
    symbol_table = _build_symbol_table(registry)
    dependencies = _build_dependency_graph(registry)
    cov = coverage_metric(blocks)

    if test_result is None:
        test_result = registry.run_tests(strict=True)

    return Report(
        symbol_table=symbol_table,
        dependencies=dependencies,
        test_passed=test_result.passed,
        test_errors=test_result.errors,
        test_warnings=test_result.warnings,
        coverage={
            "total_math": cov.total_math,
            "covered_math": cov.covered_math,
            "uncovered_sections": cov.uncovered_sections,
        },
    )


def _build_symbol_table(registry: Registry) -> list[dict]:
    """Build a list of symbol descriptors in registration order."""
    table: list[dict] = []
    for name in registry._registration_order:
        sym = registry.symbols[name]
        entry: dict = {
            "name": sym.name,
            "description": sym.description,
        }
        match sym:
            case SetSymbol():
                entry["type"] = "Set"
            case ParameterSymbol():
                entry["type"] = "Parameter"
                entry["index"] = list(sym.index) if sym.index else []
                entry["domain"] = sym.domain
                entry["units"] = str(sym.units)
            case VariableSymbol():
                entry["type"] = "Variable"
                entry["index"] = list(sym.index) if sym.index else []
                entry["domain"] = sym.domain
                entry["bounds"] = list(sym.bounds)
                entry["units"] = str(sym.units)
            case ExpressionSymbol():
                entry["type"] = "Expression"
                entry["index"] = list(sym.index) if sym.index else []
                entry["units"] = str(sym.units)
            case ConstraintSymbol():
                entry["type"] = "Constraint"
                entry["over"] = [sym.over] if sym.over else []
                entry["constraint_type"] = sym.constraint_type
            case ObjectiveSymbol():
                entry["type"] = "Objective"
                entry["sense"] = sym.sense
        table.append(entry)
    return table


def _build_dependency_graph(registry: Registry) -> list[dict]:
    """Build dependency edges from over/index fields."""
    edges: list[dict] = []
    for name in registry._registration_order:
        sym = registry.symbols[name]
        refs = []
        if hasattr(sym, "over") and sym.over:
            refs.append(sym.over)
        if hasattr(sym, "index") and sym.index:
            for idx in (sym.index if isinstance(sym.index, tuple) else (sym.index,)):
                refs.append(idx)
        for ref in sorted(set(refs)):
            edges.append({"from": name, "to": ref})
    return edges
