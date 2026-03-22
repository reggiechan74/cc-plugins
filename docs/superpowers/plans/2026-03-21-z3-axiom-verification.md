# Z3 Axiom Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `Axiom` and `Property` symbol types to the meta-compiler with Z3-based consistency and implication verification.

**Architecture:** Two new symbol types (`AxiomSymbol`, `PropertySymbol`) register through the existing registry pattern. A new `verification.py` module wraps Z3 solver calls behind a lazy import so the feature degrades gracefully when z3-solver is not installed. The executor gains a verification pass that runs after constraint evaluation, and results appear in reports and CLI output.

**Tech Stack:** Python 3.10+, z3-solver (optional dependency via `[verification]` extra), pytest

**Spec:** `docs/superpowers/specs/2026-03-20-z3-axiom-verification-design.md`

---

## Design Decisions (from spec open questions)

1. **Z3 variable namespace:** Z3 expressions use their own `z3.Real`/`z3.Int`/`z3.Bool` variables, not meta-compiler SymbolProxy objects. The `z3_expr` lambda captures Z3 variables from the validate block's local scope. This keeps Z3's type system separate from the meta-compiler's domain system.

2. **Z3 types:** Users declare Z3 variables explicitly in their validate block (`from z3 import Real; H = Real('H')`). The meta-compiler does not auto-infer Z3 types — this avoids a fragile mapping layer and keeps Z3 usage transparent.

3. **Counterexamples:** Failed implication checks report the counterexample model in the error message (e.g., `H=1, M=1, beta=2`). They are NOT auto-converted to fixture scenarios — that's a separate future feature.

4. **Indexed axioms:** Out of scope for v1. Axioms operate on unindexed Z3 variables. Quantified axioms (`ForAll`) can be expressed directly in Z3 syntax by the user.

5. **Comparative statics (monotonicity verification):** Deferred to v2. The spec lists this as Verification Mode 3, but it requires quantifier reasoning (`ForAll beta1, beta2...`) which adds significant complexity. Users can express these directly in Z3 syntax via `Property` if needed.

6. **Z3 variables live in validate blocks, not fixture blocks:** Z3 symbolic variables (`Real('H')`) are part of the logical validation, not concrete fixture data. Declaring them in `python:fixture` blocks would cause them to be wrapped in `SymbolProxy` by the executor's auto-injection, breaking Z3 operations. Always declare Z3 variables in `python:validate` blocks.

## File Structure

```
src/meta_compiler/
  symbols.py          — MODIFY: add AxiomSymbol, PropertySymbol dataclasses
  registry.py         — MODIFY: add register_axiom(), register_property()
  __init__.py          — MODIFY: add Axiom(), Property() DSL functions
  verification.py     — CREATE: Z3 consistency/implication checker
  compiler/
    executor.py       — MODIFY: add verification pass after constraint evaluation
    report.py         — MODIFY: add verification section to report
  cli.py              — MODIFY: add verify subcommand
commands/
  author.md           — MODIFY: add axiom authoring in Step 2, verification in Step 4
templates/
  _checklist.md       — MODIFY: add advisory for axiom declaration
pyproject.toml        — MODIFY: add z3-solver optional dependency
tests/
  test_axioms.py      — CREATE: axiom/property registration tests
  test_verification.py — CREATE: Z3 verification logic tests
  compiler/
    test_executor_verification.py — CREATE: executor verification integration tests
    test_cli_verify.py — CREATE: CLI verify subcommand tests
```

---

### Task 1: Add AxiomSymbol and PropertySymbol dataclasses

**Files:**
- Modify: `src/meta_compiler/symbols.py`
- Test: `tests/test_axioms.py`

- [ ] **Step 1: Write failing test for AxiomSymbol**

Create `tests/test_axioms.py`:

```python
from meta_compiler.symbols import AxiomSymbol

def test_axiom_symbol_fields():
    ax = AxiomSymbol(name="A1", statement="H > 0", z3_expr=None, description="Positivity")
    assert ax.name == "A1"
    assert ax.statement == "H > 0"
    assert ax.z3_expr is None
    assert ax.description == "Positivity"

def test_axiom_symbol_is_frozen():
    ax = AxiomSymbol(name="A1", statement="H > 0", z3_expr=None, description="Positivity")
    import pytest
    with pytest.raises(AttributeError):
        ax.name = "A2"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_axioms.py -v`
