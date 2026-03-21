# Changelog

All notable changes to math-paper-creator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-03-21

### Added
- Prose-math reconciliation checkpoint in author skill section loop (#11)
- `reconcile` CLI subcommand with `--section` scoping flag
- `check_directional_claims` — flags directional keywords in prose for manual verification
- `check_value_reporting` — warns when computed values are absent from prose
- `check_constraint_tolerance` — flags suspiciously large arithmetic offsets in constraints via AST inspection
- `extract_section_blocks` parser helper for section-level block scoping

## [0.4.1] - 2026-03-21

### Fixed
- Constraint evaluation now accepts `np.True_` from numpy-backed computations (#9)
- Scalar auto-unwrap detects `np.float64`/`np.int64` instead of wrapping them as `SymbolProxy` (#9)
- Objective numeric check accepts numpy scalar types (#9)

## [0.4.0] - 2026-03-20

### Added
- **Epistemic hygiene checks** — scope declaration prompt at Step 2 with `epistemic_type` stored in frontmatter (#8)
- Parameter provenance batch prompt (data / literature / illustrative) at Step 3.2 (#8)
- Scenario decomposition flag for multi-parameter changes at Step 3.2 (#8)
- Epistemic language scan at Step 4, calibrated by paper type (#8)
- Four-tests conclusion frame for structural/decision framework papers at Step 4 (#8)
- Four advisory checklist items for epistemic completeness (#8)
- Expr-based dependency tracing for scalar models in report dependency graph (#7)

### Changed
- Orphan checking fully suppressed for scalar models (no Sets) — no more warning noise in reports
- Scalar parameter API note updated in author skill to reflect v0.3.0 auto-unwrap

## [0.3.0] - 2026-03-20

### Added
- **Scalar model support** — scalar fixture values (int, float, str) are auto-unwrapped as raw Python types instead of SymbolProxy, enabling `M * beta` arithmetic directly in expressions (#3)
- `collect_scalar_refs()` helper in checks.py for tokenizer-based scalar access logging
- `--no-strict` CLI flag for `compile`, `paper`, and `report` subcommands (#4)
- `strict` parameter on `compile_document()` (default `True`) for programmatic control (#4)
- `Report.__str__()` delegating to `to_text()` — `str(report)` and `print(report)` now work as expected (#5)

### Changed
- **Strict mode auto-detection** — when no `Set` symbols are registered, orphan warnings are automatically demoted from errors to warnings in strict mode (#4)
- `generate_report` signature: `(blocks, *, registry, test_result=None)` — `blocks` is now the first positional arg, `registry` is keyword-only (**breaking**) (#6)
- `generate_runner` signature: `(blocks, *, model_path="model.model.md")` — `blocks` is now the first positional arg, `model_path` is keyword-only with default (**breaking**) (#6)
- `Registry.data_store` type annotation broadened from `dict[str, dict]` to `dict[str, Any]`

## [0.2.0] - 2026-03-14

### Added
- Template system for 10 mathematical paper types (optimization, statistical, game-theoretic, simulation, decision-analysis, financial-pricing, actuarial, econometric, queueing, graph-network)

## [0.1.0] - 2026-03-10

### Added
- Initial release with meta-compiler v2, interactive authoring workflow, and validation engine
