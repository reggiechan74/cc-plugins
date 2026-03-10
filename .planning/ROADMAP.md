# Roadmap: Meta-Compiler Plugin

## Overview

This roadmap delivers a meta-compiler Claude Code plugin that transforms YAML problem specs into executable, diagnosable optimization systems. The journey proceeds from plugin infrastructure through the core compiler pipeline (spec, IR, validation, codegen, solver), then domain content, reporting, and finally verification and stress testing. The IR design in Phase 2 is the highest-risk decision -- every subsequent phase depends on it. Epistemic status enforcement and CP-SAT integer-only constraints are baked in from Phase 2 to prevent structural debt.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Plugin Infrastructure** - Feature branch, plugin scaffolding, setup/doctor commands, cc-plugins conventions
- [ ] **Phase 2: Spec Layer and IR Core** - YAML spec schema, Pydantic validation, typed IR with epistemic status, integer-only type enforcement
- [ ] **Phase 3: Structural Validation** - All six validator passes plus model:check command
- [ ] **Phase 4: Code Generation** - Jinja2 CP-SAT codegen, reference model, test suite, provenance metadata
- [ ] **Phase 5: Solver Execution** - model:solve command, feasibility pre-checks, structured results, epistemic labeling
- [ ] **Phase 6: Domain Module** - Generic allocation domain, constraint/objective templates, uncertainty models, domain:create
- [ ] **Phase 7: Reporting and Epistemic Surface** - model:report command, all report sections, simplified epistemic taxonomy
- [ ] **Phase 8: Z3 Verification** - model:verify and model:prove commands, finite-domain checking, verification result labeling
- [ ] **Phase 9: Stress and Sensitivity** - model:stress command, scenario sweeps, scipy sensitivity, counterexample candidates

## Phase Details

### Phase 1: Plugin Infrastructure
**Goal**: User can install the plugin, set up the Python runtime, and confirm a healthy environment -- all cc-plugins conventions satisfied
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, INFRA-04
**Success Criteria** (what must be TRUE):
  1. User can install the plugin via two-step marketplace install and see it listed in their plugins
  2. User can run `model:setup` and have all Python dependencies installed and importable
  3. User can run `model:doctor` and see a pass/fail health check for every required dependency
  4. Plugin README has correct shields.io badges inside badge markers
**Plans**: 2 plans

Plans:
- [ ] 01-01-PLAN.md — Plugin scaffold, Wave 0 test stubs, README with badges (INFRA-03, INFRA-04)
- [ ] 01-02-PLAN.md — setup_runtime.py and doctor_runtime.py (INFRA-01, INFRA-02)

### Phase 2: Spec Layer and IR Core
**Goal**: User can author a YAML optimization spec and compile it into a typed, epistemic-status-enforced IR that handles CP-SAT integer-only constraints
**Depends on**: Phase 1
**Requirements**: COMP-01, COMP-02, COMP-03, COMP-04, COMP-05, COMP-15, EPIST-01, EPIST-03
**Success Criteria** (what must be TRUE):
  1. User can run `model:init` to create a new model project from a domain template with a valid YAML spec skeleton
  2. User can author entities, parameters, decisions, objectives, and constraints in YAML and have malformed specs rejected with actionable errors
  3. Compiling a valid spec produces a JSON IR artifact where every node carries a required epistemic status from the 14-category taxonomy
  4. Specs with continuous parameters that would violate CP-SAT integer-only semantics are flagged with a documented scaling/discretization strategy at the IR level
  5. The IR JSON artifact is the canonical source of truth -- serialized to a stable format that downstream phases will read
**Plans**: TBD

Plans:
- [ ] 02-01: TBD
- [ ] 02-02: TBD
- [ ] 02-03: TBD

### Phase 3: Structural Validation
**Goal**: Structural validator catches all categories of malformed models before any solver execution
**Depends on**: Phase 2
**Requirements**: COMP-06, COMP-07, COMP-08, COMP-09, COMP-10, COMP-11, COMP-16
**Success Criteria** (what must be TRUE):
  1. User can run `model:check` and see clear pass/fail results for each validation category
  2. Undefined symbols, duplicate definitions, and unused symbols are detected and reported with source locations
  3. Incompatible index dimensions, impossible variable bounds, circular dependencies, and contradictory constraints are caught before compilation proceeds
  4. Potentially redundant constraints, soft/hard conflicts, and big-M pathologies are flagged as warnings
  5. Unbounded objectives, variable type misuse, and inconsistent uncertainty declarations are detected
**Plans**: TBD

Plans:
- [ ] 03-01: TBD
- [ ] 03-02: TBD

### Phase 4: Code Generation
**Goal**: Compiler generates human-readable, traceable OR-Tools CP-SAT code and supporting artifacts from the IR
**Depends on**: Phase 3
**Requirements**: COMP-12, COMP-13, COMP-14, COMP-17
**Success Criteria** (what must be TRUE):
  1. Running `model:compile` produces executable OR-Tools CP-SAT Python code that a user can read and trace back to IR nodes
  2. A Python reference model is generated that provides a canonical human-readable implementation of the model structure
  3. A test suite is generated with unit tests, invariant checks, and edge-case tests derived from the IR
  4. Every generated artifact includes provenance metadata linking each node to its IR source
