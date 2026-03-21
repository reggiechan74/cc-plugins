# Meta-Compiler Scalar Model Support Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable scalar optimization models to compile without workarounds by auto-unwrapping scalar fixture data, auto-detecting scalar models for strict mode, fixing Report's string representation, and normalizing generator signatures.

**Architecture:** Four coordinated changes to the meta-compiler: (1) registry detects scalar fixture values and injects raw Python types instead of SymbolProxy, (2) checks.py auto-demotes orphan errors for set-free models and provides a scalar access-logging helper, (3) Report gains `__str__`, (4) generator signatures standardize on `blocks` as first arg.

**Tech Stack:** Python 3.12+, pytest, Python tokenize module

**Spec:** `docs/superpowers/specs/2026-03-20-meta-compiler-scalar-model-support-design.md`

---

## Chunk 1: Report `__str__` and Generator Signatures (Issues #5, #6)

These are the simplest changes with no dependencies on the scalar work.

### Task 1: Add `Report.__str__` (Issue #5)

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/compiler/report.py:19-27`
- Test: `math-paper-creator/tests/compiler/test_report.py`

- [ ] **Step 1: Write failing test**

In `tests/compiler/test_report.py`, add:

```python
def test_report_str_delegates_to_to_text(fresh_registry):
    """str(report) should produce the same output as report.to_text()."""
    from meta_compiler.compiler.report import Report

    report = Report(
        symbol_table=[{"name": "x", "type": "Variable", "description": "test"}],
        dependencies=[],
        test_passed=True,
        test_errors=[],
        test_warnings=[],
        coverage={"total_math": 1, "covered_math": 1, "uncovered_sections": []},
    )
    assert str(report) == report.to_text()
    assert repr(report) != str(report)  # __str__ is not __repr__
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_report.py::test_report_str_delegates_to_to_text -v`
Expected: FAIL — `str(report)` returns the default dataclass repr, not `to_text()`

- [ ] **Step 3: Implement `__str__` on Report**

In `src/meta_compiler/compiler/report.py`, add method to the `Report` dataclass (after `to_text`):

```python
def __str__(self) -> str:
    return self.to_text()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_report.py::test_report_str_delegates_to_to_text -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add math-paper-creator/src/meta_compiler/compiler/report.py math-paper-creator/tests/compiler/test_report.py
git commit -m "fix(meta-compiler): add Report.__str__ delegating to to_text()

Closes #5"
```

---

### Task 2: Normalize `generate_report` signature (Issue #6, part 1)

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/compiler/report.py:80`
- Modify: `math-paper-creator/src/meta_compiler/compiler/__init__.py:34`
- Test: `math-paper-creator/tests/compiler/test_report.py`

- [ ] **Step 1: Write failing test for new signature**

In `tests/compiler/test_report.py`, add:

```python
def test_generate_report_blocks_first_signature(fresh_registry):
    """generate_report takes blocks as first positional arg, registry as keyword-only."""
    from meta_compiler.compiler.report import generate_report
    from meta_compiler.compiler.parser import parse_document
    from meta_compiler.registry import registry
    from meta_compiler import Set, Parameter

    Set("W", description="workers")
    registry.data_store["W"] = ["a", "b"]

    source = '''
Some prose.

```python:validate
Set("W", description="workers")
Parameter("cap", index="W", description="capacity")
```
'''
    blocks = parse_document(source)
    # New signature: blocks first, registry keyword-only
    report = generate_report(blocks, registry=registry)
    assert report.test_passed is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_report.py::test_generate_report_blocks_first_signature -v`
Expected: FAIL — TypeError because current signature expects `registry` as first positional arg

- [ ] **Step 3: Update `generate_report` signature**

In `src/meta_compiler/compiler/report.py`, change:

```python
# FROM:
def generate_report(registry, blocks, *, test_result=None):

# TO:
def generate_report(blocks, *, registry, test_result=None):
```

- [ ] **Step 4: Update call site in `compile_document`**

In `src/meta_compiler/compiler/__init__.py`, change the `generate_report` call:

```python
# FROM:
report = generate_report(result.registry, blocks, test_result=result)

# TO:
report = generate_report(blocks, registry=result.registry, test_result=result)
```

- [ ] **Step 5: Update existing tests to use new signature**

