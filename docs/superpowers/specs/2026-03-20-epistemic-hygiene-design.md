# Epistemic Hygiene Checks for Author Skill

**Date:** 2026-03-20
**Plugin:** math-paper-creator
**Issue:** #8
**Status:** Design

## Problem

During authoring of scalar optimization papers, epistemic claims can be stronger than what the model earns. Illustrative parameters get treated as calibrated truth, scenario outputs are framed as empirical findings, and the conclusion overstates what a structural model can claim. These issues are straightforward to fix but should be caught by the tooling itself.

## Design

Six additions to the authoring workflow, all prompt-level changes to `commands/author.md` and `templates/_checklist.md`. No meta-compiler changes.

### 1. Scope Declaration (Step 2)

**When:** After the Introduction is written and approved.

**Prompt:**
> "What type of model is this paper? (1) Empirical — estimated from observed data, (2) Structural/theoretical — specifies mechanisms and derives consequences from assumptions, (3) Decision framework — helps reason more clearly even when exact calibration is unavailable."

**Action:** Store the choice in YAML frontmatter as `epistemic_type: empirical | structural | decision_framework`. Generate a `**Scope and epistemic status:**` paragraph appended to the Introduction. For `structural` and `decision_framework`, include: "Parameters are illustrative, not estimated from observational data. Scenario outputs are model-implied examples, not observed outcomes."

**Used by:** Items 4 (language scan calibration) and 5 (four-tests conclusion gating).

### 2. Parameter Provenance (Step 3.2)

**When:** During formalization, when a `python:fixture` block assigns a value to a Parameter.

**Prompt (per parameter):**
> "Is [parameter] = [value] (a) estimated from data, (b) adopted from literature with citation, or (c) illustrative/assumed?"

**Action:** Frame the prose near the parameter definition accordingly:
- **(a)** "Estimated from [source]..." (author provides source)
- **(b)** "Following [Author] ([year]), we set..." (author provides citation)
- **(c)** "We adopt [value] as a representative value..."

Fires per-parameter during Step 3.2 prose writing. No separate tracking structure — the prose itself is the record. For blocks with multiple parameters, prompt once per parameter.

### 3. Scenario Decomposition Flag (Step 3.2)

**When:** During formalization of a scenario or sensitivity analysis section that changes 2+ previously defined parameters simultaneously.

**Detection:** When a fixture block assigns new values to parameters already defined in earlier fixtures, count the changed parameters. If >= 2, flag.

**Prompt:**
> "This scenario modifies [N] parameters at once ([list]). The combined effect should be decomposed — show each factor's contribution separately before reporting the total."

**Action:** Generate the section with per-parameter effect decomposition before the combined result. Author can override if parameters are genuinely inseparable.

Only applies to scenario/sensitivity sections (signaled by heading or author description), not initial parameter definitions.

### 4. Epistemic Language Scan (Step 4)

**When:** At completion, after the final meta-compiler check, before showing the summary.

**Action:** Scan the full `.model.md` for patterns that overstate epistemic status:

| Pattern | Suggestion |
|---------|------------|
| "the model proves" | "the model shows that, under these assumptions" |
| "demonstrates that" | "illustrates that" or "model-implied analysis suggests" |
| "findings" (for scenario outputs) | "implications under illustrative calibration" |
| "the math says" | "under these assumptions" |
| "yields [N] results/findings" | "yields [N] implications" |

**Calibrated by `epistemic_type`:**
- `empirical`: softer framing — "Review these — they may be appropriate for an empirical paper."
- `structural` / `decision_framework`: stronger framing — "These may overstate what the model has earned."

Not auto-fix. Present flagged instances with line context and suggestions. Author decides which to change. Skill offers to apply accepted changes.

### 5. Four-Tests Conclusion Frame (Step 4, conditional)

**When:** Only for `epistemic_type: structural` or `decision_framework`. Not offered for `empirical`.

**Prompt:**
> "For a formalization-of-intuition paper, the conclusion can be strengthened by stating which formal tests the intuition passed. Would you like me to evaluate against the four-tests framework?"

**Four tests (qualitative evaluation):**
1. **Non-contradiction** — do the variables interact coherently without logical inconsistencies?
2. **Mechanistic plausibility** — does the model have a causal structure rather than a curve-fit?
3. **Comparative statics** — do parameter changes shift the optimum in the expected direction?
4. **Organizational/domain interpretability** — can a practitioner inspect the result and understand *why* it occurs?

**Action:** Generate a conclusion paragraph reporting which tests pass, framed as: "The model does not identify the true empirical optimum. It formalizes a [common intuition] and shows that, under reasonable structural assumptions, [the core claim]."

Tests 1-2 are partially inferable from meta-compiler validation (no cycles, explicit mechanisms). Tests 3-4 require reading scenario sections and prose. All evaluation is qualitative.

### 6. Checklist Additions

**Location:** `templates/_checklist.md`, Advisory section.

Append:
```markdown
- Paper declares epistemic status (empirical / structural / decision framework) in Introduction
- Scenario outputs framed as model-implied rather than empirical findings
- Parameters have stated provenance (estimated / literature / illustrative)
- Multi-parameter scenarios include effect decomposition
```

Advisory items — informational notes at completion, not warnings. Evaluated against document text during existing Step 4 checklist scan.

## Files Changed

| File | Change |
|------|--------|
| `commands/author.md` | Add items 1-5 to Steps 2, 3.2, and 4 |
| `templates/_checklist.md` | Add 4 advisory items (item 6) |

## Testing Strategy

These are prompt-level changes to a skill file — no unit tests. Validation is manual:
- Author a new paper and verify each prompt fires at the correct step
- Verify `epistemic_type` is stored in frontmatter
- Verify the language scan runs at completion and respects paper type
- Verify four-tests conclusion is only offered for non-empirical papers
- Verify checklist advisory items appear at completion

## Out of Scope

- Automated epistemic scoring or grading
- Changes to the meta-compiler or validation engine
- Changes to the `compile`, `check`, or `review` commands
- Enforcing provenance as a hard requirement (it's advisory)
