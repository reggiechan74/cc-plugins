---
name: export-curriculum
description: Export curriculum as a single combined document in various formats
argument-hint: "--format [full|summary|syllabus]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
---

# Export Curriculum Command

Combine curriculum files into a single document suitable for sharing, printing, or conversion.

## Prerequisites

- Must be in a course project directory with completed curriculum files
- Recommended: Run `/review-curriculum` first to validate quality

## Command Behavior

When user invokes `/export-curriculum --format [format]`:

1. **Discover curriculum files:**
   - Glob for all `.md` files in the course directory
   - Verify core files exist (positioning, objectives, outline, lesson plans, rubrics)
   - Note any missing files

2. **Combine based on format** (see format options below)

3. **Write output file:**
   - Full: `[course-dir]/export/[CourseName]-full-curriculum.md`
   - Summary: `[course-dir]/export/[CourseName]-summary.md`
   - Syllabus: `[course-dir]/export/[CourseName]-syllabus.md`

4. **Suggest PDF conversion:**
   "Export saved to [path]. To convert to PDF, you can use pandoc:
   `pandoc [output-file] -o [output-file].pdf --pdf-engine=xelatex`"

## Export Formats

### --format full (Complete Curriculum Document)

Intended audience: Instructional designers, curriculum reviewers, stakeholders

**Structure:**
```markdown
# [Course Title] - Complete Curriculum

**Version:** [version] | **Date:** [date] | **Status:** [status]
**Instructor:** [name] | **Organization:** [org]

---

## Table of Contents

1. Course Overview
2. Learning Objectives
3. Assessment Strategy
4. Course Outline
5. Detailed Lesson Plans
6. Assessment Rubrics
7. Supporting Materials

---

<!-- page break -->

## 1. Course Overview

[Content from course-positioning.md - target audience, value proposition, scope]

---

<!-- page break -->

## 2. Learning Objectives

[Content from learning-objectives.md - full objectives with cognitive levels]

---

<!-- page break -->

## 3. Assessment Strategy

[Content from rubrics.md - assessment philosophy, rubric summaries]

---

<!-- page break -->

## 4. Course Outline

[Content from course-outline.md - module structure, schedule]

---

<!-- page break -->

## 5. Detailed Lesson Plans

[Content from lesson-plans.md - all module lesson plans]

---

<!-- page break -->

## 6. Assessment Rubrics

[Full rubric tables from rubrics.md]

---

<!-- page break -->

## 7. Supporting Materials

[List of available materials from 04-materials/]
```

### --format summary (Stakeholder Overview)

Intended audience: Managers, sponsors, decision-makers who need high-level understanding

**Structure:**
```markdown
# [Course Title] - Curriculum Summary

**Duration:** [duration] | **Audience:** [audience] | **Level:** [level]

## Course Purpose

[2-3 paragraphs from course-positioning.md - value proposition and problem solved]

## Learning Outcomes

By the end of this workshop, participants will be able to:
[Numbered list of objectives - statement only, no metadata]

## Workshop Structure

[Module list with titles and durations only - from course-outline.md]

### Day 1
| Time | Session | Duration |
|------|---------|----------|
[Schedule table]

### Day 2 (if applicable)
[Schedule table]

## Assessment Approach

[Brief summary of assessment strategy - 1-2 paragraphs, not full rubrics]

## Instructor

[Instructor name and brief bio]

## Next Steps

[Registration, logistics information placeholder]
```

### --format syllabus (Student-Facing)

Intended audience: Students/participants who will attend the workshop

**Structure:**
```markdown
# [Course Title]

## Welcome

[Content from course-description.md - overview section]

## What You'll Learn

[Objectives reworded as student benefits - from course-description.md]

## Workshop Schedule

[Simplified schedule from course-outline.md - module titles and times only]

### Day 1
[Time blocks with module names]

### Day 2 (if applicable)
[Time blocks with module names]

## What to Bring / Prerequisites

[Prerequisites from course-positioning.md]

## How You'll Be Assessed

[Brief, student-friendly description of assessment approach]

## What's Included

[From course-description.md - materials, certificate, etc.]

## About Your Instructor

[Instructor info]

## Questions?

[Contact information placeholder]
```

## Error Handling

**Missing curriculum files:**
- If core files are missing, warn: "⚠ Missing [file]. Export will be incomplete. Run [command] to generate."
- Proceed with available files, noting gaps

**Export directory doesn't exist:**
- Create `export/` subdirectory in the course directory

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `instructor_name`: For instructor sections
- `instructor_bio`: For instructor sections
- `organization`: For header information

If settings file doesn't exist, use values from course-positioning.md frontmatter.

---

Export curriculum documents for sharing with stakeholders, students, and reviewers in appropriate formats.
