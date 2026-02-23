# /design-series Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a `/design-series` command that decomposes broad topics into leveled course series (101/201/301/401), and make existing commands series-aware with enforcement.

**Architecture:** New `commands/design-series.md` command file produces a `[series]-series-plan.md` output. Existing commands (`create-course`, `generate-objectives`, `review-curriculum`) gain series-aware sections that read series plan metadata from `course-positioning.md` frontmatter and enforce Bloom's band constraints. All files are markdown with YAML frontmatter -- no code, no tests.

**Tech Stack:** Markdown command files with YAML frontmatter (Claude Code plugin system)

**Design doc:** `docs/plans/2026-02-23-course-series-design.md`

---

## Context for Implementer

**Plugin root:** `/workspaces/claude-plugins/course-curriculum-creator`

**What this plugin is:** An all-markdown Claude Code plugin. Commands are `.md` files with YAML frontmatter that instruct the Claude agent how to behave when a slash command is invoked. There is no runtime code -- the markdown IS the implementation. "Implementing" means writing/editing these instruction files.

**Key conventions:**
- YAML frontmatter: `name`, `description`, `argument-hint`, `allowed-tools`
- `${CLAUDE_PLUGIN_ROOT}` for portable internal references
- Sections like `## Prerequisites`, `## Command Behavior`, `## Settings Integration`, `## Error Handling`
- File output templates are shown as markdown code blocks inside the command file
- Settings read from `.claude/course-curriculum-creator.local.md` YAML frontmatter

**Bloom's Center-of-Gravity Model (from design doc):**
- **Primary band** (60-70% of objectives): Where bulk of teaching time lives
- **Stretch zone**: Higher Bloom's levels touched with scaffolding
- **Assumed floor**: Levels mastered in prior courses, not re-taught
- Default distribution:
  - 101: Primary=Remember/Understand/Apply, Stretch=Analyze, Floor=none
  - 201: Primary=Apply/Analyze, Stretch=Evaluate, Floor=101 outcomes
  - 301: Primary=Analyze/Evaluate, Stretch=Create, Floor=201 outcomes
  - 401: Primary=Evaluate/Create, Stretch=original work, Floor=301 outcomes

---

### Task 1: Create commands/design-series.md -- YAML frontmatter and prerequisites

**Files:**
- Create: `commands/design-series.md`

**Step 1: Create the file with frontmatter and top sections**

Write the file with this exact content:

```markdown
---
name: design-series
description: Design a leveled course series (101/201/301/401) by partitioning a broad topic across progressive Bloom's taxonomy bands
argument-hint: "\"Topic Name\" --levels N [--from-existing path1/ path2/ ...]"
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Glob
---

# Design Series Command

Decompose a broad topic into a progressive course series with distinct scope, Bloom's taxonomy bands, and handoff outcomes for each level.

## Prerequisites

- A broad topic that warrants multiple courses at different levels
- For `--from-existing` mode: existing course directories with `01-planning/learning-objectives.md` and `01-planning/course-positioning.md`

## Command Behavior

When user invokes `/design-series "Topic" --levels N`:

1. **Determine mode:**
   - If `--from-existing` paths provided: use **Retrofit Mode** (see below)
   - Otherwise: use **Design from Scratch Mode**

2. **Gather requirements** (scratch mode) or **analyze existing courses** (retrofit mode)

3. **Generate series plan** using the Bloom's Center-of-Gravity model

4. **Write output:** `[series-name]-series-plan.md` in the courses parent directory

5. **Suggest next steps:** Create individual courses with `/create-course "Topic 101" --series [name] --level 101`
```

**Step 2: Commit**

```bash
git add -f course-curriculum-creator/commands/design-series.md
git commit -m "feat(commands): scaffold design-series.md with frontmatter and prerequisites"
```

---

### Task 2: Add Bloom's Center-of-Gravity model section to design-series.md

**Files:**
- Modify: `commands/design-series.md`

**Step 1: Append the pedagogical model section**

Add after the `## Command Behavior` section:

```markdown
## Bloom's Center-of-Gravity Model

Each level in the series defines three Bloom's taxonomy zones:

- **Primary band** (60-70% of objectives): Where the bulk of teaching time lives
- **Stretch zone**: Higher Bloom's levels touched with heavy scaffolding and low stakes
- **Assumed floor**: Bloom's levels mastered in prior courses -- not re-taught, but assumed as prerequisite knowledge

**The handoff mechanism:** Level N's handoff outcomes become Level N+1's assumed floor.

### Default Distribution

| Level | Primary Band | Stretch Zone | Assumed Floor |
|-------|-------------|-------------|---------------|
| 101 | Remember, Understand, Apply | Analyze | (none -- entry level) |
| 201 | Apply, Analyze | Evaluate | 101 handoff outcomes |
| 301 | Analyze, Evaluate | Create | 201 handoff outcomes |
| 401 | Evaluate, Create | Original synthesis | 301 handoff outcomes |

These defaults are starting points. Adjust per series based on topic and audience:
- A technical series might compress to 3 levels
- A broad domain might expand to 5+ levels
- Audience background shifts where the 101 starts (e.g., professionals vs. students)

### Key Principles

- Every level includes objectives across multiple Bloom's levels -- the primary band is where the center of gravity sits, not a hard ceiling
- Even a 101 can include Analyze-level stretch activities (e.g., a simple case study)
- Even a 401 includes Remember/Understand moments (recalling advanced concepts)
- The stretch zone is always scaffolded: guided, low-stakes, and brief
- The assumed floor is NOT re-taught -- if a 201 student lacks 101 outcomes, they need the prerequisite course
```

**Step 2: Commit**

```bash
git add -f course-curriculum-creator/commands/design-series.md
git commit -m "feat(commands): add Bloom's Center-of-Gravity model to design-series"
```

---

### Task 3: Add Design from Scratch mode to design-series.md

**Files:**
- Modify: `commands/design-series.md`

**Step 1: Append the scratch mode workflow**

Add after the Bloom's model section:

```markdown
## Mode 1: Design from Scratch

When invoked as `/design-series "Topic" --levels N`:

### Step 1: Gather Topic Scope

Use AskUserQuestion to understand the full domain:
- "What is the complete scope of knowledge in [topic]? What would a true expert know?"
- "Who is the entry-level audience (101) and who is the advanced audience (highest level)?"
- "Are there natural breaking points or prerequisite chains in this topic?"
- "How many levels do you want? (default: 4 -- 101/201/301/401)"

### Step 2: Partition Scope Across Levels

For each level (starting from 101):

1. **Define scope statement:** What's in and out of scope for this level
2. **Identify target audience:** Who takes this level, what they should already know
3. **Apply Bloom's bands** from the default distribution (adjust if user specified differently)
4. **List topic areas:** High-level list of what this level covers
5. **Define handoff outcomes:** 3-5 key outcomes students must achieve. These become the next level's prerequisites.
   - Handoff outcomes should be written as Bloom's-aligned objectives at the TOP of this level's primary band
   - Example for 101: "Apply [framework] to analyze [simple case]" (Apply level -- top of 101's primary band)
6. **Suggest duration:** 1-day or 2-day based on scope breadth

### Step 3: Validate Series Coherence

Before writing, check:
- [ ] Every level's assumed floor matches the prior level's handoff outcomes
- [ ] Topic areas don't overlap between levels (or overlap is explicitly intentional as reinforcement)
- [ ] Bloom's progression makes sense across the full series
- [ ] Total scope covers the domain comprehensively (no major gaps)
- [ ] Each level is achievable in the suggested duration

### Step 4: Present Plan for User Approval

Show the user the complete series structure before writing:

For each level, display:
- Scope (1-2 sentences)
- Primary Bloom's band and stretch zone
- Handoff outcomes (bulleted list)
- Suggested duration

Ask: "Does this series structure look right? Any levels to adjust?"

### Step 5: Write Series Plan

Write `[series-name]-series-plan.md` to the courses parent directory (or current directory if no course directory exists yet).
```

**Step 2: Commit**

```bash
git add -f course-curriculum-creator/commands/design-series.md
git commit -m "feat(commands): add Design from Scratch mode to design-series"
```

---

### Task 4: Add Retrofit mode and output template to design-series.md

**Files:**
- Modify: `commands/design-series.md`

**Step 1: Append the retrofit mode and output template**

Add after Mode 1:

```markdown
## Mode 2: Retrofit from Existing Courses

When invoked as `/design-series "Topic" --from-existing ./Course-A/ ./Course-B/ ...`:

### Step 1: Read Existing Courses

For each provided course directory:
1. Read `01-planning/course-positioning.md` for scope, audience, duration
2. Read `01-planning/learning-objectives.md` for objectives and Bloom's levels
3. If available, read `02-design/course-outline.md` for module structure

### Step 2: Analyze Bloom's Distribution

For each course, compute:
- Count of objectives at each Bloom's level
- Percentage distribution across levels
- Identify the "center of gravity" (where most objectives cluster)

### Step 3: Identify Issues

Compare across courses to find:
- **Gaps:** Bloom's levels or topic areas not covered by any course
- **Overlaps:** Content or objectives duplicated across courses
- **Progression issues:** A "beginner" course teaching at Evaluate level, or an "advanced" course re-teaching Apply-level basics
- **Missing handoffs:** No clear prerequisite chain between courses

### Step 4: Propose Series Structure

Based on analysis:
1. Assign each existing course to a series level based on its Bloom's center of gravity
2. Propose adjustments: objectives to move between levels, gaps to fill, overlaps to eliminate
3. Define handoff outcomes for each level
4. Present to user with specific revision recommendations per course

### Step 5: Write Series Plan

Write the series plan with an additional `## Revision Notes` section per level noting what needs to change in each existing course.

## Output Format

### File: [series-name]-series-plan.md

```markdown
---
title: "[Topic] Series Plan"
seriesName: "[kebab-case-name]"
levels: [101, 201, 301, 401]
topic: "[Full topic description]"
createdDate: YYYY-MM-DD
version: 0.1.0
status: draft
bloomsModel: center-of-gravity
---

# [Topic] Course Series Plan

## Series Overview

**Topic:** [Full topic description]
**Levels:** [N] courses (101 through [highest])
**Total Duration:** [Sum of all level durations]
**Audience Progression:** [101 audience] → [highest level audience]

---

## Level 101: [Level Title]

**Scope:** [What this level covers and explicitly excludes]

**Target Audience:** [Who takes this, what they already know]

**Bloom's Taxonomy Bands:**
- **Primary band (60-70%):** Remember, Understand, Apply
- **Stretch zone:** Analyze (scaffolded, guided)
- **Assumed floor:** None (entry level)

**Suggested Duration:** [1-day or 2-day]

**Topic Areas:**
- [Topic 1]
- [Topic 2]
- [Topic 3]

**Handoff Outcomes** (become 201 prerequisites):
1. [Outcome 1 -- written as Bloom's-aligned objective]
2. [Outcome 2]
3. [Outcome 3]

---

## Level 201: [Level Title]

**Scope:** [What this level covers]

**Target Audience:** [Who takes this -- must have completed 101 or equivalent]

**Bloom's Taxonomy Bands:**
- **Primary band (60-70%):** Apply, Analyze
- **Stretch zone:** Evaluate (scaffolded)
- **Assumed floor:** 101 handoff outcomes (not re-taught)

**Suggested Duration:** [1-day or 2-day]

**Prerequisites** (from 101 handoff outcomes):
1. [101 Outcome 1]
2. [101 Outcome 2]
3. [101 Outcome 3]

**Topic Areas:**
- [Topic 1]
- [Topic 2]

**Handoff Outcomes** (become 301 prerequisites):
1. [Outcome 1]
2. [Outcome 2]
3. [Outcome 3]

---

[Repeat for each level]

---

## Series Coherence Summary

### Bloom's Progression

| Level | Remember | Understand | Apply | Analyze | Evaluate | Create |
|-------|----------|-----------|-------|---------|----------|--------|
| 101 | ● | ● | ●● | ○ | | |
| 201 | | | ● | ●● | ○ | |
| 301 | | | | ● | ●● | ○ |
| 401 | | | | | ● | ●● |

● = primary band, ○ = stretch zone

### Handoff Chain

101 outcomes → 201 prerequisites → 201 outcomes → 301 prerequisites → ...

### Topic Coverage

[Matrix or list showing which topics are covered at which level]

## Next Steps

1. Create individual courses:
   - `/create-course "[Topic] 101" --series [name] --level 101`
   - `/create-course "[Topic] 201" --series [name] --level 201`
   - [etc.]
2. When generating objectives for each course, the series plan will enforce Bloom's band constraints
3. Run `/review-curriculum` on each course to validate series alignment

## Revision Notes (Retrofit Mode Only)

### [Existing Course Name]
**Assigned Level:** [N]
**Changes Needed:**
- Move objectives [X, Y] to level [N+1] (above this level's Bloom's band)
- Add objectives for [gap topic] at [Bloom's level]
- Remove/revise objective [Z] (duplicates level [N-1] content)
```
```

**Step 2: Commit**

```bash
git add -f course-curriculum-creator/commands/design-series.md
git commit -m "feat(commands): add Retrofit mode and output template to design-series"
```

---

### Task 5: Add Settings Integration, Error Handling, and examples to design-series.md

**Files:**
- Modify: `commands/design-series.md`

**Step 1: Append the remaining sections**

Add after the output format:

```markdown
## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `courses_directory`: Default location for writing series plan (if not in a courses directory)
- `default_duration`: Suggest as default duration for each level
- `default_audience_level`: Inform where the 101 starts

