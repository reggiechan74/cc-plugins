# `python:results` Block Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `python:results` block type that executes in the fixture namespace and replaces itself with its stdout in the compiled paper, so computed values appear in the published output.

**Architecture:** New `ResultsBlock` dataclass flows through the existing parse → execute → generate pipeline. The parser recognizes `python:results` fences, the executor runs them in the fixture namespace and captures stdout, and the paper generator emits the captured output. Four files change; `__init__.py` and `report.py` need no modifications.

**Tech Stack:** Python 3.10+, pytest, `io.StringIO`, `contextlib.redirect_stdout`

**Spec:** `docs/superpowers/specs/2026-03-21-results-block-design.md`

---

### Task 1: Parser — Add `ResultsBlock` and parse `python:results` fences

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/compiler/parser.py:37-43` (add dataclass, update Block union)
- Modify: `math-paper-creator/src/meta_compiler/compiler/parser.py:60-77` (add fence recognition)
- Test: `math-paper-creator/tests/compiler/test_parser.py`

- [ ] **Step 1: Write failing test — ResultsBlock is parseable**

Add to `tests/compiler/test_parser.py`:

```python
from meta_compiler.compiler.parser import ResultsBlock

def test_parse_results_block():
    source = '''# Model

```python:fixture
x = 42
```

```python:results
print(f"x = {x}")
```
'''
    blocks = parse_document(source)
    results_blocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    assert len(results_blocks) == 1
    assert 'print(f"x = {x}")' in results_blocks[0].code


def test_parse_results_block_tracks_line_number():
    source = "# Title\n\n```python:results\nprint('hi')\n```\n"
    blocks = parse_document(source)
    rblocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    assert len(rblocks) == 1
    assert rblocks[0].line_number == 4  # line after the fence


def test_coverage_results_does_not_interrupt():
    """A results block between math and validate doesn't break coverage."""
    source = '''# Model

$$x = 1$$

```python:results
print("x is 1")
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

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_parser.py::test_parse_results_block tests/compiler/test_parser.py::test_parse_results_block_tracks_line_number tests/compiler/test_parser.py::test_coverage_results_does_not_interrupt -v`

Expected: ImportError — `ResultsBlock` does not exist yet.

- [ ] **Step 3: Implement ResultsBlock dataclass and parser recognition**

In `parser.py`, add the dataclass after `FixtureBlock`:

```python
@dataclass
class ResultsBlock:
    """A python:results fenced code block — stdout replaces block in paper."""
    code: str
    line_number: int
    output: str | None = None  # Populated by executor
```

Update the `Block` union:

```python
Block = ProseBlock | MathBlock | ValidationBlock | FixtureBlock | ResultsBlock
```

In `parse_document()`, add recognition for `python:results` fences after the `python:fixture` check (before the `python:validate` check). Follow the exact same pattern as fixture block parsing:

```python
# Check for results block: ```python:results
if line.strip().startswith("```python:results"):
    flush_prose()
    code_lines: list[str] = []
    start_line = i + 1
    i += 1
    while i < len(lines) and not lines[i].strip().startswith("```"):
        code_lines.append(lines[i])
        i += 1
    blocks.append(ResultsBlock(
        code="\n".join(code_lines),
        line_number=start_line,
    ))
    i += 1  # Skip closing ```
    continue
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_parser.py -v`

Expected: All pass, including the 3 new tests.

- [ ] **Step 5: Commit**

```bash
git add math-paper-creator/src/meta_compiler/compiler/parser.py math-paper-creator/tests/compiler/test_parser.py
git commit -m "feat(meta-compiler): add ResultsBlock type and parser recognition"
```

---

### Task 2: Executor — Execute results blocks in fixture namespace, capture stdout

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/compiler/executor.py:16` (import ResultsBlock)
- Modify: `math-paper-creator/src/meta_compiler/compiler/executor.py:56-75` (add results execution after fixtures)
- Test: `math-paper-creator/tests/compiler/test_executor.py`

- [ ] **Step 1: Write failing tests — results blocks execute and capture stdout**

Add to `tests/compiler/test_executor.py`:

```python
RESULTS_DOC = '''# Model

```python:fixture
W = ["alice", "bob"]
cap = {"alice": 40, "bob": 35}
```

