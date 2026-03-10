# Domain Pitfalls

**Domain:** Meta-compiler for constrained optimization systems (Claude Code plugin)
**Researched:** 2026-03-09

## Critical Pitfalls

Mistakes that cause rewrites or major issues.

### Pitfall 1: Natural Language Soup in Spec Layer

**What goes wrong:** The YAML spec allows freeform string expressions for constraints and objectives (e.g., `rule: "load should be balanced"`). Claude interprets these differently each time. The compiler becomes a glorified prompt wrapper.

**Why it happens:** Temptation to make the spec "user-friendly" by accepting natural language. Feels easier to build initially.

**Consequences:** Non-deterministic compilation. Users cannot debug why the same spec produces different code. The IR becomes meaningless because the mapping from spec to IR is LLM-dependent rather than schema-deterministic.

**Prevention:** Constraint expressions must use a closed grammar. Either:
- Named constraint templates from the domain module (e.g., `type: capacity_limit`, `params: {resource: workers, bound: capacity}`)
- A simple expression DSL that maps deterministically to IR (e.g., `sum(assign[w,p] for w in Workers) == 1`)

Claude helps users WRITE the structured spec, but the spec itself must be parseable without Claude.

**Detection:** If you cannot compile the spec with `python cli.py compile spec.yaml` (no LLM involved), the spec is too loose.

### Pitfall 2: Implementation Drift from IR

**What goes wrong:** Generated code starts being hand-edited or the code generator adds logic not represented in the IR. The IR and the running code diverge.

**Why it happens:** Users tweak generated code for "quick fixes." Code generator accumulates special cases. Phase 2 features bypass IR for speed.

**Consequences:** Reports claim things the code does not implement. Verification checks properties the solver does not enforce. Trust collapses.

**Prevention:**
- Generated code files carry a header: `# AUTO-GENERATED FROM IR. DO NOT EDIT. Regenerate with /model:compile`
- All code generation reads exclusively from serialized IR files
- A `model:check --drift` command compares IR hash with generated code hash
- Never add "escape hatches" that let users inject raw code into the generated solver

**Detection:** IR hash differs from code generation metadata hash. Generated code contains manual edits.

### Pitfall 3: Epistemic Status Collapse

**What goes wrong:** Reports present solver results, assumptions, and verified claims at the same confidence level. Users treat solver output as proof.

**Why it happens:** Status labels feel like bureaucratic overhead. Developers skip them "for now." Reports use uniform formatting that does not distinguish status levels.

**Consequences:** The core differentiator (epistemic hygiene) disappears. Users make decisions based on unverified solver output presented as fact. The product becomes indistinguishable from a solver wrapper.

**Prevention:**
- `EpistemicStatus` is a required field on all IR nodes (Pydantic validation fails without it)
- Report templates use different formatting per status level (e.g., bold for assumptions, italic for conjectures, checkmarks for verified)
- The validator flags any IR node missing a status as an error

**Detection:** Any IR node without an `epistemic_status` field. Any report section without per-claim status labels.

### Pitfall 4: OR-Tools CP-SAT API Misuse

**What goes wrong:** Generated CP-SAT code uses floating-point values, unbounded domains, or unsupported constraint types. CP-SAT is integer-only internally.

**Why it happens:** The design brief mentions continuous variables and LP relaxations. Developers assume CP-SAT handles continuous optimization. It does not. CP-SAT works exclusively with integers internally, using scaling for pseudo-continuous behavior.

**Consequences:** Silent precision errors. Infeasible models that should be feasible. Incorrect objective values from integer rounding.

**Prevention:**
- The IR type system must distinguish integer-domain problems (CP-SAT eligible) from continuous-domain problems (scipy/future Pyomo backend)
- Code generator refuses to emit CP-SAT code for continuous variables. Returns error: "Use scipy backend for continuous optimization"
- All CP-SAT parameters are scaled to integers at code generation time, with scaling factors tracked in IR metadata
- scipy.optimize.linprog handles LP relaxations, NOT CP-SAT

**Detection:** Generated CP-SAT code contains `model.NewIntVar` with bounds derived from unscaled floats. Solver returns unexpected INFEASIBLE for valid-looking models.

### Pitfall 5: Z3 Verification Scope Creep

**What goes wrong:** Z3 is asked to verify properties that are undecidable or computationally infeasible (e.g., "prove optimality of all solutions" or "verify for all possible parameter values").

**Why it happens:** Excitement about having a theorem prover. Users request unbounded verification. Developers do not scope verification targets.

**Consequences:** Z3 times out silently or returns UNKNOWN. Users lose trust in the verification layer. Or worse: developers suppress UNKNOWN results and only show SATISFIABLE/UNSATISFIABLE.

