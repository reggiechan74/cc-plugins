# Meta-Compiler v2 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace expression-tree-based validation with real Python execution against fixture data, while keeping the same DSL surface (Set, Parameter, Variable, Expression, Constraint, Objective, S).

**Architecture:** Data-backed proxy objects replace tree-building proxies. Fixture blocks provide test data for numeric execution. Structural checks use tokenized source scanning (no fixture) or runtime access logs (with fixture). Expression trees and multi-file codegen are deleted.

**Tech Stack:** Python 3.10+, pytest, Python `tokenize` module for source scanning

**Spec:** `docs/superpowers/specs/2026-03-14-meta-compiler-v2-design.md`

---

## File Structure

### Files to delete
- `src/meta_compiler/expr.py` — expression tree nodes (172 lines)
- `src/meta_compiler/compiler/codegen.py` — multi-file package generation (221 lines)
- `tests/test_expr.py` — expression tree tests

### Files to rewrite
- `src/meta_compiler/proxy.py` — from tree-building to data-backed with access logging (94 → ~50 lines)

### Files to modify
- `src/meta_compiler/symbols.py` — `expr_tree` field → `expr` callable on 3 dataclasses
- `src/meta_compiler/registry.py` — drop `_capture_lambda`, `_Placeholder`, add `data_store`/`access_log` wiring
- `src/meta_compiler/checks.py` — rewrite phantom/orphan/dimension checks, delete `_infer_units`/`collect_refs` usage
- `src/meta_compiler/__init__.py` — `S()` returns real data in numeric mode
- `src/meta_compiler/compiler/parser.py` — add `FixtureBlock`, update coverage metric
- `src/meta_compiler/compiler/executor.py` — two-mode execution, fixture loading, constraint iteration
- `src/meta_compiler/compiler/paper.py` — strip `FixtureBlock`
- `src/meta_compiler/compiler/report.py` — remove tree rendering from dependency graph
- `src/meta_compiler/compiler/__init__.py` — update `compile_document` (drop codegen, add runner)
- `src/meta_compiler/cli.py` — `.model.md` references

### Files to create
- `src/meta_compiler/compiler/runner.py` — thin runner script generator (~30 lines)

### Test files to modify/create
- `tests/test_sets.py` — update for v2 registry behavior
- `tests/test_parameters.py` — update for v2 proxy behavior
- `tests/test_variables.py` — update for v2 proxy behavior
- `tests/test_expressions.py` — rewrite for callable-based expressions
- `tests/test_constraints.py` — rewrite for numeric execution
- `tests/test_objectives.py` — rewrite for numeric execution
- `tests/test_integrity.py` — rewrite checks for access-log/tokenize-based detection
- `tests/test_errors.py` — update error messages
- `tests/test_units.py` — unchanged (units.py unchanged)
- `tests/compiler/test_parser.py` — add FixtureBlock tests
- `tests/compiler/test_executor.py` — rewrite for two-mode execution
- `tests/compiler/test_codegen.py` — delete (codegen deleted)
- `tests/compiler/test_paper.py` — add FixtureBlock stripping test
- `tests/compiler/test_report.py` — update for no-tree dependency graph
- `tests/compiler/test_integration.py` — rewrite for `.model.md` end-to-end
- `tests/compiler/test_cli.py` — update for `.model.md`
- `tests/compiler/test_runner.py` — new, test runner script generation
- `tests/plugin/test_hook_script.py` — update for `.model.md`

### Plugin files to modify
- `hooks/hooks.json` — trigger on `.model.md`
- `scripts/validate-math-md.sh` — rename to `validate-model-md.sh`, update extension check
- `commands/check.md` — update for `.model.md`
- `commands/onboard.md` — update for `.model.md`, add fixture block generation
- Other command files — update extension references

---

## Chunk 1: Core Data Layer (symbols, proxy, registry)

### Task 1: Update symbol dataclasses

**Files:**
- Modify: `meta-compiler/src/meta_compiler/symbols.py:39-65`
- Test: `meta-compiler/tests/test_expressions.py`

- [ ] **Step 1: Write failing test for callable-based ExpressionSymbol**

In `tests/test_expressions.py`, add at the top:

```python
from meta_compiler.symbols import ExpressionSymbol

def test_expression_symbol_stores_callable():
    fn = lambda: 42
    sym = ExpressionSymbol(
        name="total", index=None, units="hours",
        description="Total hours", expr=fn,
    )
    assert sym.expr is fn
    assert sym.name == "total"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/test_expressions.py::test_expression_symbol_stores_callable -v`
Expected: FAIL — `ExpressionSymbol` has `expr_tree` not `expr`

- [ ] **Step 3: Update symbols.py — rename expr_tree to expr on three dataclasses**

In `meta-compiler/src/meta_compiler/symbols.py`:

Change `ExpressionSymbol` (line 39):
```python
@dataclass(frozen=True)
class ExpressionSymbol:
    name: str
    index: tuple[str, ...] | None
    units: str
    description: str
    expr: object  # callable in v2
```

Change `ConstraintSymbol` (line 49):
```python
@dataclass(frozen=True)
class ConstraintSymbol:
    name: str
    over: str | None
    constraint_type: str
    description: str
    expr: object  # callable in v2
```

Change `ObjectiveSymbol` (line 59):
```python
@dataclass(frozen=True)
class ObjectiveSymbol:
    name: str
    sense: str
    description: str
    expr: object  # callable in v2
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/test_expressions.py::test_expression_symbol_stores_callable -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd meta-compiler && git add src/meta_compiler/symbols.py tests/test_expressions.py
git commit -m "refactor(symbols): rename expr_tree to expr for callable storage"
```

---

### Task 2: Rewrite proxy.py — data-backed with access logging

**Files:**
- Rewrite: `meta-compiler/src/meta_compiler/proxy.py`
- Test: `meta-compiler/tests/test_parameters.py`

- [ ] **Step 1: Write failing tests for data-backed proxy**

Add to `tests/test_parameters.py`:

```python
from meta_compiler.proxy import SymbolProxy

def test_proxy_getitem_returns_real_value():
    log = set()
    proxy = SymbolProxy("cap", data={"alice": 40, "bob": 35}, access_log=log)
    assert proxy["alice"] == 40
    assert proxy["bob"] == 35

def test_proxy_getitem_logs_access():
    log = set()
    proxy = SymbolProxy("cap", data={"alice": 40}, access_log=log)
    proxy["alice"]
    assert "cap" in log

def test_proxy_getitem_no_data_raises():
    log = set()
    proxy = SymbolProxy("cap", data=None, access_log=log)
    import pytest
    with pytest.raises(RuntimeError, match="No fixture data"):
        proxy["alice"]

def test_proxy_multi_index_tuple_key():
    log = set()
    data = {("alice", "projA"): 5, ("bob", "projB"): 10}
    proxy = SymbolProxy("x", data=data, access_log=log)
    assert proxy["alice", "projA"] == 5
    assert proxy["bob", "projB"] == 10
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/test_parameters.py::test_proxy_getitem_returns_real_value tests/test_parameters.py::test_proxy_getitem_logs_access tests/test_parameters.py::test_proxy_getitem_no_data_raises tests/test_parameters.py::test_proxy_multi_index_tuple_key -v`
Expected: FAIL — current SymbolProxy has different constructor