Expected: FAIL with `ImportError: cannot import name 'AxiomSymbol'`

- [ ] **Step 3: Write failing test for PropertySymbol**

Append to `tests/test_axioms.py`:

```python
from meta_compiler.symbols import PropertySymbol

def test_property_symbol_fields():
    prop = PropertySymbol(
        name="P1", claim="t_eff >= 0",
        z3_expr=lambda: None, given=("A1", "A2"), description="Non-negative"
    )
    assert prop.name == "P1"
    assert prop.claim == "t_eff >= 0"
    assert prop.given == ("A1", "A2")
    assert prop.description == "Non-negative"
```

- [ ] **Step 4: Implement AxiomSymbol and PropertySymbol**

Add to `src/meta_compiler/symbols.py` after `ObjectiveSymbol`:

```python
@dataclass(frozen=True)
class AxiomSymbol:
    """A foundational axiom like A1 (non-negativity of hours)."""
    name: str
    statement: str
    z3_expr: object | None  # callable returning z3 expr, or None
    description: str


@dataclass(frozen=True)
class PropertySymbol:
    """A derived property like P1 (effective time is non-negative)."""
    name: str
    claim: str
    z3_expr: object  # callable returning z3 expr
    given: tuple[str, ...]  # axiom names this property depends on
    description: str
```

Update the `Symbol` union type to include both:

```python
Symbol = (SetSymbol | ParameterSymbol | VariableSymbol | ExpressionSymbol
          | ConstraintSymbol | ObjectiveSymbol | AxiomSymbol | PropertySymbol)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_axioms.py -v`
Expected: PASS (3 tests)

- [ ] **Step 6: Run full test suite for regressions**

Run: `python3 -m pytest -v`
Expected: All tests pass

- [ ] **Step 7: Commit**

```bash
git add src/meta_compiler/symbols.py tests/test_axioms.py
git commit -m "feat(math-paper-creator): add AxiomSymbol and PropertySymbol dataclasses"
```

---

### Task 2: Add registry registration methods

**Files:**
- Modify: `src/meta_compiler/registry.py`
- Test: `tests/test_axioms.py`

- [ ] **Step 1: Write failing test for register_axiom**

Append to `tests/test_axioms.py`:

```python
from meta_compiler.symbols import AxiomSymbol

def test_register_axiom(fresh_registry):
    fresh_registry.register_axiom("A1", statement="H > 0", description="Positivity")
    assert "A1" in fresh_registry.symbols
    assert isinstance(fresh_registry.symbols["A1"], AxiomSymbol)
    assert fresh_registry.symbols["A1"].statement == "H > 0"

def test_register_axiom_duplicate_raises(fresh_registry):
    fresh_registry.register_axiom("A1", statement="H > 0", description="Positivity")
    import pytest
    with pytest.raises(ValueError, match="already registered"):
        fresh_registry.register_axiom("A1", statement="M > 0", description="Other")

def test_register_axiom_with_z3_expr(fresh_registry):
    expr = lambda: "fake_z3_expr"
    fresh_registry.register_axiom("A1", statement="H > 0", z3_expr=expr, description="Positivity")
    assert fresh_registry.symbols["A1"].z3_expr is expr
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_axioms.py::test_register_axiom -v`
Expected: FAIL with `AttributeError: 'Registry' object has no attribute 'register_axiom'`

- [ ] **Step 3: Write failing test for register_property**

Append to `tests/test_axioms.py`:

```python
from meta_compiler.symbols import PropertySymbol

def test_register_property(fresh_registry):
    fresh_registry.register_axiom("A1", statement="H > 0", description="Pos")
    fresh_registry.register_axiom("A2", statement="M <= H", description="Bound")
    fresh_registry.register_property(
        "P1", claim="t_eff >= 0", z3_expr=lambda: None,
        given=["A1", "A2"], description="Non-neg"
    )
    assert "P1" in fresh_registry.symbols
    assert isinstance(fresh_registry.symbols["P1"], PropertySymbol)
    assert fresh_registry.symbols["P1"].given == ("A1", "A2")

def test_register_property_missing_axiom_raises(fresh_registry):
    import pytest
    with pytest.raises(ValueError, match="references axiom.*not registered"):
        fresh_registry.register_property(
            "P1", claim="t_eff >= 0", z3_expr=lambda: None,
            given=["A1"], description="Non-neg"
        )

def test_register_property_given_not_axiom_raises(fresh_registry):
    from meta_compiler import Set
    Set("W", description="Workers")
    import pytest
    with pytest.raises(ValueError, match="not an Axiom"):
        fresh_registry.register_property(
            "P1", claim="t_eff >= 0", z3_expr=lambda: None,
            given=["W"], description="Non-neg"
        )
```