If settings file doesn't exist, use sensible defaults or prompt user.

## Error Handling

**No topic provided:**
- Prompt: "What broad topic should this series cover?"

**Invalid --levels value:**
- "Error: --levels must be a number between 2 and 6. Example: `/design-series \"PropTech\" --levels 4`"

**--from-existing paths don't exist:**
- "Error: Course directory [path] not found. Verify the path and try again."

**--from-existing courses missing objectives:**
- "Warning: [course] is missing learning-objectives.md. Analysis will be based on course-positioning.md only. For complete analysis, generate objectives first with `/generate-objectives`."

**Series plan already exists:**
- Prompt: "A series plan for [name] already exists. Options: (1) Overwrite, (2) Create new version, (3) Cancel"

## Example Usage

**Design from scratch:**
```
User: /design-series "PropTech" --levels 4
[Plugin gathers scope, partitions across 101/201/301/401, writes proptech-series-plan.md]
```

**Retrofit existing:**
```
User: /design-series "PropTech" --from-existing ./PropTech-Basics-2026-01/ ./PropTech-Advanced-2026-02/
[Plugin reads existing courses, analyzes Bloom's distribution, proposes series structure]
```

**Custom level count:**
```
User: /design-series "Data Science" --levels 3
[Plugin creates 101/201/301 series with 3-level Bloom's distribution]
```

---

Design progressive course series that build systematically from foundational to advanced mastery, with clear handoffs and enforced Bloom's taxonomy progression.
```

**Step 2: Commit**

```bash
git add -f course-curriculum-creator/commands/design-series.md
git commit -m "feat(commands): complete design-series with settings, errors, and examples"
```

---

### Task 6: Modify create-course.md to support --series and --level flags

**Files:**
- Modify: `commands/create-course.md`

**Step 1: Update argument-hint**

Change line 4 from:
```
argument-hint: "[Course Title] [--duration 1-day|2-day] [--location path]"
```
To:
```
argument-hint: "[Course Title] [--duration 1-day|2-day] [--location path] [--series name --level N]"
```

**Step 2: Add Series Integration section**

Add a new `## Series Integration` section after the `## Settings Integration` section (after line 79). Insert:

```markdown
## Series Integration

When `--series` and `--level` flags are provided:

### Step 1: Locate Series Plan

Search for `[series-name]-series-plan.md`:
1. In the `--location` directory (if provided)
2. In the `courses_directory` from settings
3. In the current working directory
4. In the parent of the current working directory

If not found: "Error: Series plan '[name]-series-plan.md' not found. Run `/design-series` first to create the series plan."

### Step 2: Read Level Configuration

From the series plan, read the section for the specified level:
- Target audience → use as audience description
- Prerequisites (from prior level's handoff outcomes) → use as prerequisites
- Scope statement → use as value proposition context
- Suggested duration → use as default duration (can be overridden by `--duration`)

### Step 3: Pre-populate Course Positioning

When generating `course-positioning.md`, add series metadata to the YAML frontmatter:

```yaml
seriesName: "[series-name]"
seriesLevel: [N]
seriesPlanFile: "[relative-path-to-series-plan.md]"
```

And pre-populate these sections from the series plan:
- **Target Audience**: From the level's target audience
- **Prerequisites**: From the prior level's handoff outcomes (listed explicitly)
- **Scope > In Scope**: From the level's scope statement and topic areas
- **Scope > Out of Scope**: Topics covered by other levels in the series

### Step 4: Report Series Context

In the completion message, add:
```
Series: [series-name] (Level [N] of [total])
Prerequisites from Level [N-1]: [list handoff outcomes]

