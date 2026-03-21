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
- Counts Parameters/Variables in the registry with computed fixture values
- Scans prose text for matching numerical values
- Warning if section computes N values but prose reports none

**2. `check_constraint_tolerance(registry)`**
- Inspects each Constraint's tolerance after evaluation
- Flags any constraint with tolerance exceeding 1e-4
- Example: `"Constraint 'X' uses tolerance 50 — verify this is intentional"`

**3. `check_directional_claims(prose_blocks)`**
- Scans prose for directional keywords: `increases`, `decreases`, `widens`, `narrows`, `higher`, `lower`, `maximizes`, `minimizes`, `monotone`, `non-monotone`
- Returns each match with surrounding context for manual verification

### CLI Subcommand (`cli.py`)

```
python3 -m meta_compiler.cli reconcile "<file_path>" --section "<heading>"
```

- Parses document, isolates blocks under the given section heading
- Runs `run_reconciliation_checks()` on scoped blocks
- Prints warnings or "Reconciliation: OK"
- Exit code 0 always (warnings are advisory; the manual prompt is the gate)
- `--section` flag scopes checks to avoid re-flagging already-approved sections

### Author Skill Integration (`commands/author.md`)

New Step 3.4b inserted between Step 3.4 (present/approve) and Step 3.5 (write/validate):

1. Write approved section content to a temporary file
2. Run automated checks via CLI:
   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && PYTHONPATH=src python3 -m meta_compiler.cli reconcile "<temp_file>" --section "<heading>"
   ```
3. Display any warnings to the user
4. Show manual reconciliation prompt:
   > "Reconciliation check:
   > - Do the interpretation paragraphs match the computed values?
   > - Are spatial/directional claims consistent with the boundary values?
   > - Are any claims made about variables that don't appear in the section's equations?
   >
   > Type 'confirmed' to proceed, or describe issues."
5. If user describes issues → revise and loop back to Step 3.4
6. If 'confirmed' → clean up temp file, proceed to Step 3.5

### Testing

**Unit tests for each check function:**

- `check_value_reporting`: prose with/without numbers vs registry with/without computed values
- `check_constraint_tolerance`: tolerance 50 flagged, tolerance 1e-6 not flagged, no explicit tolerance not flagged
- `check_directional_claims`: directional words flagged with context, clean prose produces no warnings

**Integration test for CLI:**

- Small `.model.md` with known issues → correct warnings produced
- Section scoping only checks the named section

## Files to Change

1. `math-paper-creator/src/meta_compiler/checks.py` — add three check functions and `run_reconciliation_checks()`
2. `math-paper-creator/src/meta_compiler/cli.py` — add `reconcile` subcommand
3. `math-paper-creator/commands/author.md` — add Step 3.4b reconciliation checkpoint
4. `math-paper-creator/tests/` — unit and integration tests for new checks