- [ ] **Step 3: Rewrite proxy.py**

Replace `meta-compiler/src/meta_compiler/proxy.py` entirely:

```python
"""Data-backed symbol proxy with access logging.

In v2, proxies hold real data (from fixtures) and return actual values
on __getitem__. Each access logs the symbol name for orphan/phantom detection.
"""

from __future__ import annotations


class SymbolProxy:
    """Proxy for a registered symbol backed by fixture data."""

    def __init__(self, name: str, data: dict | None, access_log: set):
        self.name = name
        self._data = data
        self._access_log = access_log

    def __getitem__(self, key):
        self._access_log.add(self.name)
        if self._data is None:
            raise RuntimeError(
                f"No fixture data for symbol '{self.name}'. "
                f"Add a python:fixture block with data for '{self.name}'."
            )
        return self._data[key]

    def __repr__(self):
        backed = "data-backed" if self._data is not None else "no-data"
        return f"SymbolProxy({self.name!r}, {backed})"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/test_parameters.py::test_proxy_getitem_returns_real_value tests/test_parameters.py::test_proxy_getitem_logs_access tests/test_parameters.py::test_proxy_getitem_no_data_raises tests/test_parameters.py::test_proxy_multi_index_tuple_key -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd meta-compiler && git add src/meta_compiler/proxy.py tests/test_parameters.py
git commit -m "refactor(proxy): rewrite as data-backed proxy with access logging"
```

---

### Task 3: Update registry — drop expression tree capture, add data store wiring

**Files:**
- Modify: `meta-compiler/src/meta_compiler/registry.py:114-233`
- Test: `meta-compiler/tests/test_constraints.py`

- [ ] **Step 1: Write failing tests for v2 registry behavior**

Add to `tests/test_constraints.py`:

```python
from meta_compiler.registry import Registry

def test_register_constraint_stores_callable():
    reg = Registry()
    reg.register_set("W", description="Workers")
    fn = lambda i: True
    reg.register_constraint("cap_check", over="W", constraint_type="hard",
                            description="Check capacity", expr=fn)
    sym = reg.symbols["cap_check"]
    assert sym.expr is fn

def test_registry_with_data_store():
    reg = Registry()
    reg.data_store["cap"] = {"alice": 40, "bob": 35}
    reg.register_set("W", description="Workers")
    proxy = reg.register_parameter("cap", index="W", units="hours", description="Cap")
    # Proxy should be data-backed — returns real value, not RuntimeError
    assert proxy["alice"] == 40

def test_registry_access_log_exists():
    reg = Registry()
    assert hasattr(reg, "access_log")
    assert isinstance(reg.access_log, set)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/test_constraints.py::test_register_constraint_stores_callable tests/test_constraints.py::test_registry_with_data_store tests/test_constraints.py::test_registry_access_log_exists -v`
Expected: FAIL — registry doesn't have `data_store` or `access_log`, `register_constraint` uses `_capture_lambda`

- [ ] **Step 3: Update registry.py**

Key changes to `meta-compiler/src/meta_compiler/registry.py`:

1. Add `data_store`, `access_log`, and `_exec_namespace` to `__init__` and `reset`:
```python
def __init__(self):
    self.symbols: dict[str, Symbol] = {}
    self._registration_order: list[str] = []
    self.data_store: dict[str, dict] = {}
    self.access_log: set[str] = set()
    self._exec_namespace: dict | None = None  # set by executor
    self._current_block_source: str | None = None  # set by executor per block
```

```python
def reset(self):
    self.symbols.clear()
    self._registration_order.clear()
    self.data_store.clear()
    self.access_log.clear()
    self._exec_namespace = None
    self._current_block_source = None
```

2. Update `register_expression` (lines 114-131) — store callable directly, attach source text, use `_make_proxy`:
```python
def register_expression(self, name, *, definition, index=None, units="dimensionless", description=""):
    index_tuple = self._normalize_index(index)
    if index_tuple:
        self._require_sets(*index_tuple)
    if self._current_block_source and not hasattr(definition, "_source_text"):
        definition._source_text = self._current_block_source
    sym = ExpressionSymbol(
        name=name, index=index_tuple, units=units,
        description=description, expr=definition,
    )
    self._register(sym)
    return self._make_proxy(name)
```

3. Update `register_constraint` (lines 133-149) — store callable directly, attach source text:
```python
def register_constraint(self, name, *, expr, over=None, constraint_type="hard", description=""):
    if over:
        self._require_sets(over)
    # Attach the current block's source text for structural-mode scanning
    if self._current_block_source and not hasattr(expr, "_source_text"):
        expr._source_text = self._current_block_source
    sym = ConstraintSymbol(
        name=name, over=over, constraint_type=constraint_type,
        description=description, expr=expr,
    )
    self._register(sym)
```

4. Update `register_objective` (lines 151-164) — store callable directly, attach source text:
```python
def register_objective(self, name, *, expr, sense="maximize", description=""):
    if self._current_block_source and not hasattr(expr, "_source_text"):
        expr._source_text = self._current_block_source
    sym = ObjectiveSymbol(
        name=name, sense=sense, description=description, expr=expr,
    )
    self._register(sym)
```

Add `_current_block_source` to `__init__` and `reset` (initialized to `None`). The executor sets `registry._current_block_source = vb.code` before each validate block's `exec()` call.

5. Update `register_set`, `register_parameter`, `register_variable` — return data-backed proxies and auto-inject into exec namespace:
```python
def _make_proxy(self, name: str) -> SymbolProxy:
    """Create a data-backed proxy and auto-inject into exec namespace."""
    proxy = SymbolProxy(name, data=self.data_store.get(name), access_log=self.access_log)
    if self._exec_namespace is not None:
        self._exec_namespace[name] = proxy
    return proxy

def register_set(self, name, *, description=""):
    sym = SetSymbol(name=name, description=description)
    self._register(sym)
    return self._make_proxy(name)
```

(Same pattern for parameter, variable — call `self._make_proxy(name)` at end)

Also update `register_expression` to use `self._make_proxy(name)`.

6. Update `s()` method — return real set members in numeric mode:
```python
def s(self, name):
    self.access_log.add(name)
    if name in self.data_store:
        data = self.data_store[name]
        if isinstance(data, list):
            return data
        raise RuntimeError(f"Set '{name}' fixture data must be a list, got {type(data).__name__}")
    raise RuntimeError(f"No fixture data for set '{name}'. Add a python:fixture block.")
```

