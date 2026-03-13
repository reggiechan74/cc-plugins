# HSF v5 Templates

Fill-in-the-blank starting points for each specification tier. Copy the template that matches your complexity, replace `[bracketed placeholders]` with your values, and delete any optional sections you do not need.

**What is new in v5 (Hybrid Specification Format):**

- Natural language prose replaces BEHAVIOR/PROCEDURE/RULE/STEP blocks
- Markdown headers and bold list items provide structure
- @route tables, @config blocks, $variable threading preserved for when they add value
- Errors consolidated into a single table
- Reduced line budgets: Micro ≤80, Standard ≤200, Complex ≤400

---

## Micro Tier Template (~20-80 lines)

```markdown
---
title: [Short title]
description: "[One-line description]"
[other frontmatter as needed]
---

# [Spec Name]

[1-3 sentence purpose statement]

**Not in scope:** [brief exclusions]

## Configuration

[Inline values or @config block if 3+ params]

## Instructions

[Prose instructions with clear sequencing. Use numbered lists for ordered steps,
bullet lists for parallel concerns. Bold key terms.]

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| [name] | critical/warning | [what to do] |
```

**Notes for Micro tier:**

- YAML frontmatter is optional. Omit the `---` block if your tooling does not need it.
- Configuration section is optional. Include it only when static params exist.
- No @route tables or $variable threading at micro tier (too small to benefit).
- No separate Rules or Examples sections needed — state constraints inline in Instructions.

---

## Standard Tier Template (~80-200 lines)

```markdown
---
title: [Short title]
description: "[One-line description]"
[other frontmatter]
---

# [Spec Name]

[Purpose — 1-3 sentences]

**Not in scope:** [exclusions]

## Configuration

@config
  [key]: [value]
  [key]: [value]
  [key]: [value]

## [Processing/Routing] Logic

@route [route_name] [first_match_wins]
  [condition]  → [action]
  [condition]  → [action]
  [condition]  → [action]

## Instructions

### [Phase/Step 1]: [Name]

[Prose instructions. Include the rules that apply to THIS phase inline,
not in a separate rules section.]

### [Phase/Step 2]: [Name]

[Prose instructions.]

## Rules

### [Rule Group Name]

- **[Rule name]:** [Natural language statement with MUST/SHOULD/MAY.]
- **[Rule name]:** [Natural language statement.]

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| [name] | critical | [action] |
| [name] | warning | [action] |

## Examples

[Edge cases only]
[name]: [input] → [expected outcome — pass or fail and why]
```

**Notes for Standard tier:**

- YAML frontmatter is optional. Omit the `---` block if your tooling does not need it.
- @config is optional. Omit if the spec has no configurable parameters (or fewer than 3).
- @route is for 3+ branch conditionals only. For binary conditions, use prose conditionals.
- $variable threading is optional. Use only when data flow between phases is complex.
- Inputs/Outputs sections are optional. Include when the spec has clear data boundaries.
- Rules section is for cross-cutting rules only. Phase-specific rules go inline in Instructions.

---

## Complex Tier Template (~200-400 lines)

```markdown
---
title: [Short title]
description: "[One-line description]"
[other frontmatter]
---

# [Spec Name]

[Purpose — 1-3 sentences]

**Not in scope:** [exclusions]

## Inputs

- `[param]`: [type] - [description] - required/optional

## Outputs

- `[output]`: [type] - [description] - required/optional/conditional

## Configuration

@config
  [structured config block]

## [Routing] Logic

@route [name] [first_match_wins]
  [decision table]

## Instructions

[Prose instructions organized by phase/step with ### headers.
Include applicable rules inline within each phase.
Use $variable threading if data flow between phases is complex.]

### [Phase 1]: [Name] → `artifact_name`

[Instructions. State constraints that apply to this phase HERE,
not in a separate rules section.]

### [Phase 2]: [Name] → `artifact_name`

[Instructions. Constraints for this phase stated here.]

## Rules

### [Cross-cutting rule group — only for rules that apply across ALL phases]

- **[Rule]:** [Statement]
- **[Rule]:** [Statement]

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| [comprehensive error table] |

## Examples

[Edge-case worked examples with pass/fail]

[good_example]:
  [multi-line worked example showing correct behavior]

[bad_example]:
  [multi-line showing incorrect behavior and why it fails]
```

**Notes for Complex tier:**

- YAML frontmatter is optional. Omit the `---` block if your tooling does not need it.
- Inputs/Outputs sections are required at complex tier.
- $variable threading is recommended when data flows between phases are complex enough to need explicit tracking.
- Rules section is for cross-cutting rules that apply across ALL phases only. Phase-specific rules go inline in Instructions.
- @route wildcard row (`*`) is optional. Include only when a meaningful default exists.
- Worked examples SHOULD demonstrate edge cases with explicit pass/fail outcomes.
