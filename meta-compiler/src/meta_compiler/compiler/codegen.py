"""Generate standalone Python codebase from registry state."""

from __future__ import annotations

from meta_compiler.registry import Registry
from meta_compiler.symbols import (
    ConstraintSymbol,
    ExpressionSymbol,
    ObjectiveSymbol,
    ParameterSymbol,
    SetSymbol,
    VariableSymbol,
)


def generate_codebase(registry: Registry) -> dict[str, str]:
    """Generate a dict of filename → Python source code.

    Splits registered symbols by type into separate modules.
    Each module imports from the shared registry.
    """
    files: dict[str, str] = {}

    files["registry.py"] = _REGISTRY_TEMPLATE
    files["sets.py"] = _generate_sets(registry)
    files["parameters.py"] = _generate_parameters(registry)
    files["variables.py"] = _generate_variables(registry)
    files["expressions.py"] = _generate_expressions(registry)
    files["constraints.py"] = _generate_constraints(registry)
    files["objectives.py"] = _generate_objectives(registry)
    files["__main__.py"] = _MAIN_TEMPLATE

    return files


def _symbols_of_type(registry: Registry, sym_type: type) -> list:
    """Get symbols in registration order filtered by type."""
    return [
        registry.symbols[name]
        for name in registry._registration_order
        if isinstance(registry.symbols.get(name), sym_type)
    ]


def _generate_sets(registry: Registry) -> str:
    lines = [
        '"""Set declarations."""',
        "from meta_compiler import Set",
        "",
    ]
    for sym in _symbols_of_type(registry, SetSymbol):
        lines.append(f'Set({sym.name!r}, description={sym.description!r})')
    return "\n".join(lines) + "\n"


def _generate_parameters(registry: Registry) -> str:
    lines = [
        '"""Parameter declarations."""',
        "from meta_compiler import Parameter",
        "",
    ]
    for sym in _symbols_of_type(registry, ParameterSymbol):
        idx = list(sym.index) if sym.index else None
        parts = [repr(sym.name)]
        if idx:
            parts.append(f"index={idx}")
        parts.append(f"domain={sym.domain!r}")
        parts.append(f"units={str(sym.units)!r}")
        parts.append(f"description={sym.description!r}")
        lines.append(f'{sym.name} = Parameter({", ".join(parts)})')
    return "\n".join(lines) + "\n"


def _generate_variables(registry: Registry) -> str:
    lines = [
        '"""Variable declarations."""',
        "from meta_compiler import Variable",
        "",
    ]
    for sym in _symbols_of_type(registry, VariableSymbol):
        idx = list(sym.index) if sym.index else None
        parts = [repr(sym.name)]
        if idx:
            parts.append(f"index={idx}")
        parts.append(f"domain={sym.domain!r}")
        parts.append(f"bounds={sym.bounds}")
        parts.append(f"units={str(sym.units)!r}")
        parts.append(f"description={sym.description!r}")
        lines.append(f'{sym.name} = Variable({", ".join(parts)})')
    return "\n".join(lines) + "\n"


def _render_expr(node: object) -> str:
    """Render an expression tree node back to Python source code."""
    from meta_compiler.expr import (
        ArithExpr,
        CompareExpr,
        IndexExpr,
        NegExpr,
        SumExpr,
        SymbolRef,
    )

    match node:
        case SymbolRef(name=name):
            return name
        case IndexExpr(symbol=symbol, indices=indices):
            idx_str = ", ".join(indices)
            return f"{symbol}[{idx_str}]"
        case ArithExpr(left=left, op=op, right=right):
            return f"{_render_expr(left)} {op} {_render_expr(right)}"
        case CompareExpr(left=left, op=op, right=right):
            return f"{_render_expr(left)} {op} {_render_expr(right)}"
        case SumExpr(body=body, over_set=over_set):
            return f"sum({_render_expr(body)} for _{over_set} in S(\"{over_set}\"))"
        case NegExpr(operand=operand):
            return f"-{_render_expr(operand)}"
        case _:
            return repr(node)


def _lambda_params(index: tuple[str, ...]) -> str:
    """Generate lambda parameter names from index sets."""
    if not index:
        return ""
    params = [s.lower()[0] if s else "_" for s in index]
    seen: dict[str, int] = {}
    result: list[str] = []
    for p in params:
        if p in seen:
            seen[p] += 1
            result.append(f"{p}{seen[p]}")
        else:
            seen[p] = 0
            result.append(p)
    return ", ".join(result)


def _generate_expressions(registry: Registry) -> str:
    lines = [
        '"""Expression declarations."""',
        "from meta_compiler import Expression, S",
        "",
    ]
    for sym in _symbols_of_type(registry, ExpressionSymbol):
        idx = list(sym.index) if sym.index else None
        params = _lambda_params(sym.index)
        body = _render_expr(sym.expr_tree)
        parts = [repr(sym.name)]
        parts.append(f"definition=lambda {params}: {body}")
        if idx:
            parts.append(f"index={idx}")
        parts.append(f"units={str(sym.units)!r}")
        parts.append(f"description={sym.description!r}")
        lines.append(f'{sym.name} = Expression({", ".join(parts)})')
    return "\n".join(lines) + "\n"


def _generate_constraints(registry: Registry) -> str:
    lines = [
        '"""Constraint declarations."""',
        "from meta_compiler import Constraint, S",
        "",
    ]
    for sym in _symbols_of_type(registry, ConstraintSymbol):
        over = list(sym.over) if sym.over else None
        params = _lambda_params(sym.over)
        body = _render_expr(sym.expr_tree)
        parts = [repr(sym.name)]
        parts.append(f"expr=lambda {params}: {body}")
        if over:
            parts.append(f"over={over}")
        parts.append(f"type={sym.constraint_type!r}")
        parts.append(f"description={sym.description!r}")
        lines.append(f'Constraint({", ".join(parts)})')
    return "\n".join(lines) + "\n"


def _generate_objectives(registry: Registry) -> str:
    lines = [
        '"""Objective declarations."""',
        "from meta_compiler import Objective, S",
        "",
    ]
    for sym in _symbols_of_type(registry, ObjectiveSymbol):
        body = _render_expr(sym.expr_tree)
        parts = [repr(sym.name)]
        parts.append(f"expr=lambda: {body}")
        parts.append(f"sense={sym.sense!r}")
        parts.append(f"description={sym.description!r}")
        lines.append(f'Objective({", ".join(parts)})')
    return "\n".join(lines) + "\n"


_REGISTRY_TEMPLATE = '''"""Registry engine — imports and re-exports the meta_compiler registry."""
from meta_compiler import Set, Parameter, Variable, Expression, Constraint, Objective, S
from meta_compiler.registry import registry
'''

_MAIN_TEMPLATE = '''"""Entry point: import all modules in order and run validation."""
import sets as model_sets
import parameters as model_parameters
import variables as model_variables
import expressions as model_expressions
import constraints as model_constraints
import objectives as model_objectives

from meta_compiler.registry import registry

if __name__ == "__main__":
    result = registry.run_tests(strict=True)
    if result.passed:
        print("ALL CHECKS PASSED")
    else:
        print("VALIDATION FAILED")
        for error in result.errors:
            print(f"  ERROR: {error}")
    for warning in result.warnings:
        print(f"  WARNING: {warning}")
'''
