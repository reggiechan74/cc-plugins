# Meta-Compiler v2 Design Spec

**Date:** 2026-03-14
**Status:** Draft
**Scope:** Architecture redesign of the meta-compiler from expression trees to LLM-executed real Python

## Motivation

The v0.1 meta-compiler uses symbolic expression trees built via operator overloading in lambdas. Every new math operator (min, max, abs, `**`, piecewise, cardinality) requires new AST node classes in `expr.py`, updates to `collect_refs()`, `_check_dimensions()`, and `_render_expr()`. Onboarding a single paper surfaced 7 operator gaps in `future-upgrades.md`. The approach doesn't scale.

v2 eliminates expression trees. The LLM writes real Python validation code that executes numerically. The compiler shrinks to a symbol registry + runner. Python IS the specification language; Claude IS the intelligence layer.

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| DSL surface | Keep same API (Set, Parameter, Variable, Expression, Constraint, Objective, S) | Proven, terse, close to math notation |
| Expr execution | Real Python — numeric execution against test data, not symbolic capture | Eliminates expression tree ceiling |
| Test data | Layered — fixture blocks when provided, structural checks only when absent | LLM writes coherent scenarios; no algorithmic feasibility problem |
| Structural checks | Runtime instrumentation via proxy access logs (numeric mode) or source scanning (structural mode) | Accurate orphan/phantom detection without expression trees |
| Unit checking | Boundary-only — compare declared units at Constraint/Objective registration | Simpler than per-operation propagation; avoids custom numeric wrapper |
| Codegen | Dropped — optional thin runner script instead of multi-file package | `.model.md` is already executable; codegen was compensating for non-executable trees |
| Migration | Clean break — new `.model.md` extension, coexists with `.math.md` | Avoids backward-compat contortions |
| Expr function signature | Positional index binding (system iterates) + zero-arg fallback (self-iterating) | Keeps v0.1's terse `lambda i: load[i] <= cap[i]`; handles complex cases via zero-arg |

## File Format

`.model.md` files contain four block types:

| Block | Fence | Purpose |
|-------|-------|---------|
| Prose | (unfenced markdown) | Narrative, headings, tables |
| Math | `$$...$$` | LaTeX equations |
| Fixture | ` ```python:fixture ` | Test data as Python dicts |
| Validate | ` ```python:validate ` | Symbol declarations + constraint/objective definitions |

### Execution order

1. Parser collects all blocks top-to-bottom
2. Fixture blocks execute first, populating a cumulative data store (later fixtures override earlier ones)
3. Validate blocks execute sequentially in a shared namespace with fixture data available via proxy objects

### Example

```markdown
# Workforce Model

## Sets & Parameters

` ``python:fixture
sets = {"W": ["alice", "bob", "carol"], "P": ["projA", "projB"]}
cap = {"alice": 40, "bob": 35, "carol": 40}
demand = {"projA": 60, "projB": 45}
` ``

$$\sum_{i \in W} x_{i,p} \geq d_p \quad \forall p \in P$$

` ``python:validate
Set("W", description="Workers")
Set("P", description="Projects")
Parameter("cap", index="W", units="hours", description="Weekly capacity")
Parameter("demand", index="P", units="hours", description="Project demand")
Variable("x", index=("W", "P"), domain="continuous", bounds=(0, None), units="hours", description="Assignment")
Constraint("meet_demand", over="P", expr=lambda p: sum(x[i, p] for i in S("W")) >= demand[p])
Constraint("respect_cap", over="W", expr=lambda i: sum(x[i, p] for p in S("P")) <= cap[i])
` ``
```

## Symbol Registry & Proxy Objects

### Registry

Same structure as v0.1: central accumulator with `register_set`, `register_parameter`, `register_variable`, `register_expression`, `register_constraint`, `register_objective`. Same global instance, same `reset()` between runs.

Key change: `expr` functions are stored as callables, not as captured expression trees. `_capture_lambda()` is eliminated.

All v0.1 keyword arguments are preserved:

- `Constraint(name, *, expr, over=None, type="hard", description="")` — `type` and `description` unchanged
- `Objective(name, *, expr, sense="maximize", description="")` — `sense` and `description` unchanged
- `Parameter`, `Variable`, `Expression` — all kwargs unchanged

The example blocks in this spec omit optional kwargs for brevity.

### Proxy objects

Proxies become data-backed instead of tree-building:

| Operation | v0.1 | v2 |
|-----------|------|-----|
| `cap[i]` | `IndexExpr("cap", ("i",))` | Actual numeric value (e.g., `40`) |
| `cap[i] + load[i]` | `ArithExpr(...)` node | Plain Python number (e.g., `78`) |
| `cap[i] <= 40` | `CompareExpr(...)` node | `True` or `False` |
| Side effect | None | Logs `"cap"` to access tracker |