Existing tests in `tests/compiler/test_report.py` call `generate_report(registry, blocks, ...)` with the old positional signature. Update all calls to use the new `generate_report(blocks, registry=registry, ...)` form. Search for all `generate_report(` calls in the file and update each one.

- [ ] **Step 6: Run all report and compiler tests**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_report.py tests/compiler/test_integration.py tests/compiler/test_cli.py -v`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add math-paper-creator/src/meta_compiler/compiler/report.py math-paper-creator/src/meta_compiler/compiler/__init__.py math-paper-creator/tests/compiler/test_report.py
git commit -m "refactor(meta-compiler): normalize generate_report signature — blocks first

Part of #6"
```

---

### Task 3: Normalize `generate_runner` signature (Issue #6, part 2)

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/compiler/runner.py:13`
- Modify: `math-paper-creator/src/meta_compiler/compiler/__init__.py:37`
- Test: `math-paper-creator/tests/compiler/test_runner.py`

- [ ] **Step 1: Write failing test for new signature**

In `tests/compiler/test_runner.py`, add:

```python
def test_generate_runner_blocks_first_signature():
    """generate_runner takes blocks as first positional arg, model_path as keyword-only."""
    from meta_compiler.compiler.runner import generate_runner
    from meta_compiler.compiler.parser import parse_document

    source = '''
Some prose.

```python:fixture
W = ["alice", "bob"]
```

```python:validate
Set("W", description="workers")
```
'''
    blocks = parse_document(source)
    # New signature: blocks first, model_path keyword-only with default
    script = generate_runner(blocks, model_path="test.model.md")
    assert "test.model.md" in script
    assert "#!/usr/bin/env python3" in script
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_runner.py::test_generate_runner_blocks_first_signature -v`
Expected: FAIL — current signature expects `model_path` as first positional arg

- [ ] **Step 3: Update `generate_runner` signature**

In `src/meta_compiler/compiler/runner.py`, change:

```python
# FROM:
def generate_runner(model_path, blocks=None):

# TO:
def generate_runner(blocks, *, model_path="model.model.md"):
```

Also update the legacy fallback path — since `blocks` is now required and positional, the legacy path (no blocks) needs to be triggered by `blocks` being empty or a flag. Since `compile_document` always passes blocks, change the legacy check:

```python
# FROM:
if blocks is None:

# TO:
if not blocks:
```

- [ ] **Step 4: Update call site in `compile_document`**

In `src/meta_compiler/compiler/__init__.py`, change:

```python
# FROM:
"runner": generate_runner(filename, blocks=blocks),

# TO:
"runner": generate_runner(blocks, model_path=filename),
```

- [ ] **Step 5: Update existing tests to use new signature**

Existing tests in `tests/compiler/test_runner.py` call `generate_runner("model_path")` or `generate_runner("model_path", blocks=...)` with the old positional signature. Update all calls to use the new `generate_runner(blocks, model_path=...)` form. For legacy-mode tests that passed only a model path, pass an empty list: `generate_runner([], model_path="model_path")`.

- [ ] **Step 6: Run all runner and compiler tests**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_runner.py tests/compiler/test_integration.py tests/compiler/test_cli.py -v`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add math-paper-creator/src/meta_compiler/compiler/runner.py math-paper-creator/src/meta_compiler/compiler/__init__.py math-paper-creator/tests/compiler/test_runner.py
git commit -m "refactor(meta-compiler): normalize generate_runner signature — blocks first

Part of #6. Closes #6"
```

---

## Chunk 2: Scalar Auto-Unwrap and Access Logging (Issue #3)

### Task 4: Add `collect_scalar_refs` helper to checks.py

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/checks.py`
- Create: `math-paper-creator/tests/test_scalar_refs.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_scalar_refs.py`:

