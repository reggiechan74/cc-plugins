# Project Research Summary

**Project:** Meta-Compiler for Domain-Specific Constrained Optimization Systems
**Domain:** Developer tooling -- optimization meta-compiler as Claude Code plugin
**Researched:** 2026-03-09
**Confidence:** HIGH

## Executive Summary

This project is a hybrid Claude Code plugin that pairs LLM reasoning (spec formalization, IR authoring) with a deterministic Python runtime (compilation, solving, verification). The optimization meta-compiler ecosystem in Python is mature and well-documented: OR-Tools CP-SAT for combinatorial/integer optimization, Z3 for SMT-based verification, Pydantic for schema validation, and Jinja2 for code generation. All core dependencies are pip-installable with no system-level binary requirements, which is critical for a distributable plugin. The recommended approach is a strict compiler pipeline -- YAML spec to typed IR to generated code -- where the IR (not Claude, not the spec) is the single source of truth for all downstream artifacts.

The architecture must enforce a hard boundary between Claude (reasoning) and Python (execution). Claude helps users write structured YAML specs and interprets results; the Python runtime compiles, validates, solves, and verifies. The IR serialized as YAML/JSON is the interface contract. This separation is not optional -- without it, the product collapses into an unreliable prompt wrapper. Epistemic status labels on every IR node are the core differentiator that separates this from commodity solver wrappers, and they must be enforced at the type level from Phase 1.

The top risks are natural language creep in the spec layer (destroying deterministic compilation), implementation drift between IR and generated code (destroying trust), and CP-SAT API misuse around integer-only semantics. All three are preventable with upfront design decisions: a closed constraint grammar, IR-hash-based drift detection, and a type system that routes continuous problems away from CP-SAT. Z3 verification scope must be bounded explicitly to avoid timeout-induced trust erosion.

## Key Findings

### Recommended Stack

The stack is Python 3.12+ with seven runtime dependencies, all available via pip. The solver layer uses OR-Tools CP-SAT (integer/combinatorial) and scipy (LP relaxations, sensitivity analysis). Verification uses Z3. The DSL layer uses Pydantic v2 for schema validation and ruamel.yaml for YAML 1.2 parsing with comment preservation. Code generation uses Jinja2 with composable templates. NetworkX handles graph-based structural validation.

**Core technologies:**
- **Python 3.12+**: Runtime -- entire optimization/verification ecosystem is Python-native
- **OR-Tools CP-SAT 9.15**: Primary solver -- self-contained, no external binaries, best-in-class for combinatorial problems
- **Z3 4.16**: SMT verification -- finite-case checking, counterexample generation, satisfiability
- **Pydantic 2.12**: IR type system and validation -- discriminated unions, required field enforcement, JSON Schema export
- **ruamel.yaml 0.18**: YAML 1.2 parsing -- avoids PyYAML boolean coercion bugs, preserves comments
- **Jinja2 3.1**: Code generation -- template inheritance for domain-specific extensions
- **NetworkX 3.6**: Structural validation -- cycle detection, dependency analysis

**Critical version note:** Avoid Python 3.13+ until OR-Tools confirms support. Pin OR-Tools to `>=9.15,<10`.

### Expected Features

**Must have (table stakes):**
- YAML spec input with Pydantic validation
- Typed IR compilation with symbol table and epistemic status labels
- Structural validation (undefined symbols, circular deps, index mismatches, impossible bounds)
- OR-Tools CP-SAT code generation via Jinja2
- Deterministic solve with solution extraction
- Solution summary report (notation table, constraint catalog, assignment table)
- One working domain (generic allocation)
- Slash command surface (`/model:init`, `/model:compile`, `/model:check`, `/model:solve`, `/model:report`)

**Should have (differentiators):**
- Z3 finite logical verification and constraint contradiction detection
- Feasibility pre-checks before full solve
- Sensitivity/perturbation harness via scipy
- Assumptions register with provenance tracking
- Domain template system for extensibility

**Defer (v2+):**
- Lean 4 proof scaffolding (Phase 4-5, requires stable Z3 verification first)
- Stress testing / adversarial parameter search (Phase 3, needs sensitivity harness)
- Additional solver backends: Pyomo, CVXPY (Phase 2+)
- Additional domains beyond generic allocation (Phase 2+)
- Multi-language code generation (Phase 3+)

### Architecture Approach