- [ ] **Step 4: Implement register_axiom and register_property**

Add to `src/meta_compiler/registry.py` — import the new symbol types at the top:

```python
from meta_compiler.symbols import (
    AxiomSymbol,
    ...existing imports...,
    PropertySymbol,
)
```

Add methods to the `Registry` class (after `register_objective`):

```python
def register_axiom(
    self,
    name: str,
    *,
    statement: str,
    z3_expr: object | None = None,
    description: str = "",
) -> None:
    """Register a foundational axiom."""
    sym = AxiomSymbol(
        name=name, statement=statement,
        z3_expr=z3_expr, description=description,
    )
    self._register(name, sym)

def register_property(
    self,
    name: str,
    *,
    claim: str,
    z3_expr: object,
    given: list[str] | tuple[str, ...],
    description: str = "",
) -> None:
    """Register a derived property with axiom dependencies."""
    given_tuple = tuple(given)
    for axiom_name in given_tuple:
        if axiom_name not in self.symbols:
            raise ValueError(
                f'Property "{name}" references axiom "{axiom_name}" '
                f"which is not registered"
            )
        if not isinstance(self.symbols[axiom_name], AxiomSymbol):
            raise ValueError(
                f'Property "{name}" references "{axiom_name}" '
                f"which is not an Axiom (it is {type(self.symbols[axiom_name]).__name__})"
            )
    sym = PropertySymbol(
        name=name, claim=claim, z3_expr=z3_expr,
        given=given_tuple, description=description,
    )
    self._register(name, sym)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_axioms.py -v`
Expected: All tests pass

- [ ] **Step 6: Run full test suite for regressions**

Run: `python3 -m pytest -v`
Expected: All tests pass

- [ ] **Step 7: Commit**

```bash
git add src/meta_compiler/registry.py tests/test_axioms.py
git commit -m "feat(math-paper-creator): add register_axiom and register_property to Registry"
```

---

### Task 3: Add DSL surface functions

**Files:**
- Modify: `src/meta_compiler/__init__.py`
- Modify: `src/meta_compiler/compiler/executor.py` (validation namespace)
- Test: `tests/test_axioms.py`

- [ ] **Step 1: Write failing test for Axiom() DSL function**

Append to `tests/test_axioms.py`:

```python
def test_axiom_dsl_function(fresh_registry):
    from meta_compiler import Axiom
    Axiom("A1", statement="H > 0", description="Positivity")
    assert "A1" in fresh_registry.symbols

def test_property_dsl_function(fresh_registry):
    from meta_compiler import Axiom, Property
    Axiom("A1", statement="H > 0", description="Pos")
    Property("P1", claim="t_eff >= 0", z3_expr=lambda: None, given=["A1"], description="Non-neg")
    assert "P1" in fresh_registry.symbols
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_axioms.py::test_axiom_dsl_function -v`
Expected: FAIL with `ImportError: cannot import name 'Axiom'`

- [ ] **Step 3: Implement Axiom() and Property() DSL functions**

Add to `src/meta_compiler/__init__.py`:

```python
def Axiom(
    name: str,
    *,
    statement: str,
    z3_expr: object | None = None,
    description: str = "",
) -> None:
    """Declare a foundational axiom."""
    registry.register_axiom(name, statement=statement, z3_expr=z3_expr, description=description)


def Property(
    name: str,
    *,
    claim: str,
    z3_expr: object,
    given: list[str] | tuple[str, ...],
    description: str = "",
) -> None:
    """Declare a derived property."""
    registry.register_property(name, claim=claim, z3_expr=z3_expr, given=given, description=description)
```

- [ ] **Step 4: Add Axiom and Property to executor validation namespace**

In `src/meta_compiler/compiler/executor.py`, update the namespace dict in `execute_blocks` (lines 95-100):

