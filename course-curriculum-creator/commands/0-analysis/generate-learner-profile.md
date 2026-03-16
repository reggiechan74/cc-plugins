---
name: generate-learner-profile
description: Generate a learner profile analyzing audience prior knowledge, motivational drivers, learning constraints, transfer environment, and resistance points
argument-hint: "[--from-tna]"
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Edit
---

# Generate Learner Profile Command

Generate a comprehensive learner profile that informs curriculum differentiation, example selection, and transfer planning. The profile captures five dimensions of the target audience: prior knowledge, motivational drivers, learning preferences and constraints, transfer environment, and resistance points. Each dimension maps directly to concrete curriculum design decisions.

## Why This Matters

Designing a course without understanding the audience leads to:

- **Mismatched difficulty** — content too basic for experienced learners or too advanced for novices
- **Low engagement** — examples and framing that don't connect to participants' real context
- **Poor transfer** — skills taught but never applied because the workplace doesn't support them
- **Unnecessary resistance** — objections that could have been preemptively addressed in design

A learner profile ensures that differentiation tiers, example domains, scaffolding depth, and transfer strategies are calibrated to the actual audience rather than assumed defaults.

## Prerequisites

- A course topic or context (can come from existing course-positioning.md or be gathered interactively)
- Ideally, a training needs analysis has been completed first (`01-planning/training-needs-analysis.md`)

## Command Behavior

When user invokes `/generate-learner-profile [--from-tna]`:

### Step 1: Load Existing Context

1. **Read `01-planning/course-positioning.md`** (if exists) for audience context — extract course title, target audience description, and any stated prerequisites. Use this to pre-populate questions where possible.

2. **Read `01-planning/training-needs-analysis.md`** (if exists or `--from-tna` flag provided) for gap type and population data — pre-populate answers where TNA already has the data. Specifically extract:
   - Target population skill range
   - Prior related training
   - Gap type classification
   - Learning context

If either file exists and provides relevant data, inform the user: "I found existing data in [file] — I'll pre-populate where I can. You can confirm or override each item."

### Step 2: Gather Five Dimensions Interactively

Use AskUserQuestion to gather each dimension. For each dimension, present pre-populated data from Step 1 (if available) and ask the user to confirm, correct, or expand.

#### Dimension 1: Prior Knowledge Inventory

What participants already know and what they cannot yet do.

Ask: "What can participants already do related to this topic? List 3-5 skills or concepts they're comfortable with."

Then ask: "What can participants NOT yet do? List 3-5 skills or concepts that represent gaps. For each, indicate whether it's a critical prerequisite, moderate gap, or minor gap."

Map responses to prerequisites — what must be true before Day 1 versus what the course will teach.

#### Dimension 2: Motivational Drivers

Why participants are attending and what drives their engagement.

Ask: "Why are participants taking this course?
(a) Required by organization — mandatory attendance
(b) Self-selected for career growth
(c) Mixed — some mandatory, some voluntary
(d) Other — please describe"

Follow up: "What do participants hope to gain? What would make them say 'this was worth my time'?"

#### Dimension 3: Learning Preferences & Constraints

Practical constraints that shape design decisions.

Ask: "What constraints should we design around? Consider:
- Technology access and proficiency level
- Language considerations (primary languages, proficiency)
- Accessibility needs (known or anticipated)
- Schedule constraints (time zones, availability windows)
- Expected group size
- Attention span expectations (e.g., max session length)"

#### Dimension 4: Transfer Environment

Whether the workplace will support applying new skills after the course.

Ask: "After the workshop, what support will participants have?
(a) Manager actively reinforcing — follows up, provides practice opportunities
(b) Manager aware but hands-off — knows about the training but won't actively support
(c) No manager involvement — manager may not know about the training
(d) Unknown — we don't have this information yet"

Follow up: "Will participants have access to the tools and resources needed to practice? Are there competing priorities that might prevent application?"

#### Dimension 5: Resistance Points

Anticipated objections, prior negative experiences, or competing priorities.

Ask: "What resistance or skepticism do you anticipate? Consider:
- Prior negative training experiences
- 'We've tried this before' attitudes
- Competing workload pressures
- Skepticism about the topic's relevance
- Cultural or organizational barriers"

### Step 3: Generate Design Implications

Map each finding to a concrete curriculum decision. For each significant finding, create a row in the Design Implications table following this pattern:

| Finding | Curriculum Impact | Action |
|---|---|---|
| High tech anxiety | Add Module 0 tech orientation | Include step-by-step screenshots in all activities |
| Mandatory attendance | Extra engagement hooks needed | Add immediate relevance connections in every module opening |
| Low manager support | Stronger self-directed transfer plan | Add peer accountability groups, self-directed action items |
| Mixed skill levels | Wider differentiation tiers needed | Design floor/extension tiers with larger spread in practice activities |

Generate differentiation guidance:
- **Floor tier** should assume: [baseline capability derived from prior knowledge inventory]
- **Extension tier** should challenge: [stretch capability derived from gaps and motivations]
- **Scaffolding emphasis**: [where extra support is needed based on constraints and resistance]

### Step 4: Write Output

Write the learner profile to `01-planning/learner-profile.md`.

Compute sourceHashes by running:
```bash
md5sum 01-planning/course-positioning.md 2>/dev/null | cut -c1-8
```

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if it exists:
- `instructor_name`: Use as analyst name in the output document
- `organization`: Use as organization in the output document

