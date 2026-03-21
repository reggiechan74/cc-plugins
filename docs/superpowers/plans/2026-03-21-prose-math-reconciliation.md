# Prose-Math Reconciliation Checkpoint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a prose-math reconciliation checkpoint to the author skill that catches interpretation errors after each section is written.

**Architecture:** Three automated check functions in `checks.py` (value reporting, constraint tolerance via AST, directional claims) exposed through a `reconcile` CLI subcommand. The author skill invokes this after meta-compiler validation passes, followed by a manual reconciliation prompt.

**Tech Stack:** Python 3, `ast` module for constraint source inspection, existing meta-compiler parser/executor infrastructure.

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `math-paper-creator/src/meta_compiler/checks.py` | Modify | Add 3 reconciliation check functions + `run_reconciliation_checks()` |
| `math-paper-creator/src/meta_compiler/cli.py` | Modify | Add `reconcile` subcommand with `--section` flag |
| `math-paper-creator/src/meta_compiler/compiler/parser.py` | Modify | Add `extract_section_blocks()` helper for section scoping |
| `math-paper-creator/commands/author.md` | Modify | Add reconciliation checkpoint between Steps 3.5.2 and 3.5.3 |
| `math-paper-creator/tests/test_reconciliation.py` | Create | Unit tests for the 3 check functions |
| `math-paper-creator/tests/compiler/test_reconcile_cli.py` | Create | Integration tests for CLI `reconcile` subcommand |

---

### Task 1: Section scoping helper in parser.py

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/compiler/parser.py`
- Test: `math-paper-creator/tests/compiler/test_parser.py`

The `reconcile` CLI needs to scope checks to a specific section. Add a helper that extracts blocks belonging to a named section.

- [ ] **Step 1: Write the failing test**

Add to `tests/compiler/test_parser.py`:

```python
from meta_compiler.compiler.parser import parse_document, extract_section_blocks, ProseBlock, ValidationBlock


def test_extract_section_blocks_isolates_named_section():
    """extract_section_blocks returns only blocks under the named heading."""
    doc = """## Setup

Some setup prose.

```python:validate
Set("W", description="Workers")
```

## Analysis

Analysis prose here.

```python:validate
Parameter("cap", index="W", description="Cap")
```

## Conclusion

Final prose.
"""
    blocks = parse_document(doc)
    section_blocks = extract_section_blocks(blocks, "Analysis")
    # Should contain the Analysis prose and its validate block
    assert len(section_blocks) == 2
    assert isinstance(section_blocks[0], ProseBlock)
    assert "Analysis prose" in section_blocks[0].content
    assert isinstance(section_blocks[1], ValidationBlock)


def test_extract_section_blocks_respects_heading_level():
    """Stops at same-or-higher heading level, includes sub-headings."""
    doc = """## Section A

Prose A.

### Subsection A.1

Sub prose.

## Section B

Prose B.
"""
    blocks = parse_document(doc)
    section_blocks = extract_section_blocks(blocks, "Section A")
    prose_text = " ".join(b.content for b in section_blocks if isinstance(b, ProseBlock))
    assert "Prose A" in prose_text
    assert "Sub prose" in prose_text
    assert "Prose B" not in prose_text