```python
from meta_compiler import Set, Parameter, Variable, Expression, Constraint, Objective, S, Axiom, Property
ns = {
    "Set": Set, "Parameter": Parameter, "Variable": Variable,
    "Expression": Expression, "Constraint": Constraint,
    "Objective": Objective, "S": S, "Axiom": Axiom,
    "Property": Property, "registry": registry,
}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_axioms.py -v`
Expected: All tests pass

- [ ] **Step 6: Run full test suite for regressions**

Run: `python3 -m pytest -v`
Expected: All tests pass

- [ ] **Step 7: Commit**

```bash
git add src/meta_compiler/__init__.py src/meta_compiler/compiler/executor.py tests/test_axioms.py
git commit -m "feat(math-paper-creator): add Axiom() and Property() DSL surface functions"
```

---

### Task 4: Create verification module

**Files:**
- Create: `src/meta_compiler/verification.py`
- Test: `tests/test_verification.py`

- [ ] **Step 1: Write failing tests for verification logic**

Create `tests/test_verification.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_verification.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'meta_compiler.verification'`

- [ ] **Step 3: Implement verification module**

Create `src/meta_compiler/verification.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_verification.py -v`
Expected: All tests pass (or skip if z3 not installed — install first: `pip3 install z3-solver --break-system-packages`)

- [ ] **Step 5: Commit**

```bash
git add src/meta_compiler/verification.py tests/test_verification.py
git commit -m "feat(math-paper-creator): add Z3 verification module with consistency and implication checks"
```

---

### Task 5: Integrate verification into executor

**Files:**
- Modify: `src/meta_compiler/compiler/executor.py`
- Create: `tests/compiler/test_executor_verification.py`

- [ ] **Step 1: Write failing integration test**

Create `tests/compiler/test_executor_verification.py`:

```python
import pytest
z3 = pytest.importorskip("z3")

from meta_compiler.compiler.parser import parse_document
from meta_compiler.compiler.executor import execute_blocks


CONSISTENT_AXIOM_DOC = '''# Model

```python:validate
from z3 import Real
H = Real('H')
M = Real('M')
Axiom("A1", statement="H is positive", z3_expr=lambda: H > 0, description="Positivity")
Axiom("A2", statement="M bounded by H", z3_expr=lambda: M <= H, description="Bound")
```
'''


def test_consistent_axioms_pass():
    blocks = parse_document(CONSISTENT_AXIOM_DOC)
    result = execute_blocks(blocks)
    assert result.passed, f"Errors: {result.errors}"


CONTRADICTORY_AXIOM_DOC = '''# Model

```python:validate
from z3 import Real
H = Real('H')
Axiom("A1", statement="H is positive", z3_expr=lambda: H > 0, description="Pos")
Axiom("A2", statement="H is negative", z3_expr=lambda: H < 0, description="Neg")
```
'''


def test_contradictory_axioms_fail():
    blocks = parse_document(CONTRADICTORY_AXIOM_DOC)
    result = execute_blocks(blocks)
    assert not result.passed
    assert any("contradictory" in e.lower() for e in result.errors)


PROPERTY_HOLDS_DOC = '''# Model

```python:validate
from z3 import Real
H = Real('H')
M = Real('M')
Axiom("A1", statement="H positive", z3_expr=lambda: H > 0, description="Pos")
Axiom("A2", statement="M non-negative", z3_expr=lambda: M >= 0, description="Non-neg")
Axiom("A3", statement="M bounded by H", z3_expr=lambda: M <= H, description="Bound")
Property("P1", claim="H - M >= 0", z3_expr=lambda: H - M >= 0, given=["A1", "A2", "A3"], description="Non-neg effective")
```
'''


def test_property_holds_passes():
    blocks = parse_document(PROPERTY_HOLDS_DOC)
    result = execute_blocks(blocks)
    assert result.passed, f"Errors: {result.errors}"


PROPERTY_FAILS_DOC = '''# Model

```python:validate
from z3 import Real
H = Real('H')
M = Real('M')
Axiom("A1", statement="H positive", z3_expr=lambda: H > 0, description="Pos")
Axiom("A2", statement="M non-negative", z3_expr=lambda: M >= 0, description="Non-neg")
Property("P1", claim="H - M >= 0", z3_expr=lambda: H - M >= 0, given=["A1", "A2"], description="Non-neg effective")
```
'''


def test_property_fails_with_counterexample():
    blocks = parse_document(PROPERTY_FAILS_DOC)
    result = execute_blocks(blocks)
    assert not result.passed
    assert any("P1" in e and "does NOT follow" in e for e in result.errors)


NO_Z3_EXPR_DOC = '''# Model

```python:validate
Axiom("A1", statement="H is positive", description="Positivity")
```
'''


def test_axiom_without_z3_expr_skips_verification():
    """Axioms without z3_expr should register fine and skip verification."""
    blocks = parse_document(NO_Z3_EXPR_DOC)
    result = execute_blocks(blocks)
    assert result.passed
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/compiler/test_executor_verification.py -v`
Expected: FAIL — executor doesn't have verification pass yet

