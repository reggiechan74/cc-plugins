# Requirements: Meta-Compiler Plugin

**Defined:** 2026-03-09
**Core Value:** Transform ambiguous constrained decision problems into executable, diagnosable, and partially verifiable optimization systems while preserving explicit epistemic separation between assumptions, heuristics, solver outputs, and formally verified claims.

## v1 Requirements

### Plugin Infrastructure

- [ ] **INFRA-01**: User can run `model:setup` to install Python runtime dependencies (ortools, z3-solver, scipy, pydantic, jinja2) via uv or pip
- [ ] **INFRA-02**: User can run `model:doctor` to diagnose runtime environment, verify dependency versions, and surface any missing or incompatible packages
- [ ] **INFRA-03**: Plugin follows cc-plugins two-step install conventions (`/plugin marketplace add` + `/plugin install meta-compiler@cc-plugins`)
- [ ] **INFRA-04**: Plugin README includes shields.io badges inside `<!-- badges-start -->` / `<!-- badges-end -->` markers

### Core Compiler Pipeline

- [ ] **COMP-01**: User can define a new optimization model project from a domain template via `model:init`
- [ ] **COMP-02**: User can define or update entities, parameters, decisions, objectives, constraints, and uncertainty via YAML spec using `model:define`
- [ ] **COMP-03**: YAML spec is validated against a Pydantic v2 JSON Schema on load — malformed specs are rejected with actionable error messages before any compilation
- [ ] **COMP-04**: Compiler normalizes a valid YAML spec into a typed, indexed intermediate representation (IR) with epistemic status required on every node
- [ ] **COMP-05**: IR is serialized to a stable JSON artifact that is the canonical source of truth — all downstream artifacts (code, docs, reports) are derived from the IR, never regenerated from the spec
- [ ] **COMP-06**: Structural validator detects undefined symbols, duplicate definitions, and unused symbols before solver execution
- [ ] **COMP-07**: Structural validator detects incompatible index dimensions and impossible variable bounds
- [ ] **COMP-08**: Structural validator detects circular derived dependencies and contradictory hard constraints
- [ ] **COMP-09**: Structural validator detects unbounded objective formulations and variable type misuse
- [ ] **COMP-10**: Structural validator detects inconsistent uncertainty declarations and mixed deterministic/stochastic references without explicit mode
- [ ] **COMP-11**: Structural validator flags potentially redundant constraints, soft constraints that systematically conflict with hard constraints, and likely big-M pathologies
- [ ] **COMP-12**: Compiler generates executable OR-Tools CP-SAT solver code from IR — generated code is human-readable and traceable to IR nodes
- [ ] **COMP-13**: Compiler generates a Python reference model from IR — canonical human-readable implementation of the model structure
- [ ] **COMP-14**: Compiler generates a test suite from IR — unit tests, invariant checks, and edge-case tests
- [ ] **COMP-15**: IR type system enforces CP-SAT integer-only constraint — continuous parameters are flagged and a scaling/discretization strategy is documented at the IR level
- [ ] **COMP-16**: User can run `model:check` to execute structural validation independently before compilation
- [ ] **COMP-17**: All compilation artifacts include provenance metadata linking each artifact node back to its IR source

### Solver Execution

- [ ] **SOLVER-01**: User can run `model:solve` to execute the compiled OR-Tools CP-SAT model in deterministic mode
- [ ] **SOLVER-02**: Solver performs feasibility pre-checks before full solve — infeasibility is reported with structural diagnostics, not raw solver error
- [ ] **SOLVER-03**: Solve results are returned as structured JSON and human-readable summary — feasible / infeasible / unbounded / optimal / approximate status clearly labeled
- [ ] **SOLVER-04**: Solver results carry explicit epistemic status (Solver Result) — system must not imply solver optima equal truth

### Domain Module

- [ ] **DOMAIN-01**: Plugin ships one domain module: generic allocation — covering workforce allocation, portfolio bucket allocation, territory assignment, project-resource matching, and budget allocation
- [ ] **DOMAIN-02**: Domain module provides YAML ontology extensions, named constraint templates, named objective templates, and common variable patterns
- [ ] **DOMAIN-03**: Domain module provides typical uncertainty models for allocation problems (interval-bounded, scenario-based)
- [ ] **DOMAIN-04**: Domain module provides data adapter stubs for loading instance data into the spec
- [ ] **DOMAIN-05**: User can create a new domain module skeleton via `domain:create`

### Reporting

- [ ] **REPORT-01**: User can run `model:report` to generate a technical brief from the compiled IR and solve results
- [ ] **REPORT-02**: Report includes notation/symbol table — all sets, parameters, variables, and derived quantities with types, units, and epistemic status
- [ ] **REPORT-03**: Report includes objective decomposition — every objective term, its semantics, units, and status
- [ ] **REPORT-04**: Report includes constraint catalog — hard and soft constraints grouped by family with epistemic status labels
- [ ] **REPORT-05**: Report includes validation results — undefined symbols, inferred issues, warnings, and contradictions
- [ ] **REPORT-06**: Report includes solve summary — feasibility status, objective value, solution quality
- [ ] **REPORT-07**: Report includes assumptions register — all assumptions explicitly listed and separated from derived results and solver outputs
- [ ] **REPORT-08**: Report explicitly separates what is executable-coherent, numerically verified, SMT-checked, scaffolded for proof, and formally proved

