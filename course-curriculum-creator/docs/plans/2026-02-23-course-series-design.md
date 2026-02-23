# Design: /design-series Command for Course Series Planning

**Date:** 2026-02-23
**Status:** Approved
**Component:** `commands/design-series.md` (new command)
**Plugin:** course-curriculum-creator v0.2.0

---

## Problem

The plugin treats each course as a standalone island. There's no way to:
- Decompose a broad topic into a leveled series (101/201/301/401)
- Track what Bloom's levels one course tops out at so the next starts there
- Ensure prerequisites and outcomes chain across courses
- Avoid content overlap between levels
- Retrofit existing standalone courses into a coherent pathway

## Solution

A `/design-series` command that produces a **series plan document** defining scope, Bloom's bands, and handoff outcomes for each level. Existing commands become series-aware through enforcement prompts and CRITICAL review findings.

## Core Concept: Bloom's Center-of-Gravity Model

Rather than hard Bloom's ceilings per level, the series plan defines three zones:

- **Primary band** (60-70% of objectives): Where the bulk of teaching time lives
- **Stretch zone**: Higher Bloom's levels touched with heavy scaffolding, low stakes
- **Assumed floor**: Bloom's levels mastered in prior courses, not re-taught

The handoff mechanism: Level N's **handoff outcomes** become Level N+1's **assumed floor**.

### Default Bloom's Distribution

| Level | Primary Band | Stretch Zone | Assumed Floor |
|-------|-------------|-------------|---------------|
| 101 | Remember, Understand, Apply | Analyze | (none) |
| 201 | Apply, Analyze | Evaluate | 101 handoff outcomes |
| 301 | Analyze, Evaluate | Create | 201 handoff outcomes |
| 401 | Evaluate, Create | (original research/synthesis) | 301 handoff outcomes |

These defaults are configurable per series.

## Output: Series Plan Document

### File Location

Stored at the parent level alongside course directories:

```
~/courses/
├── proptech-series-plan.md          ← series plan
├── PropTech-101-2026-03-01/         ← individual courses
├── PropTech-201-2026-03-15/
└── ...
```

### File Structure

```yaml
---
title: "[Topic] Series Plan"
seriesName: "[kebab-case-name]"
levels: [101, 201, 301, 401]
topic: "[Full topic description]"
createdDate: YYYY-MM-DD
version: 0.1.0
status: draft
---
```

For each level, a section containing:

- **Scope statement**: What's in/out for this level
- **Target audience**: Who takes this level, what they already know
- **Bloom's primary band**: Where 60-70% of objectives live
- **Bloom's stretch zone**: Higher levels touched with scaffolding
- **Assumed floor**: Bloom's levels/outcomes mastered from prior level (empty for 101)
- **Handoff outcomes**: 3-5 key outcomes that become the next level's prerequisites
- **Suggested duration**: 1-day or 2-day
- **Topic areas**: High-level list of what's covered

## Command Workflow

### Mode 1: Design from Scratch

```
/design-series "PropTech" --levels 4
```

1. Gather the broad topic scope and overall audience progression
2. Use AskUserQuestion to understand:
   - What's the full scope of knowledge in this domain?
   - Who's the 101 audience vs. the 401 audience?
   - Are there natural breaking points in the topic?
3. Partition scope across levels using Bloom's center-of-gravity model
4. For each level, define handoff outcomes (what the next level assumes you can do)
5. Write `[series-name]-series-plan.md`
6. Suggest next steps: `/create-course "[Topic] 101" --series [name] --level 101`

### Mode 2: From Existing Courses

```
/design-series "PropTech" --from-existing ./PropTech-Basics/ ./PropTech-Advanced/
```

1. Read each existing course's `learning-objectives.md` and `course-positioning.md`
2. Analyze Bloom's distribution and scope of each course
3. Identify:
   - **Gaps**: Topics or Bloom's levels not covered by any course
   - **Overlaps**: Content duplicated across courses
   - **Bloom's progression issues**: Level N teaching above its band, Level N+1 re-teaching floor content
4. Propose a series structure that reorganizes the content
5. Generate the series plan with revision notes for each existing course

## Integration with Existing Commands

### /create-course --series [name] --level [N]

When creating a course linked to a series:
- Reads the series plan to pre-populate:
  - Prerequisites (from prior level's handoff outcomes)
  - Audience description (from this level's target audience section)
  - Scope boundaries (from this level's in/out-of-scope)
- Adds `seriesName` and `seriesLevel` to `course-positioning.md` YAML frontmatter

### /generate-objectives (within a series-linked course)

Detects `seriesName`/`seriesLevel` in positioning frontmatter. After generating objectives:
- Validates each objective's Bloom's level against the series plan's bands
- If an objective falls outside the primary band + stretch zone, **prompts the user**:
  "Objective #3 (Evaluate level) is outside 101's primary band (Remember/Understand/Apply) and stretch zone (Analyze). Options: (1) Keep it anyway, (2) Move it to 201's plan, (3) Revise to a lower Bloom's level"
- Checks for objectives that duplicate the assumed floor (re-teaching prior level content)

### /review-curriculum (within a series-linked course)

Adds series-specific validation with **CRITICAL** severity:
- Bloom's distribution matches the level's defined bands
- Handoff outcomes from prior level appear as prerequisites
- No scope creep into other levels' domains
- Handoff outcomes for this level are actually covered by objectives

Series violations appear as CRITICAL findings requiring resolution before the review can pass.

### hooks.json (optional extension)

Could extend the existing PreToolUse hooks to validate series constraints when writing objectives files. Deferred to implementation planning.

## What This Does NOT Do

- Does not auto-generate individual courses (plan only, user drives `/create-course`)
- Does not manage enrollment or student progression between levels
- Does not enforce a fixed number of levels (user chooses 2, 3, 4, or more)
- Does not require all levels to be the same duration

## Files Changed/Created

| File | Action | Description |
|------|--------|-------------|
| `commands/design-series.md` | Create | New command with both modes |
| `commands/create-course.md` | Modify | Add `--series` and `--level` argument handling |
| `commands/generate-objectives.md` | Modify | Add series-aware Bloom's validation with prompts |
| `commands/review-curriculum.md` | Modify | Add series-specific CRITICAL validation |
| `README.md` | Modify | Add command to table, document series workflow |
| `plugin.json` | Modify | Version bump |