- [ ] **Step 3: Add verification pass to executor**

In `src/meta_compiler/compiler/executor.py`, add these imports at the top:

```python
from meta_compiler.symbols import AxiomSymbol, ConstraintSymbol, ObjectiveSymbol, PropertySymbol
```

(Replace the existing `ConstraintSymbol, ObjectiveSymbol` import at line 18.)

Add a new step between constraint evaluation (Step 4, ends at line ~146) and structural checks (Step 5, line ~147). Insert after the `if has_fixtures:` block that checks constraints/objectives:

> **Note:** The executor now has a Step 1b (results block execution, lines 76-92) added after this plan was written. The verification pass is independent of results blocks.

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/compiler/test_executor_verification.py -v`
Expected: All tests pass

- [ ] **Step 5: Run full test suite for regressions**

Run: `python3 -m pytest -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add src/meta_compiler/compiler/executor.py tests/compiler/test_executor_verification.py
git commit -m "feat(math-paper-creator): integrate Z3 verification into executor pipeline"
```

---

### Task 6: Add verification results to report

**Files:**
- Modify: `src/meta_compiler/compiler/report.py`
- Modify: `tests/compiler/test_report.py`

- [ ] **Step 1: Write failing test for report with axioms**

Add to `tests/compiler/test_report.py`:

```python
def test_report_includes_axiom_in_symbol_table(fresh_registry):
    from meta_compiler import Set, Parameter, Axiom
    from meta_compiler.compiler.parser import parse_document
    from meta_compiler.compiler.report import generate_report

    Set("W", description="Workers")
    Parameter("cap", index="W", description="Capacity")
    Axiom("A1", statement="Capacity is positive", description="Positivity")

    blocks = parse_document('''# Model
```python:validate
Set("W", description="Workers")
Parameter("cap", index="W", description="Capacity")
Axiom("A1", statement="Capacity is positive", description="Positivity")
```
''')
    report = generate_report(blocks, registry=fresh_registry)
    types = [s["type"] for s in report.symbol_table]
    assert "Axiom" in types
    axiom_entry = [s for s in report.symbol_table if s["type"] == "Axiom"][0]
    assert axiom_entry["statement"] == "Capacity is positive"