```python
"""Tests for scalar reference collection in checks.py."""
from meta_compiler.checks import collect_scalar_refs


def test_collect_scalar_refs_finds_matching_names():
    source = "Expression('t_eff', definition=lambda: H - M * beta)"
    scalar_names = {"H", "M", "beta"}
    access_log = set()
    collect_scalar_refs(source, scalar_names, access_log)
    assert access_log == {"H", "M", "beta"}


def test_collect_scalar_refs_ignores_non_scalar_names():
    source = "Expression('cost', definition=lambda: cap[i] + overhead)"
    scalar_names = {"overhead"}
    access_log = set()
    collect_scalar_refs(source, scalar_names, access_log)
    assert access_log == {"overhead"}
    assert "cap" not in access_log  # cap is not in scalar_names


def test_collect_scalar_refs_handles_empty_scalars():
    source = "Parameter('cap', index='W')"
    scalar_names = set()
    access_log = set()
    collect_scalar_refs(source, scalar_names, access_log)
    assert access_log == set()


def test_collect_scalar_refs_no_false_positives_from_substrings():
    """'capacity' should not match scalar 'cap'."""
    source = "capacity = 100"
    scalar_names = {"cap"}
    access_log = set()
    collect_scalar_refs(source, scalar_names, access_log)
    assert access_log == set()  # tokenizer sees 'capacity', not 'cap'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd math-paper-creator && python -m pytest tests/test_scalar_refs.py -v`
Expected: FAIL — ImportError, `collect_scalar_refs` doesn't exist

- [ ] **Step 3: Implement `collect_scalar_refs`**

In `src/meta_compiler/checks.py`, add the function (after the existing `_extract_names_from_source`):

```python
def collect_scalar_refs(
    block_source: str, scalar_names: set[str], access_log: set[str]
) -> None:
    """Add scalar symbol names found in block_source to access_log.

    Uses Python's tokenizer to avoid substring false positives.
    """
    if not scalar_names:
        return
    try:
        tokens = tokenize.generate_tokens(io.StringIO(block_source).readline)
        for tok_type, tok_string, *_ in tokens:
            if tok_type == tokenize.NAME and tok_string in scalar_names:
                access_log.add(tok_string)
    except tokenize.TokenError:
        pass  # partial source is OK — best-effort
```

Add `import io` to the module-level imports at the top of `checks.py` (it is currently only used inside `_extract_names_from_source` locally; the new function needs it at module scope).

- [ ] **Step 4: Run test to verify it passes**

Run: `cd math-paper-creator && python -m pytest tests/test_scalar_refs.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add math-paper-creator/src/meta_compiler/checks.py math-paper-creator/tests/test_scalar_refs.py
git commit -m "feat(meta-compiler): add collect_scalar_refs helper for scalar access logging

Part of #3"
```

---

### Task 5: Scalar auto-unwrap in Registry

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/registry.py:37,42-49,78-83`
- Modify: `math-paper-creator/src/meta_compiler/__init__.py` (type annotations)
- Test: `math-paper-creator/tests/test_scalar_unwrap.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_scalar_unwrap.py`:

```python
"""Tests for scalar auto-unwrap in registry."""
from meta_compiler.registry import registry
from meta_compiler import Parameter, Variable, Set


def test_scalar_parameter_returns_raw_float(fresh_registry):
    """Scalar fixture data should be injected as raw float, not SymbolProxy."""
    registry.data_store["M"] = 5.0
    registry._exec_namespace = {}
    result = Parameter("M", description="meeting hours")
    assert result == 5.0
    assert isinstance(result, float)


def test_scalar_arithmetic_works(fresh_registry):
    """Scalars should support arithmetic directly."""
    registry.data_store["M"] = 5.0
    registry.data_store["beta"] = 0.8
    registry._exec_namespace = {}
    M = Parameter("M", description="meeting hours")
    beta = Parameter("beta", description="productivity factor")
    assert M * beta == 4.0
    assert M + beta == 5.8
    assert M - beta == 4.2


def test_indexed_data_still_returns_proxy(fresh_registry):
    """Dict/list fixture data should still get a SymbolProxy."""
    from meta_compiler.proxy import SymbolProxy

    registry.data_store["cap"] = {"alice": 10, "bob": 20}
    registry._exec_namespace = {}
    result = Parameter("cap", index="W", description="capacity")
    assert isinstance(result, SymbolProxy)


def test_no_fixture_data_returns_proxy(fresh_registry):
    """Missing fixture data should still get a SymbolProxy (helpful error on access)."""
    from meta_compiler.proxy import SymbolProxy

    # data_store does NOT have "M"
    registry._exec_namespace = {}
    result = Parameter("M", description="meeting hours")
    assert isinstance(result, SymbolProxy)


