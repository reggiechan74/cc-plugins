# Design: `python:results` Block Type

**Date:** 2026-03-21
**Status:** Draft
**Issue:** [#10](https://github.com/reggiechan74/cc-plugins/issues/10) — computed values lost when code blocks stripped during compilation

## Problem

When the meta-compiler produces `paper.md`, it strips all `python:fixture` and `python:validate` blocks. Numerical results computed in fixture blocks are invisible in the compiled paper. The prose says "the solution yields" but the actual solved values exist only in code. Authors must manually extract and hardcode values — error-prone, tedious, and defeats validated computation.

## Solution

Add a third code block type, `python:results`, that executes Python in the fixture namespace and replaces itself with its stdout in the compiled paper.

### Block Type

```python
@dataclass
class ResultsBlock:
    code: str
    line_number: int
    output: str | None = None  # Populated by executor
```

The parser recognizes `` ```python:results `` fences using the same pattern as fixture and validate blocks. The `Block` union becomes:

```python
Block = ProseBlock | MathBlock | ValidationBlock | FixtureBlock | ResultsBlock
```

### Execution Order

Results blocks execute **after** fixtures but **before** validation:

1. **Fixture blocks** — execute via `exec()` into `fixture_ns`, populate `registry.data_store`
2. **Results blocks** — execute in `fixture_ns`, capture stdout via `io.StringIO` + `contextlib.redirect_stdout`, store in `block.output`
3. **Validation blocks** — register DSL symbols, check constraints numerically

The existing executor collects blocks by type via list comprehensions (`fixture_blocks = [b for b in blocks if isinstance(b, FixtureBlock)]`). A third collection pass for `ResultsBlock` is added between the fixture and validation loops, following the same pattern.

Results blocks run in the fixture namespace because they display computed values, not model structure. Running before validation means computed values are visible even when debugging validation failures.

**Error handling:** If a results block raises an exception (including `NameError` for undefined variables), the error is appended to `ExecutionResult.errors` with the source line number, and the executor returns early with `passed=False`. This follows the same pattern as fixture block errors (executor.py lines 66-70).

**Empty output:** A results block that runs successfully but prints nothing produces an empty string. This is treated as no output — the block is silently omitted from the paper, same as fixture/validate blocks.

### Paper Generation

In `paper.py`, results blocks are the only code block type that produces output:

```python
elif isinstance(block, ResultsBlock) and block.output:
    parts.append(block.output.rstrip())
```

The captured stdout replaces the code block in-place. Output is raw markdown — results blocks can produce tables, bullet lists, inline math, or any valid markdown.

Fixture and validate blocks remain silently skipped.

### Runner Generation

The existing runner generator filters blocks by type into `fixture_blocks` and `validate_blocks` lists. A third list, `results_blocks`, is added. Results block code is emitted indented into `main()`, placed after fixture blocks and the `registry.data_store` population, but before validation blocks. Output goes directly to the console via unmediated `print()` calls — no stdout capture in the runner. This makes the runner a complete reproduction of both validation and displayed results.

### Depth Filtering

Results blocks respect the same depth filtering as other blocks. If a results block appears after a `<!-- depth:appendix -->` marker, it is excluded when compiling at `technical` or `executive` depth. The `_filter_by_depth` function in `paper.py` does not need changes — it operates on the block list before the paper generation loop, and non-`ProseBlock` types pass through the filter based on the current depth state.

### Coverage Metric

Results blocks are transparent to the `coverage_metric()` function in `parser.py`. They do not count as `ValidationBlock` for coverage purposes — a math block still requires a following validation block to be considered "covered." Results blocks falling between a math block and its validation block are harmless (they pass through the isinstance checks).

### Validation Guarantees

The values displayed in the paper are the **same Python objects** that fixture blocks computed and that validation blocks checked constraints against. There is no copy, lookup, or translation layer.

- If `H_f_star = 1.847` passes `Constraint("boundary_positive", expr=lambda: H_f_star > 0)`, then `print(f"{H_f_star:.4f}")` in a results block displays `1.847` — guaranteed by object identity.
- If a fixture value changes, the results block output changes on the next compile.
- If a results block references an undefined variable, `exec()` raises a `NameError` and compilation fails — stale references are caught automatically.
- Phantom/orphan detection is **not** extended to results blocks. These checks operate on the validation namespace (DSL symbols). Results blocks reference raw Python variables in the fixture namespace. The `NameError`-on-undefined guarantee is sufficient.

## Example

### Source (`.model.md`)

````markdown
## 5.3 Stage-Dependent Free Boundaries

The optimal stopping problem yields stage-dependent free boundaries
that determine employer termination and employee quit thresholds.

```python:fixture
import numpy as np
H_f_star = 1.847
H_q_star = 0.312
boundaries = {
    "stage_1": (1.92, 0.29),
    "stage_2": (1.85, 0.31),
    "stage_3": (1.78, 0.33),
}
```

```python:results
print(f"The termination boundary is $H_f^* = {H_f_star:.3f}$ "
      f"and the quit boundary is $H_q^* = {H_q_star:.3f}$.")
print()
print("| Stage | $H_f^*$ | $H_q^*$ |")
print("|-------|---------|---------|")
for stage, (hf, hq) in boundaries.items():
    label = stage.replace("_", " ").title()
    print(f"| {label} | {hf:.2f} | {hq:.2f} |")
```

```python:validate
Parameter("H_f_star", description="Termination boundary")
Parameter("H_q_star", description="Quit boundary")
Constraint("boundary_ordering",
           expr=lambda: H_f_star > H_q_star,
           description="Termination above quit")
```
````

### Compiled Output (`paper.md`)

```markdown
## 5.3 Stage-Dependent Free Boundaries

The optimal stopping problem yields stage-dependent free boundaries
that determine employer termination and employee quit thresholds.

The termination boundary is $H_f^* = 1.847$ and the quit boundary is $H_q^* = 0.312$.

| Stage | $H_f^*$ | $H_q^*$ |
|-------|---------|---------|
| Stage 1 | 1.92 | 0.29 |
| Stage 2 | 1.85 | 0.31 |
| Stage 3 | 1.78 | 0.33 |
```

## Files to Change

| File | Change |
|------|--------|
| `compiler/parser.py` | Add `ResultsBlock` dataclass, recognize `python:results` fences, update `Block` union |
| `compiler/executor.py` | Execute results blocks in `fixture_ns` after fixtures, capture stdout |
| `compiler/paper.py` | Emit `block.output` for `ResultsBlock` instead of stripping |
| `compiler/runner.py` | Include results blocks in standalone runner |
| `compiler/__init__.py` | No code changes. The executor mutates `ResultsBlock.output` in place on the same block objects that `generate_paper` later reads — shared mutability makes this work without explicit wiring. |
| `compiler/report.py` | No changes needed. Report builds from registry symbols, not block types. |

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Fixture namespace, not validation | Results display computed values, not model structure. No need for DSL symbols or proxies. |
| Execute before validation | Computed values visible even when debugging validation failures. |
| Mutable `output` field on dataclass | Avoids creating a parallel data structure to carry captured output through the pipeline. |
| No phantom/orphan checks for results | These checks are for DSL symbols. Results blocks use raw Python variables — `NameError` on undefined is sufficient. |
| Stdout capture, not return value | Stdout allows multiple print statements, formatted tables, conditional output — full Python expressiveness. |
