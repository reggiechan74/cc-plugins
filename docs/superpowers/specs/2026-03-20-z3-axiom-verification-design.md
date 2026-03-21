# Z3 Axiom Verification

**Date:** 2026-03-20
**Plugin:** math-paper-creator
**Status:** Draft (future milestone)

## Problem

The meta-compiler validates numerical consistency (formulas compute, constraints hold against fixture data) but cannot verify logical properties. Papers make structural claims — "these axioms are consistent," "this constraint system has no contradictions," "parameter changes shift the optimum in the expected direction" — that are currently unverified assertions. Z3 can close this gap without requiring users to install external toolchains.

## Proposed Solution

Add an `Axiom` symbol type to the meta-compiler and use Z3 (Microsoft's SMT solver, `pip install z3-solver`) to verify axiom consistency and logical properties.

### What Z3 Can Verify

Z3 is a Satisfiability Modulo Theories (SMT) solver. It works with first-order logic + arithmetic, not full higher-order proofs. Practical for:

| Verification | Example |
|---|---|
| Axiom consistency | "Axioms A1-A4 are not self-contradicting" |
| Constraint satisfiability | "There exists at least one feasible solution" |
| Implication checking | "If A1 and A2 hold, then property P follows" |
| Comparative statics | "If beta increases, t_eff decreases" (monotonicity) |
| Bound verification | "x is always in [0, 1] given these constraints" |
| Counterexample generation | "Here's a concrete case where the constraint is violated" |

Not practical for: inductive proofs, proofs over infinite structures, higher-order logic (those need Lean/Coq).

### New Symbol Type: Axiom

```python
Axiom("A1",
      statement="Total hours H is strictly positive",
      z3_expr=lambda: H > 0,
      description="Non-negativity of available hours")

Axiom("A2",
      statement="Meeting hours cannot exceed total hours",
      z3_expr=lambda: M <= H,
      description="Physical feasibility bound")
```

**Fields:**
- `statement` — human-readable text for the paper prose
- `z3_expr` — a lambda returning a Z3 expression for machine verification
- `description` — standard meta-compiler description

Axioms are declared at the front of the paper (before Parameters), establishing the foundational assumptions everything else builds on.

### Verification Modes

**1. Consistency check** — verify axioms don't contradict each other:

```python
from z3 import Solver, sat
s = Solver()
for axiom in registry.axioms:
    s.add(axiom.z3_expr())
result = s.check()  # sat = consistent, unsat = contradictory
```

**2. Implication check** — verify a property follows from axioms:

```python
Property("P1",
         claim="Effective time is non-negative",
         z3_expr=lambda: H - M * beta >= 0,
         given=["A1", "A2", "A3"])
# Checks: A1 ∧ A2 ∧ A3 → P1
```

**3. Comparative statics** — verify monotonicity:

```python
# "Increasing beta decreases t_eff"
# Z3 checks: ∀ beta1, beta2. beta1 < beta2 → t_eff(beta1) > t_eff(beta2)
```

### Integration with Epistemic Hygiene (#8)

The `epistemic_type` from issue #8 determines which verifications are offered:

- **`structural` / `decision_framework`:** Offer axiom consistency + implication checks. The paper earns: "Under axioms A1-A4, verified consistent by SMT solver, the model implies X."
- **`empirical`:** Axioms less relevant (assumptions are empirical, not logical). Skip or offer only constraint satisfiability.

The four-tests conclusion frame (#8, item 5) can reference Z3 results:
- Test 1 (Non-contradiction): Z3 axiom consistency check
- Test 3 (Comparative statics): Z3 monotonicity verification

## Symbol Registration

```python
# New in meta_compiler/__init__.py
def Axiom(name, *, statement, z3_expr=None, description=""):
    return registry.register_axiom(name, statement=statement,
                                    z3_expr=z3_expr, description=description)

def Property(name, *, claim, z3_expr, given, description=""):
    return registry.register_property(name, claim=claim,
                                       z3_expr=z3_expr, given=given,
                                       description=description)
```

### New Symbol Dataclasses

```python
@dataclass(frozen=True)
class AxiomSymbol:
    name: str
    statement: str
    z3_expr: Callable | None
    description: str

@dataclass(frozen=True)
class PropertySymbol:
    name: str
    claim: str
    z3_expr: Callable
    given: tuple[str, ...]  # axiom names
    description: str
```

## Authoring Workflow

### Step 2 (after scope declaration)

For `structural` / `decision_framework` papers:

> "Would you like to declare foundational axioms for this model? Axioms are explicit assumptions stated without proof — everything else derives from them. (Recommended for structural papers.)"

If accepted, the first authoring section is "Axioms and Assumptions" where each axiom gets:
- Prose statement
- Display math
- `python:validate` block with `Axiom(...)` registration
- Optional `z3_expr` for machine verification

### Step 4 (completion)

After the meta-compiler check, if axioms and Z3 expressions exist:

1. Run axiom consistency check
2. Run any property implication checks
3. Report results in the completion summary:

```
Axiom verification (Z3):
  ✓ Axioms A1-A4 are consistent (sat in 0.02s)
  ✓ Property P1 follows from A1, A2, A3
  ✗ Property P2 does NOT follow from A1, A2 — counterexample: H=1, M=1, beta=2
```

## Dependencies

- `z3-solver` — pip installable, no external toolchain
- Optional dependency: `pip install math-paper-creator[verification]`
- Z3 expressions are optional on Axiom symbols — papers work without Z3 installed, they just skip machine verification

## Files Changed (Estimated)

| File | Change |
|------|--------|
| `src/meta_compiler/symbols.py` | Add `AxiomSymbol`, `PropertySymbol` dataclasses |
| `src/meta_compiler/registry.py` | Add `register_axiom()`, `register_property()` |
| `src/meta_compiler/__init__.py` | Add `Axiom()`, `Property()` DSL functions |
| `src/meta_compiler/verification.py` | New — Z3 consistency/implication checker |
| `src/meta_compiler/compiler/report.py` | Add verification results to report |
| `src/meta_compiler/cli.py` | Add `verify` subcommand |
| `commands/author.md` | Add axiom authoring in Step 2, verification in Step 4 |
| `templates/_checklist.md` | Add advisory: "Axioms declared for structural papers" |
| `pyproject.toml` | Add `z3-solver` as optional dependency |

## Relationship to Other Specs

- **Epistemic hygiene (#8):** Z3 results feed into the four-tests conclusion frame and strengthen epistemic claims
- **Pyomo solver:** Axioms could become additional constraints in the Pyomo model, ensuring the solver respects foundational assumptions
- **Dependency tracing (#7):** Axioms appear in the dependency graph — expressions/constraints reference axioms they depend on

## Open Questions

- Should Z3 expressions use the same variable names as the meta-compiler symbols, or a separate Z3 variable namespace?
- How to handle Z3 types (Int vs Real vs Bool) — infer from meta-compiler domain, or require explicit declaration?
- Should counterexamples from failed implication checks be presented as new fixture scenarios?
- How to express axioms over indexed symbols (forall i in W: cap[i] > 0)?

## Out of Scope

- Full proof verification (Lean/Coq territory)
- Inductive proofs over infinite structures
- Automated axiom discovery from model structure
- Z3 optimization (use Pyomo solver spec instead)