def test_scalar_names_tracked_on_registry(fresh_registry):
    """Registry should track which symbols were auto-unwrapped as scalars."""
    registry.data_store["M"] = 5.0
    registry._exec_namespace = {}
    Parameter("M", description="meeting hours")
    assert "M" in registry.scalar_names


def test_reset_clears_scalar_names(fresh_registry):
    """reset() should clear the scalar_names set."""
    registry.scalar_names.add("M")
    registry.reset()
    assert len(registry.scalar_names) == 0


def test_namespace_injection_uses_raw_value(fresh_registry):
    """Auto-unwrapped scalar should be injected as raw value in exec namespace."""
    registry.data_store["H"] = 8.0
    ns = {}
    registry._exec_namespace = ns
    Parameter("H", description="hours")
    assert ns["H"] == 8.0
    assert isinstance(ns["H"], float)


def test_bool_scalar_auto_unwrapped(fresh_registry):
    """bool is a subclass of int, so booleans should be auto-unwrapped."""
    registry.data_store["flag"] = True
    registry._exec_namespace = {}
    result = Parameter("flag", description="a boolean flag")
    assert result is True
    assert isinstance(result, bool)
    assert "flag" in registry.scalar_names


def test_str_scalar_auto_unwrapped(fresh_registry):
    """String scalars should be auto-unwrapped."""
    registry.data_store["mode"] = "fast"
    registry._exec_namespace = {}
    result = Parameter("mode", description="execution mode")
    assert result == "fast"
    assert isinstance(result, str)
    assert "mode" in registry.scalar_names
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd math-paper-creator && python -m pytest tests/test_scalar_unwrap.py -v`
Expected: FAIL — scalar values return SymbolProxy, `scalar_names` attribute doesn't exist

- [ ] **Step 3: Implement scalar auto-unwrap**

In `src/meta_compiler/registry.py`:

**Add `scalar_names` attribute** — in `__init__` (around line 37):

```python
self.scalar_names: set[str] = set()
```

**Update `data_store` type annotation** — change from `dict[str, dict]` to:

```python
self.data_store: dict[str, Any] = {}
```

Add `from typing import Any` at the top if not already present.

**Clear `scalar_names` in `reset()`** — add to the reset method:

```python
self.scalar_names = set()
```

**Modify `_make_proxy()`** — replace the current implementation:

```python
def _make_proxy(self, name: str) -> "SymbolProxy | int | float | str":
    if name in self.data_store and isinstance(
        self.data_store[name], (int, float, str)
    ):
        # Scalar value — inject raw value, not a proxy
        value = self.data_store[name]
        self.scalar_names.add(name)
        if self._exec_namespace is not None:
            self._exec_namespace[name] = value
        return value
    proxy = SymbolProxy(name, data=self.data_store.get(name), access_log=self.access_log)
    if self._exec_namespace is not None:
        self._exec_namespace[name] = proxy
    return proxy
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd math-paper-creator && python -m pytest tests/test_scalar_unwrap.py -v`
Expected: ALL PASS

- [ ] **Step 5: Run existing tests to verify no regressions**

Run: `cd math-paper-creator && python -m pytest tests/ -v`
Expected: ALL PASS (existing tests use dict/list fixture data, so they remain on the proxy path)

- [ ] **Step 6: Commit**

```bash
git add math-paper-creator/src/meta_compiler/registry.py math-paper-creator/tests/test_scalar_unwrap.py
git commit -m "feat(meta-compiler): auto-unwrap scalar fixture values as raw Python types

Scalars (int, float, str) are injected directly into the exec namespace
instead of SymbolProxy, enabling arithmetic like M * beta.

Part of #3"
```

---

### Task 6: Wire `collect_scalar_refs` into executor

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/compiler/executor.py`
- Test: `math-paper-creator/tests/test_scalar_access_logging.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_scalar_access_logging.py`:

```python
"""Tests that scalar symbols are correctly logged during execution."""
from meta_compiler.compiler import check_document


SCALAR_MODEL = '''
```python:fixture
M = 5.0
beta = 0.8
H = 8.0
```

```python:validate
Parameter("M", description="meeting hours")
Parameter("beta", description="productivity factor")
Parameter("H", description="total hours")
Expression("t_eff", definition=lambda: H - M * beta, description="effective time")
```
'''


def test_scalar_refs_not_flagged_as_orphans(fresh_registry):
    """Scalar symbols used in expressions should not be orphans."""
    result = check_document(SCALAR_MODEL, strict=True)
    orphan_warnings = [w for w in result.warnings if "Orphan" in w]
    orphan_errors = [e for e in result.errors if "Orphan" in e]
    # M, beta, H are all referenced in the expression — none should be orphans
    assert not any("M" in w for w in orphan_warnings), f"M flagged as orphan: {orphan_warnings}"
    assert not any("M" in e for e in orphan_errors), f"M flagged as orphan error: {orphan_errors}"
    assert not any("beta" in w for w in orphan_warnings)
    assert not any("H" in w for w in orphan_warnings)


MIXED_MODEL = '''
```python:fixture
W = ["alice", "bob"]
cap = {"alice": 10, "bob": 20}
overhead = 5.0
```

```python:validate
Set("W", description="workers")
Parameter("cap", index="W", description="capacity")
Parameter("overhead", description="fixed overhead")
Expression("total", definition=lambda: cap[S("W")[0]] + overhead, description="total")
```
'''


def test_mixed_model_scalar_refs_logged(fresh_registry):
    """In mixed models, scalar refs should still be logged correctly."""
    result = check_document(MIXED_MODEL, strict=True)
    # overhead is scalar but referenced in expression — should not be orphan
    orphan_msgs = result.errors + result.warnings
    assert not any("overhead" in m for m in orphan_msgs if "Orphan" in m)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd math-paper-creator && python -m pytest tests/test_scalar_access_logging.py -v`
Expected: FAIL — scalar symbols flagged as orphans because `collect_scalar_refs` is not called in executor

- [ ] **Step 3: Wire `collect_scalar_refs` into executor**

In `src/meta_compiler/compiler/executor.py`, after each validation block is executed, add a call to `collect_scalar_refs`. Find the section where validation blocks are executed (around lines 77-84 in the numeric mode path):

```python
# After: exec(vb.code, ns)
# Add:
from meta_compiler.checks import collect_scalar_refs
collect_scalar_refs(vb.code, registry.scalar_names, registry.access_log)
```

Move the import to the top of the file to keep it clean.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd math-paper-creator && python -m pytest tests/test_scalar_access_logging.py -v`
Expected: ALL PASS

- [ ] **Step 5: Run full test suite**

Run: `cd math-paper-creator && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add math-paper-creator/src/meta_compiler/compiler/executor.py math-paper-creator/tests/test_scalar_access_logging.py
git commit -m "feat(meta-compiler): wire collect_scalar_refs into executor for scalar access logging

Closes #3"
```

---

## Chunk 3: Strict Mode Auto-Detection and CLI (Issue #4)

### Task 7: Auto-detect scalar models in `run_all_checks`

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/checks.py:23-45,66-96`
- Test: `math-paper-creator/tests/test_scalar_strict_mode.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_scalar_strict_mode.py`:

```python
"""Tests for scalar model auto-detection in strict mode."""
from meta_compiler.registry import registry
from meta_compiler import Parameter, Expression, Set
from meta_compiler.compiler import check_document


def test_strict_no_sets_demotes_orphans(fresh_registry):
    """With strict=True but no Sets, orphans should be warnings, not errors."""
    Parameter("M", description="meeting hours")
    result = registry.run_tests(strict=True)
    # M is an orphan (never referenced), but no sets → demote to warning
    orphan_errors = [e for e in result.errors if "Orphan" in e]
    orphan_warnings = [w for w in result.warnings if "Orphan" in w]
    assert len(orphan_errors) == 0, f"Orphans should not be errors: {orphan_errors}"
    assert len(orphan_warnings) > 0, "Orphans should still appear as warnings"


def test_strict_with_sets_keeps_orphans_as_errors(fresh_registry):
    """With strict=True and Sets present, orphans remain errors."""
    Set("W", description="workers")
    Parameter("M", description="unused")
    registry.data_store["W"] = ["a"]
    result = registry.run_tests(strict=True)
    orphan_errors = [e for e in result.errors if "Orphan" in e]
    assert any("M" in e for e in orphan_errors), "M should be an orphan error"


def test_non_orphan_errors_unaffected_by_scalar_heuristic(fresh_registry):
    """Phantom errors should remain errors even in scalar models."""
    registry.access_log.add("nonexistent")
    result = registry.run_tests(strict=True)
    phantom_errors = [e for e in result.errors if "Phantom" in e]
    assert len(phantom_errors) > 0, "Phantoms should still be errors"


SCALAR_MODEL_STRICT = '''
```python:fixture
M = 5.0
H = 8.0
```

```python:validate
Parameter("M", description="meeting hours")
Parameter("H", description="total hours")
Expression("t_eff", definition=lambda: H - M, description="effective time")
```
'''


def test_check_document_strict_scalar_passes(fresh_registry):
    """check_document with strict=True on scalar model should pass (orphans demoted)."""
    result = check_document(SCALAR_MODEL_STRICT, strict=True)
    assert result.passed, f"Should pass but got errors: {result.errors}"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd math-paper-creator && python -m pytest tests/test_scalar_strict_mode.py -v`