```python:results
for w in W:
    print(f"| {w} | {cap[w]} |")
```

```python:validate
Set("W", description="Workers")
Parameter("cap", index="W", units="hours", description="Capacity")
Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
```
'''

def test_results_block_captures_stdout():
    from meta_compiler.compiler.parser import ResultsBlock
    blocks = parse_document(RESULTS_DOC)
    result = execute_blocks(blocks)
    assert result.passed
    rblocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    assert len(rblocks) == 1
    assert "| alice | 40 |" in rblocks[0].output
    assert "| bob | 35 |" in rblocks[0].output


RESULTS_ERROR_DOC = '''# Model

```python:fixture
x = 1
```

```python:results
print(undefined_var)
```
'''

def test_results_block_error_fails_compilation():
    blocks = parse_document(RESULTS_ERROR_DOC)
    result = execute_blocks(blocks)
    assert not result.passed
    assert any("Results error" in e for e in result.errors)


RESULTS_NO_FIXTURE_DOC = '''# Model

```python:results
print("no fixtures needed for simple text")
```
'''

def test_results_block_without_fixtures():
    from meta_compiler.compiler.parser import ResultsBlock
    blocks = parse_document(RESULTS_NO_FIXTURE_DOC)
    result = execute_blocks(blocks)
    assert result.passed
    rblocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    assert rblocks[0].output == "no fixtures needed for simple text\n"


RESULTS_MULTI_DOC = '''# Model

```python:fixture
x = 10
y = 20
```

```python:results
print(f"x = {x}")
```

Some prose.

```python:results
print(f"y = {y}")
print(f"sum = {x + y}")
```
'''

def test_multiple_results_blocks():
    from meta_compiler.compiler.parser import ResultsBlock
    blocks = parse_document(RESULTS_MULTI_DOC)
    result = execute_blocks(blocks)
    assert result.passed
    rblocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    assert len(rblocks) == 2
    assert "x = 10" in rblocks[0].output
    assert "y = 20" in rblocks[1].output
    assert "sum = 30" in rblocks[1].output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_executor.py::test_results_block_captures_stdout tests/compiler/test_executor.py::test_results_block_error_fails_compilation tests/compiler/test_executor.py::test_results_block_without_fixtures tests/compiler/test_executor.py::test_multiple_results_blocks -v`

Expected: FAIL — results blocks are not executed yet.

- [ ] **Step 3: Implement results block execution in executor**

In `executor.py`, add import at line 16:

```python
from meta_compiler.compiler.parser import Block, FixtureBlock, ResultsBlock, ValidationBlock
```

After the fixture execution loop (after line 75 where `registry.data_store` is populated), add a new section to execute results blocks. Insert before the validation namespace setup (before the current "Step 2"):

```python
    # Step 1b: Execute results blocks in fixture namespace, capture stdout
    results_blocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    if results_blocks:
        import io
        import contextlib

        for rb in results_blocks:
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    exec(rb.code, fixture_ns if has_fixtures else {})
            except Exception as e:
                errors.append(f"Results error (line {rb.line_number}): {e}")
                return ExecutionResult(passed=False, errors=errors,
                                       warnings=warnings, registry=None)
            rb.output = buf.getvalue()
```

Note: When there are no fixtures, results blocks execute in an empty namespace. This allows simple results blocks like `print("Table of Contents")` without requiring fixtures.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_executor.py -v`

Expected: All pass, including the 3 new tests.

- [ ] **Step 5: Commit**

```bash
git add math-paper-creator/src/meta_compiler/compiler/executor.py math-paper-creator/tests/compiler/test_executor.py
git commit -m "feat(meta-compiler): execute results blocks and capture stdout"
```

---

### Task 3: Paper Generator — Emit results block output

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/compiler/paper.py:5` (import ResultsBlock)
- Modify: `math-paper-creator/src/meta_compiler/compiler/paper.py:28-34` (add ResultsBlock branch)
- Test: `math-paper-creator/tests/compiler/test_paper.py`

- [ ] **Step 1: Write failing tests — paper includes results output**

Add to `tests/compiler/test_paper.py`:

```python
from meta_compiler.compiler.parser import ResultsBlock


def test_paper_includes_results_output():
    """Results block output appears in paper, code does not."""
    source = '''# Model

