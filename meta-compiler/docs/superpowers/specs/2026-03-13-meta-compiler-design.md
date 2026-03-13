# Meta-Compiler for Validated Mathematical Models

## Problem

LLMs produce mathematically beautiful but structurally incoherent papers. Symbols get reused with different meanings, derivations create orphans, index dimensions silently mismatch, and forward references go unresolved. You don't discover this until you try to implement the math — often 50 pages later.

This was observed directly on a workforce optimization engagement where Claude produced a 1,750-line mathematical framework paper with:

- `F_i` used three different ways (theoretical decay, explicit superscript variant, rubric fragility-resilience with inverted polarity)
- `W_j` vs `W_i` overload (project importance weight vs employee receptivity)
- `epsilon` dual use (coverage premium coefficient vs minimum assignment granularity)
- Orphaned variables introduced but never referenced by any constraint or objective
- Stale section cross-references from prior renumbering

## Product

A co-development pipeline where mathematical models and executable validation code grow together as a single document. Every new symbol and formula is immediately validated against a cumulative symbol table and tested with generated Python code. Hard block on any inconsistency.

The workflow:

1. User describes intent in plain language
2. Claude proposes the math (LaTeX) and its validation shadow (Python)
3. The system immediately validates the Python against everything that exists so far
4. If validation fails — hard block. Claude must fix it before continuing.
5. If validation passes — the symbol table and code grow, and the next concept can be introduced.

The user is not a mathematician. Claude does the math. The system keeps Claude honest.

## Output Artifacts

Three artifacts from one source document:

### Artifact 1: The Paper

A clean Markdown/LaTeX document with all validation blocks stripped. Supports multiple reading depths via section markers:

- `<!-- depth:executive -->` — executive summary for leadership
- `<!-- depth:technical -->` — full mathematical framework for technical staff
- `<!-- depth:appendix -->` — derivations, proofs, calibration details

Same source, different slices. Renders to PDF via standard tooling (Pandoc, etc.).

### Artifact 2: The Codebase

A standalone Python package extracted from the validation blocks. The compiler splits the single sequence of validation blocks into files by symbol type — each `Set()` call goes to `sets.py`, each `Parameter()` to `parameters.py`, etc. All files import the shared global registry from `registry.py`. Symbols are available globally after registration — `expressions.py` doesn't import from `parameters.py`, it accesses symbols via the registry (e.g., `S("W")`, `cap[i]`). The `__main__.py` entry point imports each module in dependency order (sets, parameters, variables, expressions, constraints, objectives) to rebuild the full registry state.

```
model/
  registry.py        # The registry engine (not generated — part of the framework)
  sets.py            # Set declarations (generated from Set() calls)
  parameters.py      # Parameter declarations (generated from Parameter() calls)
  variables.py       # Decision variable declarations (generated from Variable() calls)
  expressions.py     # Derived expressions (generated from Expression() calls)
  constraints.py     # All constraints (generated from Constraint() calls)
  objectives.py      # Objective functions (generated from Objective() calls)
  __main__.py        # Entry point: imports all modules in order, runs registry.run_tests()
  tests/
    test_integrity.py  # Full cumulative validation suite
```

Runs independently. `python -m model` executes the full registry and reports pass/fail. Serves as the foundation for wiring up an actual solver later.

### Artifact 3: The Validation Report

- Symbol table — every symbol, its type, index sets, domain, units, description, and which section introduced it
- Dependency graph — what references what
- Constraint catalog — hard vs soft, grouped by family, with cross-references to paper sections
- Test results — full pass/fail log from the cumulative suite
- Coverage audit — which symbols are used where, orphan status, phantom status
- Epistemic status summary — which claims are definitions, assumptions, or derived

## Document Structure

The source document is a Markdown file with three interleaved block types:

**Prose blocks** — normal Markdown. Narrative, explanations, executive summaries. The compiler ignores these.

**Math blocks** — LaTeX in `$$...$$` or `$...$`. The formulas that appear in the final paper. Extracted for the paper artifact but not validated directly.

**Validation blocks** — fenced Python code blocks opened with the literal tag ` ```python:validate ` (triple backtick, then `python:validate` with no space). The executable shadow of the math. The compiler runs these. Not included in the client-facing paper.

Example source section:

````markdown
### 2.1 Worker Capacity

Each worker $i \in \mathcal{W}$ has a maximum available capacity
measured in effort-hours per period:

$$cap_i \in \mathbb{R}^+, \quad \forall i \in \mathcal{W}$$

```python:validate
cap = Parameter("cap", index=["W"], domain="nonneg_real",
                units="hours", description="Maximum capacity of worker i")