Expected: FAIL — orphans are errors in strict mode regardless of Sets

- [ ] **Step 3: Implement auto-detection in `run_all_checks`**

In `src/meta_compiler/checks.py`, modify `run_all_checks`:

```python
def run_all_checks(registry, *, strict=False):
    errors = []
    warnings = []
    source_refs = _collect_source_refs(registry)
    all_accessed = registry.access_log | source_refs

    _check_phantoms(registry, all_accessed, errors)

    # Auto-detect scalar models: if strict but no Sets registered,
    # demote orphan checking to non-strict (orphans become warnings)
    # Note: SetSymbol is already imported at the top of checks.py
    has_sets = any(isinstance(s, SetSymbol) for s in registry.symbols.values())
    effective_orphan_strict = strict and has_sets

    _check_orphans(registry, all_accessed, errors, warnings, effective_orphan_strict)
    _check_cycles(registry, errors)
    _check_unit_boundaries(registry, errors)

    return TestResult(passed=len(errors) == 0, errors=errors, warnings=warnings)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd math-paper-creator && python -m pytest tests/test_scalar_strict_mode.py -v`
Expected: ALL PASS

- [ ] **Step 5: Run full test suite**

Run: `cd math-paper-creator && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add math-paper-creator/src/meta_compiler/checks.py math-paper-creator/tests/test_scalar_strict_mode.py
git commit -m "feat(meta-compiler): auto-detect scalar models in strict mode

When strict=True but no Set symbols are registered, orphan warnings are
demoted from errors to warnings. Other checks (phantoms, cycles, units)
remain strict.

Part of #4"
```

---

### Task 8: Add `strict` param to `compile_document` and `--no-strict` CLI flag

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/compiler/__init__.py:18-39`
- Modify: `math-paper-creator/src/meta_compiler/cli.py`
- Test: `math-paper-creator/tests/compiler/test_cli.py`

- [ ] **Step 1: Write failing test for `compile_document` strict param**

In `tests/compiler/test_integration.py`, add:

```python
def test_compile_document_accepts_strict_param(fresh_registry):
    """compile_document should accept strict kwarg."""
    from meta_compiler.compiler import compile_document

    source = '''
```python:fixture
M = 5.0
```

```python:validate
Parameter("M", description="meeting hours")
```
'''
    # With strict=False, this should succeed even without the auto-detect heuristic
    result = compile_document(source, strict=False)
    assert "paper" in result
    assert "report" in result
    assert "runner" in result
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_integration.py::test_compile_document_accepts_strict_param -v`
Expected: FAIL — TypeError, `compile_document` doesn't accept `strict`

- [ ] **Step 3: Add `strict` param to `compile_document`**

In `src/meta_compiler/compiler/__init__.py`, update the signature and pass it through:

```python
def compile_document(
    source: str,
    *,
    depth: str | None = None,
    filename: str = "model.model.md",
    strict: bool = True,
) -> dict:
    blocks = parse_document(source)
    result = execute_blocks(blocks, strict=strict)

    if not result.passed:
        raise RuntimeError(
            "Validation failed:\n"
            + "\n".join(f"  - {e}" for e in result.errors)
        )

    paper = generate_paper(blocks, depth=depth)
    report = generate_report(blocks, registry=result.registry, test_result=result)

    return {
        "paper": paper,
        "report": report,
        "report_text": report.to_text(),
        "runner": generate_runner(blocks, model_path=filename),
    }
```

Note: The generator call sites should already use the new signatures from Tasks 2-3.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_integration.py::test_compile_document_accepts_strict_param -v`
Expected: PASS