The architecture is a hybrid Claude + Python runtime connected by serialized IR files. Claude owns reasoning and formalization; Python owns compilation, validation, solving, and verification. The IR is a tree of Pydantic models with a flat symbol table, serialized to YAML/JSON as the canonical artifact. All code generation reads from the serialized IR, never from in-memory state or the original spec. The plugin uses slash commands (markdown files) that invoke Claude, which then calls the Python runtime via subprocess.

**Major components:**
1. **Spec parser** -- loads YAML, validates against Pydantic schema (ruamel.yaml + Pydantic)
2. **IR compiler** -- normalizes spec into typed IR with symbol table, index sets, epistemic labels
3. **Structural validator** -- checks IR well-formedness using NetworkX graph analysis
4. **Code generator** -- emits executable OR-Tools CP-SAT code from IR via composable Jinja2 templates
5. **Solver runner** -- executes generated code, extracts solutions
6. **Z3 verifier** -- finite logical verification, counterexample search from IR
7. **Report builder** -- generates markdown reports from IR + solve results
8. **Domain registry** -- loads and validates domain templates, extends spec schema

**Key patterns:** IR as single source of truth, discriminated unions for polymorphic IR nodes, registry pattern for extensibility, validation as a distinct compiler pass, epistemic status as a required type-level field.

### Critical Pitfalls

1. **Natural language soup in spec layer** -- Constraint expressions must use a closed grammar (named templates with typed parameters), not freeform strings. If the spec cannot compile without Claude, it is too loose.
2. **Implementation drift from IR** -- All generated code must derive from serialized IR only. Generated files carry "DO NOT EDIT" headers. A drift detection command compares IR hash with code generation hash.
3. **Epistemic status collapse** -- `EpistemicStatus` is a required Pydantic field on all IR nodes. Report templates must format claims differently by status level. Skipping this destroys the core differentiator.
4. **CP-SAT integer-only misuse** -- CP-SAT works exclusively with integers internally. The type system must prevent continuous variables from reaching the CP-SAT backend. Scaling factors must be tracked in IR metadata.
5. **Z3 verification scope creep** -- Verification targets must declare explicit bounds. Z3 calls need hard timeouts (30s default). UNKNOWN results are reported honestly as "conjecture" status, never suppressed.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Core Compiler Pipeline

**Rationale:** Everything downstream depends on the IR. The spec-to-IR-to-code pipeline is the foundation. Getting this right -- especially the closed constraint grammar and epistemic status enforcement -- prevents the two highest-risk pitfalls from becoming structural debt.
**Delivers:** Working end-to-end pipeline: YAML spec in, solver code + solution + report out. One domain (generic allocation).
**Addresses:** All table-stakes features: spec parsing, IR compilation, structural validation, CP-SAT code generation, deterministic solve, basic reports, epistemic labels, slash command surface, plugin setup.
**Avoids:** Natural language soup (closed grammar from day one), epistemic status collapse (required Pydantic field), CP-SAT misuse (type system enforces integer-only).

### Phase 2: Verification and Analysis

**Rationale:** Z3 verification and sensitivity analysis are the primary differentiators. They depend on a stable IR and working solver from Phase 1. Grouping them together is natural because both extend the pipeline after solve.
**Delivers:** Z3 finite verification, constraint contradiction detection, feasibility pre-checks, sensitivity/perturbation harness via scipy.
**Uses:** Z3 4.16, scipy 1.17 (both already in dependency list but not exercised in Phase 1 beyond feasibility stubs).
**Avoids:** Z3 scope creep (explicit verification target scoping), scipy/CP-SAT boundary confusion (clear backend routing).

### Phase 3: Extensibility and Robustness

**Rationale:** Domain template system and stress testing require stable core + verification. This phase shifts from "does it work" to "does it scale and extend."
**Delivers:** Domain template system with schema validation, stress testing / adversarial parameter search, additional domains, report enhancements.
**Addresses:** Domain registry pattern, schema-less domain extension pitfall, constraint explosion pitfall.

### Phase 4: Additional Solver Backends

**Rationale:** Pyomo and CVXPY unlock continuous optimization and mixed-integer problems that CP-SAT cannot handle. Requires the backend abstraction to be proven by Phase 1-2.
**Delivers:** Pyomo backend for MILP/LP, CVXPY backend for convex continuous, backend selection based on IR model family classification.

### Phase 5: Formal Verification Bridge

**Rationale:** Lean 4 proof scaffolding is the most ambitious feature and has the lowest-confidence dependencies (LeanInteract/leanclient are 0.x). Requires Z3 verification to be mature.
**Delivers:** Lean 4 `.lean` file generation with type signatures and proof obligations, optional LeanInteract integration for type-checking.

### Phase Ordering Rationale