def test_extract_section_blocks_unknown_heading_returns_empty():
    doc = "## Intro\n\nSome text.\n"
    blocks = parse_document(doc)
    assert extract_section_blocks(blocks, "Nonexistent") == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_parser.py::test_extract_section_blocks_isolates_named_section tests/compiler/test_parser.py::test_extract_section_blocks_respects_heading_level tests/compiler/test_parser.py::test_extract_section_blocks_unknown_heading_returns_empty -v`
Expected: FAIL with ImportError (extract_section_blocks doesn't exist)

- [ ] **Step 3: Implement extract_section_blocks**

Add at the end of `math-paper-creator/src/meta_compiler/compiler/parser.py`:

```python
def extract_section_blocks(blocks: list[Block], heading: str) -> list[Block]:
    """Extract blocks belonging to a specific section heading.

    Finds the ProseBlock containing the heading, then collects all blocks
    until the next heading at the same or higher level (fewer '#' characters).
    """
    target_level = 0
    start_idx = None

    for i, block in enumerate(blocks):
        if not isinstance(block, ProseBlock):
            continue
        for line in block.content.split("\n"):
            stripped = line.strip()
            if not stripped.startswith("#"):
                continue
            hashes = len(stripped) - len(stripped.lstrip("#"))
            title = stripped.lstrip("#").strip()
            if title == heading:
                target_level = hashes
                start_idx = i
                break
        if start_idx is not None:
            break

    if start_idx is None:
        return []

    result: list[Block] = [blocks[start_idx]]
    for block in blocks[start_idx + 1:]:
        if isinstance(block, ProseBlock):
            for line in block.content.split("\n"):
                stripped = line.strip()
                if stripped.startswith("#"):
                    hashes = len(stripped) - len(stripped.lstrip("#"))
                    if hashes <= target_level:
                        return result
        result.append(block)

    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_parser.py -v -k "extract_section"`
Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add math-paper-creator/src/meta_compiler/compiler/parser.py math-paper-creator/tests/compiler/test_parser.py
git commit -m "feat(meta-compiler): add extract_section_blocks helper for section scoping"
```

---

### Task 2: check_directional_claims

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/checks.py`
- Test: `math-paper-creator/tests/test_reconciliation.py` (create)

Simplest of the three checks — no registry dependency. Start here.

- [ ] **Step 1: Write the failing tests**

Create `math-paper-creator/tests/test_reconciliation.py`:

```python
import pytest
from meta_compiler.compiler.parser import ProseBlock
from meta_compiler.checks import check_directional_claims


class TestCheckDirectionalClaims:
    def test_flags_increases(self):
        blocks = [ProseBlock(content="Higher σ increases the outside option.\n")]
        warnings = check_directional_claims(blocks)
        assert len(warnings) == 1
        assert "increases" in warnings[0].lower()

    def test_flags_multiple_keywords(self):
        blocks = [ProseBlock(content="As x increases, y decreases and is monotone.\n")]
        warnings = check_directional_claims(blocks)
        # Should flag "increases", "decreases", and "monotone"
        assert len(warnings) == 3

    def test_no_warnings_for_clean_prose(self):
        blocks = [ProseBlock(content="The model defines a set of workers.\n")]
        warnings = check_directional_claims(blocks)
        assert warnings == []

    def test_ignores_non_prose_blocks(self):
        """Only ProseBlock content is scanned."""
        from meta_compiler.compiler.parser import ValidationBlock
        blocks = [ValidationBlock(code="# value increases here", line_number=1)]
        warnings = check_directional_claims(blocks)
        assert warnings == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd math-paper-creator && python -m pytest tests/test_reconciliation.py::TestCheckDirectionalClaims -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Implement check_directional_claims**

Add to `math-paper-creator/src/meta_compiler/checks.py` (after existing imports, add `import re` and `from meta_compiler.compiler.parser import Block, ProseBlock`):

```python
import re

from meta_compiler.compiler.parser import Block, ProseBlock

_DIRECTIONAL_KEYWORDS = re.compile(
    r'\b(increases|decreases|widens|narrows|higher|lower'
    r'|maximizes|minimizes|monotone|non-monotone)\b',
    re.IGNORECASE,
)


def check_directional_claims(blocks: list[Block]) -> list[str]:
    """Flag directional keywords in prose for manual verification."""
    warnings: list[str] = []
    for block in blocks:
        if not isinstance(block, ProseBlock):
            continue
        for line in block.content.split("\n"):
            for match in _DIRECTIONAL_KEYWORDS.finditer(line):
                keyword = match.group()
                # Show ~40 chars of context around the match
                start = max(0, match.start() - 20)
                end = min(len(line), match.end() + 20)
                context = line[start:end].strip()
                warnings.append(
                    f'Directional claim "{keyword}": "...{context}..." '
                    f"— verify against computed values"
                )
    return warnings
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd math-paper-creator && python -m pytest tests/test_reconciliation.py::TestCheckDirectionalClaims -v`
Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add math-paper-creator/src/meta_compiler/checks.py math-paper-creator/tests/test_reconciliation.py
git commit -m "feat(meta-compiler): add check_directional_claims for prose reconciliation"
```

---

### Task 3: check_value_reporting

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/checks.py`
- Modify: `math-paper-creator/tests/test_reconciliation.py`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_reconciliation.py`:

```python
from meta_compiler.checks import check_value_reporting
from meta_compiler.registry import registry