Some prose.

```python:fixture
x = 42
```

```python:results
print(f"The answer is {x}.")
```

```python:validate
Parameter("x", description="the answer")
```

More prose.
'''
    from meta_compiler.compiler.executor import execute_blocks
    blocks = parse_document(source)
    execute_blocks(blocks)  # populates ResultsBlock.output
    paper = generate_paper(blocks)
    assert "The answer is 42." in paper
    assert "python:results" not in paper
    assert "python:fixture" not in paper
    assert "python:validate" not in paper
    assert "Some prose" in paper
    assert "More prose" in paper


def test_paper_empty_results_omitted():
    """A results block that prints nothing is silently omitted."""
    source = '''# Model

```python:results
pass  # no output
```

Some prose.
'''
    blocks = parse_document(source)
    from meta_compiler.compiler.executor import execute_blocks
    execute_blocks(blocks)
    rblocks = [b for b in blocks if isinstance(b, ResultsBlock)]
    assert rblocks[0].output == ""
    paper = generate_paper(blocks)
    assert "python:results" not in paper
    assert "Some prose" in paper


def test_paper_results_with_depth_filter():
    """Results blocks respect depth filtering."""
    source = '''<!-- depth:executive -->
# Summary

Key findings.

<!-- depth:appendix -->
# Appendix

```python:results
print("Detailed computation log")
```
'''
    blocks = parse_document(source)
    from meta_compiler.compiler.executor import execute_blocks
    execute_blocks(blocks)
    paper = generate_paper(blocks, depth="executive")
    assert "Key findings" in paper
    assert "Detailed computation log" not in paper
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_paper.py::test_paper_includes_results_output tests/compiler/test_paper.py::test_paper_empty_results_omitted tests/compiler/test_paper.py::test_paper_results_with_depth_filter -v`

Expected: FAIL — paper generator does not handle `ResultsBlock` yet.

- [ ] **Step 3: Implement ResultsBlock handling in paper generator**

In `paper.py`, update the import:

```python
from meta_compiler.compiler.parser import Block, MathBlock, ProseBlock, ResultsBlock, ValidationBlock, FixtureBlock
```

In the `generate_paper` loop, add a branch for `ResultsBlock` before the comment about silently skipping:

```python
    for block in blocks:
        if isinstance(block, ProseBlock):
            parts.append(block.content)
        elif isinstance(block, MathBlock):
            parts.append(block.raw)
            parts.append("")
        elif isinstance(block, ResultsBlock) and block.output:
            parts.append(block.output.rstrip())
        # ValidationBlocks and FixtureBlocks are silently skipped
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_paper.py -v`

Expected: All pass, including the 3 new tests.

- [ ] **Step 5: Commit**

```bash
git add math-paper-creator/src/meta_compiler/compiler/paper.py math-paper-creator/tests/compiler/test_paper.py
git commit -m "feat(meta-compiler): emit results block output in paper"
```

---

### Task 4: Runner Generator — Include results blocks in standalone runner

**Files:**
- Modify: `math-paper-creator/src/meta_compiler/compiler/runner.py:10` (import ResultsBlock)
- Modify: `math-paper-creator/src/meta_compiler/compiler/runner.py:23-24` (collect results blocks)
- Modify: `math-paper-creator/src/meta_compiler/compiler/runner.py:74-76` (emit results code after fixtures)
- Test: `math-paper-creator/tests/compiler/test_runner.py`

- [ ] **Step 1: Write failing tests — runner includes results block code**

Add to `tests/compiler/test_runner.py`:

```python
def test_runner_includes_results_blocks():
    from meta_compiler.compiler.parser import parse_document
    source = '''# Model

```python:fixture
x = 42
```

```python:results
print(f"The answer is {x}")
```

```python:validate
Parameter("x", description="the answer")
```
'''
    blocks = parse_document(source)
    script = generate_runner(blocks, model_path="test.model.md")
    assert 'print(f"The answer is {x}")' in script
    compile(script, "<runner>", "exec")  # valid Python


def test_runner_results_without_fixtures():
    from meta_compiler.compiler.parser import parse_document
    source = '''# Model