- Phase 1 must come first because every other phase reads from the IR. Getting the IR schema, symbol table, and epistemic status enforcement wrong would require rewrites across all subsequent phases.
- Phase 2 follows immediately because Z3 verification is the primary differentiator and has a clean dependency on Phase 1 IR. Deferring it further risks the product being perceived as "just a solver wrapper."
- Phases 3-5 can be reordered with minimal impact, but the suggested order follows increasing dependency complexity and decreasing confidence in available tooling.
- The closed constraint grammar must ship in Phase 1. Retrofitting it later is a rewrite, not a refactor.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** Z3 verification target scoping needs concrete examples for the generic allocation domain. What properties are verifiable in bounded time? Need to prototype Z3 encoding before committing to verification scope.
- **Phase 4:** Pyomo/CVXPY integration patterns need API research. Backend abstraction layer design needs validation.
- **Phase 5:** LeanInteract and leanclient are both 0.x with unclear stability. Need to evaluate which library to use and whether Lean 4 toolchain installation can be automated.

Phases with standard patterns (skip research-phase):
- **Phase 1:** All technologies are mature with extensive documentation. CP-SAT, Pydantic, Jinja2, ruamel.yaml are well-documented. The compiler pipeline pattern is standard.
- **Phase 3:** Domain template systems and stress testing follow established patterns. No novel integration challenges.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All dependencies verified on PyPI with recent releases (Jan-Mar 2026). Version compatibility confirmed. |
| Features | HIGH | Feature landscape derived from design brief with clear prioritization. Dependencies between features are well-understood. |
| Architecture | HIGH | Hybrid Claude + Python runtime is a proven pattern for Claude Code plugins. IR-as-contract is standard compiler architecture. |
| Pitfalls | HIGH | Pitfalls are domain-specific and actionable. Prevention strategies are concrete and implementable in Phase 1. |

**Overall confidence:** HIGH

### Gaps to Address

- **Expression DSL design:** Phase 1 uses named constraint templates to avoid natural language soup, but Phase 2+ will need a proper expression DSL. The grammar design is unresearched.
- **CP-SAT scaling strategy:** When users specify parameters as floats but the solver needs integers, the scaling factor strategy needs experimentation during Phase 1.
- **Plugin setup UX:** How `/model:setup` works (venv creation vs system Python, dependency isolation) needs prototyping.
- **Lean 4 toolchain distribution:** How to handle Lean 4 installation for end users is unclear. LeanInteract vs leanclient evaluation deferred to Phase 5.
- **Large model performance:** MVP targets small-to-medium models (<10K variables). Performance characteristics for larger models need profiling during Phase 3.
- **Subprocess reliability:** The subprocess seam between Claude and Python (error handling, timeouts, cross-platform) needs validation during Phase 1 implementation.

## Sources

### Primary (HIGH confidence)
- [OR-Tools PyPI](https://pypi.org/project/ortools/) -- v9.15.6755, solver capabilities and API
- [OR-Tools CP-SAT docs](https://developers.google.com/optimization/cp/cp_solver) -- integer-only solver behavior
- [CP-SAT Primer](https://d-krupke.github.io/cpsat-primer/) -- community guide, API patterns
- [z3-solver PyPI](https://pypi.org/project/z3-solver/) -- v4.16.0.0, verification capabilities
- [Pydantic docs](https://docs.pydantic.dev/latest/) -- v2.12.5, discriminated unions, validation
- [Jinja2 PyPI](https://pypi.org/project/Jinja2/) -- v3.1.6, template inheritance
- [Claude Code plugin docs](https://code.claude.com/docs/en/discover-plugins) -- plugin architecture

### Secondary (MEDIUM confidence)
- [Z3 Python tutorial](https://ericpony.github.io/z3py-tutorial/guide-examples.htm) -- verification scope and timeout behavior
- [NetworkX docs](https://networkx.org/documentation/stable/reference/index.html) -- graph algorithm performance
- [ruamel.yaml PyPI](https://pypi.org/project/ruamel.yaml/) -- YAML 1.2 compliance, comment preservation
- Design brief sections 5, 7, 11, 12, 15, 16, 17, 18, 21, 27 -- feature requirements, risks, architecture

### Tertiary (LOW confidence)
- [LeanInteract GitHub](https://github.com/augustepoiroux/LeanInteract) -- 0.x, Python interface for Lean 4
- [leanclient PyPI](https://pypi.org/project/leanclient/) -- 0.x, thin Lean 4 LSP wrapper

---
*Research completed: 2026-03-09*
*Ready for roadmap: yes*