- [ ] **Step 5: Write CLI test for `--no-strict`**

In `tests/compiler/test_cli.py`, add:

```python
def test_compile_no_strict_flag(tmp_path):
    """compile --no-strict should pass for scalar models with orphans."""
    model = tmp_path / "scalar.model.md"
    model.write_text('''
```python:fixture
M = 5.0
```

```python:validate
Parameter("M", description="meeting hours")
Parameter("H", description="total hours")
```
''')
    out_dir = tmp_path / "output"
    result = subprocess.run(
        [sys.executable, "-m", "meta_compiler.cli", "compile", str(model),
         "--output", str(out_dir), "--no-strict"],
        capture_output=True, text=True, env=_CLI_ENV,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
```

- [ ] **Step 6: Add `--no-strict` to CLI subcommands**

In `src/meta_compiler/cli.py`, add `--no-strict` to `compile`, `paper`, and `report` subparsers:

```python
# After each subparser is created, add:
compile_parser.add_argument(
    "--no-strict", action="store_true",
    help="Treat orphan symbols as warnings instead of errors",
)
paper_parser.add_argument(
    "--no-strict", action="store_true",
    help="Treat orphan symbols as warnings instead of errors",
)
report_parser.add_argument(
    "--no-strict", action="store_true",
    help="Treat orphan symbols as warnings instead of errors",
)
```

Update `_cmd_compile`, `_cmd_paper`, and `_cmd_report` to pass `strict=not args.no_strict` to `compile_document()`.

- [ ] **Step 7: Run CLI tests**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_cli.py -v`
Expected: ALL PASS

- [ ] **Step 8: Run full test suite**

Run: `cd math-paper-creator && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 9: Commit**

```bash
git add math-paper-creator/src/meta_compiler/compiler/__init__.py math-paper-creator/src/meta_compiler/cli.py math-paper-creator/tests/compiler/test_integration.py math-paper-creator/tests/compiler/test_cli.py
git commit -m "feat(meta-compiler): add strict param to compile_document and --no-strict CLI flag

compile_document() now accepts strict kwarg (default True).
CLI compile, paper, and report subcommands accept --no-strict flag.

Closes #4"
```

---

## Chunk 4: Integration Test

### Task 9: End-to-end scalar model compilation

**Files:**
- Test: `math-paper-creator/tests/compiler/test_integration.py`

- [ ] **Step 1: Write integration test**

In `tests/compiler/test_integration.py`, add:

```python
def test_scalar_model_compiles_end_to_end(fresh_registry):
    """A pure scalar model should compile through compile_document with no workarounds."""
    from meta_compiler.compiler import compile_document

    source = '''
# Organizational Productivity

A simple scalar optimization model.

$$t_{eff} = H - M \\cdot \\beta$$

```python:fixture
H = 8.0
M = 2.0
beta = 0.75
```

```python:validate
Parameter("H", description="Total work hours per day")
Parameter("M", description="Meeting hours per day")
Parameter("beta", description="Productivity impact factor")
Expression("t_eff", definition=lambda: H - M * beta, description="Effective productive time")
Variable("M_opt", domain="continuous", bounds=(0, None), description="Optimal meeting hours")
Objective("maximize_productivity", expr=lambda: H - M * beta, sense="maximize", description="Maximize productive time")
Constraint("meeting_bound", expr=lambda: M <= H, description="Cannot exceed total hours")
```
'''
    # Should compile without errors — no workarounds needed
    result = compile_document(source, strict=True)

    assert "paper" in result
    assert "Organizational Productivity" in result["paper"]

    assert "report" in result
    report = result["report"]
    assert report.test_passed
    assert str(report) == report.to_text()  # __str__ works

    assert "runner" in result
    assert "#!/usr/bin/env python3" in result["runner"]
```

- [ ] **Step 2: Run test**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_integration.py::test_scalar_model_compiles_end_to_end -v`
Expected: PASS (all prior tasks should make this work)

- [ ] **Step 3: Run full test suite one final time**

Run: `cd math-paper-creator && python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add math-paper-creator/tests/compiler/test_integration.py
git commit -m "test(meta-compiler): add end-to-end scalar model compilation test

Verifies that all four fixes (#3, #4, #5, #6) work together."
```