registry.run_tests()
```
````

## The Symbol Registry

The heart of the system. A Python object that accumulates state as the document grows.

### Symbol Types

- **Sets** — `W` (workers), `P` (projects), `T` (time periods)
- **Parameters** — `cap_i` (capacity), `h_j` (effort-hours), `d_{jp}` (demand)
- **Decision variables** — `x_{ijp}` (allocation fraction)
- **Derived expressions** — `U_{ijp}` (utility, defined in terms of other symbols)
- **Constants** — `alpha`, `beta` (coefficients)

### Registration-Time Checks

- **Uniqueness** — no symbol can be registered twice with different meanings
- **Index validity** — if you declare `cap_i`, set `W` (indexed by `i`) must already exist
- **Domain consistency** — a binary variable can't appear in a continuous expression without explicit casting
- **Dependency tracking** — derived expressions must reference only previously defined symbols. No forward references, no orphans.

### Cumulative Test Checks (on every `registry.run_tests()`)

- **No orphans** — every registered symbol is referenced by at least one constraint, objective, or expression. During authoring, orphans produce warnings (the symbol may be used in a later section). At compilation time (when `/model:compile` is run), orphans become hard blocks. The user explicitly triggers compilation when the document is complete.
- **No phantoms** — every symbol used in an expression must be in the registry
- **Dimensional consistency** — unit checking uses a simple unit algebra supporting base units (`hours`, `headcount`, `dollars`, `points`, `dimensionless`) and compound units formed by multiplication and division (e.g., `hours/headcount`, `dollars/hour`). When a parameter declares `units="hours"` and another declares `units="headcount"`, the registry rejects addition or comparison between them. Compound units propagate through expressions: `x` (dimensionless) times `h` (hours) yields hours. Custom base units can be declared via `Unit("effort_points")`. This is not a full physical units library — it is a lightweight tag system sufficient to catch the most common errors.
- **Dependency cycle detection** — no circular references in derived expressions

## Registry API

Six nouns, one verb. Constructors implicitly register with the global registry — no separate `register()` call needed. Each constructor returns a proxy object with overloaded `__getitem__` and comparison operators, enabling symbolic expressions in lambdas.

```python
# Declare index sets
Set("W", description="Workers")
Set("P", description="Project types")
Set("T", description="Time periods")

# Declare parameters
Parameter("cap", index=["W"], domain="nonneg_real",
          units="hours", description="Maximum capacity of worker i")
Parameter("h", index=["P"], domain="nonneg_real",
          units="hours", description="Effort-hours required per project type")

# Declare decision variables
Variable("x", index=["W", "P", "T"], domain="continuous",
         bounds=(0, 1), description="Allocation fraction")

# Declare derived expressions
Expression("load",
    definition=lambda i: sum(x[i,j,t] * h[j] for j in S("P") for t in S("T")),
    index=["W"], units="hours",
    description="Total load on worker i")

# Declare constraints
Constraint("capacity_limit",
    expr=lambda i: load[i] <= cap[i],
    over=["W"], type="hard",
    description="No worker exceeds their capacity")

# Declare objectives
Objective("maximize_utility",
    expr=lambda: sum(x[i,j,t] * U[i,j,t]
                     for i in S("W") for j in S("P") for t in S("T")),
    sense="maximize",
    description="Maximize total weighted utility across assignments")

