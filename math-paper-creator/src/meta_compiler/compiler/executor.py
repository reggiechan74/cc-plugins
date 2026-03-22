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
from meta_compiler.compiler.parser import Block, FixtureBlock, ResultsBlock, ValidationBlock
from meta_compiler.registry import Registry, registry
from meta_compiler.symbols import AxiomSymbol, ConstraintSymbol, ObjectiveSymbol, PropertySymbol


def _coerce_bool(value) -> bool:
    """Coerce constraint result to Python bool (handles numpy scalars)."""
    try:
        return bool(value)
    except (ValueError, TypeError):
        return value is True


def _is_numeric(value) -> bool:
    """Check if a value is numeric, including numpy scalar types."""
    if isinstance(value, (int, float)):
        return True
    try:
        import numpy as np
        return isinstance(value, (np.integer, np.floating))
    except ImportError:
        return False


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

    # Step 1b: Execute results blocks in fixture namespace, capture stdout
    results_blocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    if results_blocks:
        import io
        import contextlib

        for rb in results_blocks:
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    exec(rb.code, fixture_ns if has_fixtures else {})
            except Exception as e:
                errors.append(f"Results error (line {rb.line_number}): {e}")
                return ExecutionResult(passed=False, errors=errors,
                                       warnings=warnings, registry=None)
            rb.output = buf.getvalue()

    # Step 2: Build validation namespace
    from meta_compiler import Set, Parameter, Variable, Expression, Constraint, Objective, S, Axiom, Property
    ns = {
        "Set": Set, "Parameter": Parameter, "Variable": Variable,
        "Expression": Expression, "Constraint": Constraint,
        "Objective": Objective, "S": S, "Axiom": Axiom,
        "Property": Property, "registry": registry,
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
                    if result is not None and not _is_numeric(result):
                        errors.append(
                            f"Objective \"{sym.name}\" returned {type(result).__name__}, "
                            f"expected numeric value"
                        )
                except Exception as e:
                    errors.append(f"Error in objective \"{sym.name}\": {e}")

    # Step 4b: Verify axioms and properties (if Z3 expressions present)
    axiom_syms = [
        sym for sym in registry.symbols.values()
        if isinstance(sym, AxiomSymbol) and sym.z3_expr is not None
    ]
    if axiom_syms:
        from meta_compiler.verification import check_axiom_consistency, check_property, z3_available
        if z3_available():
            # Consistency check
            consistency = check_axiom_consistency([s.z3_expr for s in axiom_syms])
            if consistency.status == "contradictory":
                axiom_names = ", ".join(s.name for s in axiom_syms)
                errors.append(
                    f"Axioms are contradictory: {axiom_names} cannot all hold simultaneously"
                )
            elif consistency.status == "error":
                errors.append(f"Axiom consistency check error: {consistency.error}")

            # Property implication checks
            for name, sym in registry.symbols.items():
                if isinstance(sym, PropertySymbol):
                    given_exprs = [
                        registry.symbols[ax_name].z3_expr
                        for ax_name in sym.given
                        if isinstance(registry.symbols.get(ax_name), AxiomSymbol)
                        and registry.symbols[ax_name].z3_expr is not None
                    ]
                    if given_exprs:
                        prop_result = check_property(given_exprs, sym.z3_expr)
                        if prop_result.status == "failed":
                            ce = prop_result.counterexample or {}
                            ce_str = ", ".join(f"{k}={v}" for k, v in ce.items())
                            errors.append(
                                f'Property "{sym.name}" does NOT follow from '
                                f'{", ".join(sym.given)}'
                                f'{" — counterexample: " + ce_str if ce_str else ""}'
                            )
                        elif prop_result.status == "error":
                            errors.append(
                                f'Property "{sym.name}" verification error: {prop_result.error}'
                            )

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
        try:
            result = sym.expr()
        except NameError as e:
            missing = str(e).split("'")[1]
            if missing in reg.data_store:
                errors.append(
                    f'Constraint "{sym.name}": "{missing}" is computed in fixture '
                    f'but not registered as a Parameter — add Parameter("{missing}", ...) '
                    f'to the validate block to use it in constraints'
                )
            else:
                errors.append(f'Error in constraint "{sym.name}": {e}')
            return
        if not _coerce_bool(result):
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
            try:
                result = sym.expr(member)
            except NameError as e:
                missing = str(e).split("'")[1]
                if missing in reg.data_store:
                    errors.append(
                        f'Constraint "{sym.name}": "{missing}" is computed in fixture '
                        f'but not registered as a Parameter — add Parameter("{missing}", ...) '
                        f'to the validate block to use it in constraints'
                    )
                else:
                    errors.append(f'Error in constraint "{sym.name}": {e}')
                return
            if not _coerce_bool(result):
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
