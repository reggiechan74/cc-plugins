# Meta-Compiler: Scalar Model Support

**Date:** 2026-03-20
**Plugin:** math-paper-creator
**Issues:** #3, #4, #5, #6
**Status:** Design

## Problem

The meta-compiler's v2 architecture assumes indexed symbols (sets, indexed parameters). Scalar optimization models — where every symbol is a plain float with no indexing — hit friction at multiple levels:

1. `SymbolProxy` lacks arithmetic operators, so `M * beta` fails (#3)
2. `compile_document()` hardcodes `strict=True`, flagging all scalar symbols as orphans (#4)
3. `generate_report()` returns a `Report` object instead of a string, unlike the other generators (#5)
4. Generator function signatures are inconsistent, making direct usage confusing (#6)

Issues #4-#6 compound: strict mode forces users to call generators directly, where the inconsistencies bite.

## Design

### 1. Scalar Auto-Unwrap (Issue #3)

**Location:** `meta_compiler/registry.py` — `_make_proxy()` method

When fixture data for a symbol is a scalar type (`int`, `float`, `str`), inject the raw value directly into the execution namespace instead of wrapping it in a `SymbolProxy`. Indexed data (dicts, lists, arrays) continues to use `SymbolProxy` as before. Symbols with no fixture data (`name not in data_store`) retain the current `SymbolProxy` behavior, which provides a helpful error message on access.

**Detection heuristic:** `name in self.data_store and isinstance(self.data_store[name], (int, float, str))`. This distinguishes "scalar value" from "no fixture data" — `data_store.get(name)` returns `None` for both cases, so the `in` check is required. Note: `bool` is a subclass of `int`, so booleans are auto-unwrapped; this is correct behavior.

**Return type change:** `_make_proxy()` currently always returns `SymbolProxy`. For scalar symbols it will return the raw value (`int | float | str`). This propagates through `register_parameter()`, `register_variable()`, etc., and through the DSL surface functions (`Parameter(...)`, `Variable(...)`). This is desirable — user code like `M = Parameter("M", ...)` gets a plain float, enabling `M * beta` directly. Type annotations on `_make_proxy()` and the `register_*` methods should be updated to `SymbolProxy | int | float | str`.

**Access logging:** Scalar values bypass `SymbolProxy.__getitem__`, so they won't appear in the access log via proxy interception. To compensate, add a helper `collect_scalar_refs(block_source: str, scalar_names: set[str], access_log: set[str])` in `checks.py`. This helper tokenizes the block source (reusing the existing `_extract_names_from_source()` tokenizer) and adds any matches against `scalar_names` to the access log.

Call this helper in `executor.py` — after each `exec(vb.code, ns)` call in `execute_blocks()`, invoke it with the validation block's source, the set of auto-unwrapped scalar symbol names (tracked by `Registry` during `_make_proxy()`), and `registry.access_log`. This ensures scalar references are logged before `run_all_checks()` runs.

**Result:** `Expression("t_eff", definition=lambda: H - M * beta)` works directly — `M` and `beta` are injected as plain Python floats. No workaround needed.

### 2. Strict Mode with Scalar Auto-Detection (Issue #4)

**Location:** `meta_compiler/compiler/__init__.py`, `meta_compiler/cli.py`

#### compile_document()

Add an optional `strict` parameter (default `True` for backward compatibility):

```python
def compile_document(
    source: str,
    *,
    depth: str | None = None,
    filename: str = "model.model.md",
    strict: bool = True,
) -> dict:
```

When `strict=True`, auto-detect scalar models and demote orphan checks accordingly. The auto-detection logic lives in `run_all_checks()` in `checks.py` — not in `compile_document()`. This avoids re-executing blocks or post-hoc string filtering:

```python
def run_all_checks(registry, *, strict=False):
    # If strict but no Sets registered, treat orphan check as non-strict
    has_sets = any(isinstance(s, SetSymbol) for s in registry.symbols.values())
    effective_orphan_strict = strict and has_sets
    # ... pass effective_orphan_strict to _check_orphans() ...
```

All other checks (phantoms, cycles, unit mismatches) remain strict regardless. Only orphan detection is affected by the scalar heuristic.

#### CLI

Add `--no-strict` flag to the `compile`, `paper`, and `report` subcommands (all three call `compile_document()` internally):

```python
for p in [compile_parser, paper_parser, report_parser]:
    p.add_argument("--no-strict", action="store_true",
        help="Treat orphan symbols as warnings instead of errors")
```

Pass `strict=not args.no_strict` to `compile_document()`.

#### Behavior Matrix

| Scenario | Sets present? | `--no-strict`? | Orphans treated as |
|----------|:---:|:---:|---|
| `compile model.md` | Yes | No | Errors |
| `compile model.md` | No | No | Warnings (auto-detect) |
| `compile model.md --no-strict` | Either | Yes | Warnings |

### 3. Report `__str__` (Issue #5)

**Location:** `meta_compiler/compiler/report.py`

Add `__str__` to the `Report` dataclass:

```python
def __str__(self) -> str:
    return self.to_text()
```

This makes `print(report)`, `f.write(str(report))`, and f-string interpolation work as expected. Zero risk, fully backward compatible.

### 4. Generator Signature Normalization (Issue #6)

**Location:** `meta_compiler/compiler/paper.py`, `runner.py`, `report.py`

Standardize all three generators to use `blocks` as the first positional argument, with everything else keyword-only:

| Function | Current Signature | New Signature |
|----------|-------------------|---------------|
| `generate_paper` | `(blocks, *, depth=None)` | No change |
| `generate_runner` | `(model_path, blocks=None)` | `(blocks, *, model_path="model.model.md")` |
| `generate_report` | `(registry, blocks, *, test_result=None)` | `(blocks, *, registry, test_result=None)` |

**Internal callers:** Update `compile_document()` to use new signatures. This is the only internal call site for all three generators.

**Breaking change:** External callers using positional arguments will break. Since `compile_document()` now works for scalar models (via #2), the need to call generators directly is eliminated for most users. Document the change in a changelog entry.

## Testing Strategy

- **Scalar auto-unwrap:** Test that scalar fixture values are injected as raw types and arithmetic works in expressions. Key access-log test: register a scalar parameter `M` with fixture value `5.0`, register an expression referencing `M` in arithmetic, run checks, and verify `M` is NOT flagged as orphan (i.e., `collect_scalar_refs` correctly logs it).
- **Strict mode:** Test the three-cell behavior matrix. Test that non-orphan errors (phantoms, cycles, unit mismatches) remain errors regardless of mode.
- **Report `__str__`:** Test `str(report) == report.to_text()`.
- **Signatures:** Test that `compile_document()` produces identical output before and after the refactor. Test new keyword-only signatures directly.
- **Mixed models:** Test a model with both sets/indexed parameters and scalar parameters. Auto-detection keeps strict orphan checking (sets present), but `collect_scalar_refs` must still log scalar references correctly within the mixed model.
- **Integration:** Compile the `Organizational_Productivity_Optimization.model.md` scalar model end-to-end with no workarounds.

## Files Changed

| File | Change |
|------|--------|
| `src/meta_compiler/proxy.py` | No change (SymbolProxy stays as-is) |
| `src/meta_compiler/registry.py` | Scalar detection in `_make_proxy()`, track set of scalar symbol names, update type annotations on `_make_proxy()`/`register_*` methods, update `data_store` type from `dict[str, dict]` to `dict[str, Any]`, clear scalar names set in `reset()` |
| `src/meta_compiler/checks.py` | Add `collect_scalar_refs()` helper, push scalar auto-detection into `run_all_checks()` |
| `src/meta_compiler/compiler/__init__.py` | Add `strict` param to `compile_document()` |
| `src/meta_compiler/compiler/executor.py` | Call `collect_scalar_refs()` after each validation block execution |
| `src/meta_compiler/compiler/report.py` | Add `Report.__str__`, change `generate_report` signature |
| `src/meta_compiler/compiler/runner.py` | Change `generate_runner` signature |
| `src/meta_compiler/cli.py` | Add `--no-strict` flag to `compile`, `paper`, and `report` subcommands |

## Out of Scope

- Adding a `registry.scalars()` helper (suggested in #3 but unnecessary with auto-unwrap)
- Refactoring `SymbolProxy` to add arithmetic operators (replaced by auto-unwrap approach)
- Changes to `generate_paper` signature (already consistent)