### Proxy implementation

```python
class SymbolProxy:
    def __init__(self, name: str, data: dict | None, access_log: set):
        self.name = name
        self._data = data          # from fixture, or None
        self._access_log = access_log

    def __getitem__(self, key):
        self._access_log.add(self.name)
        if self._data is None:
            raise RuntimeError(f"No fixture data for symbol '{self.name}'")
        return self._data[key]
```

### Multi-indexed fixture data

Fixture data for multi-indexed symbols uses tuple keys:

```python
# In fixture block:
x = {("alice", "projA"): 5, ("alice", "projB"): 10, ("bob", "projA"): 20, ...}
```

When `x[i, p]` is called in a lambda, Python passes a tuple `(i, p)` to `__getitem__`, which looks up `self._data[(i, p)]` directly. No nested dicts.

### Namespace wiring (fixture → proxy)

When the executor runs:

1. Fixture blocks execute in their own namespace, producing a `data_store: dict[str, dict]` mapping symbol names to their fixture dicts (e.g., `{"cap": {"alice": 40, ...}, "x": {("alice", "projA"): 5, ...}}`)
2. When a validate block calls `Set("W")`, `Parameter("cap", ...)`, etc., the registration function checks `data_store` for a matching key
3. The returned `SymbolProxy` receives `data=data_store.get(name)` — if the fixture defined data for that symbol, the proxy is data-backed; if not, the proxy has `data=None`

### `S()` behavior in v2

In v0.1, `S("W")` returns a symbolic `SetIterator`. In v2:

- **Numeric mode:** `S("W")` returns the actual set members from the fixture data (e.g., `["alice", "bob", "carol"]`), enabling real iteration in `for i in S("W")`
- **Structural mode:** `S("W")` is not called (expr functions are not invoked). The symbol name `"W"` is detected via tokenized source text scanning for orphan/phantom checks.

## Execution Model

### Two modes

**Structural mode (no fixture):**

1. Reset registry and access log
2. Execute validate blocks sequentially in shared namespace
3. `expr` functions are stored but not called
4. Structural checks run on the registry alone:
   - Orphans/phantoms: the parser captures the raw source text of each `expr` lambda at parse time (from the fenced code block content). Symbol names are extracted by tokenizing the source with Python's `tokenize` module and collecting all `NAME` tokens that match registered symbol names. This avoids regex false positives (e.g., `cap` matching inside `capacity`).
   - Cycles: from registration-order dependency graph
   - Unit boundary check: compare declared units using symbol names extracted from tokenized source text

**Numeric mode (fixture present):**

1. Reset registry and access log
2. Load fixture data into data store
3. Execute validate blocks — proxy `__getitem__` returns real values, access log records accesses
4. For each constraint with `over`: iterate the set, call `expr(element)` for each, collect failures
5. For each constraint without `over` (zero-arg): call `expr()` once, check result is `True`
6. For objectives: call `expr`, verify it returns a numeric value
7. Run structural checks (orphans/phantoms from access log)
8. Run unit boundary checks

### Expr function signatures

Two forms detected by arity:

- **Positional args** (e.g., `lambda i: load[i] <= cap[i]`): system iterates `over` set, calls once per element
- **Zero args** (e.g., `lambda: all(load[i] <= cap[i] for i in sets["W"])`): self-iterating, called once, must return `True`/`False`

### Error reporting

| Check | Message format |
|-------|---------------|
| Phantom | `Symbol "foo" referenced but never declared` |
| Orphan | `Symbol "bar" declared but never referenced` (warning in authoring, error in strict) |
| Constraint failure | `Constraint "respect_cap" violated for i="carol": 45 <= 40 is False` |
| Unit mismatch | `Constraint "balance": left side is "hours", right side is "dollars"` |
| Python error | `Error in constraint "meet_demand": KeyError 'dave'` |

## Checks System

### Phantoms
- **Numeric mode:** symbols accessed at runtime (via access log) but not registered
- **Structural mode:** symbol names found in `expr` tokenized source text but not registered
- Always an error

### Orphans
- **Numeric mode:** symbols registered but never accessed at runtime
- **Structural mode:** symbols registered but never mentioned in any `expr` tokenized source text
- Authoring mode (`strict=False`): warning
- Compilation mode (`strict=True`): error

### Cycles
- Same as v0.1: DFS on expression dependency graph built from registration order
- Works identically in both modes — derived from registration, not execution