class TestCheckValueReporting:
    def setup_method(self):
        registry.reset()

    def test_warns_when_values_computed_but_not_reported(self):
        registry.register_set("W", description="Workers")
        registry.register_parameter("cap", index="W", description="Cap")
        registry.data_store = {"W": ["a"], "cap": {"a": 40}}
        blocks = [ProseBlock(content="The model defines capacity constraints.\n")]
        warnings = check_value_reporting(blocks, registry)
        assert len(warnings) == 1
        assert "computes" in warnings[0].lower()

    def test_no_warning_when_values_reported_in_prose(self):
        registry.register_set("W", description="Workers")
        registry.register_parameter("cap", index="W", description="Cap")
        registry.data_store = {"W": ["a"], "cap": {"a": 40}}
        blocks = [ProseBlock(content="The capacity is 40 hours per worker.\n")]
        warnings = check_value_reporting(blocks, registry)
        assert warnings == []

    def test_no_warning_when_no_computed_values(self):
        registry.register_set("W", description="Workers")
        blocks = [ProseBlock(content="We define a set of workers.\n")]
        warnings = check_value_reporting(blocks, registry)
        assert warnings == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd math-paper-creator && python -m pytest tests/test_reconciliation.py::TestCheckValueReporting -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Implement check_value_reporting**

Add to `math-paper-creator/src/meta_compiler/checks.py`:

```python
def check_value_reporting(blocks: list[Block], registry: "Registry") -> list[str]:
    """Warn if a section computes values but prose doesn't mention any."""
    # Collect numeric values from data_store
    numeric_values: set[str] = set()
    for name, data in registry.data_store.items():
        if name in registry.symbols and isinstance(
            registry.symbols[name], (ParameterSymbol, VariableSymbol, ExpressionSymbol)
        ):
            if isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, (int, float)):
                        numeric_values.add(str(v))
            elif isinstance(data, (int, float)):
                numeric_values.add(str(data))

    if not numeric_values:
        return []

    # Check if any numeric value appears in prose
    prose_text = " ".join(
        block.content for block in blocks if isinstance(block, ProseBlock)
    )

    for val in numeric_values:
        if val in prose_text:
            return []

    return [
        f"Section computes {len(numeric_values)} value(s) but prose reports none "
        f"(values: {', '.join(sorted(numeric_values)[:5])})"
    ]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd math-paper-creator && python -m pytest tests/test_reconciliation.py::TestCheckValueReporting -v`
Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add math-paper-creator/src/meta_compiler/checks.py math-paper-creator/tests/test_reconciliation.py
git commit -m "feat(meta-compiler): add check_value_reporting for prose reconciliation"
```

---

### Task 4: check_constraint_tolerance

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/checks.py`
- Modify: `math-paper-creator/tests/test_reconciliation.py`

This check inspects constraint expression source code via `ast` to find arithmetic offsets in comparisons.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_reconciliation.py`:

```python
from meta_compiler.checks import check_constraint_tolerance