```python:results
print("hello")
```
'''
    blocks = parse_document(source)
    script = generate_runner(blocks, model_path="test.model.md")
    assert 'print("hello")' in script
    compile(script, "<runner>", "exec")  # valid Python
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_runner.py::test_runner_includes_results_blocks tests/compiler/test_runner.py::test_runner_results_without_fixtures -v`

Expected: FAIL — runner does not include results blocks.

- [ ] **Step 3: Implement results block inclusion in runner**

In `runner.py`, update the import:

```python
from meta_compiler.compiler.parser import Block, FixtureBlock, ResultsBlock, ValidationBlock
```

Add results block collection alongside the existing fixture/validate collection:

```python
results_blocks = [b for b in blocks if isinstance(b, ResultsBlock)]
```

After the fixture code emission and `registry.data_store` population section (around line 74), and before the validation blocks section, add:

```python
    # Emit results blocks — display computed values
    if results_blocks:
        parts.append('    # ── Results blocks ─────────────────────────────────')
        for i, rb in enumerate(results_blocks):
            parts.append(f'    # Results block {i + 1} (source line {rb.line_number})')
            for line in rb.code.splitlines():
                if line.strip():
                    parts.append(f'    {line}')
                else:
                    parts.append('')
            parts.append('')
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_runner.py -v`

Expected: All pass, including the 2 new tests.

- [ ] **Step 5: Commit**

```bash
git add math-paper-creator/src/meta_compiler/compiler/runner.py math-paper-creator/tests/compiler/test_runner.py
git commit -m "feat(meta-compiler): include results blocks in standalone runner"
```

---

### Task 5: Integration Tests — End-to-end with results blocks

**Files:**
- Modify: `math-paper-creator/tests/compiler/test_integration.py`

- [ ] **Step 1: Write integration test — full pipeline with results blocks**

Add to `tests/compiler/test_integration.py`:

```python
RESULTS_MODEL = '''# Workforce Model

```python:fixture
W = ["alice", "bob"]
cap = {"alice": 40, "bob": 35}
total_cap = sum(cap.values())
```

```python:results
print("| Worker | Capacity |")
print("|--------|----------|")
for w in W:
    print(f"| {w} | {cap[w]} |")
print()
print(f"Total capacity: {total_cap} hours")
```

$$\\text{cap}_i \\leq 100$$

```python:validate
Set("W", description="Workers")
Parameter("cap", index="W", units="hours", description="Capacity")
Constraint("check", over="W", expr=lambda i: cap[i] <= 100)
```
'''


def test_compile_with_results_blocks():
    result = compile_document(RESULTS_MODEL)

    # Paper includes results output, not code
    paper = result["paper"]
    assert "| alice | 40 |" in paper
    assert "Total capacity: 75 hours" in paper
    assert "python:results" not in paper
    assert "python:fixture" not in paper
    assert "python:validate" not in paper

    # Runner includes results code
    runner = result["runner"]
    assert "print(f\"| {w} | {cap[w]} |\")" in runner or "cap[w]" in runner

    # Report still works
    assert result["report"].test_passed


def test_compile_results_to_disk(tmp_path):
    """Full compile with results blocks writes correct paper to disk."""
    doc_path = tmp_path / "model.model.md"
    doc_path.write_text(RESULTS_MODEL)

    out_dir = tmp_path / "output"

    result = subprocess.run(
        [sys.executable, "-m", "meta_compiler.cli", "compile",
         str(doc_path), "--output", str(out_dir)],
        capture_output=True, text=True, env=_CLI_ENV,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"

    paper = (out_dir / "paper.md").read_text()
    assert "| alice | 40 |" in paper
    assert "Total capacity: 75 hours" in paper
    assert "python:results" not in paper
```

- [ ] **Step 2: Run integration tests**

Run: `cd math-paper-creator && python -m pytest tests/compiler/test_integration.py::test_compile_with_results_blocks tests/compiler/test_integration.py::test_compile_results_to_disk -v`

Expected: All pass.

- [ ] **Step 3: Run full test suite to verify no regressions**

Run: `cd math-paper-creator && python -m pytest tests/ -v`

Expected: All existing tests still pass, all new tests pass.

- [ ] **Step 4: Commit**

```bash
git add math-paper-creator/tests/compiler/test_integration.py
git commit -m "test(meta-compiler): add integration tests for python:results blocks"
```
