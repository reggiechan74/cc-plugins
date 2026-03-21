# Pyomo Solver Integration

**Date:** 2026-03-20
**Plugin:** math-paper-creator
**Status:** Draft (future milestone)

## Problem

The meta-compiler validates that a mathematical model is internally consistent — formulas compute, constraints hold against fixture data. But it never answers "what's the optimal solution?" For papers with an Objective, the natural next question after validation is: given these parameters and constraints, what are the optimal decision variable values?

## Proposed Solution

Add a solver step that translates the meta-compiler's registry into a Pyomo `ConcreteModel`, invokes a solver, and reports optimal values.

**Dependencies:** `pyomo` (pip installable), plus a free solver: GLPK or CBC (system install, or via `pyomo`'s conda-forge packages).

## Symbol Mapping

The meta-compiler's symbol types map nearly 1:1 to Pyomo:

| meta-compiler | Pyomo |
|---|---|
| `Set("W", ...)` | `model.W = Set(initialize=data)` |
| `Parameter("cap", index="W", ...)` | `model.cap = Param(model.W, initialize=data)` |
| `Variable("x", domain="continuous", bounds=(0,1), ...)` | `model.x = Var(model.W, bounds=(0,1), within=Reals)` |
| `Constraint("limit", expr=..., over="W", ...)` | `model.limit = Constraint(model.W, rule=...)` |
| `Objective("cost", expr=..., sense="minimize", ...)` | `model.cost = Objective(rule=..., sense=minimize)` |

## Key Challenges

### Lambda Translation

The meta-compiler stores constraints/objectives as Python lambdas that operate on fixture data (raw values). Pyomo needs constraint rules that operate on Pyomo symbolic variables to build an expression tree the solver can process. The same lambdas cannot be reused.

**Options:**
- **A) Dual-lambda approach:** The author skill generates both a validation lambda (current) and a Pyomo-compatible rule during authoring. More verbose but explicit.
- **B) Registry-to-Pyomo translator:** A translation layer that re-interprets the registry's symbols and source code to build Pyomo expressions. More automated but complex.
- **C) Source text rewriting:** Use the existing `_source_text` on expr callables, tokenize and rewrite symbol references to Pyomo model attributes. Fragile but requires no author changes.

Recommendation: Option A for v1 — explicit is better than clever. The author skill can generate the Pyomo rule alongside the validation lambda, stored as a second field on the symbol.

### Scalar Models

The v0.3.0 scalar auto-unwrap means scalar symbols are plain Python values in the exec namespace. The solver step would need to re-wrap them as `Param` objects for Pyomo. This is straightforward — iterate `registry.symbols`, check for scalar fixture data, create `Param(initialize=value)`.

### Not All Papers Are Solvable

The solver step should only be offered when:
- At least one `Objective` symbol exists
- At least one `Variable` symbol exists
- A solver is installed (`pyomo` importable, solver binary available)

Papers with only Parameters, Expressions, and Constraints (no optimization) skip this entirely.

## User Interface

### CLI

```bash
meta_compiler.cli solve model.md --solver glpk --output solution.json
```

### Author Skill (Step 4)

After validation passes and an Objective exists:

> "This model has an objective function. Would you like me to solve for optimal values? (Requires pyomo and a solver like GLPK.)"

If accepted, run solver and append a "Solution" section to the paper with optimal variable values, objective value, and constraint slack.

### Compile Integration

`compile_document()` gains an optional `solve: bool = False` parameter. When True, the output dict includes a `"solution"` key with optimal values.

## Output

```json
{
  "status": "optimal",
  "objective_value": 42.5,
  "variables": {
    "x": {"alice": 0.8, "bob": 0.6, "carol": 1.0}
  },
  "constraint_slack": {
    "cap_limit": {"alice": 2.0, "bob": 0.0, "carol": 5.0}
  }
}
```

## Files Changed (Estimated)

| File | Change |
|------|--------|
| `src/meta_compiler/solver.py` | New — registry-to-Pyomo translator, solve runner |
| `src/meta_compiler/compiler/__init__.py` | Add `solve` parameter to `compile_document()` |
| `src/meta_compiler/cli.py` | Add `solve` subcommand |
| `commands/author.md` | Add solver prompt at Step 4 |
| `pyproject.toml` | Add `pyomo` as optional dependency |

## Open Questions

- Should Pyomo be a hard dependency or optional (`pip install math-paper-creator[solver]`)?
- Which free solver to recommend as default (GLPK vs CBC)?
- Should the solution be appended to the `.model.md` or written as a separate artifact?
- How to handle infeasible models gracefully in the author workflow?

## Out of Scope

- Custom solver configuration (tolerances, time limits)
- Multi-objective optimization
- Integer programming solver selection
- Stochastic programming extensions
