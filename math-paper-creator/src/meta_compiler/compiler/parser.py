"""Document parser for .math.md files.

Splits source documents into typed blocks: ProseBlock, MathBlock, and
ValidationBlock. This is the foundation module — all other compiler modules
depend on it.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProseBlock:
    """Normal markdown text — narrative, explanations."""

    content: str


@dataclass
class MathBlock:
    """LaTeX math block ($$...$$ or $...$)."""

    content: str
    raw: str  # Original with delimiters for paper output


@dataclass
class ValidationBlock:
    """Python validation code (```python:validate ... ```)."""

    code: str
    line_number: int  # For error reporting


@dataclass
class FixtureBlock:
    """A python:fixture fenced code block containing test data."""
    code: str
    line_number: int


@dataclass
class ResultsBlock:
    """A python:results fenced code block — stdout replaces block in paper."""
    code: str
    line_number: int
    output: str | None = None  # Populated by executor


Block = ProseBlock | MathBlock | ValidationBlock | FixtureBlock | ResultsBlock


def parse_document(source: str) -> list[Block]:
    """Parse a .math.md document into a sequence of blocks."""
    blocks: list[Block] = []
    lines = source.split("\n")
    i = 0
    current_prose: list[str] = []

    def flush_prose() -> None:
        if current_prose:
            text = "\n".join(current_prose)
            if text.strip():
                blocks.append(ProseBlock(content=text + "\n" if not text.endswith("\n") else text))
            current_prose.clear()

    while i < len(lines):
        line = lines[i]

        # Check for fixture block: ```python:fixture
        if line.strip().startswith("```python:fixture"):
            flush_prose()
            code_lines: list[str] = []
            start_line = i + 1
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append(FixtureBlock(
                code="\n".join(code_lines),
                line_number=start_line,
            ))
            i += 1  # Skip closing ```
            continue

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

        # Check for validation block: ```python:validate
        if line.strip().startswith("```python:validate"):
            flush_prose()
            code_lines: list[str] = []
            start_line = i + 1
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append(ValidationBlock(
                code="\n".join(code_lines),
                line_number=start_line,
            ))
            i += 1  # Skip closing ```
            continue

        # Check for display math block: $$...$$
        if line.strip().startswith("$$"):
            flush_prose()
            if line.strip().endswith("$$") and len(line.strip()) > 2:
                # Single-line $$...$$ block
                blocks.append(MathBlock(
                    content=line.strip()[2:-2].strip(),
                    raw=line,
                ))
                i += 1
            else:
                # Multi-line $$...$$ block
                math_lines = [line]
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("$$"):
                    math_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    math_lines.append(lines[i])
                    i += 1
                raw = "\n".join(math_lines)
                inner = "\n".join(math_lines[1:-1]) if len(math_lines) > 2 else ""
                blocks.append(MathBlock(content=inner.strip(), raw=raw))
            continue

        # Regular prose line
        current_prose.append(line)
        i += 1

    flush_prose()
    return blocks


@dataclass
class CoverageResult:
    """Result of checking math block coverage."""

    total_math: int
    covered_math: int
    uncovered_sections: list[str]  # Section headings with uncovered math

    @property
    def ratio(self) -> float:
        if self.total_math == 0:
            return 1.0
        return self.covered_math / self.total_math


def coverage_metric(blocks: list[Block]) -> CoverageResult:
    """Check how many math blocks have a following validation block.

    A math block is 'covered' if a ValidationBlock appears before the next
    MathBlock or end of document (possibly with prose in between).
    """
    total = 0
    covered = 0
    uncovered_sections: list[str] = []
    current_section = ""

    i = 0
    while i < len(blocks):
        block = blocks[i]

        # Track current section heading
        if isinstance(block, ProseBlock):
            for line in block.content.split("\n"):
                stripped = line.strip()
                if stripped.startswith("#"):
                    current_section = stripped.lstrip("#").strip()

        if isinstance(block, MathBlock):
            total += 1
            found_validation = False
            for j in range(i + 1, len(blocks)):
                if isinstance(blocks[j], ValidationBlock):
                    found_validation = True
                    break
                if isinstance(blocks[j], MathBlock):
                    break
            if found_validation:
                covered += 1
            else:
                uncovered_sections.append(current_section)
        i += 1

    return CoverageResult(
        total_math=total,
        covered_math=covered,
        uncovered_sections=uncovered_sections,
    )


def extract_section_blocks(blocks: list[Block], heading: str) -> list[Block]:
    """Extract blocks belonging to a specific section heading.

    Finds the ProseBlock containing the heading, then collects all blocks
    until the next heading at the same or higher level (fewer '#' characters).

    Because the parser may group multiple headings into one ProseBlock,
    this function also trims prose content at section boundaries.
    """
    target_level = 0
    start_idx = None
    heading_line_idx = None  # line index within the ProseBlock

    for i, block in enumerate(blocks):
        if not isinstance(block, ProseBlock):
            continue
        for li, line in enumerate(block.content.split("\n")):
            stripped = line.strip()
            if not stripped.startswith("#"):
                continue
            hashes = len(stripped) - len(stripped.lstrip("#"))
            title = stripped.lstrip("#").strip()
            if title == heading:
                target_level = hashes
                start_idx = i
                heading_line_idx = li
                break
        if start_idx is not None:
            break

    if start_idx is None:
        return []

    def _trim_prose_at_boundary(text: str, level: int, *, skip_first_heading: bool = False) -> tuple[str, bool]:
        """Return (trimmed_text, hit_boundary).

        If skip_first_heading is True, the first heading matching the target
        heading is skipped (used for the starting block).
        """
        lines = text.split("\n")
        skipped = False
        out: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                hashes = len(stripped) - len(stripped.lstrip("#"))
                if hashes <= level:
                    if skip_first_heading and not skipped:
                        skipped = True
                    else:
                        # Hit a boundary — return what we have so far
                        trimmed = "\n".join(out)
                        return trimmed, True
            out.append(line)
        return "\n".join(out), False

    # Build the starting ProseBlock content: lines from heading onward,
    # trimmed at the next same-or-higher heading.
    start_block = blocks[start_idx]
    start_lines = start_block.content.split("\n")
    section_text = "\n".join(start_lines[heading_line_idx:])
    trimmed_text, hit = _trim_prose_at_boundary(section_text, target_level, skip_first_heading=True)

    result: list[Block] = []
    if trimmed_text.strip():
        result.append(ProseBlock(content=trimmed_text))

    if hit:
        return result

    for block in blocks[start_idx + 1:]:
        if isinstance(block, ProseBlock):
            trimmed, hit = _trim_prose_at_boundary(block.content, target_level, skip_first_heading=False)
            if trimmed.strip():
                result.append(ProseBlock(content=trimmed))
            if hit:
                return result
        else:
            result.append(block)

    return result