def test_report_includes_property_in_symbol_table(fresh_registry):
    from meta_compiler import Axiom, Property
    from meta_compiler.compiler.parser import parse_document
    from meta_compiler.compiler.report import generate_report

    Axiom("A1", statement="H > 0", description="Pos")
    Property("P1", claim="t_eff >= 0", z3_expr=lambda: None, given=["A1"], description="Non-neg")

    blocks = parse_document('''# Model
```python:validate
Axiom("A1", statement="H > 0", description="Pos")
Property("P1", claim="t_eff >= 0", z3_expr=lambda: None, given=["A1"], description="Non-neg")
```
''')
    report = generate_report(blocks, registry=fresh_registry)
    types = [s["type"] for s in report.symbol_table]
    assert "Property" in types
    prop_entry = [s for s in report.symbol_table if s["type"] == "Property"][0]
    assert prop_entry["claim"] == "t_eff >= 0"
    assert prop_entry["given"] == ["A1"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/compiler/test_report.py::test_report_includes_axiom_in_symbol_table -v`
Expected: FAIL — report doesn't handle AxiomSymbol in match statement

- [ ] **Step 3: Update report to handle new symbol types**

In `src/meta_compiler/compiler/report.py`, add imports:

```python
from meta_compiler.symbols import (
    AxiomSymbol,
    ...existing imports...,
    PropertySymbol,
)
```

Add cases to the `match sym:` block in `_build_symbol_table` (after `case ObjectiveSymbol()`):

```python
            case AxiomSymbol():
                entry["type"] = "Axiom"
                entry["statement"] = sym.statement
            case PropertySymbol():
                entry["type"] = "Property"
                entry["claim"] = sym.claim
                entry["given"] = list(sym.given)
```

Add an "Axiom Verification" section to `Report.to_text()` (before "## Test Results"):

```python
        # Axiom verification summary
        axioms = [s for s in self.symbol_table if s["type"] == "Axiom"]
        properties = [s for s in self.symbol_table if s["type"] == "Property"]
        if axioms:
            lines.append("## Axiom Verification")
            lines.append("")
            lines.append(f"  Axioms declared: {len(axioms)}")
            lines.append(f"  Properties declared: {len(properties)}")
            lines.append("")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/compiler/test_report.py -v`
Expected: All tests pass

- [ ] **Step 5: Run full test suite for regressions**

Run: `python3 -m pytest -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add src/meta_compiler/compiler/report.py tests/compiler/test_report.py
git commit -m "feat(math-paper-creator): add Axiom and Property to validation reports"
```

---

### Task 7: Add `verify` CLI subcommand

**Files:**
- Modify: `src/meta_compiler/cli.py`
- Create: `tests/compiler/test_cli_verify.py`

- [ ] **Step 1: Write failing test for verify subcommand**

Create `tests/compiler/test_cli_verify.py`:

```python
import pytest
z3 = pytest.importorskip("z3")

from meta_compiler.cli import main


CONSISTENT_DOC = '''# Model

```python:validate
from z3 import Real
H = Real('H')
Axiom("A1", statement="H > 0", z3_expr=lambda: H > 0, description="Pos")
```
'''

CONTRADICTORY_DOC = '''# Model

```python:validate
from z3 import Real
H = Real('H')
Axiom("A1", statement="H > 0", z3_expr=lambda: H > 0, description="Pos")
Axiom("A2", statement="H < 0", z3_expr=lambda: H < 0, description="Neg")
```
'''


def test_cli_verify_consistent(tmp_path):
    f = tmp_path / "test.model.md"
    f.write_text(CONSISTENT_DOC)
    result = main(["verify", str(f)])
    assert result == 0


def test_cli_verify_contradictory(tmp_path):
    f = tmp_path / "test.model.md"
    f.write_text(CONTRADICTORY_DOC)
    result = main(["verify", str(f)])
    assert result == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/compiler/test_cli_verify.py -v`
Expected: FAIL — no "verify" subcommand

- [ ] **Step 3: Implement verify subcommand**

Add to `src/meta_compiler/cli.py`, in `main()` after the `reconcile` parser (line 71):

```python
    # verify
    verify_parser = subparsers.add_parser("verify", help="Run Z3 axiom verification")
    verify_parser.add_argument("file", type=Path, help="Path to .model.md file")
```

Update the module docstring (line 1-9) to include the verify subcommand:

```python
    python -m meta_compiler.cli verify <file.model.md>
```

Add handler in the dispatch block (after the `reconcile` handler at line 87):

```python
    elif args.command == "verify":
        return _cmd_verify(source)
```

Add the command function:

```python
def _cmd_verify(source: str) -> int:
    from meta_compiler.compiler.parser import parse_document
    from meta_compiler.compiler.executor import execute_blocks
    from meta_compiler.verification import z3_available

    if not z3_available():
        print("z3-solver is not installed. Install with: pip install z3-solver",
              file=sys.stderr)
        return 1

    blocks = parse_document(source)
    result = execute_blocks(blocks)

    # Extract axiom/property info from registry
    from meta_compiler.symbols import AxiomSymbol, PropertySymbol
    reg = result.registry
    if reg is None:
        print("FAILED — could not build registry", file=sys.stderr)
        return 1

    axioms = [s for s in reg.symbols.values() if isinstance(s, AxiomSymbol)]
    properties = [s for s in reg.symbols.values() if isinstance(s, PropertySymbol)]
    z3_axioms = [a for a in axioms if a.z3_expr is not None]

    if not z3_axioms:
        print("No axioms with Z3 expressions found.")
        return 0

    print(f"Axiom verification (Z3):")
    print(f"  Axioms: {len(z3_axioms)}, Properties: {len(properties)}")

    if result.passed:
        print(f"  PASSED")
        for w in result.warnings:
            print(f"  WARNING: {w}")
        return 0
    else:
        print(f"  FAILED")
        for e in result.errors:
            print(f"  ERROR: {e}")
        return 1
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/compiler/test_cli_verify.py -v`
Expected: All tests pass

- [ ] **Step 5: Run full test suite for regressions**

Run: `python3 -m pytest -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add src/meta_compiler/cli.py tests/compiler/test_cli_verify.py
git commit -m "feat(math-paper-creator): add verify CLI subcommand for Z3 axiom checking"
```

---

### Task 8: Add orphan check support for Axiom/Property symbols

**Files:**
- Modify: `src/meta_compiler/checks.py`
- Test: `tests/test_axioms.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_axioms.py`:

```python
def test_axiom_not_flagged_as_orphan(fresh_registry):
    """Axioms are foundational — they shouldn't be flagged as orphans."""
    from meta_compiler import Set, Parameter, Constraint, Axiom
    Set("W", description="Workers")
    Parameter("cap", index="W", description="Capacity")
    Constraint("check", over="W", expr=lambda i: cap[i] <= 100, description="Cap check")
    Axiom("A1", statement="Capacity positive", description="Pos")
    result = fresh_registry.run_tests(strict=True)
    orphan_errors = [e for e in result.errors if "Orphan" in e and "A1" in e]
    assert orphan_errors == [], f"Axiom flagged as orphan: {orphan_errors}"

def test_property_not_flagged_as_orphan(fresh_registry):
    """Properties are consumers — they shouldn't be flagged as orphans."""
    from meta_compiler import Set, Parameter, Constraint, Axiom, Property
    Set("W", description="Workers")
    Parameter("cap", index="W", description="Capacity")
    Constraint("check", over="W", expr=lambda i: cap[i] <= 100, description="Cap check")
    Axiom("A1", statement="Capacity positive", description="Pos")
    Property("P1", claim="Some claim", z3_expr=lambda: None, given=["A1"], description="Prop")
    result = fresh_registry.run_tests(strict=True)
    orphan_errors = [e for e in result.errors if "Orphan" in e and "P1" in e]
    assert orphan_errors == [], f"Property flagged as orphan: {orphan_errors}"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_axioms.py::test_axiom_not_flagged_as_orphan -v`
Expected: Likely FAIL — AxiomSymbol not in consumer_names set

- [ ] **Step 3: Update orphan check to exclude Axiom and Property**

In `src/meta_compiler/checks.py`, update the imports:

```python
from meta_compiler.symbols import (
    AxiomSymbol,
    ConstraintSymbol, ExpressionSymbol, ObjectiveSymbol,
    PropertySymbol,
    SetSymbol, ParameterSymbol, VariableSymbol,
)
```

In `_check_orphans`, update the `consumer_names` set to include Axiom and Property:

```python
    consumer_names = {
        name for name, sym in registry.symbols.items()
        if isinstance(sym, (ConstraintSymbol, ObjectiveSymbol, AxiomSymbol, PropertySymbol))
    }
```

Also add Property's `given` axiom references to `implicit_refs`:

```python
        if isinstance(sym, PropertySymbol) and sym.given:
            for axiom_name in sym.given:
                implicit_refs.add(axiom_name)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_axioms.py -v`
Expected: All tests pass

- [ ] **Step 5: Run full test suite for regressions**

Run: `python3 -m pytest -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add src/meta_compiler/checks.py tests/test_axioms.py
git commit -m "feat(math-paper-creator): exclude Axiom/Property from orphan checks, track given refs"
```

---

### Task 9: Update pyproject.toml with optional Z3 dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add z3-solver as optional dependency**

Add to `pyproject.toml` under `[project.optional-dependencies]`:

```toml
[project.optional-dependencies]
dev = ["pytest>=7.0"]
verification = ["z3-solver>=4.12"]
```

- [ ] **Step 2: Verify install works**

Run: `pip3 install -e ".[verification]" --break-system-packages 2>&1 | tail -5`
Expected: z3-solver installs successfully

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore(math-paper-creator): add z3-solver as optional verification dependency"
```

---

### Task 10: Update authoring workflow and checklist

**Files:**
- Modify: `commands/author.md`
- Modify: `templates/_checklist.md`

- [ ] **Step 1: Update author.md Step 2 — add axiom prompt**

After the epistemic scope declaration section in Step 2, add:

```markdown
#### Axiom Declaration (structural / decision_framework papers only)

If `epistemic_type` is `structural` or `decision_framework`, prompt:

> "Would you like to declare foundational axioms for this model? Axioms are explicit assumptions stated without proof — everything else derives from them. (Recommended for structural papers.)"

If accepted, the first authoring section (before Parameters) is "Axioms and Assumptions." For each axiom:
- Prose statement explaining the assumption
- Display math: `$$H > 0$$`
- `python:validate` block registering: `Axiom("A1", statement="H > 0", z3_expr=lambda: H > 0, description="...")`
- The `z3_expr` is optional — include it if Z3 verification is desired

Z3 variables must be declared in the `python:validate` block (NOT in fixture blocks — fixture data gets wrapped in SymbolProxy which breaks Z3 operations):
```python
from z3 import Real
H = Real('H')
Axiom("A1", statement="H > 0", z3_expr=lambda: H > 0, description="...")
```
```

- [ ] **Step 2: Update author.md Step 4 — add verification output**

> **Note:** `author.md` now has a prose-math reconciliation checkpoint at Step 3.5 (added after this plan was written). Position verification output after reconciliation in the Step 4 completion flow.

In the Step 4 completion section, after the meta-compiler check, add:

```markdown
#### Axiom Verification (if Z3 expressions present)

If any Axiom symbols have `z3_expr`, the executor automatically:
1. Checks axiom consistency
2. Checks property implications
3. Reports results in the completion summary:

```
Axiom verification (Z3):
  ✓ Axioms A1-A4 are consistent (sat in 0.02s)
  ✓ Property P1 follows from A1, A2, A3
  ✗ Property P2 does NOT follow from A1, A2 — counterexample: H=1, M=1, beta=2
```

Reference Z3 results in the four-tests conclusion frame:
- Test 1 (Non-contradiction): cite axiom consistency check
- Test 3 (Comparative statics): cite monotonicity verification if applicable
```

- [ ] **Step 3: Update author.md API reference section**

In the "API reference and known constraints" section (lines 298-367), add `Axiom` and `Property` to the import line and add usage examples after the Objective section:

```python
from meta_compiler import Set, Parameter, Variable, Expression, Constraint, Objective, S, Axiom, Property, registry

# ... existing examples ...

# Axioms — foundational assumptions (z3_expr optional, for machine verification)
Axiom("A1", statement="H > 0", z3_expr=lambda: H > 0, description="Positivity")

# Properties — derived claims that follow from axioms
Property("P1", claim="H - M >= 0",
         z3_expr=lambda: H - M >= 0,
         given=["A1", "A2"],
         description="Non-negative effective time")
```

- [ ] **Step 4: Update _checklist.md — add advisory**

Add to the Advisories section in `templates/_checklist.md`:

```markdown
- Structural/decision papers declare foundational axioms with Z3 expressions for machine verification
```

- [ ] **Step 5: Commit**

```bash
git add commands/author.md templates/_checklist.md
git commit -m "feat(math-paper-creator): add axiom authoring workflow and checklist advisory"
```

---

### Task 11: Full integration test and version bump

**Files:**
- Test: run full suite
- Modify: version files (via `/version-bump`)

- [ ] **Step 1: Run complete test suite**

Run: `python3 -m pytest -v`
Expected: All tests pass

- [ ] **Step 2: Run a manual end-to-end verify**

Create a temporary test document and run the CLI:

```bash
cat > /tmp/test-axioms.model.md << 'EOF'
# Test Model

## Axioms

```python:validate
from z3 import Real
H = Real('H')
M = Real('M')
Axiom("A1", statement="H is positive", z3_expr=lambda: H > 0, description="Positivity")
Axiom("A2", statement="M bounded by H", z3_expr=lambda: M <= H, description="Feasibility bound")
Property("P1", claim="H - M >= 0", z3_expr=lambda: H - M >= 0, given=["A1", "A2"], description="Non-negative effective time")
```
EOF
python3 -m meta_compiler.cli verify /tmp/test-axioms.model.md
```

Expected: Output shows axiom consistency and property verification passing.

- [ ] **Step 3: Version bump**

Run: `/version-bump math-paper-creator 0.6.0`

- [ ] **Step 4: Final commit and push**

```bash
git push
```