**Plans**: TBD

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD

### Phase 5: Solver Execution
**Goal**: User can solve compiled models and receive structured, epistemically honest results
**Depends on**: Phase 4
**Requirements**: SOLVER-01, SOLVER-02, SOLVER-03, SOLVER-04
**Success Criteria** (what must be TRUE):
  1. User can run `model:solve` and get a deterministic solve of the compiled CP-SAT model
  2. Infeasible models are caught by pre-checks and reported with structural diagnostics, not raw solver errors
  3. Solve results are returned as both structured JSON and human-readable summary with clear status labels (feasible/infeasible/unbounded/optimal/approximate)
  4. All solver results carry explicit "Solver Result" epistemic status -- the system never implies solver optima equal truth
**Plans**: TBD

Plans:
- [ ] 05-01: TBD
- [ ] 05-02: TBD

### Phase 6: Domain Module
**Goal**: Plugin ships one complete domain module (generic allocation) that demonstrates the full spec-to-solve workflow across multiple problem families
**Depends on**: Phase 5
**Requirements**: DOMAIN-01, DOMAIN-02, DOMAIN-03, DOMAIN-04, DOMAIN-05
**Success Criteria** (what must be TRUE):
  1. User can create a new model using the generic allocation domain and solve a workforce allocation, portfolio bucket, or territory assignment problem end-to-end
  2. Domain module provides named constraint templates, objective templates, and common variable patterns that the user can reference in their spec
  3. Domain module includes uncertainty models (interval-bounded, scenario-based) usable in specs
  4. User can run `domain:create` to scaffold a new domain module skeleton
**Plans**: TBD

Plans:
- [ ] 06-01: TBD
- [ ] 06-02: TBD

### Phase 7: Reporting and Epistemic Surface
**Goal**: User can generate comprehensive technical reports that maintain strict epistemic separation between assumptions, results, and verified claims
**Depends on**: Phase 5
**Requirements**: REPORT-01, REPORT-02, REPORT-03, REPORT-04, REPORT-05, REPORT-06, REPORT-07, REPORT-08, EPIST-02, EPIST-04
**Success Criteria** (what must be TRUE):
  1. User can run `model:report` and receive a technical brief covering notation, objectives, constraints, validation, solve results, and assumptions
  2. Report explicitly separates what is executable-coherent, numerically verified, SMT-checked, scaffolded for proof, and formally proved
  3. User-facing report uses a simplified ~5-category epistemic taxonomy (Assumption, Derived, Solver Result, Verified, Conjecture) automatically inferred from the full IR taxonomy
  4. The system never implies solver success equals proof, runtime execution equals correctness, or simulated robustness equals formal theorem -- enforced in report language
**Plans**: TBD

Plans:
- [ ] 07-01: TBD
- [ ] 07-02: TBD

### Phase 8: Z3 Verification
**Goal**: User can run finite-domain logical verification on their models and export proof scaffolds
**Depends on**: Phase 5
**Requirements**: VERIFY-01, VERIFY-02, VERIFY-03, VERIFY-04, VERIFY-05
**Success Criteria** (what must be TRUE):
  1. User can run `model:verify` and see Z3 check results for feasibility pre-conditions, acyclicity, and assignment uniqueness
  2. Verification is hard-scoped to finite-domain checks with wall-clock timeouts -- unbounded queries are rejected at the IR level
  3. Verification results carry epistemic strength labels (unchecked / numerically checked / SMT-checked / scaffolded for proof / formally proved)
  4. User can run `model:prove` to export selected IR theorem candidates as Z3 obligations or proof scaffolds
**Plans**: TBD

Plans:
- [ ] 08-01: TBD
- [ ] 08-02: TBD

### Phase 9: Stress and Sensitivity
**Goal**: User can stress-test models against uncertainty and understand how parameter changes affect outcomes
**Depends on**: Phase 5
**Requirements**: STRESS-01, STRESS-02, STRESS-03, STRESS-04
**Success Criteria** (what must be TRUE):
  1. User can run `model:stress` to execute a scenario sweep across declared uncertainty ranges
  2. Interval-bounded parameters are expanded into robust counterpart formulations
  3. Sensitivity analysis via scipy reports how objective value changes under parameter perturbation
  4. Stress results include counterexample candidates -- parameter combinations that cause feasibility failure or objective degradation beyond thresholds
**Plans**: TBD

Plans:
- [ ] 09-01: TBD
- [ ] 09-02: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6, 7, 8, 9 (Phases 6-9 depend on Phase 5; 7, 8, 9 are parallelizable in principle)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Plugin Infrastructure | 0/2 | Not started | - |
| 2. Spec Layer and IR Core | 0/3 | Not started | - |
| 3. Structural Validation | 0/2 | Not started | - |
| 4. Code Generation | 0/2 | Not started | - |
| 5. Solver Execution | 0/2 | Not started | - |
| 6. Domain Module | 0/2 | Not started | - |
| 7. Reporting and Epistemic Surface | 0/2 | Not started | - |
| 8. Z3 Verification | 0/2 | Not started | - |
| 9. Stress and Sensitivity | 0/2 | Not started | - |
