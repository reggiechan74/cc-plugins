---
name: Universal Structural Checklist
description: Structural completeness checks applied regardless of paper type
---

# Structural Checklist

Evaluate each item by examining the `.model.md` document's validate blocks and section structure. This checklist is prompt-based — read the document and reason about whether each item is satisfied.

## How to Use

- **At completion:** Run every item. Report Required failures as warnings. Report Advisory matches as informational notes.
- **Between sections (when user asks "what's next?"):** Scan Required items to identify structural gaps and suggest what to add next.

### Required

These produce warnings at completion if not satisfied:

- [ ] At least one Set declared
- [ ] At least one Parameter declared with index referencing a declared Set
- [ ] At least one computable output (Expression, Constraint, or Objective)
- [ ] Every Variable referenced in at least one Constraint or Expression
- [ ] Every section with `$$...$$` display math also has a validate block in that section (one validate block per section, not per math block)
- [ ] Introduction section exists
- [ ] Conclusion section exists

### Advisories

Informational notes — not blocking, but worth surfacing:

- Variables declared but no Objective — is this a scoring/classification model rather than optimization?
- Constraints declared but no Variables — are these validation rules on Parameters?
- More than 20 symbols with no Part/section grouping — consider organizing into parts
- Parameters with no units specified — intentional or missing?
- Sets declared but never used as an index — orphan sets
- Paper declares epistemic status (empirical / structural / decision framework) in Introduction
- Scenario outputs framed as model-implied rather than empirical findings
- Parameters have stated provenance (estimated / literature / illustrative)
- Multi-parameter scenarios include effect decomposition
