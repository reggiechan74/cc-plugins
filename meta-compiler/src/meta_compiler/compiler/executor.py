"""Execute validation blocks from a parsed .math.md document."""

from __future__ import annotations

from dataclasses import dataclass, field

from meta_compiler.compiler.parser import Block, ValidationBlock
from meta_compiler.registry import Registry, TestResult


@dataclass
class ExecutionResult:
    """Result of executing all validation blocks in a document."""
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    registry: Registry | None = None


def execute_blocks(
    blocks: list[Block],
    *,
    strict: bool = False,
) -> ExecutionResult:
    """Execute all validation blocks sequentially against a fresh registry.

    Each block runs in a shared namespace that has access to the registry
    API functions (Set, Parameter, Variable, Expression, Constraint, Objective, S)
    and the registry instance (for registry.run_tests()).

    Args:
        blocks: Parsed document blocks (only ValidationBlocks are executed).
        strict: If True, orphans are errors (compilation mode).

    Returns:
        ExecutionResult with pass/fail status, errors, and the final registry.
    """
    from meta_compiler import (
        Constraint,
        Expression,
        Objective,
        Parameter,
        S,
        Set,
        Variable,
    )
    from meta_compiler.registry import registry

    # Reset registry for clean execution
    registry.reset()

    # Build the execution namespace
    namespace = {
        "Set": Set,
        "Parameter": Parameter,
        "Variable": Variable,
        "Expression": Expression,
        "Constraint": Constraint,
        "Objective": Objective,
        "S": S,
        "registry": registry,
    }

    all_errors: list[str] = []
    all_warnings: list[str] = []

    for block in blocks:
        if not isinstance(block, ValidationBlock):
            continue

        try:
            exec(block.code, namespace)  # noqa: S102
        except Exception as e:
            all_errors.append(
                f"Line {block.line_number}: {type(e).__name__}: {e}"
            )
            return ExecutionResult(
                passed=False,
                errors=all_errors,
                warnings=all_warnings,
                registry=registry,
            )

    # Final cumulative check
    final_result = registry.run_tests(strict=strict)
    all_errors.extend(final_result.errors)
    all_warnings.extend(final_result.warnings)

    return ExecutionResult(
        passed=final_result.passed,
        errors=all_errors,
        warnings=all_warnings,
        registry=registry,
    )
