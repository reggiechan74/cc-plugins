"""Two-mode executor for .model.md validation blocks.

Structural mode (no fixture): registers symbols, stores expr callables,
runs structural checks only.

Numeric mode (fixture present): loads fixture data, executes expr functions
against real values, checks constraints numerically, then runs structural checks.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field

from meta_compiler.checks import collect_scalar_refs
from meta_compiler.compiler.parser import Block, FixtureBlock, ValidationBlock
from meta_compiler.registry import Registry, registry
from meta_compiler.symbols import ConstraintSymbol, ObjectiveSymbol


@dataclass
class ExecutionResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    registry: Registry | None = None


def execute_blocks(
    blocks: list[Block], *, strict: bool = False
) -> ExecutionResult:
    """Execute fixture + validation blocks and run checks."""
    registry.reset()
    errors: list[str] = []
    warnings: list[str] = []

    fixture_blocks = [b for b in blocks if isinstance(b, FixtureBlock)]
    validate_blocks = [b for b in blocks if isinstance(b, ValidationBlock)]

    has_fixtures = len(fixture_blocks) > 0

    # Step 1: Execute fixture blocks to build data store
    if has_fixtures:
        fixture_ns: dict = {}
        for fb in fixture_blocks:
            try:
                exec(fb.code, fixture_ns)
            except Exception as e:
                errors.append(f"Fixture error (line {fb.line_number}): {e}")
                return ExecutionResult(passed=False, errors=errors,
                                       warnings=warnings, registry=None)

        # Build data_store: every name in fixture namespace that isn't a dunder
        for name, value in fixture_ns.items():
            if not name.startswith("_"):
                registry.data_store[name] = value

    # Step 2: Build validation namespace
    from meta_compiler import Set, Parameter, Variable, Expression, Constraint, Objective, S
    ns = {
        "Set": Set, "Parameter": Parameter, "Variable": Variable,
        "Expression": Expression, "Constraint": Constraint,
        "Objective": Objective, "S": S, "registry": registry,
    }

    # Step 3: Execute validation blocks
    # The DSL surface (Set, Parameter, etc.) does NOT require users to
    # capture return values. The validate block says:
    #   Set("W", description="Workers")
    #   Parameter("cap", index="W", ...)
    #   Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
    #
    # The lambda references `cap` by name, but `cap` was never assigned
    # in the namespace. The registry auto-injects proxies into `ns` when
    # symbols are registered via registry._exec_namespace.
    registry._exec_namespace = ns

    for vb in validate_blocks:
        try:
            registry._current_block_source = vb.code
            exec(vb.code, ns)
            collect_scalar_refs(vb.code, registry.scalar_names, registry.access_log)
        except Exception as e:
            errors.append(f"Validation error (line {vb.line_number}): {e}")
            return ExecutionResult(passed=False, errors=errors,
                                   warnings=warnings, registry=registry)

    registry._exec_namespace = None
    registry._current_block_source = None

    # Step 4: In numeric mode, evaluate constraints and objectives
    if has_fixtures:
        for name, sym in registry.symbols.items():
            if isinstance(sym, ConstraintSymbol) and sym.expr is not None:
                try:
                    _check_constraint(sym, registry, errors)
                except Exception as e:
                    errors.append(f"Error in constraint \"{sym.name}\": {e}")

            elif isinstance(sym, ObjectiveSymbol) and sym.expr is not None:
                try:
                    result = sym.expr() if _arity(sym.expr) == 0 else None
                    if result is not None and not isinstance(result, (int, float)):
                        errors.append(
                            f"Objective \"{sym.name}\" returned {type(result).__name__}, "
                            f"expected numeric value"
                        )
                except Exception as e:
                    errors.append(f"Error in objective \"{sym.name}\": {e}")

    # Step 5: Run structural checks
    from meta_compiler.checks import run_all_checks
    check_result = run_all_checks(registry, strict=strict)
    errors.extend(check_result.errors)
    warnings.extend(check_result.warnings)

    return ExecutionResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        registry=registry,
    )


def _check_constraint(sym: ConstraintSymbol, reg: Registry, errors: list[str]):
    """Evaluate a constraint against fixture data."""
    arity = _arity(sym.expr)

    if arity == 0:
        result = sym.expr()
        if result is not True:
            errors.append(
                f"Constraint \"{sym.name}\" failed (returned {result!r})"
            )
    else:
        if sym.over is None:
            errors.append(
                f"Constraint \"{sym.name}\" has positional args but no 'over' set"
            )
            return

        if sym.over not in reg.data_store:
            errors.append(
                f"Constraint \"{sym.name}\": set \"{sym.over}\" has no fixture data"
            )
            return

        members = reg.data_store[sym.over]
        if not isinstance(members, list):
            errors.append(
                f"Constraint \"{sym.name}\": fixture data for set \"{sym.over}\" "
                f"must be a list"
            )
            return

        for member in members:
            result = sym.expr(member)
            if result is not True:
                errors.append(
                    f"Constraint \"{sym.name}\" violated for "
                    f"{sym.over}=\"{member}\": result is {result!r}"
                )


def _arity(fn) -> int:
    """Return the number of positional parameters of a function."""
    sig = inspect.signature(fn)
    return sum(
        1 for p in sig.parameters.values()
        if p.default is inspect.Parameter.empty
        and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    )
