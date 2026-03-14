"""Artifact compiler for .math.md documents."""

from __future__ import annotations

from meta_compiler.compiler.executor import ExecutionResult, execute_blocks
from meta_compiler.compiler.paper import generate_paper
from meta_compiler.compiler.parser import parse_document
from meta_compiler.compiler.report import generate_report


def check_document(source: str, *, strict: bool = False) -> ExecutionResult:
    """Parse and validate a .math.md document.

    Args:
        source: The document source text.
        strict: If True, orphans are errors (compilation mode).

    Returns:
        ExecutionResult with pass/fail status and diagnostics.
    """
    blocks = parse_document(source)
    return execute_blocks(blocks, strict=strict)


def compile_document(
    source: str,
    *,
    depth: str | None = None,
) -> dict:
    """Compile a .math.md document into all three artifacts.

    Args:
        source: The document source text.
        depth: Optional depth filter for paper artifact.

    Returns:
        Dict with keys 'paper' (str), 'codebase' (dict[str, str]),
        'report' (Report object), and 'report_text' (str).
    """
    blocks = parse_document(source)

    # Execute in strict mode for compilation
    result = execute_blocks(blocks, strict=True)
    if not result.passed:
        raise ValueError(
            "Cannot compile: validation failed.\n"
            + "\n".join(f"  {e}" for e in result.errors)
        )

    paper = generate_paper(blocks, depth=depth)
    codebase = generate_codebase(result.registry)
    # Pass the executor's test result to avoid re-running tests
    from meta_compiler.registry import TestResult
    test_result = TestResult(
        passed=result.passed,
        errors=result.errors,
        warnings=result.warnings,
    )
    report = generate_report(result.registry, blocks, test_result=test_result)

    return {
        "paper": paper,
        "codebase": codebase,
        "report": report,
        "report_text": report.to_text(),
    }
