# HSF v6 Templates

Fill-in-the-blank starting points for each specification tier. Copy the template that matches your complexity, replace `[bracketed placeholders]` with your values, and delete any optional sections you do not need.

**What is new in v6 (Hybrid Specification Format):**

- XML envelope tags (`<purpose>`, `<scope>`, `<config>`, `<instructions>`, `<rules>`, `<errors>`, `<examples>`) replace `##` top-level headers
- `<config>` uses JSON body instead of `@config` with YAML-like syntax
- `<route>` uses XML `<case>`/`<default>` elements instead of `@route` with `→` rows
- `<output-schema>` for specifying structured output format (SHOULD for standard+, MAY for micro)
- Configuration references use `config.key` instead of `$config.key`
- `###` markdown headers still used for sub-structure within sections
- $variable threading, RFC 2119 keywords, error tables, examples format all preserved
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

<purpose>

[1-3 sentence purpose statement]

</purpose>

<scope>

**Not in scope:** [brief exclusions]

</scope>

[Inline configuration values if any — no <config> block at micro tier]

<instructions>

[Prose instructions with clear sequencing. Use numbered lists for ordered steps,
bullet lists for parallel concerns. Bold key terms.]

</instructions>

<errors>

| Error | Severity | Action |
|-------|----------|--------|
| [name] | critical/warning | [what to do] |

</errors>
```

**Notes for Micro tier:**

- YAML frontmatter is optional. Omit the `---` block if your tooling does not need it.
- Configuration values go inline in prose. No `<config>` block at micro tier (too few values).
- No `<route>` tables or $variable threading at micro tier (too small to benefit).
- No separate `<rules>` or `<examples>` sections needed — state constraints inline in `<instructions>`.

---

## Standard Tier Template (~80-200 lines)

```markdown
---
title: [Short title]
description: "[One-line description]"
[other frontmatter]
---

# [Spec Name]

<purpose>

[Purpose — 1-3 sentences]

</purpose>

<scope>

**Not in scope:** [exclusions]

</scope>

<config>
{
  "[key]": "[value]",
  "[key]": "[value]",
  "[key]": "[value]"
}
</config>

<instructions>

### [Processing/Routing] Logic

<route name="[route_name]" mode="first_match_wins">
  <case when="[condition]">[action]</case>
  <case when="[condition]">[action]</case>
  <case when="[condition]">[action]</case>
</route>

### [Phase/Step 1]: [Name]

[Prose instructions. Include the rules that apply to THIS phase inline,
not in a separate rules section.]

### [Phase/Step 2]: [Name]

[Prose instructions.]

[If this phase produces structured output:]

<output-schema format="json">
{
  "[field]": "[type]",
  "[field]": "[type]"
}
</output-schema>

</instructions>

<rules>

### [Rule Group Name]

- **[Rule name]:** [Natural language statement with MUST/SHOULD/MAY.]
- **[Rule name]:** [Natural language statement.]

</rules>

<errors>

| Error | Severity | Action |
|-------|----------|--------|
| [name] | critical | [action] |
| [name] | warning | [action] |

</errors>

<examples>

[Edge cases only]
[name]: [input] → [expected outcome — pass or fail and why]

</examples>
```

**Notes for Standard tier:**

- YAML frontmatter is optional. Omit the `---` block if your tooling does not need it.
- `<config>` is optional. Omit if the spec has no configurable parameters (or fewer than 3).
- `<route>` is for 3+ branch conditionals only. For binary conditions, use prose conditionals. Place inside `<instructions>`.
- `<output-schema>` SHOULD be included when the spec produces structured output. Place inside `<instructions>` in the output phase.
- $variable threading is optional. Use only when data flow between phases is complex.
- `<inputs>` / `<outputs>` sections are optional. Include when the spec has clear data boundaries.
- `<rules>` section is for cross-cutting rules only. Phase-specific rules go inline in `<instructions>`.

---

## Complex Tier Template (~200-400 lines)

```markdown
---
title: [Short title]
description: "[One-line description]"
[other frontmatter]
---

# [Spec Name]

<purpose>

[Purpose — 1-3 sentences]

</purpose>

<scope>

**Not in scope:** [exclusions]

</scope>

<inputs>

- `[param]`: [type] - [description] - required/optional

</inputs>

<outputs>

- `[output]`: [type] - [description] - required/optional/conditional

</outputs>

<config>
{
  "[structured config object]": "[value]"
}
</config>

<instructions>

### [Routing] Logic

<route name="[name]" mode="first_match_wins">
  <case when="[condition]">[outcome]</case>
  <case when="[condition]">[outcome]</case>
  <default>[default outcome]</default>
</route>

### [Phase 1]: [Name] → $[variable]

[Instructions. State constraints that apply to this phase HERE,
not in a separate rules section.
Use $variable threading when data flow between phases is complex.]

### [Phase 2]: [Name] → $[variable]

[Instructions. Constraints for this phase stated here.]

### [Output Phase]: [Name]

[Instructions for final output assembly.]

<output-schema format="json">
{
  "[field]": "[type]",
  "[field]": "[type | null]",
  "[nested]": {
    "[field]": "[type]"
  }
}
</output-schema>

</instructions>

<rules>

### [Cross-cutting rule group — only for rules that apply across ALL phases]

- **[Rule]:** [Statement]
- **[Rule]:** [Statement]

</rules>

<errors>

| Error | Severity | Action |
|-------|----------|--------|
| [comprehensive error table] |

</errors>

<examples>

[Edge-case worked examples with pass/fail]

[good_example]:
  [multi-line worked example showing correct behavior]

[bad_example]:
  [multi-line showing incorrect behavior and why it fails]

</examples>
```

**Notes for Complex tier:**

- YAML frontmatter is optional. Omit the `---` block if your tooling does not need it.
- `<inputs>` / `<outputs>` sections are required at complex tier.
- $variable threading is recommended when data flows between phases are complex enough to need explicit tracking.
- `<rules>` section is for cross-cutting rules that apply across ALL phases only. Phase-specific rules go inline in `<instructions>`.
- `<route>` `<default>` element is optional. Include only when a meaningful default exists.
- `<output-schema>` SHOULD be included when the spec produces structured output. Place inside `<instructions>` in the output phase.
- Worked examples SHOULD demonstrate edge cases with explicit pass/fail outcomes.
