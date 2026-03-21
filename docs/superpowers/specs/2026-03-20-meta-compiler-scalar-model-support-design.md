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

When fixture data for a symbol is a scalar type (`int`, `float`, `str`, or `None`), inject the raw value directly into the execution namespace instead of wrapping it in a `SymbolProxy`. Indexed data (dicts, lists, arrays) continues to use `SymbolProxy` as before.

**Detection heuristic:** `isinstance(data, (int, float, str))` or `data is None`. This is conservative — only plain Python scalars are unwrapped.

**Access logging:** Scalar values bypass `SymbolProxy.__getitem__`, so they won't appear in the access log via proxy interception. Instead, use the existing source-tokenization path (`_extract_names_from_source()` in `checks.py`) to detect scalar symbol references. This path already exists for structural mode (no-fixture validation). For numeric mode with scalars, apply it selectively: after executing each validation block, tokenize the source and add any referenced scalar symbol names to the access log.

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

When `strict=True`, add a secondary check after execution: if the registry contains zero `Set` symbols, auto-demote orphan errors to warnings. This is the "scalar model heuristic" — no sets means no indexed cross-references exist, so orphan symbols are expected and harmless.

Implementation: after `execute_blocks()`, if `strict=True` and `registry` has no sets, re-run with effective strict=False (or filter orphan errors from the result and move them to warnings).

#### CLI

Add `--no-strict` flag to the `compile` subcommand:

```python
compile_parser.add_argument("--no-strict", action="store_true",
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

- **Scalar auto-unwrap:** Test that scalar fixture values are injected as raw types, arithmetic works in expressions, and access logging still detects scalar references.
- **Strict mode:** Test the three-cell behavior matrix. Test that non-orphan errors (phantoms, cycles, unit mismatches) remain errors regardless of mode.
- **Report `__str__`:** Test `str(report) == report.to_text()`.
- **Signatures:** Test that `compile_document()` produces identical output before and after the refactor. Test new keyword-only signatures directly.
- **Integration:** Compile the `Organizational_Productivity_Optimization.model.md` scalar model end-to-end with no workarounds.

## Files Changed

| File | Change |
|------|--------|
| `src/meta_compiler/proxy.py` | No change (SymbolProxy stays as-is) |
| `src/meta_compiler/registry.py` | Scalar detection in `_make_proxy()`, selective source-tokenization for access logging |
| `src/meta_compiler/checks.py` | Expose scalar-aware access logging helper |
| `src/meta_compiler/compiler/__init__.py` | Add `strict` param to `compile_document()`, scalar auto-detection logic |
| `src/meta_compiler/compiler/report.py` | Add `Report.__str__`, change `generate_report` signature |
| `src/meta_compiler/compiler/runner.py` | Change `generate_runner` signature |
| `src/meta_compiler/cli.py` | Add `--no-strict` flag to `compile` subcommand |

## Out of Scope

- Adding a `registry.scalars()` helper (suggested in #3 but unnecessary with auto-unwrap)
- Refactoring `SymbolProxy` to add arithmetic operators (replaced by auto-unwrap approach)
- Changes to `generate_paper` signature (already consistent)
