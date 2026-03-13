# SESF v4.1 Templates

Fill-in-the-blank starting points for each specification tier. Copy the template that matches your complexity, replace `[bracketed placeholders]` with your values, and delete any optional sections you do not need.

**What is new in v4.1 (vs SESF v4):**

- Errors consolidated into a single `## Errors` table (no more scattered inline ERROR declarations)
- Rationale annotations as parentheticals after non-obvious rules
- Section-level summaries on every BEHAVIOR and PROCEDURE block
- Removed: Meta, Notation, Types, Functions, Precedence, Dependencies, Changelog sections
- Same @route, @config, $variable threading, RFC 2119 keywords

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

**PROCEDURE** [name]: [one-line description]

  **STEP** [step_name]: [description]
    [instructions]
    WHEN [condition] THEN [action].

  **STEP** [step_name]: [description]
    [instructions]

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| [name] | [severity] | [action] |
```

**Notes for Micro tier:**

- YAML frontmatter is optional. Omit the `---` block if your tooling does not need it.
- Configuration section is optional. Include it only when static params exist.
- Micro specs typically use ONE PROCEDURE block. BEHAVIOR blocks are optional at this tier.
- No @route tables or $variable threading at micro tier (too small to benefit).
- No separate Rules or Examples sections needed — state constraints inside STEP entries.
- Rationale annotations are optional but encouraged for non-obvious rules.

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

## Scope

**In scope:**
- [item]
- [item]

**Not in scope:**
- [item]

## Configuration

@config
  [key]: [value]
  [key]: [value]
  [key]: [value]

**BEHAVIOR** [name]: [one-line description]

  @route [route_name] [first_match_wins]
    [condition]  → [outcome]
    [condition]  → [outcome]
    [condition]  → [outcome]

  **RULE** [rule_name]:
    WHEN [condition]
    THEN [action]
    ELSE [alternative]
    (Rationale: [why])

  **RULE** [rule_name]:
    [constraint] MUST [be true]

**BEHAVIOR** [name]: [one-line description]

  **RULE** [rule_name]:
    WHEN [condition]
    THEN [action]

**PROCEDURE** [name]: [one-line description]

  **STEP** [step_name]: [description] → $[output_var]
    [instructions]

  **STEP** [step_name]: [description]
    [instructions using $output_var]

## Rules

[Cross-cutting rules that apply across ALL behaviors and procedures]

- **[Rule name]:** [statement with MUST/SHOULD/MAY]
- **[Rule name]:** [statement]

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
- @route is for 3+ branch conditionals only. For 1-2 branches, use WHEN/THEN/ELSE in a RULE.
- $variable threading is optional. Use only when data flow between steps is complex.
- Inputs/Outputs sections are optional. Include when the spec has clear data boundaries.
- Rules section is for cross-cutting rules only. Concern-specific rules go inside BEHAVIOR blocks.

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

- `[param]`: [type] — [description] (required/optional)

## Outputs

- `[output]`: [type] — [description]

## Configuration

@config
  [structured config block]

## Routing

@route [name] [first_match_wins]
  [decision table]

@route [name] [first_match_wins]
  [decision table]

**BEHAVIOR** [name]: [one-line description]

  **RULE** [rule_name]:
    WHEN [condition]
    THEN [action]
    (Rationale: [why])

  **RULE** [rule_name]:
    [constraint] MUST [be true]

**BEHAVIOR** [name]: [one-line description]

  **RULE** [rule_name]:
    WHEN [condition]
    THEN [action]
    ELSE [alternative]

**PROCEDURE** [name]: [one-line description]

  **STEP** [step_name]: [description] → $[output_var]
    [instructions]

  **STEP** [step_name]: [description] → $[output_var]
    [instructions using prior $vars]

**PROCEDURE** [name]: [one-line description]

  **STEP** [step_name]: [description]
    [instructions using $vars from prior procedures]

  **STEP** [step_name]: [description]
    [instructions]

## Rules

[Cross-cutting rules that span ALL behaviors and procedures]

- **[Rule name]:** [statement]
- **[Rule name]:** [statement]

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| [comprehensive error table] |

## Examples

[Edge-case worked examples with pass/fail]

[example_name]:
  Input: [concrete values]
  Expected: [concrete outcome]
  Why: [which rule applies]
```

**Notes for Complex tier:**

- YAML frontmatter is optional. Omit the `---` block if your tooling does not need it.
- Inputs/Outputs sections are required at complex tier.
- $variable threading is recommended when data flows between procedures.
- Use STEP → $var syntax to make data dependencies explicit.
- Rules section is for cross-cutting rules that apply across ALL behaviors/procedures only.
- @route wildcard row (`*`) is optional. Include only when a meaningful default exists.
- Multiple BEHAVIOR and PROCEDURE blocks are expected at complex tier.
- Rationale annotations SHOULD appear on non-obvious rules throughout.
- Worked examples SHOULD demonstrate edge cases with explicit pass/fail outcomes.