**Prevention:**
- Verification targets must declare their scope: finite-case check (bounded parameters), satisfiability check (specific instance), or universal claim (requires proof assistant)
- Z3 calls have hard timeouts (30 seconds default, configurable)
- UNKNOWN results are reported honestly with the epistemic status "conjecture" (not "verified")
- The validator flags verification targets that exceed Z3's scope

**Detection:** Z3 returning UNKNOWN frequently. Verification targets without explicit bounds.

## Moderate Pitfalls

### Pitfall 6: Constraint Explosion in Domain Templates

**What goes wrong:** Domain templates with many optional constraint families generate models with thousands of constraints, most of which are trivially satisfied or redundant.

**Prevention:** Templates generate constraints lazily based on which entities/parameters are present in the spec. Constraint templates declare their activation conditions. The validator reports redundant constraints as warnings.

### Pitfall 7: YAML Spec Backwards Compatibility

**What goes wrong:** Spec schema changes between versions break existing user specs. Users cannot upgrade without rewriting their models.

**Prevention:** Version the spec schema (`version: "1.0"` in spec header). Write migration scripts for schema changes. The parser reads the version and applies the correct Pydantic model.

### Pitfall 8: Subprocess Failure Modes

**What goes wrong:** Claude invokes `python3 meta_compiler/cli.py compile` but the user's Python environment does not have dependencies installed, or uses the wrong Python version.

**Prevention:** `/model:setup` command runs dependency installation. CLI entry point checks for required packages and reports clear errors. The setup command verifies Python version >= 3.12.

### Pitfall 9: Jinja2 Template Injection

**What goes wrong:** User-supplied strings from the YAML spec are interpolated into Jinja2 templates without sanitization, producing invalid or dangerous Python code.

**Prevention:** All user-supplied values go through a sanitization layer before template rendering. Template variables are typed (not raw strings). The code generator validates generated code parses as valid Python AST before writing to disk.

### Pitfall 10: Over-Engineering the Expression DSL

**What goes wrong:** Building a full expression parser with custom grammar, lexer, and evaluator for the constraint DSL. This becomes a maintenance burden that exceeds the compiler itself.

**Prevention:** Use named constraint templates with typed parameters for MVP. The "expression" field in the spec is a reference to a template, not a custom expression language. A proper expression DSL is Phase 2+.

## Minor Pitfalls

### Pitfall 11: NetworkX Performance on Large Graphs

**What goes wrong:** Structural validation runs cycle detection and dependency analysis on the constraint graph. For large models (1000+ constraints), NetworkX graph algorithms slow down.

**Prevention:** Profile validation pass on medium-sized models. Use NetworkX efficient algorithms (e.g., `nx.is_directed_acyclic_graph` is O(V+E)). Cache graph construction.

### Pitfall 12: OR-Tools Version Pinning

**What goes wrong:** OR-Tools API changes between major versions. Generated code breaks on update.

**Prevention:** Pin to `>=9.15,<10`. Test against latest version in CI. The code generator uses the stable `CpModel`/`CpSolver` API, not internal/experimental APIs.

### Pitfall 13: Report Generation Assumes Solve Success

**What goes wrong:** Report template crashes when the solver returns INFEASIBLE or times out because the template expects solution values.

**Prevention:** Report templates handle all solve statuses: OPTIMAL, FEASIBLE, INFEASIBLE, UNKNOWN, TIMEOUT. Each status has a different report section. Infeasibility reports include diagnostic information (which constraints are likely conflicting).

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Spec parsing (Phase 1) | Natural language creep in constraint expressions | Enforce closed grammar from day one |
| IR design (Phase 1) | Missing epistemic status on nodes | Make it a required Pydantic field |
| CP-SAT generation (Phase 1) | Float values in integer-only solver | Type system prevents continuous vars from reaching CP-SAT backend |
| Structural validation (Phase 1) | Incomplete check coverage | Start with top-5 checks from design brief section 15; expand iteratively |
| Z3 verification (Phase 2) | Scope creep, unbounded queries | Hard timeouts, explicit verification target scoping |
| Sensitivity analysis (Phase 2) | scipy and CP-SAT boundary confusion | scipy for continuous relaxations, CP-SAT for integer re-solves |
| Domain templates (Phase 2+) | Schema-less domain extensions | Domain templates must validate against domain Pydantic schema |
| Lean scaffolding (Phase 4-5) | Uncompilable Lean output | Generate minimal `.lean` files, test with LeanInteract |
| Plugin packaging (Phase 1) | Missing Python deps at runtime | `/model:setup` with explicit dependency verification |

## Sources

- Design brief section 27 (failure modes and risks)
- PROJECT.md constraints section
- [CP-SAT Primer](https://d-krupke.github.io/cpsat-primer/) -- integer-only solver behavior
- [Z3 Python tutorial](https://ericpony.github.io/z3py-tutorial/guide-examples.htm) -- solver timeout behavior
- [Pydantic validation docs](https://docs.pydantic.dev/latest/concepts/models/) -- required field enforcement