# After every block
registry.run_tests()
```

Design choices:

- **Implicit registration** — constructors (`Set(...)`, `Parameter(...)`, etc.) auto-register with the global registry. No separate `register()` call. This keeps validation blocks concise.
- **Proxy objects** — each constructor returns a proxy with overloaded `__getitem__` (for indexing like `x[i,j,t]`) and comparison operators (for constraints like `load[i] <= cap[i]`). These build symbolic expression trees — nested data structures (e.g., `CompareExpr(lhs=IndexExpr("load", ["i"]), op="<=", rhs=IndexExpr("cap", ["i"]))`) — that the registry walks to extract referenced symbols, validate index dimensions, and check unit compatibility. Lambdas are called once with symbolic placeholder arguments to capture the expression tree; they are never evaluated numerically during validation.
- **Declarative** — you say what things are, not how to compute them
- **Lambda expressions** — constraints and expressions use Python lambdas that mirror the LaTeX. Loop variables must match set names: `i` for `W`, `j` for `P`, `t` for `T`.
- **`S("P")` for set references** — a lightweight accessor that verifies the set exists at call time
- **Everything takes a description** — these feed the validation report's symbol table and the paper's auto-generated notation table
- **`registry.run_tests()` returns structured results** — a `TestResult` object with `.passed` (bool), `.errors` (list of blocking issues), and `.warnings` (list of advisory issues). The hook inspects `.passed` to determine hard block. Non-negotiable hard gate.

## Validation Pipeline

The compiler runs validation blocks sequentially, enforcing a natural ordering:

**Stage 1: Set Declaration** — define index sets. Foundation for everything else.

**Stage 2: Parameter Registration** — parameters register against existing sets.

**Stage 3: Decision Variable Registration** — variables declare type, index sets, bounds. All index sets must exist.

**Stage 4: Expression and Constraint Registration** — derived expressions and constraints reference existing symbols. The registry verifies:
- All referenced symbols exist
- Index dimensions match
- Units are compatible
- Constraints that involve decision variables must reference at least one; parameter-only constraints are permitted as input validation checks

**Stage 5: Objective Registration** — same checks as constraints, plus: must reference at least one decision variable, all terms must be dimensionally summable.

**Stage 6: Cumulative Integrity Check** — orphan scan, phantom scan, cycle detection, dimensional consistency across all expressions.

Any failure at any stage is a hard block.

## Error Model

Every error names the exact symbols involved, states what was expected vs found, and suggests a fix where possible.

### Symbol Conflict

```
BLOCK: Symbol "F" already registered as "fragility decay rate (dimensionless)"
Cannot redefine as "fragility-resilience rubric score (points)"
Suggestion: Use a distinct symbol, e.g., "FR" for the rubric score
```

### Undefined Reference

```
BLOCK: Constraint "capacity_limit" references symbol "cap" which is not registered
Defined symbols: W, P, x, h, d
```

### Index Mismatch

```
BLOCK: Expression "load[i]" sums over x[i,j,p] but Variable "x"
is indexed by ["W", "P"] (2 dimensions), not 3
```

### Dimensional Inconsistency

```
BLOCK: Constraint "capacity_limit" compares left side (units: hours)
with right side (units: headcount). Cannot compare incompatible units.
```

### Orphan (at completion)

```
BLOCK: Symbol "buildability" was registered in Section 17 but is never
referenced by any Constraint, Objective, or Expression.
Either use it or remove it.
```

### Dependency Cycle

```
BLOCK: Circular dependency detected:
  load -> utilization -> adjusted_cap -> load
```

## Claude Code Integration

This is a Claude Code plugin with hooks and commands.

### Live Validation (PostToolUse Hook)

When Claude writes or edits a file with the `.math.md` extension (the canonical extension for validated math documents):

1. Hook detects the Write or Edit tool was used on a `.math.md` file
2. Re-runs **all** validation blocks in the document from top to bottom, rebuilding the registry from scratch. This ensures consistency regardless of where the edit occurred (middle, beginning, or end). The registry is stateless between hook invocations — no serialization needed.
3. If validation fails — returns the error message to Claude as hook feedback, forcing a fix before the conversation continues
4. If validation passes — conversation continues

The full re-run is acceptable because validation blocks are lightweight declarations, not heavy computations. For a 50-page paper, the full pipeline runs in under a second.

### Commands

- `/model:check` — run full pipeline against current document, report status
- `/model:paper` — compile clean paper artifact (strips validation blocks)
- `/model:report` — generate validation report
- `/model:status` — show current symbol table and defined/undefined/orphan status
- `/model:compile` — produce all three artifacts

## Implementation Order

This spec covers three subsystems that should be built in sequence:

1. **The symbol registry and validation engine** — the core Python library (`Set`, `Parameter`, `Variable`, `Expression`, `Constraint`, `Objective`, `registry.run_tests()`). This is the foundation. It can be built and tested standalone with no Claude Code dependency.

2. **The artifact compiler** — the pipeline that reads a `.math.md` document, extracts validation blocks, runs them, and emits the three artifacts (paper, codebase, report). Depends on subsystem 1.

3. **The Claude Code plugin** — the hooks and commands that integrate subsystems 1 and 2 into the live authoring workflow. Depends on subsystems 1 and 2.

Each subsystem has a clear boundary: the registry is a Python library with a public API, the compiler is a CLI tool that reads files and emits files, and the plugin is a thin integration layer that calls the compiler on hook events.

Each subsystem should be planned and implemented as a separate phase. This spec describes the full system; the implementation plan should break it into three sequential phases with separate deliverables and test criteria for each.

## Relationship to Original Design Document

The original design doc (2026-03-09) described a broad meta-compiler for generating domain-specific optimization systems from YAML specifications. This spec refocuses on the core problem that motivated that vision:

**LLMs cannot be trusted to produce structurally coherent mathematical models.** The solution is not a generic optimization system generator — it is a validated authoring pipeline that forces structural coherence during the writing process itself.

Key differences from the original design:

- **Paper-first, not schema-first** — the math paper is the primary artifact, not a YAML spec
- **Validation during authoring, not after** — problems are caught as they're introduced, not discovered during implementation
- **Claude Code plugin, not standalone compiler** — integrates into the existing workflow where Claude writes the math
- **Domain-agnostic** — works for any mathematical model, not just allocation-class optimization
- **Reusability is secondary** — the primary value is building any new model from scratch with structural validation baked in

The original design's concepts (epistemic status tracking, domain instantiation, proof scaffolding, solver backends) remain valid as future extensions once the core validation pipeline is proven.