class TestCheckConstraintTolerance:
    def setup_method(self):
        registry.reset()

    def test_flags_large_arithmetic_offset(self):
        registry.register_set("W", description="Workers")
        registry.register_parameter("V_W", index="W", description="Value")
        registry.register_constraint(
            "participation", over="W", constraint_type="hard",
            description="Participation",
            expr=lambda i: V_W[i] >= 2750 - 50,
        )
        warnings = check_constraint_tolerance(registry)
        assert len(warnings) == 1
        assert "50" in warnings[0]
        assert "participation" in warnings[0].lower()

    def test_ignores_small_offset(self):
        registry.register_set("W", description="Workers")
        registry.register_constraint(
            "tight", over="W", constraint_type="hard",
            description="Tight",
            expr=lambda i: x[i] >= 100 - 1e-6,
        )
        warnings = check_constraint_tolerance(registry)
        assert warnings == []

    def test_ignores_no_comparison(self):
        registry.register_set("W", description="Workers")
        registry.register_constraint(
            "simple", over="W", constraint_type="hard",
            description="Simple",
            expr=lambda i: True,
        )
        warnings = check_constraint_tolerance(registry)
        assert warnings == []

    def test_flags_addition_offset(self):
        registry.register_set("W", description="Workers")
        registry.register_constraint(
            "slack", over="W", constraint_type="hard",
            description="Slack",
            expr=lambda i: x[i] <= 100 + 25,
        )
        warnings = check_constraint_tolerance(registry)
        assert len(warnings) == 1
        assert "25" in warnings[0]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd math-paper-creator && python -m pytest tests/test_reconciliation.py::TestCheckConstraintTolerance -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Implement check_constraint_tolerance**

Add to `math-paper-creator/src/meta_compiler/checks.py` (add `import ast` to imports):

```python
import ast

_TOLERANCE_THRESHOLD = 1.0


def check_constraint_tolerance(registry: "Registry") -> list[str]:
    """Flag constraints with suspiciously large arithmetic offsets."""
    warnings: list[str] = []

    for name, sym in registry.symbols.items():
        if not isinstance(sym, ConstraintSymbol):
            continue
        if sym.expr is None:
            continue

        try:
            source = inspect.getsource(sym.expr)
        except (OSError, TypeError):
            source = getattr(sym.expr, "_source_text", "")
            if not source:
                continue

        offsets = _find_arithmetic_offsets(source)
        for offset_val in offsets:
            if abs(offset_val) > _TOLERANCE_THRESHOLD:
                warnings.append(
                    f'Constraint "{name}" has arithmetic offset {offset_val} '
                    f"in comparison — verify this is intentional"
                )

    return warnings


def _find_arithmetic_offsets(source: str) -> list[float]:
    """Find numeric literals used as +/- offsets in comparison expressions."""
    offsets: list[float] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return offsets

    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        # Check both sides of comparisons for BinOp with Add/Sub
        all_exprs = [node.left] + list(node.comparators)
        for expr in all_exprs:
            if isinstance(expr, ast.BinOp) and isinstance(expr.op, (ast.Add, ast.Sub)):
                # Check if right operand is a numeric literal
                num = _extract_num(expr.right)
                if num is not None:
                    offsets.append(num)
                # Also check left operand
                num = _extract_num(expr.left)
                if num is not None:
                    offsets.append(num)

    return offsets


def _extract_num(node: ast.expr) -> float | None:
    """Extract a numeric value from an AST node."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        inner = _extract_num(node.operand)
        if inner is not None:
            return -inner
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd math-paper-creator && python -m pytest tests/test_reconciliation.py::TestCheckConstraintTolerance -v`
Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add math-paper-creator/src/meta_compiler/checks.py math-paper-creator/tests/test_reconciliation.py
git commit -m "feat(meta-compiler): add check_constraint_tolerance for prose reconciliation"
```

---

### Task 5: run_reconciliation_checks and CLI reconcile subcommand

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/checks.py`
- Modify: `math-paper-creator/src/meta_compiler/cli.py`
- Modify: `math-paper-creator/src/meta_compiler/compiler/__init__.py`
- Test: `math-paper-creator/tests/compiler/test_reconcile_cli.py` (create)

- [ ] **Step 1: Write the failing tests**

Create `math-paper-creator/tests/compiler/test_reconcile_cli.py`:

```python
import os
import subprocess
from pathlib import Path

_SRC = str(Path(__file__).parent.parent.parent / "src")
_CLI_ENV = {**os.environ, "PYTHONPATH": _SRC}


def test_reconcile_cli_flags_directional_claims():
    """reconcile command flags directional keywords in prose."""
    doc = """## Setup

```python:validate
Set("W", description="Workers")
```

## Analysis

As sigma increases, the outside option widens.

```python:validate
Parameter("sigma", index="W", description="Volatility")
```
"""
    tmp = Path("/tmp/test_reconcile.model.md")
    tmp.write_text(doc)
    result = subprocess.run(
        ["python", "-m", "meta_compiler.cli", "reconcile", str(tmp), "--section", "Analysis"],
        capture_output=True, text=True, env=_CLI_ENV,
    )
    assert result.returncode == 2
    assert "increases" in result.stdout.lower()
    assert "widens" in result.stdout.lower()
    tmp.unlink()


def test_reconcile_cli_clean_section():
    """reconcile command returns 0 for clean section."""
    doc = """## Setup

```python:validate
Set("W", description="Workers")
```

## Analysis

We define a parameter for the worker set.

```python:validate
Parameter("cap", index="W", description="Cap")
```
"""
    tmp = Path("/tmp/test_reconcile_clean.model.md")
    tmp.write_text(doc)
    result = subprocess.run(
        ["python", "-m", "meta_compiler.cli", "reconcile", str(tmp), "--section", "Analysis"],
        capture_output=True, text=True, env=_CLI_ENV,
    )
    assert result.returncode == 0
    assert "Reconciliation: OK" in result.stdout
    tmp.unlink()


def test_reconcile_cli_scopes_to_section():
    """reconcile command does not flag issues in other sections."""
    doc = """## Setup

The value increases over time.

```python:validate
Set("W", description="Workers")
```

## Analysis

We define a parameter.

```python:validate
Parameter("cap", index="W", description="Cap")
```
"""
    tmp = Path("/tmp/test_reconcile_scope.model.md")
    tmp.write_text(doc)
    result = subprocess.run(
        ["python", "-m", "meta_compiler.cli", "reconcile", str(tmp), "--section", "Analysis"],
        capture_output=True, text=True, env=_CLI_ENV,
    )
    # "increases" is in Setup, not Analysis — should not be flagged
    assert result.returncode == 0
    assert "increases" not in result.stdout.lower()
    tmp.unlink()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_reconcile_cli.py -v`
Expected: FAIL

- [ ] **Step 3: Add run_reconciliation_checks to checks.py**

Add to `math-paper-creator/src/meta_compiler/checks.py`:

```python
def run_reconciliation_checks(
    blocks: list[Block], registry: "Registry"
) -> list[str]:
    """Run all prose-math reconciliation checks. Returns list of warnings."""
    warnings: list[str] = []
    warnings.extend(check_value_reporting(blocks, registry))
    warnings.extend(check_constraint_tolerance(registry))
    warnings.extend(check_directional_claims(blocks))
    return warnings
```

- [ ] **Step 4: Add reconcile_document to compiler/__init__.py**

Add to `math-paper-creator/src/meta_compiler/compiler/__init__.py`:

```python
from meta_compiler.compiler.parser import extract_section_blocks
from meta_compiler.checks import run_reconciliation_checks


def reconcile_document(
    source: str, *, section: str | None = None, strict: bool = False
) -> tuple[list[str], bool]:
    """Parse, execute, and run reconciliation checks.

    Returns (warnings, validation_passed). Executes the full document to
    populate the registry, then scopes reconciliation checks to the named
    section (if provided).
    """
    blocks = parse_document(source)
    result = execute_blocks(blocks, strict=strict)

    if section:
        scoped_blocks = extract_section_blocks(blocks, section)
    else:
        scoped_blocks = blocks

    warnings = run_reconciliation_checks(scoped_blocks, result.registry)
    return warnings, result.passed
```

- [ ] **Step 5: Add reconcile subcommand to cli.py**

Add to `math-paper-creator/src/meta_compiler/cli.py`:

In the `main()` function, after the `compile_parser` block (around line 60), add:

```python
    # reconcile
    reconcile_parser = subparsers.add_parser(
        "reconcile", help="Run prose-math reconciliation checks"
    )
    reconcile_parser.add_argument("file", type=Path, help="Path to .model.md file")
    reconcile_parser.add_argument(
        "--section", type=str, default=None,
        help="Scope checks to a specific section heading"
    )
```

