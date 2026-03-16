---
name: generate-pre-work
description: Design pre-workshop micro-learning units to cover prerequisites and free Day 1 for Apply+ activities
argument-hint: "[--format full|micro-only|emails-only]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Skill
---

# Generate Pre-Work Command

Design pre-workshop micro-learning units that cover foundational prerequisites, freeing Day 1 for hands-on application activities.

## Prerequisites

- Must have `01-planning/learning-objectives.md` (run `/generate-objectives` first if missing)
- Should have `01-planning/learner-profile.md` (optional — used to calibrate depth and format)

## Staleness Check

Before generating, check if source files have changed since this file was last generated:

1. If the output file `04-materials/pre-work.md` already exists, read its YAML frontmatter `sourceHashes`
2. Compute current hash of each source file:
   - `md5sum 01-planning/learning-objectives.md | cut -c1-8`
   - `md5sum 01-planning/learner-profile.md | cut -c1-8` (if file exists)
3. Compare hashes:
   - If hashes match: sources are unchanged, proceed normally
   - If hashes differ: warn the user: "⚠ Source file [name] has changed since this file was last generated. Regenerating will incorporate these changes."
   - If output file doesn't exist: skip check, proceed with generation

When generating, always compute and write current source hashes to the output file's frontmatter.

## Command Behavior

1. Load `blooms-taxonomy` skill for cognitive level identification
2. Read `01-planning/learning-objectives.md` — identify:
   - Remember-level objectives → candidates for full pre-work coverage
   - Understand-level objectives → candidates for introduction/preview in pre-work
   - Apply+ objectives → extract implied prerequisites not covered by explicit objectives
3. Read `01-planning/learner-profile.md` (if exists) — calibrate:
   - High prior knowledge → shorter pre-work, quiz-only fast track
   - Low prior knowledge → fuller explanations, more examples
   - Tech constraints → text-based pre-work over video
4. Design micro-learning units (see rules below)
5. Generate readiness self-assessment
6. Generate reminder email templates
7. Write to `04-materials/pre-work.md`

## Micro-Learning Unit Design Rules

- **Maximum 3 units**, maximum 30 minutes total completion time
- Each unit: **10-15 minutes**, single concept focus, one self-check question at end
- Two paths per unit:
  - **Fast track:** Already familiar — read 2-sentence summary, take self-check quiz, done (2-3 min)
  - **Full path:** Concept explanation + 1-2 examples + self-check quiz (10-15 min)
- Units ordered by **dependency** (if concept B requires concept A, unit A comes first)

## Readiness Self-Assessment

- **5-8 questions** matching prerequisite concepts (not workshop content)
- Include answer key with brief explanations for each answer
- Score interpretation:
  - 8/8 or 7/8: Well prepared. The workshop will build on these foundations.
  - 5/8 or 6/8: Review the units for questions missed.
  - Below 5/8: Complete all pre-work units in full path mode before attending.

## Email Templates

### T-7 Days: Welcome & Pre-Work Instructions

- **Subject:** Prepare for [Course Title] — [Date]
- Body includes: welcome message, pre-work link, estimated completion time, contact for questions

### T-2 Days: Reminder

- **Subject:** Reminder: Complete pre-work for [Course Title] — [Date]
- Body includes: reminder, direct link to self-assessment, support contact

## Format Options

- `--format full` (default): All components — micro-learning units, self-assessment, email templates
- `--format micro-only`: Just the micro-learning units
- `--format emails-only`: Just the email templates (for when pre-work content already exists)

## Output Format

Write to `04-materials/pre-work.md` using this template:

```markdown
---
title: Pre-Work Materials - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
courseVersion: [match]
lastUpdated: YYYY-MM-DD
totalEstimatedTime: "[N] minutes (fast track: [M] minutes)"
sourceFiles:
  learning-objectives: "01-planning/learning-objectives.md"
  learner-profile: "01-planning/learner-profile.md"
sourceHashes:
  learning-objectives: "[md5-first-8]"
  learner-profile: "[md5-first-8]"
---

# Pre-Work Materials

## [Course Title]

**Purpose:** Prepare participants with foundational knowledge before the workshop, freeing Day 1 for hands-on application.

**Total Time:** [N] minutes (full path) | [M] minutes (fast track)

**Instructions for Participants:**
Complete these materials before [workshop date]. If you're already familiar with a topic, use the Fast Track option to verify your knowledge quickly.

---

## Unit 1: [Concept Title]

**Prerequisite for:** Module [N] — [Module Title]
**Estimated Time:** [N] min (full) | [M] min (fast track)

### Fast Track
[2-3 sentence summary of the concept]

**Quick Check:** [Single question to verify understanding]

If you answered correctly, skip to Unit 2. If not, complete the Full Path below.

### Full Path

[Concept explanation — clear, concise, with concrete example]

**Example 1:** [Domain-relevant example]

**Example 2:** [Different context example for transfer]

**Self-Check:** [Question matching the prerequisite level]
- Answer: [With brief explanation]

---

[Repeat for each unit, up to 3 maximum]

---

## Readiness Self-Assessment

**Instructions:** Answer these questions to verify you're ready for the workshop. You should be able to answer at least 6 of 8 correctly.

1. [Question targeting prerequisite concept 1]
2. [Question targeting prerequisite concept 2]
...

### Answer Key
[Answers with brief explanations]

### Score Interpretation
- 8/8 or 7/8: You're well prepared. The workshop will build on these foundations.
- 5/8 or 6/8: Review the units for questions you missed.
- Below 5/8: Complete all pre-work units in full path mode before attending.

---

## Email Templates

### T-7 Days: Welcome & Pre-Work Instructions

**Subject:** Prepare for [Course Title] — [Date]

[Email body with welcome, pre-work link, estimated time, contact for questions]

### T-2 Days: Reminder

**Subject:** Reminder: Complete pre-work for [Course Title] — [Date]

[Email body with reminder, direct link to self-assessment, support contact]
```

## Validation Checks

- Total pre-work time does not exceed 30 minutes (warn if it does — completion rates drop sharply)
- Every pre-work unit maps to a specific objective or prerequisite
- Self-assessment questions match prerequisite concepts, not workshop content
- Fast track path exists for every unit (don't force experienced participants through full content)

## Integration Points

- `generate-lesson-plans` checks if `04-materials/pre-work.md` exists:
  - If yes, adjust Day 1 Module 1: skip foundation content already covered in pre-work, add brief "pre-work review" activity (5-10 min recap + Q&A) instead of full instruction
  - Reference pre-work in module prerequisites
- `generate-workshop-prep` includes pre-work distribution in T-2 weeks checklist:
  - T-14 days: Finalize pre-work materials
  - T-7 days: Send welcome email with pre-work
  - T-2 days: Send reminder email
  - T-1 day: Check completion rates (if LMS tracking available)
- `curriculum-architect` agent adds pre-work generation as Phase 7.5 (after lesson plans, before description)

## Error Handling

- **Missing learning objectives:** "Error: learning-objectives.md not found. Cannot identify prerequisites. Run `/generate-objectives` first."
- **No Remember/Understand objectives found:** "Advisory: No Remember/Understand-level objectives found. Pre-work will focus on implied prerequisites for Apply+ objectives."
- **Pre-work already exists:** Prompt with overwrite/update/cancel options

## Implementation Notes

- When `learner-profile.md` is absent, default to moderate prior knowledge and no tech constraints
- Pre-work units should use plain language appropriate for the identified audience
- Email templates should include placeholder tokens (e.g., `[workshop date]`, `[Course Title]`) for easy customization
- The fast track path is critical for participant engagement — experienced learners who are forced through basic content will disengage from all pre-work
