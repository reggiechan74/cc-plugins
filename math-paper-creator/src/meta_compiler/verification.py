"""Z3-based axiom verification for the meta-compiler.

Provides consistency checking (are axioms self-consistent?) and
implication checking (does a property follow from given axioms?).

Requires z3-solver: pip install z3-solver
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class VerificationResult:
    """Result of a Z3 verification check."""
    status: str  # "consistent", "contradictory", "verified", "failed", "skipped", "error"
    counterexample: dict | None = None
    error: str | None = None
    duration_s: float | None = None


def z3_available() -> bool:
    """Check if z3-solver is installed."""
    try:
        import z3
        return True
    except ImportError:
        return False


def check_axiom_consistency(
    axiom_exprs: list[object],
) -> VerificationResult:
    """Check whether a set of axiom Z3 expressions are mutually consistent.

    Returns VerificationResult with status "consistent" or "contradictory".
    """
    try:
        import z3
    except ImportError:
        return VerificationResult(status="skipped", error="z3-solver not installed")

    start = time.monotonic()
    try:
        solver = z3.Solver()
        for expr_fn in axiom_exprs:
            solver.add(expr_fn())

        result = solver.check()
        duration = time.monotonic() - start

        if result == z3.sat:
            return VerificationResult(status="consistent", duration_s=duration)
        elif result == z3.unsat:
            return VerificationResult(status="contradictory", duration_s=duration)
        else:
            return VerificationResult(
                status="error", error="Z3 returned unknown",
                duration_s=duration,
            )
    except Exception as e:
        return VerificationResult(
            status="error", error=str(e),
            duration_s=time.monotonic() - start,
        )


def check_property(
    axiom_exprs: list[object],
    property_expr: object,
) -> VerificationResult:
    """Check whether a property follows from given axioms.

    Uses proof by contradiction: if axioms AND NOT(property) is unsat,
    then the property is implied by the axioms.
    """
    try:
        import z3
    except ImportError:
        return VerificationResult(status="skipped", error="z3-solver not installed")

    start = time.monotonic()
    try:
        solver = z3.Solver()
        for expr_fn in axiom_exprs:
            solver.add(expr_fn())
        solver.add(z3.Not(property_expr()))

        result = solver.check()
        duration = time.monotonic() - start

        if result == z3.unsat:
            # No counterexample exists — property is implied
            return VerificationResult(status="verified", duration_s=duration)
        elif result == z3.sat:
            # Counterexample found — property does NOT follow
            model = solver.model()
            counterexample = {
                str(d): str(model[d]) for d in model.decls()
            }
            return VerificationResult(
                status="failed", counterexample=counterexample,
                duration_s=duration,
            )
        else:
            return VerificationResult(
                status="error", error="Z3 returned unknown",
                duration_s=duration,
            )
    except Exception as e:
        return VerificationResult(
            status="error", error=str(e),
            duration_s=time.monotonic() - start,
        )
