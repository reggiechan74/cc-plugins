---
name: generate-description
description: Generate student-facing course description for marketing and enrollment
argument-hint: "[--tone professional|conversational|technical]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# Generate Description Command

Create compelling student-facing course description for marketing, course catalogs, and enrollment materials.

## Prerequisites

- Must have `01-planning/course-positioning.md`
- Must have `01-planning/learning-objectives.md`

## Staleness Check

Before generating, check if source files have changed since this file was last generated:

1. If the output file `01-planning/course-description.md` already exists, read its YAML frontmatter `sourceHashes`
2. Compute current hash of each source file:
   - `md5sum 01-planning/course-positioning.md | cut -c1-8`
   - `md5sum 01-planning/learning-objectives.md | cut -c1-8`
3. Compare hashes:
   - If hashes match: sources are unchanged, proceed normally
   - If hashes differ: warn the user: "⚠ Source file [name] has changed since this file was last generated. Regenerating will incorporate these changes."
   - If output file doesn't exist: skip check, proceed with generation

When generating, always compute and write current source hashes to the output file's frontmatter.

## Error Handling

**Missing learning-objectives.md:**
- "Error: learning-objectives.md not found. The course description's 'What You'll Learn' section must be derived from actual learning objectives. Run `/generate-objectives` first."

**Missing course-positioning.md:**
- "Error: course-positioning.md not found. Cannot generate description without course context. Run `/create-course` first."

## Command Behavior

1. Read course positioning and objectives
2. Determine tone (default: professional)
3. Generate student-facing description
4. Write to `01-planning/course-description.md`

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `instructor_name`: Populate the "About the Instructor" section
- `instructor_bio`: Populate the "About the Instructor" section with credentials and experience
- `organization`: Include in course details and registration information

If settings file doesn't exist, use sensible defaults or prompt user.

## Description Components

**Essential elements:**
- Compelling overview (what students will learn)
- Target audience (who should attend)
- Learning outcomes (what students will achieve)
- Workshop format and structure
- Prerequisites (if any)
- What's included (materials, certificate, etc.)
- Instructor information (from settings)

> **Note:** The "What You'll Learn" section must be derived directly from learning-objectives.md. Do not invent or improvise learning outcomes.

## Tone Options

**Professional** (default):
- Formal, credible language
- Focus on competencies and outcomes
- Suitable for corporate/academic catalogs

**Conversational**:
- Approachable, engaging language
- Focus on benefits and transformation
- Suitable for public workshops

**Technical**:
- Precise, detailed language
- Focus on specific skills and tools
- Suitable for technical/specialized audiences

## File Output

```markdown
---
title: Course Description - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
courseVersion: [match]
tone: [professional|conversational|technical]
lastUpdated: YYYY-MM-DD
sourceFiles:
  course-positioning: "01-planning/course-positioning.md"
  learning-objectives: "01-planning/learning-objectives.md"
sourceHashes:
  course-positioning: "[md5-first-8]"
  learning-objectives: "[md5-first-8]"
---

# [Course Title]

## Course Overview

[2-3 paragraph compelling description of the workshop]

[First paragraph: Hook - the problem or opportunity]
[Second paragraph: Solution - what this workshop provides]
[Third paragraph: Outcome - transformation students will experience]

## Who Should Attend

This workshop is designed for:

- [Audience type 1 with brief context]
- [Audience type 2 with brief context]
- [Audience type 3 with brief context]

**Prerequisites:**
[Prerequisites from course-positioning, or "No prerequisites required"]

**Experience Level:**
[Beginner/Intermediate/Advanced - from positioning]

## What You'll Learn

By the end of this workshop, you will be able to:

- [Objective 1 - reworded for student benefit]
- [Objective 2 - reworded for student benefit]
- [Objective 3 - reworded for student benefit]
[Continue for all objectives]

## Workshop Format

**Duration:** [1-day (6 hours) or 2-day (12 hours)]

**Delivery:** In-person intensive workshop with hands-on practice

**Learning Approach:**
[Brief description of instructional approach - lab-heavy, lecture-heavy, or balanced]

### Day 1 [if 2-day]

[High-level topics covered]

### Day 2 [if 2-day]

[High-level topics covered]

## What's Included

- Comprehensive workshop materials and handouts
- Hands-on exercises and case studies
- Reference guides and templates
- Access to instructor for questions during workshop
- [Certificate of completion - if applicable]
- [Any other inclusions]

## About the Instructor

[Instructor name and bio from settings]

[Brief credentials and relevant experience - 2-3 sentences]

## Course Details

- **Duration:** [1-day or 2-day]
- **Format:** In-person
- **Class Size:** [If specified]
- **Language:** [If specified]
- **Level:** [Beginner/Intermediate/Advanced]

## Registration Information

[To be added: pricing, dates, location, registration link]

---

## Internal Notes (Not for public)

**Marketing Angle:** [Key selling points]

**Competitive Differentiation:** [What makes this unique]

**Target Enrollment:** [If specified]
```

## Variants

Generate multiple versions if useful:

**Short Version (100-150 words):**
For catalogs, listings, brief promotions

**Long Version (400-600 words):**
For detailed course pages, full descriptions

**Social Media Version (50-75 words):**
For promotional posts with link to full description

## Post-Generation

Prompt: "Review the course description. Would you like me to adjust the tone, emphasize different aspects, or create additional versions (short/social)?"

---

Generate compelling course descriptions that attract the right students and clearly communicate value, outcomes, and workshop structure.