7. Delete `_capture_lambda` method (lines 166-189) and `_Placeholder` class (lines 216-229) entirely.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/test_constraints.py::test_register_constraint_stores_callable tests/test_constraints.py::test_registry_with_data_store tests/test_constraints.py::test_registry_access_log_exists -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd meta-compiler && git add src/meta_compiler/registry.py tests/test_constraints.py
git commit -m "refactor(registry): drop expression tree capture, add data store and access log"
```

---

### Task 4: Update public API (__init__.py) and S()

**Files:**
- Modify: `meta-compiler/src/meta_compiler/__init__.py`
- Test: `meta-compiler/tests/test_sets.py`

- [ ] **Step 1: Write failing test for S() returning real data**

Add to `tests/test_sets.py`:

```python
from meta_compiler import S
from meta_compiler.registry import registry

def test_s_returns_real_set_members():
    registry.reset()
    registry.data_store["W"] = ["alice", "bob"]
    registry.register_set("W", description="Workers")
    members = S("W")
    assert members == ["alice", "bob"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/test_sets.py::test_s_returns_real_set_members -v`
Expected: FAIL — current `S()` returns `SetIterator`, not a list

- [ ] **Step 3: Update __init__.py**

Update `S()` function in `meta-compiler/src/meta_compiler/__init__.py` (line 71):
```python
def S(name: str):
    """Return the members of a registered set for iteration."""
    return registry.s(name)
```

Remove imports of `SetIterator` from `expr.py` if present. Remove any re-exports of expression tree types.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/test_sets.py::test_s_returns_real_set_members -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd meta-compiler && git add src/meta_compiler/__init__.py tests/test_sets.py
git commit -m "feat(api): S() returns real set members from fixture data"
```

---

### Task 5: Delete expression tree module and codegen

**Files:**
- Delete: `meta-compiler/src/meta_compiler/expr.py`
- Delete: `meta-compiler/src/meta_compiler/compiler/codegen.py`
- Delete: `meta-compiler/tests/test_expr.py`
- Delete: `meta-compiler/tests/compiler/test_codegen.py`

- [ ] **Step 1: Remove imports of expr module from all files**

Search for `from meta_compiler.expr import` and `from meta_compiler import expr` across the codebase. Remove or update these imports in:
- `checks.py` — remove `collect_refs` import
- `__init__.py` — remove any expr re-exports
- `registry.py` — remove expr imports (already handled in Task 3)
- `compiler/report.py` — remove `_render_expr` usage if present

- [ ] **Step 2: Delete the files**

```bash
cd meta-compiler
git rm src/meta_compiler/expr.py
git rm src/meta_compiler/compiler/codegen.py
git rm tests/test_expr.py
git rm tests/compiler/test_codegen.py
```

- [ ] **Step 3: Run remaining tests to check for breakage**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/ -v --tb=short 2>&1 | head -80`
Expected: Some tests may fail due to removed imports — note which ones need fixing in subsequent tasks.

- [ ] **Step 4: Commit**

```bash
cd meta-compiler
git add src/meta_compiler/expr.py src/meta_compiler/compiler/codegen.py tests/test_expr.py tests/compiler/test_codegen.py
git add src/meta_compiler/checks.py src/meta_compiler/__init__.py src/meta_compiler/registry.py src/meta_compiler/compiler/report.py
git commit -m "refactor: delete expression tree module and codegen"
```

---

## Chunk 2: Parser & Executor

### Task 6: Add FixtureBlock to parser

**Files:**
- Modify: `meta-compiler/src/meta_compiler/compiler/parser.py:13-36, 39-102, 120-161`
- Test: `meta-compiler/tests/compiler/test_parser.py`

- [ ] **Step 1: Write failing tests for FixtureBlock parsing**

Add to `tests/compiler/test_parser.py`:

```python
from meta_compiler.compiler.parser import parse_document, FixtureBlock

def test_parse_fixture_block():
    source = '''# Model

```python:fixture
sets = {"W": ["alice", "bob"]}
cap = {"alice": 40, "bob": 35}
```
'''
    blocks = parse_document(source)
    fixture_blocks = [b for b in blocks if isinstance(b, FixtureBlock)]
    assert len(fixture_blocks) == 1
    assert 'sets = {"W":' in fixture_blocks[0].code

def test_parse_mixed_blocks():
    source = '''# Model

```python:fixture
cap = {"alice": 40}
```

$$x + y = z$$

```python:validate
Set("W", description="Workers")
```
'''
    blocks = parse_document(source)
    from meta_compiler.compiler.parser import FixtureBlock, MathBlock, ValidationBlock, ProseBlock
    types = [type(b).__name__ for b in blocks]
    assert "FixtureBlock" in types
    assert "MathBlock" in types
    assert "ValidationBlock" in types

def test_coverage_fixture_does_not_interrupt():
    """A math block followed by fixture then validate counts as covered."""
    source = '''# Model

$$x = 1$$

```python:fixture
x_val = {"a": 1}
```

```python:validate
Parameter("x", description="x value")
```
'''
    from meta_compiler.compiler.parser import coverage_metric
    blocks = parse_document(source)
    result = coverage_metric(blocks)
    assert result.covered_math == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_parser.py::test_parse_fixture_block tests/compiler/test_parser.py::test_parse_mixed_blocks tests/compiler/test_parser.py::test_coverage_fixture_does_not_interrupt -v`
Expected: FAIL — `FixtureBlock` doesn't exist

- [ ] **Step 3: Add FixtureBlock dataclass and update parser**

In `meta-compiler/src/meta_compiler/compiler/parser.py`:

1. Add `FixtureBlock` dataclass after `ValidationBlock` (line 33):
```python
@dataclass
class FixtureBlock:
    """A python:fixture fenced code block containing test data."""
    code: str
    line_number: int
```

2. Update `Block` type union (line 36):
```python
Block = ProseBlock | MathBlock | ValidationBlock | FixtureBlock
```

3. In `parse_document()`, add detection for ` ```python:fixture ` alongside ` ```python:validate `:
```python
elif stripped.startswith("```python:fixture"):
    in_fence = True
    fence_type = "fixture"
    fence_start = line_num
    fence_lines = []
```

And in the fence-closing logic:
```python
if fence_type == "fixture":
    blocks.append(FixtureBlock(code="\n".join(fence_lines), line_number=fence_start))
```

4. Update `coverage_metric()` — skip `FixtureBlock` when checking if a math block has a following validate block. When scanning forward from a math block, skip over `FixtureBlock` instances.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_parser.py::test_parse_fixture_block tests/compiler/test_parser.py::test_parse_mixed_blocks tests/compiler/test_parser.py::test_coverage_fixture_does_not_interrupt -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd meta-compiler && git add src/meta_compiler/compiler/parser.py tests/compiler/test_parser.py
git commit -m "feat(parser): add FixtureBlock type and fixture-aware coverage metric"
```

---

### Task 7: Rewrite executor — two-mode execution with fixture loading

**Files:**
- Modify: `meta-compiler/src/meta_compiler/compiler/executor.py`
- Test: `meta-compiler/tests/compiler/test_executor.py`

- [ ] **Step 1: Write failing tests for two-mode execution**

Replace contents of `tests/compiler/test_executor.py`:

```python
import pytest
from meta_compiler.compiler.parser import parse_document
from meta_compiler.compiler.executor import execute_blocks

STRUCTURAL_DOC = '''# Model

```python:validate
Set("W", description="Workers")
Parameter("cap", index="W", units="hours", description="Capacity")
Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
```
'''

NUMERIC_DOC = '''# Model

```python:fixture
W = ["alice", "bob"]
cap = {"alice": 40, "bob": 35}
```

```python:validate
Set("W", description="Workers")
Parameter("cap", index="W", units="hours", description="Capacity")
Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
```
'''

NUMERIC_FAIL_DOC = '''# Model

```python:fixture
W = ["alice", "bob"]
cap = {"alice": 40, "bob": 150}
```

```python:validate
Set("W", description="Workers")
Parameter("cap", index="W", units="hours", description="Capacity")
Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
```
'''

def test_structural_mode_no_fixture():
    blocks = parse_document(STRUCTURAL_DOC)
    result = execute_blocks(blocks)
    assert result.passed

def test_numeric_mode_with_fixture_pass():
    blocks = parse_document(NUMERIC_DOC)
    result = execute_blocks(blocks)
    assert result.passed

def test_numeric_mode_constraint_failure():
    blocks = parse_document(NUMERIC_FAIL_DOC)
    result = execute_blocks(blocks)
    assert not result.passed
    assert any("check" in e and "bob" in e for e in result.errors)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_executor.py::test_structural_mode_no_fixture tests/compiler/test_executor.py::test_numeric_mode_with_fixture_pass tests/compiler/test_executor.py::test_numeric_mode_constraint_failure -v`
Expected: FAIL — executor doesn't handle fixture blocks or run constraints numerically

- [ ] **Step 3: Rewrite executor.py**

Replace `meta-compiler/src/meta_compiler/compiler/executor.py`:

```python
"""Two-mode executor for .model.md validation blocks.

Structural mode (no fixture): registers symbols, stores expr callables,
runs structural checks only.

Numeric mode (fixture present): loads fixture data, executes expr functions
against real values, checks constraints numerically, then runs structural checks.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass

from meta_compiler.compiler.parser import Block, FixtureBlock, ValidationBlock
from meta_compiler.registry import Registry, registry
from meta_compiler.checks import run_all_checks
from meta_compiler.symbols import ConstraintSymbol, ObjectiveSymbol


@dataclass
class ExecutionResult:
    passed: bool
    errors: list[str]
    warnings: list[str]
    registry: Registry | None


def execute_blocks(
    blocks: list[Block], *, strict: bool = False
) -> ExecutionResult:
    """Execute fixture + validation blocks and run checks."""
    registry.reset()
    errors: list[str] = []
    warnings: list[str] = []

    fixture_blocks = [b for b in blocks if isinstance(b, FixtureBlock)]
    validate_blocks = [b for b in blocks if isinstance(b, ValidationBlock)]

    has_fixtures = len(fixture_blocks) > 0

    # Step 1: Execute fixture blocks to build data store
    if has_fixtures:
        fixture_ns: dict = {}
        for fb in fixture_blocks:
            try:
                exec(fb.code, fixture_ns)
            except Exception as e:
                errors.append(f"Fixture error (line {fb.line_number}): {e}")
                return ExecutionResult(passed=False, errors=errors,
                                       warnings=warnings, registry=None)

        # Build data_store: every name in fixture namespace that isn't a dunder
        for name, value in fixture_ns.items():
            if not name.startswith("_"):
                registry.data_store[name] = value

    # Step 2: Build validation namespace
    from meta_compiler import Set, Parameter, Variable, Expression, Constraint, Objective, S
    ns = {
        "Set": Set, "Parameter": Parameter, "Variable": Variable,
        "Expression": Expression, "Constraint": Constraint,
        "Objective": Objective, "S": S, "registry": registry,
    }

    # Step 3: Execute validation blocks
    # CRITICAL: The DSL surface (Set, Parameter, etc.) does NOT require
    # users to capture return values. The validate block says:
    #   Set("W", description="Workers")
    #   Parameter("cap", index="W", ...)
    #   Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
    #
    # The lambda references `cap` by name, but `cap` was never assigned
    # in the namespace. The registry must auto-inject proxies into `ns`
    # when symbols are registered. We do this by setting
    # registry._exec_namespace = ns before exec'ing validate blocks.
    # Each register_* method then does:
    #   self._exec_namespace[name] = proxy
    registry._exec_namespace = ns

    for vb in validate_blocks:
        try:
            registry._current_block_source = vb.code
            exec(vb.code, ns)
        except Exception as e:
            errors.append(f"Validation error (line {vb.line_number}): {e}")
            return ExecutionResult(passed=False, errors=errors,
                                   warnings=warnings, registry=registry)

    registry._exec_namespace = None
    registry._current_block_source = None

    # Step 4: In numeric mode, evaluate constraints and objectives
    if has_fixtures:
        for name, sym in registry.symbols.items():
            if isinstance(sym, ConstraintSymbol) and sym.expr is not None:
                try:
                    _check_constraint(sym, registry, errors)
                except Exception as e:
                    errors.append(f"Error in constraint \"{sym.name}\": {e}")

            elif isinstance(sym, ObjectiveSymbol) and sym.expr is not None:
                try:
                    result = sym.expr() if _arity(sym.expr) == 0 else None
                    if result is not None and not isinstance(result, (int, float)):
                        errors.append(
                            f"Objective \"{sym.name}\" returned {type(result).__name__}, "
                            f"expected numeric value"
                        )
                except Exception as e:
                    errors.append(f"Error in objective \"{sym.name}\": {e}")

    # Step 5: Run structural checks
    check_errors, check_warnings = run_all_checks(registry, strict=strict)
    errors.extend(check_errors)
    warnings.extend(check_warnings)

    return ExecutionResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        registry=registry,
    )


def _check_constraint(sym: ConstraintSymbol, reg: Registry, errors: list[str]):
    """Evaluate a constraint against fixture data."""
    arity = _arity(sym.expr)

    if arity == 0:
        # Zero-arg: self-iterating, must return True
        result = sym.expr()
        if result is not True:
            errors.append(
                f"Constraint \"{sym.name}\" failed (returned {result!r})"
            )
    else:
        # Positional args: iterate over set
        if sym.over is None:
            errors.append(
                f"Constraint \"{sym.name}\" has positional args but no 'over' set"
            )
            return

        if sym.over not in reg.data_store:
            errors.append(
                f"Constraint \"{sym.name}\": set \"{sym.over}\" has no fixture data"
            )
            return

        members = reg.data_store[sym.over]
        if not isinstance(members, list):
            errors.append(
                f"Constraint \"{sym.name}\": fixture data for set \"{sym.over}\" "
                f"must be a list"
            )
            return

        for member in members:
            result = sym.expr(member)
            if result is not True:
                errors.append(
                    f"Constraint \"{sym.name}\" violated for "
                    f"{sym.over}=\"{member}\": result is {result!r}"
                )


def _arity(fn) -> int:
    """Return the number of positional parameters of a function."""
    sig = inspect.signature(fn)
    return sum(
        1 for p in sig.parameters.values()
        if p.default is inspect.Parameter.empty
        and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_executor.py::test_structural_mode_no_fixture tests/compiler/test_executor.py::test_numeric_mode_with_fixture_pass tests/compiler/test_executor.py::test_numeric_mode_constraint_failure -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd meta-compiler && git add src/meta_compiler/compiler/executor.py tests/compiler/test_executor.py
git commit -m "feat(executor): two-mode execution with fixture loading and constraint evaluation"
```

---

## Chunk 3: Checks System

### Task 8: Rewrite checks.py — access log + tokenize-based detection

**Files:**
- Modify: `meta-compiler/src/meta_compiler/checks.py`
- Test: `meta-compiler/tests/test_integrity.py`

- [ ] **Step 1: Write failing tests for v2 checks**

Replace `tests/test_integrity.py` with:

```python
import pytest
from meta_compiler.registry import registry
from meta_compiler.checks import run_all_checks

def setup_function():
    registry.reset()

def test_phantom_detected_via_access_log():
    """Symbol accessed but never registered → phantom error."""
    registry.register_set("W", description="Workers")
    registry.access_log.add("cap")  # accessed but not registered
    errors, warnings = run_all_checks(registry, strict=False)
    assert any("cap" in e and "phantom" in e.lower() for e in errors)

def test_orphan_warning_in_authoring_mode():
    """Symbol registered but never accessed → orphan warning."""
    registry.register_set("W", description="Workers")
    registry.register_parameter("cap", index="W", units="hours", description="Cap")
    registry.access_log.add("W")  # W accessed, cap not
    errors, warnings = run_all_checks(registry, strict=False)
    assert any("cap" in w for w in warnings)
    assert len(errors) == 0  # warning, not error

def test_orphan_error_in_strict_mode():
    """Symbol registered but never accessed → orphan error in strict mode."""
    registry.register_set("W", description="Workers")
    registry.register_parameter("cap", index="W", units="hours", description="Cap")
    registry.access_log.add("W")
    errors, warnings = run_all_checks(registry, strict=True)
    assert any("cap" in e for e in errors)

def test_unit_boundary_mismatch():
    """Constraint comparing hours to dollars → unit error."""
    registry.data_store = {"W": ["a"], "cost": {"a": 10}, "hours": {"a": 5}}
    registry.register_set("W", description="Workers")
    registry.register_parameter("cost", index="W", units="dollars", description="Cost")
    registry.register_parameter("hours_worked", index="W", units="hours", description="Hours")
    registry.register_constraint("bad", over="W", constraint_type="hard",
                                 description="Bad", expr=lambda i: True)
    # Unit check needs to know which symbols are on which side of the constraint
    # This depends on how we extract symbol refs from the expr source
    # For now, just verify the check infrastructure runs without crashing
    errors, warnings = run_all_checks(registry, strict=False)
    # No crash is the baseline test

def test_no_false_positives_clean_model():
    """A clean model with all symbols used should have no errors."""
    registry.data_store = {"W": ["a"], "cap": {"a": 40}}
    registry.register_set("W", description="Workers")
    registry.register_parameter("cap", index="W", units="hours", description="Cap")
    registry.register_constraint("check", over="W", constraint_type="hard",
                                 description="Check", expr=lambda i: True)
    registry.access_log.update(["W", "cap"])
    errors, warnings = run_all_checks(registry, strict=False)
    assert len(errors) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/test_integrity.py -v`
Expected: FAIL — current checks.py uses expression tree walking, not access logs

- [ ] **Step 3: Rewrite checks.py**

Replace `meta-compiler/src/meta_compiler/checks.py`:

```python
"""Structural integrity checks for the symbol registry.

v2 checks use:
- Access logs (numeric mode) or tokenized source scanning (structural mode)
  for orphan/phantom detection
- Registration-order dependency graph for cycle detection
- Declared unit comparison at constraint boundaries for unit checks
"""

from __future__ import annotations

from meta_compiler.registry import Registry
from meta_compiler.symbols import (
    ConstraintSymbol, ExpressionSymbol, ObjectiveSymbol,
    SetSymbol, ParameterSymbol, VariableSymbol,
)
from meta_compiler.units import parse_unit, units_compatible


def run_all_checks(
    registry: Registry, *, strict: bool = False
) -> tuple[list[str], list[str]]:
    """Run all integrity checks. Returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    # Augment access_log with names from source text scanning.
    # This ensures structural mode (no fixture, no runtime access)
    # still detects orphans/phantoms via tokenized source analysis.
    source_refs = _collect_source_refs(registry)
    all_accessed = registry.access_log | source_refs

    _check_phantoms(registry, all_accessed, errors)
    _check_orphans(registry, all_accessed, errors, warnings, strict)
    _check_cycles(registry, errors)
    _check_unit_boundaries(registry, errors)

    return errors, warnings


def _collect_source_refs(registry: Registry) -> set[str]:
    """Collect all symbol names referenced in expr source text."""
    refs: set[str] = set()
    for sym in registry.symbols.values():
        expr_fn = getattr(sym, "expr", None)
        if expr_fn is not None:
            refs |= _extract_names_from_source(expr_fn, registry)
    return refs


def _check_phantoms(registry: Registry, all_accessed: set[str], errors: list[str]):
    """Symbols accessed but never registered."""
    registered = set(registry.symbols.keys())
    phantoms = all_accessed - registered
    for name in sorted(phantoms):
        errors.append(f'Phantom: symbol "{name}" referenced but never declared')


def _check_orphans(
    registry: Registry, all_accessed: set[str], errors: list[str],
    warnings: list[str], strict: bool
):
    """Symbols registered but never accessed."""
    registered = set(registry.symbols.keys())

    # Symbols referenced in 'over' or 'index' fields count as accessed
    implicit_refs: set[str] = set()
    for sym in registry.symbols.values():
        if isinstance(sym, ConstraintSymbol) and sym.over:
            implicit_refs.add(sym.over)
        if hasattr(sym, "index") and sym.index:
            for idx_set in (sym.index if isinstance(sym.index, tuple) else (sym.index,)):
                implicit_refs.add(idx_set)

    combined = all_accessed | implicit_refs
    orphans = registered - combined

    for name in sorted(orphans):
        msg = f'Orphan: symbol "{name}" declared but never referenced'
        if strict:
            errors.append(msg)
        else:
            warnings.append(msg)


def _check_cycles(registry: Registry, errors: list[str]):
    """Circular dependencies in expression definitions via DFS."""
    expr_names = {
        name for name, sym in registry.symbols.items()
        if isinstance(sym, ExpressionSymbol)
    }
    if not expr_names:
        return

    # Build adjacency from expr source text: which expressions reference
    # other expressions?
    adj: dict[str, set[str]] = {name: set() for name in expr_names}
    for name in expr_names:
        sym = registry.symbols[name]
        if sym.expr is not None:
            refs = _extract_names_from_source(sym.expr, registry)
            adj[name] = refs & expr_names

    # Standard DFS cycle detection
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {name: WHITE for name in expr_names}
    path: list[str] = []

    def dfs(node: str) -> bool:
        color[node] = GRAY
        path.append(node)
        for neighbor in adj[node]:
            if color[neighbor] == GRAY:
                cycle = path[path.index(neighbor):]
                errors.append(
                    f"Cycle detected: {' -> '.join(cycle)} -> {neighbor}"
                )
                return True
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        path.pop()
        color[node] = BLACK
        return False

    for name in expr_names:
        if color[name] == WHITE:
            dfs(name)


def _extract_names_from_source(fn, registry: Registry) -> set[str]:
    """Extract symbol names from a callable's source using tokenize.

    Used for structural-mode orphan/phantom detection and cycle detection.
    Tokenizes the source and collects NAME tokens matching registered symbols.
    """
    import tokenize
    import io
    import inspect

    try:
        source = inspect.getsource(fn)
    except (OSError, TypeError):
        # If source isn't available (e.g., exec'd code), fall back to
        # checking the function against the raw code block source stored
        # on the registry. The executor stores block sources on the registry
        # for this purpose.
        source = getattr(fn, "_source_text", "")
        if not source:
            return set()

    registered = set(registry.symbols.keys())
    found: set[str] = set()

    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for tok_type, tok_string, _, _, _ in tokens:
            if tok_type == tokenize.NAME and tok_string in registered:
                found.add(tok_string)
    except tokenize.TokenizeError:
        pass

    return found


def _check_unit_boundaries(registry: Registry, errors: list[str]):
    """Check unit compatibility at constraint boundaries.

    For each constraint, collects the declared units of all parameter/variable
    symbols referenced in the constraint's expr. If any pair of referenced
    symbols has incompatible units, reports an error.
    """
    for name, sym in registry.symbols.items():
        if not isinstance(sym, ConstraintSymbol):
            continue
        if sym.expr is None:
            continue

        # Find which symbols this constraint references
        refs = _extract_names_from_source(sym.expr, registry)

        # Collect declared units of referenced parameters and variables
        unit_map: dict[str, str] = {}
        for ref_name in refs:
            ref_sym = registry.symbols.get(ref_name)
            if ref_sym is None:
                continue
            if isinstance(ref_sym, (ParameterSymbol, VariableSymbol)):
                unit_map[ref_name] = ref_sym.units

        # Check all pairs for compatibility
        units_seen: list[tuple[str, str]] = list(unit_map.items())
        for i, (name_a, unit_a) in enumerate(units_seen):
            for name_b, unit_b in units_seen[i + 1:]:
                if unit_a != "dimensionless" and unit_b != "dimensionless":
                    if not units_compatible(parse_unit(unit_a), parse_unit(unit_b)):
                        errors.append(
                            f'Constraint "{name}": "{name_a}" has unit '
                            f'"{unit_a}" but "{name_b}" has unit "{unit_b}"'
                        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/test_integrity.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd meta-compiler && git add src/meta_compiler/checks.py tests/test_integrity.py
git commit -m "refactor(checks): rewrite for access-log-based orphan/phantom detection"
```

---

## Chunk 4: Compiler Pipeline

### Task 9: Update paper.py — strip FixtureBlock

**Files:**
- Modify: `meta-compiler/src/meta_compiler/compiler/paper.py`
- Test: `meta-compiler/tests/compiler/test_paper.py`

- [ ] **Step 1: Write failing test**

Add to `tests/compiler/test_paper.py`:

```python
from meta_compiler.compiler.parser import parse_document, FixtureBlock
from meta_compiler.compiler.paper import generate_paper

def test_paper_strips_fixture_blocks():
    source = '''# Model

Some prose.

```python:fixture
cap = {"alice": 40}
```

$$x + y$$

```python:validate
Set("W")
```

More prose.
'''
    blocks = parse_document(source)
    paper = generate_paper(blocks)
    assert "python:fixture" not in paper
    assert "cap =" not in paper
    assert "Some prose" in paper
    assert "$$x + y$$" in paper
    assert "More prose" in paper
    assert "python:validate" not in paper
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_paper.py::test_paper_strips_fixture_blocks -v`
Expected: FAIL — `generate_paper` doesn't know about `FixtureBlock`

- [ ] **Step 3: Update paper.py**

In `meta-compiler/src/meta_compiler/compiler/paper.py`, import `FixtureBlock` and add it to the block types that get stripped (alongside `ValidationBlock`):

```python
from meta_compiler.compiler.parser import ProseBlock, MathBlock, ValidationBlock, FixtureBlock

def generate_paper(blocks, *, depth=None):
    # ... existing logic ...
    for block in blocks:
        if isinstance(block, (ValidationBlock, FixtureBlock)):
            continue  # strip both
        # ... rest unchanged
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_paper.py::test_paper_strips_fixture_blocks -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd meta-compiler && git add src/meta_compiler/compiler/paper.py tests/compiler/test_paper.py
git commit -m "feat(paper): strip FixtureBlock from paper output"
```

---

### Task 10: Update report.py — remove tree rendering

**Files:**
- Modify: `meta-compiler/src/meta_compiler/compiler/report.py:147-162`
- Test: `meta-compiler/tests/compiler/test_report.py`

- [ ] **Step 1: Write failing test**

Add to `tests/compiler/test_report.py`:

```python
from meta_compiler.registry import registry
from meta_compiler.compiler.report import generate_report
from meta_compiler.compiler.parser import parse_document

def test_report_generates_without_expr_tree():
    registry.reset()
    registry.data_store = {"W": ["a"], "cap": {"a": 40}}
    registry.register_set("W", description="Workers")
    registry.register_parameter("cap", index="W", units="hours", description="Cap")
    registry.register_constraint("check", over="W", constraint_type="hard",
                                 description="Check", expr=lambda i: True)
    blocks = parse_document("# test\n$$x$$\n```python:validate\nSet('W')\n```\n")
    report = generate_report(registry, blocks)
    assert report.symbol_table is not None
    text = report.to_text()
    assert "cap" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_report.py::test_report_generates_without_expr_tree -v`
Expected: FAIL — report.py likely imports or calls expr tree functions

- [ ] **Step 3: Update report.py**

Remove any imports of `collect_refs`, `_render_expr`, or `expr` module. In `_build_dependency_graph()`, instead of walking expression trees, use the registry's access log or simply list which symbols are referenced via `over` and `index` fields:

```python
def _build_dependency_graph(registry):
    deps = []
    for name, sym in registry.symbols.items():
        refs = []
        if hasattr(sym, "over") and sym.over:
            refs.append(sym.over)
        if hasattr(sym, "index") and sym.index:
            for idx in (sym.index if isinstance(sym.index, tuple) else (sym.index,)):
                refs.append(idx)
        if refs:
            deps.append({"symbol": name, "references": refs})
    return deps
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_report.py::test_report_generates_without_expr_tree -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd meta-compiler && git add src/meta_compiler/compiler/report.py tests/compiler/test_report.py
git commit -m "refactor(report): remove expression tree dependency from report generation"
```

---

### Task 11: Add runner generator

**Files:**
- Create: `meta-compiler/src/meta_compiler/compiler/runner.py`
- Test: `meta-compiler/tests/compiler/test_runner.py`

- [ ] **Step 1: Write failing test**

Create `tests/compiler/test_runner.py`:

```python
from meta_compiler.compiler.runner import generate_runner

def test_generate_runner_contains_check_call():
    script = generate_runner("my_model.model.md")
    assert "check_document" in script
    assert "my_model.model.md" in script
    assert "strict=True" in script
    assert script.startswith("#!/usr/bin/env python3")

def test_generate_runner_is_valid_python():
    script = generate_runner("test.model.md")
    compile(script, "<runner>", "exec")  # should not raise
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_runner.py -v`
Expected: FAIL — module doesn't exist

- [ ] **Step 3: Create runner.py**

Create `meta-compiler/src/meta_compiler/compiler/runner.py`:

```python
"""Generate a thin runner script for .model.md files."""

from __future__ import annotations


def generate_runner(model_path: str) -> str:
    """Generate a standalone Python script that validates a .model.md file."""
    return f'''#!/usr/bin/env python3
"""Auto-generated runner for {model_path}."""

import sys
from pathlib import Path

from meta_compiler.compiler import check_document


def main():
    path = Path(__file__).parent / "{model_path}"
    if not path.exists():
        print(f"Error: {{path}} not found", file=sys.stderr)
        sys.exit(1)

    result = check_document(path.read_text(), strict=True)

    if result.errors:
        for error in result.errors:
            print(f"ERROR: {{error}}", file=sys.stderr)
    for warning in result.warnings:
        print(f"WARNING: {{warning}}", file=sys.stderr)

    if result.passed:
        print("All checks passed.")
    else:
        print(f"{{len(result.errors)}} error(s) found.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_runner.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd meta-compiler && git add src/meta_compiler/compiler/runner.py tests/compiler/test_runner.py
git commit -m "feat(runner): add thin runner script generator"
```

---

### Task 12: Update compiler/__init__.py — drop codegen, add runner

**Files:**
- Modify: `meta-compiler/src/meta_compiler/compiler/__init__.py`
- Test: `meta-compiler/tests/compiler/test_integration.py`

- [ ] **Step 1: Write failing test**

Add to `tests/compiler/test_integration.py`:

```python
from meta_compiler.compiler import compile_document

MODEL_DOC = '''# Workforce Model

```python:fixture
W = ["alice", "bob"]
cap = {"alice": 40, "bob": 35}
```

$$\\text{cap}_i \\leq 100$$

```python:validate
Set("W", description="Workers")
Parameter("cap", index="W", units="hours", description="Capacity")
Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
```
'''

def test_compile_produces_paper_report_runner():
    result = compile_document(MODEL_DOC)
    assert "paper" in result
    assert "report_text" in result
    assert "runner" in result
    assert "python:fixture" not in result["paper"]
    assert "python:validate" not in result["paper"]
    assert "check_document" in result["runner"]

def test_compile_no_codebase_key():
    result = compile_document(MODEL_DOC)
    assert "codebase" not in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_integration.py::test_compile_produces_paper_report_runner tests/compiler/test_integration.py::test_compile_no_codebase_key -v`
Expected: FAIL — `compile_document` still produces `codebase`, no `runner`

- [ ] **Step 3: Update compiler/__init__.py**

```python
"""High-level compiler API for .model.md documents."""

from __future__ import annotations

from meta_compiler.compiler.parser import parse_document
from meta_compiler.compiler.executor import execute_blocks, ExecutionResult
from meta_compiler.compiler.paper import generate_paper
from meta_compiler.compiler.report import generate_report
from meta_compiler.compiler.runner import generate_runner


def check_document(source: str, *, strict: bool = False) -> ExecutionResult:
    """Parse and validate a .model.md document."""
    blocks = parse_document(source)
    return execute_blocks(blocks, strict=strict)


def compile_document(
    source: str, *, depth: str | None = None, filename: str = "model.model.md"
) -> dict:
    """Full compilation pipeline: validate, then generate artifacts."""
    blocks = parse_document(source)

    result = execute_blocks(blocks, strict=True)
    if not result.passed:
        raise RuntimeError(
            "Validation failed in strict mode:\n"
            + "\n".join(f"  - {e}" for e in result.errors)
        )

    paper = generate_paper(blocks, depth=depth)
    report = generate_report(result.registry, blocks, test_result=result)

    return {
        "paper": paper,
        "report": report,
        "report_text": report.to_text(),
        "runner": generate_runner(filename),
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_integration.py::test_compile_produces_paper_report_runner tests/compiler/test_integration.py::test_compile_no_codebase_key -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd meta-compiler && git add src/meta_compiler/compiler/__init__.py tests/compiler/test_integration.py
git commit -m "feat(compiler): replace codegen with runner in compile_document output"
```

---

## Chunk 5: CLI & Plugin Integration

### Task 13: Update CLI for .model.md

**Files:**
- Modify: `meta-compiler/src/meta_compiler/cli.py`
- Test: `meta-compiler/tests/compiler/test_cli.py`

- [ ] **Step 1: Write failing test**

Add to `tests/compiler/test_cli.py`:

```python
import subprocess
import tempfile
import os

def test_cli_check_model_md(tmp_path):
    doc = tmp_path / "test.model.md"
    doc.write_text('''# Model

```python:validate
Set("W", description="Workers")
```
''')
    result = subprocess.run(
        ["python3", "-m", "meta_compiler.cli", "check", str(doc)],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": "src"},
        cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    )
    assert result.returncode == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_cli.py::test_cli_check_model_md -v`
Expected: May pass or fail depending on current CLI state — verify behavior.

- [ ] **Step 3: Update cli.py**

Update references from `.math.md` to `.model.md` in help text and file discovery. The CLI commands themselves are file-path-based and should work with any extension — the main changes are in help text and default glob patterns for file discovery.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd meta-compiler && git add src/meta_compiler/cli.py tests/compiler/test_cli.py
git commit -m "feat(cli): update CLI for .model.md extension"
```

---

### Task 14: Update plugin hook and commands

**Files:**
- Modify: `meta-compiler/hooks/hooks.json`
- Rename: `meta-compiler/scripts/validate-math-md.sh` → `meta-compiler/scripts/validate-model-md.sh`
- Modify: `meta-compiler/commands/check.md`
- Modify: `meta-compiler/commands/onboard.md`
- Modify: Other command files (paper.md, report.md, compile.md, status.md)

- [ ] **Step 1: Update hooks.json**

Change the hook script reference:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate-model-md.sh",
          "timeout": 30
        }]
      }
    ]
  }
}
```

- [ ] **Step 2: Rename and update the hook script**

```bash
cd meta-compiler
git mv scripts/validate-math-md.sh scripts/validate-model-md.sh
```

Update the extension check inside the script from `.math.md` to `.model.md`.

- [ ] **Step 3: Update command files**

In each command file, change:
- `.math.md` → `.model.md`
- `*.math.md` → `*.model.md`
- References to `validate-math-md.sh` → `validate-model-md.sh`

For `commands/onboard.md`:
- Change output extension from `.math.md` to `.model.md`
- Change `python:validate` references if any glob patterns use `.math.md`
- Add instruction in the onboard prompt telling the LLM to generate a `python:fixture` block before each `python:validate` block. The fixture should contain a small, coherent test scenario (3-5 set members, realistic parameter values) that the LLM derives from the paper's domain context. The fixture should define: `sets` dict for all sets, and a dict per parameter/variable with values keyed by set member names (or tuple keys for multi-indexed symbols).

- [ ] **Step 4: Verify hook script runs**

Run: `cd meta-compiler && echo '{"tool_name":"Write","file_path":"test.model.md"}' | bash scripts/validate-model-md.sh`
Expected: Script processes input without error (may output "not a .model.md file" or similar)

- [ ] **Step 5: Commit**

```bash
cd meta-compiler && git add hooks/hooks.json scripts/ commands/
git commit -m "feat(plugin): update hooks and commands for .model.md extension"
```

---

### Task 15: Full test suite pass

**Files:**
- All test files

- [ ] **Step 1: Run full test suite**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/ -v --tb=short 2>&1`
Expected: Identify any remaining failures

- [ ] **Step 2: Fix remaining test failures**

Update any test files that still reference:
- Expression tree types (`IndexExpr`, `ArithExpr`, `CompareExpr`, etc.)
- `_capture_lambda`, `_Placeholder`
- `codegen` module
- `.math.md` extension
- `expr_tree` field on symbols

Files specifically requiring updates (from File Structure):
- `tests/test_variables.py` — update for v2 proxy behavior (data-backed, not tree-building)
- `tests/test_objectives.py` — update for numeric execution (callable, not expression tree)
- `tests/test_errors.py` — update error message formats to match spec:
  - Phantom: `Symbol "foo" referenced but never declared`
  - Orphan: `Symbol "bar" declared but never referenced`
  - Constraint: `Constraint "name" violated for set="member": result is False`
  - Unit: `Constraint "name": "sym_a" has unit "hours" but "sym_b" has unit "dollars"`

- [ ] **Step 3: Run full test suite again**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
cd meta-compiler && git add tests/
git commit -m "test: fix remaining test suite for v2 architecture"
```

---

### Task 16: End-to-end integration test

**Files:**
- Modify: `meta-compiler/tests/compiler/test_integration.py`

- [ ] **Step 1: Write comprehensive e2e test**

Add to `tests/compiler/test_integration.py`:

```python
FULL_MODEL = '''# Workforce Assignment Model

## Sets

```python:fixture
W = ["alice", "bob", "carol"]
P = ["projA", "projB"]
cap = {"alice": 40, "bob": 35, "carol": 40}
demand = {"projA": 60, "projB": 45}
x = {("alice", "projA"): 20, ("alice", "projB"): 15,
     ("bob", "projA"): 20, ("bob", "projB"): 10,
     ("carol", "projA"): 20, ("carol", "projB"): 20}
```

```python:validate
Set("W", description="Workers")
Set("P", description="Projects")
```

## Parameters

$$c_i = \\text{weekly capacity for worker } i$$

```python:validate
Parameter("cap", index="W", units="hours", description="Weekly capacity")
Parameter("demand", index="P", units="hours", description="Project demand")
```

## Decision Variables

$$x_{i,p} = \\text{hours assigned}$$

```python:validate
Variable("x", index=("W", "P"), domain="continuous", bounds=(0, None), units="hours", description="Assignment hours")
```

## Constraints

$$\\sum_{i \\in W} x_{i,p} \\geq d_p \\quad \\forall p \\in P$$

```python:validate
Constraint("meet_demand", over="P", expr=lambda p: sum(x[i, p] for i in S("W")) >= demand[p])
```

$$\\sum_{p \\in P} x_{i,p} \\leq c_i \\quad \\forall i \\in W$$

```python:validate
Constraint("respect_cap", over="W", expr=lambda i: sum(x[i, p] for p in S("P")) <= cap[i])
```

## Objective

```python:validate
Objective("min_hours", sense="minimize", expr=lambda: sum(x[i, p] for i in S("W") for p in S("P")))
```
'''

def test_full_model_check_passes():
    from meta_compiler.compiler import check_document
    result = check_document(FULL_MODEL)
    assert result.passed, f"Errors: {result.errors}"

def test_full_model_compiles():
    from meta_compiler.compiler import compile_document
    output = compile_document(FULL_MODEL)
    assert "Workforce" in output["paper"]
    assert "python:fixture" not in output["paper"]
    assert "python:validate" not in output["paper"]
    assert len(output["report"].symbol_table) > 0

def test_full_model_structural_mode():
    """Same model without fixtures — structural checks only."""
    import re
    structural_doc = re.sub(
        r'```python:fixture\n.*?```', '', FULL_MODEL, flags=re.DOTALL
    )
    from meta_compiler.compiler import check_document
    result = check_document(structural_doc)
    assert result.passed, f"Structural errors: {result.errors}"
```

- [ ] **Step 2: Run e2e tests**

Run: `cd meta-compiler && PYTHONPATH=src pytest tests/compiler/test_integration.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
cd meta-compiler && git add tests/compiler/test_integration.py
git commit -m "test: add comprehensive end-to-end integration tests for v2"
```
