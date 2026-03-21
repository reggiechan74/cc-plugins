import pytest
from meta_compiler.verification import VerificationResult, check_axiom_consistency, check_property

z3 = pytest.importorskip("z3")


def test_consistent_axioms():
    """Two non-contradictory axioms should be consistent."""
    H = z3.Real('H')
    M = z3.Real('M')
    axiom_exprs = [lambda: H > 0, lambda: M >= 0]
    result = check_axiom_consistency(axiom_exprs)
    assert result.status == "consistent"
    assert result.error is None


def test_contradictory_axioms():
    """Contradictory axioms should be detected."""
    H = z3.Real('H')
    axiom_exprs = [lambda: H > 0, lambda: H < 0]
    result = check_axiom_consistency(axiom_exprs)
    assert result.status == "contradictory"


def test_property_holds():
    """A valid implication should be verified."""
    H = z3.Real('H')
    M = z3.Real('M')
    axiom_exprs = [lambda: H > 0, lambda: M >= 0, lambda: M <= H]
    prop_expr = lambda: H - M >= 0
    result = check_property(axiom_exprs, prop_expr)
    assert result.status == "verified"


def test_property_fails_with_counterexample():
    """An invalid implication should provide a counterexample."""
    H = z3.Real('H')
    M = z3.Real('M')
    axiom_exprs = [lambda: H > 0, lambda: M >= 0]
    prop_expr = lambda: H - M >= 0  # Not true: M could exceed H
    result = check_property(axiom_exprs, prop_expr)
    assert result.status == "failed"
    assert result.counterexample is not None
    assert isinstance(result.counterexample, dict)


class TestVerificationResultDataclass:
    def test_consistent_result(self):
        r = VerificationResult(status="consistent")
        assert r.status == "consistent"
        assert r.counterexample is None
        assert r.error is None
        assert r.duration_s is None

    def test_failed_result_with_counterexample(self):
        r = VerificationResult(status="failed", counterexample={"H": 1, "M": 2})
        assert r.counterexample == {"H": 1, "M": 2}