If settings file doesn't exist, omit these fields from frontmatter rather than prompting (they are optional for this document).

## Output Format

Generate the learner profile with the following structure:

```markdown
---
title: Learner Profile - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
lastUpdated: YYYY-MM-DD
sourceFiles:
  course-positioning: "01-planning/course-positioning.md"
sourceHashes:
  course-positioning: "[md5-first-8]"
---

# Learner Profile

## [Course Title]

**Purpose:** Inform curriculum differentiation, example selection, and transfer planning based on audience analysis.

---

## 1. Prior Knowledge Inventory

### What Participants Can Already Do
| Skill/Concept | Confidence Level | Evidence |
|---|---|---|
| [Skill 1] | [High/Medium/Low] | [How we know] |

### What Participants Cannot Yet Do
| Skill/Concept | Gap Severity | Implication |
|---|---|---|
| [Skill 1] | [Critical/Moderate/Minor] | [Prerequisite? Pre-work? Module focus?] |

### Prerequisite Mapping
[Map prior knowledge to course prerequisites — what must be true before Day 1]

---

## 2. Motivational Drivers

| Factor | Finding | Design Response |
|---|---|---|
| Attendance type | [Voluntary/Mandatory/Mixed] | [Engagement strategy] |
| Primary motivation | [Career/Compliance/Curiosity/Other] | [Relevance framing] |
| Expected ROI | [What participants hope to gain] | [Value prop emphasis] |

---

## 3. Learning Preferences & Constraints

| Constraint | Details | Accommodation |
|---|---|---|
| Technology proficiency | [Level] | [Tech orientation needed?] |
| Language considerations | [Primary languages] | [Glossary, pacing, visual aids] |
| Accessibility needs | [Known or anticipated] | [Specific UDL measures] |
| Schedule constraints | [Time zones, availability] | [Session timing] |
| Group size | [Expected N] | [Activity format implications] |

---

## 4. Transfer Environment

| Factor | Assessment | Risk Level |
|---|---|---|
| Manager support | [Active/Aware/None/Unknown] | [High/Medium/Low] |
| Tool/resource access | [Available/Partial/None] | [High/Medium/Low] |
| Competing priorities | [Description] | [High/Medium/Low] |
| Organizational culture | [Supports learning?] | [High/Medium/Low] |

**Transfer risk summary:** [Overall assessment of how likely participants are to apply learning post-workshop]

---

## 5. Resistance Points

| Anticipated Resistance | Source | Mitigation Strategy |
|---|---|---|
| [Resistance 1] | [Why they feel this way] | [How to address in curriculum] |

---

## 6. Design Implications

**Priority adjustments based on this profile:**

| Finding | Curriculum Impact | Action |
|---|---|---|
| [Finding 1] | [What to change] | [Specific file/command affected] |
| [Finding 2] | [What to change] | [Specific file/command affected] |

**Differentiation guidance:**
- Floor tier should assume: [baseline capability]
- Extension tier should challenge: [stretch capability]
- Scaffolding emphasis: [where extra support is needed]
```

If `sourceFiles` entries don't exist (files were not found), omit those entries from the frontmatter rather than including empty values.

## Integration Points

- `generate-lesson-plans` reads learner profile for differentiation tier calibration and example domain selection
- `generate-transfer-plan` reads transfer environment section to calibrate manager briefing depth and self-directed vs. supported action plans
- `generate-pre-work` reads prior knowledge inventory to determine pre-work depth
- `quality-reviewer` agent checks learner profile exists and flags if differentiation tiers don't match profile findings
- `curriculum-architect` agent adds learner profile generation as Phase 3.5 (after course initialization, before objectives)

## Error Handling

**No course directory:**
- Save as `learner-profile-YYYY-MM-DD.md` in current directory (same pattern as standalone TNA)
- This supports running the profile before a course directory has been created

**Course positioning missing:**
- Proceed without pre-population, gather all data interactively
- Inform the user: "No course-positioning.md found — I'll gather all information interactively."

**User skips sections:**
- Mark skipped sections as "[Not assessed — skipped by user]"
- Still generate the document with available information
- Note in the document which sections were skipped

**Settings file not found:**
- Omit optional settings-derived fields from output
- Do not block or prompt for these values

## Implementation Notes

**Date retrieval:**
Always use bash to get current date:
```bash
TZ='America/New_York' date '+%Y-%m-%d'
```

**Path handling:**
- Check for `01-planning/` directory in current working directory to determine output mode
- Use absolute paths in success messages
- Expand ~ to full path if applicable

**YAML frontmatter:**
- All dates in YYYY-MM-DD format
- Version starts at 0.1.0 (semantic versioning)
- Status starts as "draft"
- sourceHashes use first 8 characters of md5sum

**DO NOT:**
- Skip interactive questioning and fabricate learner data
- Assume all participants are the same — always probe for skill range and diversity
- Use relative dates ("today", "current") — always get actual date via bash
- Generate a profile without user input on at least the prior knowledge dimension
- Ignore resistance points — even if the user says "none", probe gently for hidden concerns
- Copy TNA population data verbatim without confirming it's still current and complete

---

Ensure every curriculum decision traces back to evidence gathered in this learner profile.
