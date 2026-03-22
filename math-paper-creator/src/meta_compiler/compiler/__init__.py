"""High-level compiler API for .model.md documents."""

from __future__ import annotations

from meta_compiler.compiler.parser import parse_document, extract_section_blocks
from meta_compiler.compiler.executor import execute_blocks, ExecutionResult
from meta_compiler.compiler.paper import generate_paper
from meta_compiler.compiler.report import generate_report
from meta_compiler.compiler.runner import generate_runner
from meta_compiler.checks import run_reconciliation_checks


def check_document(source: str, *, strict: bool = False) -> ExecutionResult:
    """Parse and validate a .model.md document."""
    blocks = parse_document(source)
    return execute_blocks(blocks, strict=strict)


def compile_document(
    source: str,
    *,
    depth: str | None = None,
    filename: str = "model.model.md",
    strict: bool = True,
    skip_validation: bool = False,
) -> dict:
    """Full compilation pipeline: validate, then generate artifacts."""
    blocks = parse_document(source)

    if skip_validation:
        paper = generate_paper(blocks, depth=depth)
        return {"paper": paper, "report": None, "report_text": None, "runner": None}

    result = execute_blocks(blocks, strict=strict)
    if not result.passed:
        raise RuntimeError(
            "Validation failed in strict mode:\n"
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