### Unit boundary check
- For each constraint: compare declared units of symbols on left and right sides
- No unit propagation through arithmetic
- Catches `hours <= dollars` but not `hours + dollars` in a sub-expression
- Objectives exempt (same as v0.1)

### Removed from v0.1
- `_infer_units()` — no expression tree to walk
- `collect_refs()` — replaced by access log or source scanning
- All `ExprNode` pattern matching in `checks.py`

## Compiler Pipeline & Artifacts

### Pipeline

`compile_document(source)`:

1. Parse — split `.model.md` into block types (Prose, Math, Fixture, Validate)
2. Execute — run fixture blocks, then validate blocks in strict mode
3. Check — all four checks must pass
4. Generate artifacts

### Artifacts

| Artifact | Description |
|----------|-------------|
| **Paper** | Clean markdown — prose + math, strips fixture and validate blocks. Same depth filtering as v0.1. |
| **Report** | Symbol table, dependency graph, coverage metric, test results. Same structure, simpler internals. |
| **Runner** (optional) | Single Python script that imports meta-compiler and runs `check_document(strict=True)` on the `.model.md` file. |

### Coverage metric

Ratio of math blocks with a following validate block. Fixture blocks don't count toward coverage and don't interrupt math-to-validate association — a math block followed by a fixture block followed by a validate block counts as covered.

### CLI

```bash
python -m meta_compiler.cli check <file.model.md> [--strict]
python -m meta_compiler.cli paper <file.model.md> [--depth ...] [--output <path>]
python -m meta_compiler.cli report <file.model.md> [--output <path>]
python -m meta_compiler.cli compile <file.model.md> [--output <dir>] [--depth ...]
```

## Plugin Integration

### Hook

PostToolUse on Write/Edit. Triggers on `*.model.md` files. Runs v2 executor in authoring mode. Returns structured JSON feedback.

### Commands

| Command | Change from v0.1 |
|---------|-------------------|
| `/model:check` | Points at `.model.md`, uses v2 executor |
| `/model:onboard` | Converts `.md` → `.model.md`. Generates fixture blocks alongside validate blocks. LLM writes coherent test scenario per section. |
| `/model:paper` | Same, operates on `.model.md` |
| `/model:report` | Same, operates on `.model.md` |
| `/model:compile` | Generates paper + report + optional runner script |
| `/model:status` | Same, operates on `.model.md` |

### v0.1 coexistence

Both `.math.md` (v0.1) and `.model.md` (v2) can exist in the same project. Hooks and commands are keyed by extension. No migration tool.

## Codebase Changes

### Deleted

| File/Component | Reason |
|----------------|--------|
| `src/meta_compiler/expr.py` | Expression tree nodes — entire file |
| `src/meta_compiler/compiler/codegen.py` | Multi-file package generation |
| `_infer_units()` in `checks.py` | No tree to walk |
| `collect_refs()` in `expr.py` | Replaced by access log / source scanning |
| `_render_expr()` in `codegen.py` | No tree to render |
| `_capture_lambda()` in `registry.py` | No symbolic capture |
| `_Placeholder` class | No symbolic placeholders |

### Modified

| File | Changes |
|------|---------|
| `registry.py` | Stores `expr` as callable. Drops `_capture_lambda`. Adds access log. |
| `symbols.py` | Expression/Constraint/Objective symbols store callable instead of `expr_tree` |
| `proxy.py` | Rewritten: data-backed with access logging |
| `checks.py` | Phantoms/orphans from access log or source scanning. Unit check simplified to boundary comparison. |
| `units.py` | Unchanged |
| `compiler/parser.py` | Adds `FixtureBlock` type. Recognizes `.model.md`. |
| `compiler/executor.py` | Fixture loading, two-mode execution (structural vs numeric), constraint iteration |
| `compiler/paper.py` | Also strips `FixtureBlock` |
| `compiler/report.py` | Minor — no tree rendering |
| `compiler/__init__.py` | Same API, updated internals |
| `cli.py` | Same commands, `.model.md` |
| `__init__.py` | Same public API |

### New

| Component | Purpose |
|-----------|---------|
| `FixtureBlock` dataclass in `parser.py` | Parsed fixture block |
| Runner generator in `compiler/` | Emits a single Python script: `#!/usr/bin/env python3` + imports meta_compiler + calls `check_document(open(path).read(), strict=True)` + prints result. ~20 lines. |
| Fixture loader in `executor.py` | Executes fixture blocks, populates data store |

### Net effect

~400 lines of expression tree machinery replaced by ~150 lines of proxy rewrite + fixture loading + source scanning. The codebase shrinks.
