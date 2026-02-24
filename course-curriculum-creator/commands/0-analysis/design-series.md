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

````markdown
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
````

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
- "Error: --levels must be a number between 2 and 6. Example: `/design-series "PropTech" --levels 4`"

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