### Epistemic Status Model

- [ ] **EPIST-01**: IR enforces a 14-category epistemic taxonomy on every artifact node: Definition, Assumption, Axiom, Input estimate, Policy constraint, Derived expression, Soft preference, Hard requirement, Empirical calibration, Heuristic, Solver result, Numerical check, Finite-case verification, Conjecture, Machine-checked theorem
- [ ] **EPIST-02**: User-facing interfaces expose a simplified ~5-category taxonomy (Assumption, Derived, Solver Result, Verified, Conjecture) with automatic inference from full IR taxonomy
- [ ] **EPIST-03**: Epistemic status is enforced at spec authoring time — specs without required status declarations on parameters are rejected
- [ ] **EPIST-04**: System never implies solver success equals proof, runtime execution equals correctness, or simulated robustness equals formal theorem

### Verification

- [ ] **VERIFY-01**: User can run `model:verify` to execute finite-domain invariant checking via Z3
- [ ] **VERIFY-02**: Z3 verification checks feasibility pre-conditions, acyclicity of dependency structures, and uniqueness of assignments where declared
- [ ] **VERIFY-03**: Z3 verification is hard-scoped to finite-domain checks with wall-clock timeouts — unbounded or undecidable queries are rejected at the IR level
- [ ] **VERIFY-04**: Verification results are labeled by epistemic strength: unchecked / numerically checked / SMT-checked / scaffolded for proof / formally proved
- [ ] **VERIFY-05**: User can run `model:prove` to export selected IR theorem candidates as Z3 obligations or proof scaffolds

### Stress and Sensitivity

- [ ] **STRESS-01**: User can run `model:stress` to execute scenario sweep across declared uncertainty ranges
- [ ] **STRESS-02**: Interval uncertainty model is supported — parameters declared as interval-bounded are expanded into robust counterpart formulations
- [ ] **STRESS-03**: Sensitivity analysis via scipy reports how objective value changes under parameter perturbation
- [ ] **STRESS-04**: Stress results include counterexample candidates — parameter combinations that cause feasibility failure or objective degradation beyond thresholds

## v2 Requirements

### Additional Solver Backends

- **BACKEND-01**: Pyomo backend for MILP problems requiring continuous variable support
- **BACKEND-02**: CVXPY backend for convex/portfolio-class problems
- **BACKEND-03**: Network flow backend for routing and transport problems

### Formal Proof Scaffolding

- **PROOF-01**: Lean 4 proof obligation export for selected theorem candidates
- **PROOF-02**: Coq stub generation for structural invariants
- **PROOF-03**: Symbolic simplification support for proof targets

### Domain Expansion

- **DOMAIN-06**: Dedicated workforce domain module with reporting tree, span-of-control, regional cohesion, skill fit
- **DOMAIN-07**: Dedicated portfolio domain module with position weights, turnover limits, risk budget, sector caps
- **DOMAIN-08**: Dedicated routing domain module with edge traversal, route continuity, time windows

### MCP Integration

- **MCP-01**: MCP server wrapper for Python runtime — enables streaming solver progress and incremental validation
- **MCP-02**: `domain:package` command to emit reusable domain-specific optimizer creator plugins

## Out of Scope

| Feature | Reason |
|---------|--------|
| Arbitrary theorem proving | Not a general proof engine — proof scaffolding only, scoped to finite/logical claims |
| Full machine-checked proofs by default | Requires stable IR + mature Lean 4 tooling — deferred to Phase 5 |
| Unconstrained natural-language spec generation | Schema-first is non-negotiable — prevents natural-language soup failure mode |
| High-end nonlinear continuous mathematics | Beyond tractable model families for MVP |
| Real-time / streaming optimization | Batch compilation model only |
| General AI mathematics claims | Explicitly anti-positioned against magic optimizer framing |

## Traceability

*Populated during roadmap creation.*

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 through INFRA-04 | Phase TBD | Pending |
| COMP-01 through COMP-17 | Phase TBD | Pending |
| SOLVER-01 through SOLVER-04 | Phase TBD | Pending |
| DOMAIN-01 through DOMAIN-05 | Phase TBD | Pending |
| REPORT-01 through REPORT-08 | Phase TBD | Pending |
| EPIST-01 through EPIST-04 | Phase TBD | Pending |
| VERIFY-01 through VERIFY-05 | Phase TBD | Pending |
| STRESS-01 through STRESS-04 | Phase TBD | Pending |

**Coverage:**
- v1 requirements: 46 total
- Mapped to phases: 0
- Unmapped: 46 ⚠️

---
*Requirements defined: 2026-03-09*
*Last updated: 2026-03-09 after initial definition*