Next: Generate objectives within this level's Bloom's bands using /generate-objectives
```
```

**Step 3: Commit**

```bash
git add course-curriculum-creator/commands/create-course.md
git commit -m "feat(commands): add --series/--level flags to create-course"
```

---

### Task 7: Modify generate-objectives.md to enforce series Bloom's bands

**Files:**
- Modify: `commands/generate-objectives.md`

**Step 1: Add Series Enforcement section**

Add a new `## Series Enforcement` section after the `## Staleness Check` section (around line 33). Insert:

```markdown
## Series Enforcement

If `course-positioning.md` contains `seriesName` and `seriesLevel` in its YAML frontmatter:

### Step 1: Load Series Context

1. Read `seriesPlanFile` path from positioning frontmatter
2. Read the series plan and extract this level's configuration:
   - Primary Bloom's band
   - Stretch zone
   - Assumed floor (prior level's handoff outcomes)

### Step 2: Constrain Generation

When generating objectives:
- Target 60-70% of objectives within the **primary band**
- Allow up to 20% in the **stretch zone** (must be scaffolded)
- Do NOT generate objectives at levels below the **assumed floor** (these are prerequisites, not learning targets)
- Ensure assumed floor outcomes appear in the course prerequisites, not as new objectives

### Step 3: Post-Generation Validation

After generating all objectives, validate each one:

For each objective, check its Bloom's level against the series bands:

**If within primary band:** Pass (no action needed)

**If within stretch zone:** Note in validation output: "Objective #N is in the stretch zone ([level]). Ensure it includes scaffolding and guided practice."

**If outside both primary band and stretch zone (too high):**
Prompt the user with AskUserQuestion:
"Objective #[N] ('[objective text]') is at [Bloom's level], which is above this level's stretch zone ([stretch zone]).

Options:
1. Keep it anyway (override series constraint)
2. Move it to Level [N+1]'s plan (note for future)
3. Revise to [highest stretch zone level] with scaffolding"

**If below assumed floor (too low / re-teaching):**
Prompt the user:
"Objective #[N] ('[objective text]') is at [Bloom's level], which is in the assumed floor for Level [level]. This should have been mastered in Level [N-1].

Options:
1. Keep it as a brief review activity (not a formal objective)
2. Remove it (trust the prerequisite chain)
3. Keep it as a formal objective (override series constraint)"

### Step 4: Update Cognitive Level Distribution

In the generated `Cognitive Level Distribution` section, add a series compliance note:

```
## Series Compliance

**Series:** [name] | **Level:** [N]
**Primary band:** [levels] | **Stretch zone:** [levels]
**Objectives in primary band:** [count] ([%])
**Objectives in stretch zone:** [count] ([%])
**Overrides:** [count] (user chose to keep objectives outside bands)
```
```

**Step 2: Commit**

```bash
git add course-curriculum-creator/commands/generate-objectives.md
git commit -m "feat(commands): add series Bloom's band enforcement to generate-objectives"
```

---

### Task 8: Modify review-curriculum.md to add series validation

**Files:**
- Modify: `commands/review-curriculum.md`

**Step 1: Add Series Validation section**

Add a new section before `## Quality Rating Criteria` (before line 95). Insert after the existing Stage 3 / Overall Coherence / Timing Reconciliation sections:

```markdown
   **Series Alignment (if course is linked to a series):**

   If `course-positioning.md` contains `seriesName` and `seriesLevel`:

   1. Read the series plan file
   2. Validate with **CRITICAL** severity:
      - **Bloom's distribution compliance:** At least 60% of objectives fall within the level's primary band. Flag as CRITICAL if below 50%.
      - **Stretch zone usage:** Stretch zone objectives include scaffolding and guided practice in lesson plans. Flag as CRITICAL if stretch objectives lack scaffolding.
      - **Assumed floor violations:** No objectives re-teach content from the assumed floor. Flag as CRITICAL if formal objectives duplicate prior level's handoff outcomes.
      - **Prerequisite chain:** Prior level's handoff outcomes appear in this course's prerequisites section. Flag as CRITICAL if missing.
      - **Scope containment:** Course topics stay within the level's defined scope. Flag as HIGH if topics encroach on other levels' domains.
      - **Handoff outcome coverage:** This level's handoff outcomes (from series plan) are covered by at least one objective. Flag as CRITICAL if a handoff outcome has no matching objective.

   3. Add to validation report:
      ```
      ### Series Alignment Validation
      **Status:** PASS / FAIL
      **Series:** [name] | **Level:** [N]

      | Check | Status | Details |
      |-------|--------|---------|
      | Bloom's distribution | PASS/FAIL | [X]% in primary band (target: 60%+) |
      | Stretch scaffolding | PASS/FAIL | [N] stretch objectives, [N] with scaffolding |
      | Assumed floor | PASS/FAIL | [N] objectives below floor |
      | Prerequisite chain | PASS/FAIL | [N] of [N] handoffs present as prereqs |
      | Scope containment | PASS/FAIL | [notes] |
      | Handoff coverage | PASS/FAIL | [N] of [N] handoffs covered by objectives |
      ```

   Note: If course is NOT linked to a series, skip this entire section silently.
```

**Step 2: Commit**

```bash
git add course-curriculum-creator/commands/review-curriculum.md
git commit -m "feat(commands): add CRITICAL series validation to review-curriculum"
```

---

### Task 9: Update README.md and plugin.json

**Files:**
- Modify: `README.md`
- Modify: `.claude-plugin/plugin.json`

**Step 1: Add /design-series to README command table**

In the `## Commands` table, add after the `/review-curriculum` row:

```markdown
| `/design-series` | Design a leveled course series (101/201/301/401) |
```

**Step 2: Add Course Series section to README**

After the `## Template System` section, add:

```markdown
## Course Series

Design progressive course series that build from foundational to advanced mastery:

```bash
# Design a 4-level series
/design-series "PropTech" --levels 4

# Create individual courses linked to the series
/create-course "PropTech 101" --series proptech --level 101
/create-course "PropTech 201" --series proptech --level 201

# Series plan enforces Bloom's bands during objective generation
/generate-objectives    # warns if objectives outside level's bands

# Retrofit existing courses into a series
/design-series "PropTech" --from-existing ./PropTech-Basics/ ./PropTech-Advanced/
```

Series use a **Bloom's Center-of-Gravity model** where each level has a primary Bloom's band (where 60-70% of objectives live), a stretch zone (higher levels with scaffolding), and an assumed floor (mastered in prior levels, not re-taught).
```

**Step 3: Bump plugin version**

Change version in `.claude-plugin/plugin.json` from `"0.2.0"` to `"0.3.0"`.

**Step 4: Commit**

```bash
git add course-curriculum-creator/README.md course-curriculum-creator/.claude-plugin/plugin.json
git commit -m "docs: add /design-series to README and bump to v0.3.0"
```

---

### Task 10: Final validation

**Files:** All modified/created files

**Step 1: Validate YAML frontmatter**

```bash
cd /workspaces/claude-plugins/course-curriculum-creator
for f in commands/design-series.md commands/create-course.md commands/generate-objectives.md commands/review-curriculum.md; do
  echo "=== $f ==="
  python3 -c "
import yaml, sys
with open('$f') as fh:
    content = fh.read()
parts = content.split('---', 2)
data = yaml.safe_load(parts[1])
print(f'OK: name={data[\"name\"]}')
"
done
```

Expected: All 4 files print OK with correct names.

**Step 2: Validate plugin.json**

```bash
python3 -c "import json; d=json.load(open('.claude-plugin/plugin.json')); print(f'OK: version={d[\"version\"]}')"
```

Expected: `OK: version=0.3.0`

**Step 3: Check README command table matches commands/ directory**

```bash
ls commands/ | wc -l
```

Expected: 15 (was 14, +1 for design-series.md). Count commands in README table and verify they match.

**Step 4: Grep for hardcoded paths**

```bash
grep -r "/home/codespace" commands/ agents/ hooks/
```

Expected: No matches.

**Step 5: Run plugin-validator**

Use the `plugin-dev:plugin-validator` agent to validate the complete plugin structure.
