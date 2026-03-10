# Feature Landscape

**Domain:** Meta-compiler for constrained optimization systems (Claude Code plugin)
**Researched:** 2026-03-09

## Table Stakes

Features users expect from an optimization meta-compiler. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| YAML spec input | Structured input is the entire premise | Med | Pydantic-validated schema with clear error messages |
| Typed IR compilation | Core product promise | High | Symbol table, index sets, type checking, epistemic labels |
| Structural validation | Catches bad models before solver runs | Med | Undefined symbols, circular deps, impossible bounds, index mismatches |
| OR-Tools CP-SAT code generation | Must produce runnable code | High | Jinja2 templates mapping IR constraints to CP-SAT API calls |
| Feasibility pre-checks | Users expect to know if model is solvable before waiting | Low | Quick constraint satisfiability check via CP-SAT or Z3 |
| Deterministic solve | Basic solver execution | Low | Wrapper around generated CP-SAT code with solution extraction |
| Solution summary report | Users need to interpret results | Med | Markdown report with objective breakdown, assignment table, constraint status |
| Epistemic status labels | Core differentiator, but also expected given the product positioning | Med | Every IR node carries status enum; reports show status per claim |
| One domain package (generic allocation) | Need at least one working domain to demonstrate the system | Med | Covers workforce/portfolio/territory assignment families |
| Slash command surface | Plugin must be usable | Low | `/model:init`, `/model:compile`, `/model:check`, `/model:solve`, `/model:report` |

## Differentiators

Features that set the product apart. Not expected, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Z3 finite logical verification | Separates this from "just another solver wrapper" | High | SMT-based bounded model checking for selected invariants |
| Constraint contradiction detection | Catches impossible specs that solvers would just return INFEASIBLE for | Med | Z3 checks for unsatisfiable hard constraint combinations |
| Sensitivity/perturbation harness | Shows how robust solutions are | Med | Parameter sweeps via scipy, scenario generation |
| Stress testing | Counterexample search beyond simple solve | Med | Boundary cases, adversarial parameter combinations |
| Proof scaffold generation | Bridge to formal verification | High | Phase 4-5. Lean 4 `.lean` files with type signatures and proof obligations |
| Notation table and constraint catalog | Professional documentation output | Low | Auto-generated from IR symbol table |
| Assumptions register | Epistemic transparency | Low | Lists all assumptions with their sources and status |
| Domain template system | Enables new domain creation without modifying core | Med | YAML-based domain ontology, constraint templates, objective templates |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Natural language spec input | Risk 1 from design brief: "natural-language soup." Unstructured input defeats the whole compiler premise. | Require YAML schema. Claude helps users write the YAML, but the schema is the contract. |
| General theorem proving | Out of scope. Would require unbounded effort with no reliable output. | Scope to finite-case verification and proof scaffolding for selected claims. |
| Automatic proof completion | Users will expect "prove my model correct" -- this is not achievable automatically. | Generate proof obligations. Users complete proofs in Lean. Label everything honestly. |
| GUI/web dashboard | Plugin is Claude Code native. Building a web UI is a different product. | Markdown reports, terminal output, file artifacts. |
| Real-time/streaming optimization | Batch compilation model only per design brief. | Clear documentation that this is a batch compiler, not a live optimizer. |
| Solver backend selection by AI | Claude should not guess which solver to use. | Model family classification in IR; explicit mapping to solver backend. |
| Multi-language code generation | Python only for MVP. Generating Julia/C++ adds massive complexity. | Python + OR-Tools. Other languages are Phase 3+. |

## Feature Dependencies

```
YAML spec parsing --> IR compilation --> structural validation --> code generation --> solve
                                    \-> Z3 verification (parallel path after IR)
                                    \-> report generation (after solve or validation)
                                    \-> proof scaffolding (after Z3 verification, Phase 4-5)

Domain templates --> spec parsing (templates provide schema extensions)
Sensitivity harness --> solve (needs baseline solution first)
Stress testing --> solve + Z3 (needs both solver and verifier)
```

## MVP Recommendation

**Prioritize (Phase 1):**
1. YAML spec parsing with Pydantic validation
2. Typed IR compilation with symbol table
3. Structural validation (undefined symbols, circular deps, index mismatches)
4. OR-Tools CP-SAT code generation via Jinja2 templates
5. Deterministic solve with solution extraction
6. Basic report generation (notation table, constraint catalog, solution summary)
7. Epistemic status labels on all IR nodes
8. One domain: generic allocation

**Phase 2:**
- Z3 finite verification hooks
- Feasibility pre-checks
- Constraint contradiction detection
- Sensitivity harness via scipy

**Defer:**
- Proof scaffolding (Lean 4): Phase 4-5. Requires Z3 verification to be stable first.
- Stress testing: Phase 3. Needs sensitivity harness.
- Additional solver backends (Pyomo, CVXPY): Phase 2+.
- Additional domains: Phase 2+.

## Sources

- Design brief sections 5, 15, 16, 17, 18, 27 (core feature requirements and risk mitigations)
- PROJECT.md active requirements list
- [OR-Tools CP-SAT docs](https://developers.google.com/optimization/cp/cp_solver) for solver capabilities
- [Z3 Python tutorial](https://ericpony.github.io/z3py-tutorial/guide-examples.htm) for verification scope
