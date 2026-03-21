"""CLI entry point for the meta-compiler.

Usage:
    python -m meta_compiler.cli check <file.model.md>
    python -m meta_compiler.cli paper <file.model.md> [--depth executive|technical|appendix]
    python -m meta_compiler.cli report <file.model.md>
    python -m meta_compiler.cli compile <file.model.md> [--output <dir>]
    python -m meta_compiler.cli reconcile <file.model.md> [--section "<heading>"]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="meta-compiler",
        description="Validated mathematical model compiler",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # check
    check_parser = subparsers.add_parser("check", help="Validate a .model.md document")
    check_parser.add_argument("file", type=Path, help="Path to .model.md file")
    check_parser.add_argument("--strict", action="store_true",
                              help="Treat orphans as errors")

    # paper
    paper_parser = subparsers.add_parser("paper", help="Generate paper artifact")
    paper_parser.add_argument("file", type=Path, help="Path to .model.md file")
    paper_parser.add_argument("--depth", choices=["executive", "technical", "appendix"],
                              help="Depth filter for paper output")
    paper_parser.add_argument("--output", type=Path, help="Output file path")
    paper_parser.add_argument(
        "--no-strict", action="store_true",
        help="Treat orphan symbols as warnings instead of errors",
    )

    # report
    report_parser = subparsers.add_parser("report", help="Generate validation report")
    report_parser.add_argument("file", type=Path, help="Path to .model.md file")
    report_parser.add_argument("--output", type=Path, help="Output file path")
    report_parser.add_argument(
        "--no-strict", action="store_true",
        help="Treat orphan symbols as warnings instead of errors",
    )

    # compile
    compile_parser = subparsers.add_parser("compile", help="Generate all artifacts")
    compile_parser.add_argument("file", type=Path, help="Path to .model.md file")
    compile_parser.add_argument("--output", type=Path, default=Path("output"),
                                help="Output directory (default: output/)")
    compile_parser.add_argument("--depth", choices=["executive", "technical", "appendix"],
                                help="Depth filter for paper output")
    compile_parser.add_argument(
        "--no-strict", action="store_true",
        help="Treat orphan symbols as warnings instead of errors",
    )

    # reconcile
    reconcile_parser = subparsers.add_parser(
        "reconcile", help="Run prose-math reconciliation checks"
    )
    reconcile_parser.add_argument("file", type=Path, help="Path to .model.md file")
    reconcile_parser.add_argument(
        "--section", type=str, default=None,
        help="Scope checks to a specific section heading"
    )

    args = parser.parse_args(argv)
    source = args.file.read_text()

    if args.command == "check":
        return _cmd_check(source, strict=args.strict)
    elif args.command == "paper":
        return _cmd_paper(source, depth=args.depth, output=args.output,
                          strict=not args.no_strict)
    elif args.command == "report":
        return _cmd_report(source, output=args.output, strict=not args.no_strict)
    elif args.command == "compile":
        return _cmd_compile(source, output=args.output, depth=args.depth,
                            strict=not args.no_strict)
    elif args.command == "reconcile":
        return _cmd_reconcile(source, section=args.section)
    return 1


def _cmd_check(source: str, *, strict: bool = False) -> int:
    from meta_compiler.compiler import check_document

    result = check_document(source, strict=strict)
    if result.passed:
        print("PASSED")
        for w in result.warnings:
            print(f"  WARNING: {w}")
        return 0
    else:
        print("FAILED")
        for e in result.errors:
            print(f"  ERROR: {e}")
        for w in result.warnings:
            print(f"  WARNING: {w}")
        return 1


def _cmd_paper(source: str, *, depth: str | None, output: Path | None,
               strict: bool = True) -> int:
    from meta_compiler.compiler import compile_document

    try:
        artifacts = compile_document(source, depth=depth, strict=strict)
    except (ValueError, RuntimeError) as e:
        print(str(e), file=sys.stderr)
        return 1

    paper = artifacts["paper"]
    if output:
        output.write_text(paper)
        print(f"Paper written to {output}")
    else:
        print(paper)
    return 0


def _cmd_report(source: str, *, output: Path | None, strict: bool = True) -> int:
    from meta_compiler.compiler import compile_document

    try:
        artifacts = compile_document(source, strict=strict)
    except (ValueError, RuntimeError) as e:
        print(str(e), file=sys.stderr)
        return 1

    text = artifacts["report_text"]
    if output:
        output.write_text(text)
        print(f"Report written to {output}")
    else:
        print(text)
    return 0


def _cmd_compile(source: str, *, output: Path, depth: str | None,
                 strict: bool = True) -> int:
    from meta_compiler.compiler import compile_document

    try:
        artifacts = compile_document(source, depth=depth, strict=strict)
    except (ValueError, RuntimeError) as e:
        print(str(e), file=sys.stderr)
        return 1

    output.mkdir(parents=True, exist_ok=True)
    (output / "paper.md").write_text(artifacts["paper"])
    (output / "runner.py").write_text(artifacts["runner"])
    (output / "report.txt").write_text(artifacts["report_text"])

    print(f"Artifacts written to {output}/")
    print("  paper.md")
    print("  runner.py")
    print("  report.txt")
    return 0


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


if __name__ == "__main__":
    sys.exit(main())
