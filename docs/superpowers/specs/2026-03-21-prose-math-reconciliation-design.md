# Prose-Math Reconciliation Checkpoint

**Issue:** [#11](https://github.com/reggiechan74/cc-plugins/issues/11)
**Date:** 2026-03-21
**Approach:** Hybrid — coded automated checks + manual reconciliation prompt

## Problem

During paper authoring, interpretation errors accumulate when prose is written after math without systematic back-checking. Five error classes were identified: infeasible results stated as binding, wrong causal explanations, incorrect spatial references, overstated claims, and missing computed values in prose.

## Design

### Automated Checks (`checks.py`)

Three new check functions, exposed via `run_reconciliation_checks(prose_blocks, registry) -> list[str]`:

**1. `check_value_reporting(prose_blocks, registry)`**
- Counts Parameters/Variables in the registry that have values in `registry.data_store` or results captured from `python:results` blocks
- Scans the section's prose text for any numerical values matching those computed values
- Warning if section computes N values but prose reports none: `"Section computes N values but prose reports none"`

**2. `check_constraint_tolerance(registry)`**
- Inspects each Constraint's `expr` source code (the lambda body) for arithmetic offsets in comparisons — patterns like `>= value - N` or `<= value + N` where N is a literal number
- Flags when the offset exceeds a threshold (e.g., > 1.0) as a suspiciously large tolerance
- Example: `"Constraint 'participation' has arithmetic offset 50 in comparison — verify this is intentional"`
- Note: `ConstraintSymbol` has no `tolerance` field; this check operates on source inspection of the constraint expression via Python's `ast` module

**3. `check_directional_claims(prose_blocks)`**
- Scans prose blocks only (not math or code blocks) for directional keywords: `increases`, `decreases`, `widens`, `narrows`, `higher`, `lower`, `maximizes`, `minimizes`, `monotone`, `non-monotone`
- Returns each match with surrounding context for manual verification

### CLI Subcommand (`cli.py`)

```
python3 -m meta_compiler.cli reconcile "<file_path>" --section "<heading>"
```

- Parses and executes the **full document** to populate the registry and data_store (same as `check`)
- Scopes the prose checks to blocks under the named `--section` heading: matches the heading text in `ProseBlock` content, collects all blocks from that heading until the next heading at the same or higher level (determined by `#` count)
- Runs `run_reconciliation_checks()` with the scoped prose blocks and the fully-populated registry
- Prints warnings or "Reconciliation: OK"
- Exit code 0 for clean, exit code 2 if warnings are present (lets the author skill conditionally show the manual prompt)
- `--section` flag scopes checks to avoid re-flagging already-approved sections

### Author Skill Integration (`commands/author.md`)

Reconciliation checkpoint runs **after** the section is written to `.model.md` and meta-compiler validation passes, but **before** declaring success and moving to the next section. This replaces the temp-file approach — the full document is available with the new section included, and the registry is fully populated.

Inserted between current Steps 3.5.2 (run meta-compiler check) and 3.5.3 (update symbol registry):

1. Run automated reconciliation checks:
   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && PYTHONPATH=src python3 -m meta_compiler.cli reconcile "<file_path>" --section "<heading>"
   ```
2. If exit code 2 (warnings present), display warnings to the user
3. Show manual reconciliation prompt:
   > "Reconciliation check:
   > - Do the interpretation paragraphs match the computed values?
   > - Are spatial/directional claims consistent with the boundary values?
   > - Are any claims made about variables that don't appear in the section's equations?
   >
   > Type 'confirmed' to proceed, or describe issues."
4. If user describes issues → revise the section in `.model.md`, re-run meta-compiler check (Step 3.5.2), then re-run reconciliation
5. If 'confirmed' → proceed to Step 3.5.3 (update symbol registry, ask for next concept)

### Testing

**Unit tests (`tests/test_reconciliation.py`):**

- `check_value_reporting`: prose with/without numbers vs registry with/without data_store values
- `check_constraint_tolerance`: lambda with `>= val - 50` flagged, `>= val - 1e-6` not flagged, no arithmetic offset not flagged
- `check_directional_claims`: directional words in prose flagged with context, clean prose produces no warnings, directional words in math/code blocks not flagged

**Integration test (`tests/compiler/test_reconcile_cli.py`):**

- Small `.model.md` with known issues → correct warnings produced, exit code 2
- Clean document → "Reconciliation: OK", exit code 0
- Section scoping only checks the named section

## Files to Change

1. `math-paper-creator/src/meta_compiler/checks.py` — add three check functions and `run_reconciliation_checks()`
2. `math-paper-creator/src/meta_compiler/cli.py` — add `reconcile` subcommand with `--section` flag
3. `math-paper-creator/commands/author.md` — add reconciliation checkpoint between Steps 3.5.2 and 3.5.3
4. `math-paper-creator/tests/test_reconciliation.py` — unit tests for check functions
5. `math-paper-creator/tests/compiler/test_reconcile_cli.py` — integration tests for CLI subcommand
