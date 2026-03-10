# Meta-Compiler Plugin

## What This Is

A Claude Code plugin that functions as a meta-compiler for domain-specific constrained optimization systems. Given a formal YAML problem specification, it compiles a complete optimization system: typed intermediate representation, structural validation, executable solver code (OR-Tools CP-SAT), diagnostics, stress harnesses, and human-readable reports. It operates one abstraction layer above individual optimizers — generating optimization systems from formal problem specs rather than solving specific instances.

## Core Value

Transform ambiguous constrained decision problems into executable, diagnosable, and partially verifiable optimization systems while preserving explicit epistemic separation between assumptions, heuristics, solver outputs, and formally verified claims.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] User can initialize a new optimization model project from a domain template
- [ ] User can define entities, parameters, decisions, objectives, and constraints via YAML spec
- [ ] Compiler normalizes spec into a typed, indexed intermediate representation (IR)
- [ ] Structural validator catches malformed models before solver execution
- [ ] Compiler generates executable OR-Tools CP-SAT solver code from IR
- [ ] Compiler generates Python reference model and test suite from IR
- [ ] User can run feasibility pre-checks and diagnostics harness
- [ ] User can run solver on deterministic or robust mode
- [ ] User can run sensitivity, perturbation, and scenario stress tests
- [ ] Compiler generates technical report with notation table, constraint catalog, and epistemic status labels
- [ ] Every artifact carries explicit epistemic status (assumption / solver result / conjecture / etc.)
- [ ] Finite logical verification hooks via Z3 for selected invariants
- [ ] One domain package: generic allocation (covering workforce, portfolio, territory)
- [ ] Plugin exposes full command surface: model:init, model:define, model:compile, model:check, model:solve, model:stress, model:verify, model:report

### Out of Scope

- Arbitrary theorem proving across all mathematics — not a general proof engine
- Full formal proof of solver behavior — proof scaffolding only, not machine-checked proofs by default
- Unconstrained natural-language-only spec generation with no schema — structured schema is required
- High-end nonlinear continuous mathematics beyond tractable model families — deferred to Phase 2+
- Pyomo / CVXPY backends — deferred to Phase 2
- Real-time or streaming optimization — batch compilation model only

## Context

This plugin is being added to the `reggiechan74/cc-plugins` Claude Code plugin marketplace. It follows all cc-plugins plugin conventions: two-step install via `/plugin marketplace add` + `/plugin install`, shields.io badges, CLAUDE.md standards.

**Architecture decision:** Hybrid model. Claude owns the spec → IR → structural validation pipeline using its reasoning — this is where the epistemic formalization work lives. A lightweight bundled Python runtime (`meta_compiler/`) handles IR → solver execution → diagnostics. The IR (YAML/JSON) is the canonical seam: Claude writes it, the runtime runs it. All outputs are derived from the IR as single source of truth.

**Solver strategy:** OR-Tools CP-SAT as primary backend for MVP — best fit for combinatorial/assignment problems, clean symbolic constraint interface, single `pip install ortools` dependency. scipy included for LP relaxations and sensitivity analysis. Pyomo and CVXPY are Phase 2 backends for continuous/convex families.

**Problem class for MVP:** Allocation under capacity, assignment, policy, and bounded uncertainty constraints — covering workforce allocation, portfolio bucket allocation, territory assignment, project-resource matching, and budget allocation.

**Epistemic model:** Every artifact must carry a status label — Definition, Assumption, Axiom, Input estimate, Policy constraint, Derived expression, Soft preference, Hard requirement, Heuristic, Solver result, Numerical check, Finite-case verification, Conjecture, or Machine-checked theorem. This is non-negotiable and enforced at the IR level.

## Constraints

- **Plugin conventions**: Must follow cc-plugins install/README/badge standards
- **Solver runtime**: OR-Tools CP-SAT + scipy must be installable via pip with no system solver binaries required
- **Schema-first**: Spec layer must be structured (YAML/JSON), not prose-first — prevents natural-language soup failure mode
- **IR as source of truth**: All generated artifacts (code, docs, proof scaffolds) must be derived from IR — no implementation drift
- **Epistemic hygiene**: Must not imply solver success equals proof, or runtime execution equals correctness

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Hybrid Claude + Python runtime | Claude owns formalization/IR; runtime owns execution/diagnostics. Preserves inspectability while enabling live feedback loop. | — Pending |
| OR-Tools CP-SAT as primary MVP backend | Clean symbolic interface maps well from IR; single pip dep; strong on combinatorial/assignment families | — Pending |
| scipy as secondary backend | Handles LP relaxations and sensitivity; already common in Python environments | — Pending |
| YAML-backed DSL for spec | Structured enough to compile reliably; human-readable enough for domain experts | — Pending |
| Single domain module for MVP: generic allocation | Broad enough to prove generality (covers workforce/portfolio/territory); narrow enough to build rigorously | — Pending |
| IR as canonical seam | Single source of truth; all outputs derived from IR prevents implementation drift (Risk 5 in design brief) | — Pending |

---
*Last updated: 2026-03-09 after initialization*