In the command dispatch block (around line 74), add before `return 1`:

```python
    elif args.command == "reconcile":
        return _cmd_reconcile(source, section=args.section)
```

Add the handler function:

```python
def _cmd_reconcile(source: str, *, section: str | None) -> int:
    from meta_compiler.compiler import reconcile_document

    warnings, _ = reconcile_document(source, section=section)
    if warnings:
        print("Reconciliation warnings:")
        for w in warnings:
            print(f"  WARNING: {w}")
        return 2
    else:
        print("Reconciliation: OK")
        return 0
```

Update the module docstring to include the new command:

```
    python -m meta_compiler.cli reconcile <file.model.md> [--section "<heading>"]
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_reconcile_cli.py -v`
Expected: 3 PASSED

- [ ] **Step 7: Run full test suite**

Run: `cd math-paper-creator && python -m pytest -v`
Expected: All tests PASS

- [ ] **Step 8: Commit**

```bash
git add math-paper-creator/src/meta_compiler/checks.py math-paper-creator/src/meta_compiler/cli.py math-paper-creator/src/meta_compiler/compiler/__init__.py math-paper-creator/tests/compiler/test_reconcile_cli.py
git commit -m "feat(meta-compiler): add reconcile CLI subcommand for prose-math checks"
```

---

### Task 6: Author skill integration

**Files:**
- Modify: `math-paper-creator/commands/author.md:200-214`

- [ ] **Step 1: Read the current Step 3.5 in author.md**

Read `math-paper-creator/commands/author.md` lines 200-214 to confirm exact content before editing.

- [ ] **Step 2: Add reconciliation checkpoint**

After Step 3.5 item 3 ("If the check fails...") and before item 4 ("If the check passes..."), insert:

```markdown
4. **Prose-math reconciliation.** After the meta-compiler check passes, run reconciliation checks scoped to the current section:
   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && PYTHONPATH=src python3 -m meta_compiler.cli reconcile "<file_path>" --section "<heading>"
   ```
   - If warnings are printed, show them to the user.
   - Then show the manual reconciliation prompt:
     > "Reconciliation check:
     > - Do the interpretation paragraphs match the computed values?
     > - Are spatial/directional claims consistent with the boundary values?
     > - Are any claims made about variables that don't appear in the section's equations?
     >
     > Type 'confirmed' to proceed, or describe issues."
   - If the user describes issues: revise the section in `.model.md`, re-run the meta-compiler check (item 2 above), then re-run reconciliation.
   - If the user confirms: proceed to the next item.
```

Renumber the existing item 4 ("If the check passes...") to item 5.

- [ ] **Step 3: Verify the edit is correct**

Read the modified section to confirm numbering and flow are correct.

- [ ] **Step 4: Commit**

```bash
git add math-paper-creator/commands/author.md
git commit -m "feat(author): add prose-math reconciliation checkpoint to section loop"
```

---

### Task 7: Final verification

- [ ] **Step 1: Run full test suite**

Run: `cd math-paper-creator && python -m pytest -v`
Expected: All tests PASS (including new reconciliation tests)

- [ ] **Step 2: Manual smoke test of CLI**

Run: `cd math-paper-creator && echo '## Analysis\n\nAs sigma increases, the value widens.\n\n```python:validate\nSet("W", description="Workers")\n```' > /tmp/smoke.model.md && PYTHONPATH=src python3 -m meta_compiler.cli reconcile /tmp/smoke.model.md --section "Analysis"`
Expected: Exit code 2, warnings for "increases" and "widens"

- [ ] **Step 3: Verify clean document**

Run: `cd math-paper-creator && echo '## Analysis\n\nWe define a set of workers.\n\n```python:validate\nSet("W", description="Workers")\n```' > /tmp/smoke_clean.model.md && PYTHONPATH=src python3 -m meta_compiler.cli reconcile /tmp/smoke_clean.model.md --section "Analysis"`
Expected: Exit code 0, "Reconciliation: OK"
