---
name: create-course
description: Initialize a new course curriculum project with directory structure and foundational files
argument-hint: "[Course Title] [--duration 1-day|2-day] [--mode in-person|virtual|hybrid] [--location path] [--series name --level N]"
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Edit
---

# Create Course Command

Initialize a new course curriculum project following the plugin's standardized structure.

## Command Behavior

When user invokes `/create-course [CourseName]`:

1. **Gather required information** (if not provided as arguments):
   - Course title
   - Duration (1-day or 2-day)
   - Target audience
   - Output location
   - Prerequisites (optional)

2. **Create directory structure** following categorized format:
   ```
   CourseName-YYYY-MM-DD/
   ├── 01-planning/
   │   ├── course-positioning.md
   │   ├── course-description.md
   │   ├── learning-objectives.md
   │   └── content-sources.md
   ├── 02-design/
   │   ├── course-outline.md
   │   └── lesson-plans.md
   ├── 03-assessment/
   │   └── rubrics.md
   └── 04-materials/
       └── README.md
   ```

3. **Generate initial files**:
   - `course-positioning.md` with YAML frontmatter and template content
   - `content-sources.md` with tracking template (see File Generation section)
   - `README.md` in project root with course overview
   - `.gitignore` (optional, based on settings)

4. **Report completion** with next steps

## Argument Handling

**Interactive mode (no args or partial args):**
Use AskUserQuestion to gather missing information:
- Course title (if not provided)
- Duration: 1-day or 2-day workshop
- Target audience description
- Delivery mode: in-person (default), virtual, or hybrid
- Output location (default from settings or prompt user)
- Prerequisites (optional)

**Args-based mode (all required args provided):**
```bash
/create-course "PropTech Fundamentals" --duration 2-day --mode virtual --location ~/courses
```

Parse arguments and create immediately without prompts.

**Support both modes** - check what's provided, prompt for what's missing.

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `instructor_name`: Use in course-positioning.md
- `instructor_bio`: Use in course-positioning.md
- `organization`: Use in course-positioning.md
- `courses_directory`: Default output location if not specified
- `default_duration`: Default if not specified
- `default_audience_level`: Suggest in prompts

If settings file doesn't exist, use sensible defaults or prompt user.

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

## Delivery Mode

When `--mode` is provided (or selected interactively):

### In-Person (default)
No changes to existing behavior. Standard workshop design.

### Virtual
Adds the following to `course-positioning.md`:
- `deliveryMode: virtual` in YAML frontmatter
- Platform requirements section (video conferencing, digital whiteboard, chat)
- Virtual logistics section (tech check schedule, backup plans)

Sets mode-specific defaults that propagate to downstream commands:
- **Max session length:** 4 hours per day (not 6)
- **Break frequency:** Every 45 minutes (not 60)
- **Break duration:** 10 minutes (not 5-10)
- **Activity format:** Breakout rooms replace table groups; digital collaboration replaces physical materials
- **Engagement cadence:** Interaction point every 15-20 minutes (polls, chat, reactions)
- **Buffer time:** 15% (not 10%)

### Hybrid
Adds the following to `course-positioning.md`:
- `deliveryMode: hybrid` in YAML frontmatter
- Dual-experience design notes (in-room and remote participants)
- Technology requirements for both audiences
- Equity considerations section

Sets mode-specific defaults:
- Inherits virtual timing constraints (shorter sessions, more breaks)
- Adds camera/audio requirements for in-room
- Activities must work for both audiences simultaneously
- Facilitator attention split guidance

### Frontmatter Addition

When generating `course-positioning.md`, add to YAML frontmatter:
```yaml
deliveryMode: "[in-person|virtual|hybrid]"
```

And add to the "## Workshop Format" section:
```markdown
- **Delivery:** [In-person intensive workshop | Virtual workshop via [Platform] | Hybrid (in-room + remote participants)]
```

## Directory Naming

Format: `CourseName-YYYY-MM-DD`

**Course name processing:**
- Remove special characters
- Replace spaces with hyphens
- Use PascalCase for each word
- Example: "PropTech Fundamentals" → "PropTech-Fundamentals"

**Date:**
- Use current date in EST timezone
- Format: YYYY-MM-DD
- Get using: `TZ='America/New_York' date '+%Y-%m-%d'`

**Full example:** `PropTech-Fundamentals-2026-02-04/`

## File Generation

### 1. course-positioning.md

```markdown
---
title: [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
instructor: [From settings or user input]
organization: [From settings or user input]
duration: [1-day or 2-day]
audience: [Target audience description]
keywords: [generated from course title]
lastUpdated: YYYY-MM-DD
---

# [Course Title] - Course Positioning

## Target Audience

[Audience description from user input]

**Prerequisites:**
[Prerequisites from user input, or "None specified"]

**Experience Level:**
[From settings default_audience_level or user input]

## Value Proposition

### What Students Will Achieve

[To be completed - learning outcomes will inform this]

### Problem Being Solved

[To be completed - describe the challenge or gap this course addresses]

### Market Differentiation

[To be completed - what makes this approach unique]

## Course Positioning Statement

**For** [target audience] **who** [have this problem/need], **this workshop** [provides this solution] **that** [delivers these unique benefits].

[To be refined after learning objectives are defined]

## Learning Outcomes Summary

[Will be populated from learning-objectives.md]

## Workshop Format

- **Duration:** [1-day or 2-day]
- **Format:** [From settings default_activity_format or TBD]
- **Delivery:** [In-person intensive workshop | Virtual workshop via [Platform] | Hybrid (in-room + remote participants)]

## Next Steps

1. Define learning objectives using `/generate-objectives`
2. Refine this positioning based on objectives
3. Generate course description for students
```

### 2. README.md (Project Root)

```markdown
# [Course Title]

**Status:** Draft
**Version:** 0.1.0
**Last Updated:** YYYY-MM-DD

## Overview

[Brief course description - to be completed]

## Project Structure

```
01-planning/          Course positioning, description, objectives
02-design/            Course outline and lesson plans
03-assessment/        Rubrics and evaluation criteria
04-materials/         Student handouts and instructor materials
```

## Development Workflow

### Backward Design Approach

1. **Define Learning Outcomes** (`01-planning/learning-objectives.md`)
   - Use `/generate-objectives` command
   - Review blooms-taxonomy skill for guidance

2. **Design Assessments** (`03-assessment/rubrics.md`)
   - Use `/generate-rubrics` command
   - Ensure alignment with objectives

3. **Plan Learning Activities** (`02-design/`)
   - Use `/generate-outline` for structure
   - Use `/generate-lesson-plans` for detailed plans
   - Validate alignment with outcomes and assessments

4. **Create Supporting Materials** (`04-materials/`)
   - Use `/generate-artifacts` command
   - Generate handouts, guides, etc.

### Quality Assurance

- Run `/review-curriculum` to validate alignment
- Check outcomes → assessments → activities coherence

## Course Details

- **Instructor:** [Instructor name]
- **Organization:** [Organization]
- **Duration:** [1-day or 2-day]
- **Target Audience:** [Audience]

## Version History

- v0.1.0 (YYYY-MM-DD): Initial course structure created
```

### 3. .gitignore (if settings specify auto_init_git: true)

```
# Temporary files
*.tmp
*~
.DS_Store

# Editor files
.vscode/
.idea/

# Draft versions
*-draft.md
*-backup.md
```

### 4. 04-materials/README.md

```markdown
# Course Materials

This directory contains supporting materials for the workshop.

## Student Materials

[To be generated]

Use `/generate-artifacts --type handout` to create student workbooks.

## Instructor Materials

[To be generated]

Use `/generate-artifacts --type instructor-guide` to create facilitator guides.

## Additional Artifacts

Use `/generate-artifacts` command to generate:
- Slide deck outlines
- Pre/post assessments
- Evaluation forms
- Supply lists
```

### 5. content-sources.md

```markdown
---
title: Content Sources & Licensing - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: tracking
lastUpdated: YYYY-MM-DD
---

# Content Sources & Licensing Tracker

## [Course Title]

**Purpose:** Track all third-party content, citations, and licensing requirements used in this course. Update this document whenever external content is incorporated into course materials.

**Why This Matters:** Professional course delivery requires clear attribution, license compliance, and awareness of content expiration. This tracker prevents IP violations and ensures materials can be legally distributed.

---

## Source Registry

[Add entries as content is incorporated during lesson plan and artifact development]

### Entry Template

| Field | Value |
|-------|-------|
| **Source Title** | [Title of source material] |
| **Author/Creator** | [Name or organization] |
| **Source Type** | [Book / Article / Video / Image / Framework / Tool / Dataset / Case Study / Software] |
| **URL/Location** | [Link or citation] |
| **License Type** | [CC-BY / CC-BY-SA / CC-BY-NC / MIT / Proprietary / Fair Use / Public Domain / Permission Granted] |
| **Usage in Course** | [Which module(s) and how it's used: quoted, adapted, referenced, screenshot] |
| **Attribution Required** | [Yes — exact text / No] |
| **Permission Status** | [Not needed / Requested / Granted / Denied] |
| **Expiration Date** | [If license or permission has a time limit, otherwise "None"] |
| **Notes** | [Any restrictions, conditions, or context] |

---

## Quick Reference: License Types

| License | Can Use in Course? | Can Distribute Handouts? | Attribution Needed? | Can Modify? |
|---------|-------------------|--------------------------|--------------------|----|
| **Public Domain** | Yes | Yes | No (but good practice) | Yes |
| **CC-BY** | Yes | Yes | Yes | Yes |
| **CC-BY-SA** | Yes | Yes (share-alike) | Yes | Yes (share-alike) |
| **CC-BY-NC** | Yes (if not charging) | Depends on fee structure | Yes | Yes |
| **Fair Use** | Limited (short excerpts) | Limited | Yes | Limited |
| **Proprietary** | Only with permission | Only with permission | Per agreement | No |
| **Permission Granted** | Per agreement | Per agreement | Per agreement | Per agreement |

---

## Frameworks & Models Used

[Track conceptual frameworks referenced in the course — these may have specific citation requirements]

| Framework/Model | Creator | Citation | License/Usage Notes |
|----------------|---------|----------|-------------------|
| [e.g., ADDIE Model] | [Creator] | [Proper citation] | [Public domain / Citation required / etc.] |

---

## Images, Diagrams & Media

[Track visual assets separately — these have stricter licensing requirements]

| Asset | Source | License | Used In | Attribution Text |
|-------|--------|---------|---------|-----------------|
| [Description] | [Source] | [License] | [Module/material] | [Required attribution] |

---

## Pre-Delivery Checklist

- [ ] All sources with "Permission Requested" status have been resolved
- [ ] All required attributions are included in course materials
- [ ] No expired licenses are in use
- [ ] Proprietary content has documented permission
- [ ] Handout distribution rights are confirmed for all included content
- [ ] Framework citations are accurate and complete

---

## Update Log

| Date | Change | Updated By |
|------|--------|-----------|
| [YYYY-MM-DD] | Initial tracker created | [Name] |
```

## Completion Message

After successful creation, output to user:

```
✓ Course project created: [full-path]/CourseName-YYYY-MM-DD/

Structure created:
  ├── 01-planning/
  │   ├── course-positioning.md (✓ initialized)
  │   ├── course-description.md (pending)
  │   ├── learning-objectives.md (pending)
  │   └── content-sources.md (✓ initialized)
  ├── 02-design/
  │   ├── course-outline.md (pending)
  │   └── lesson-plans.md (pending)
  ├── 03-assessment/
  │   └── rubrics.md (pending)
  └── 04-materials/
      └── README.md (✓ created)

Next Steps (Backward Design):
1. Define learning objectives: /generate-objectives
2. Design assessments: /generate-rubrics
3. Plan learning activities: /generate-outline then /generate-lesson-plans

Or use autonomous generation:
  Ask: "Design a complete curriculum for [topic]"
  The curriculum-architect agent will generate all components.
```

## Error Handling

**Directory already exists:**
- Check if `[location]/CourseName-YYYY-MM-DD/` exists
- If exists, prompt: "Course directory already exists. Options: (1) Use different date, (2) Overwrite, (3) Cancel"
- Handle user choice appropriately

**Invalid location:**
- Verify location is writable directory
- If invalid, prompt for new location
- Provide helpful error: "Cannot create course at [location]. Please specify a valid directory path."

**Missing settings:**
- If `.claude/course-curriculum-creator.local.md` doesn't exist, use defaults
- Suggest: "Tip: Create .claude/course-curriculum-creator.local.md to set default preferences (see plugin README)"

## Implementation Notes

**Date retrieval:**
Always use bash to get current date:
```bash
TZ='America/New_York' date '+%Y-%m-%d'
```

**Path handling:**
- Expand ~ to full path
- Validate paths before creating directories
- Use absolute paths in success messages

**YAML frontmatter:**
- All dates in YYYY-MM-DD format
- Version starts at 0.1.0 (semantic versioning)
- Status starts as "draft"

**DO NOT:**
- Create empty files without templates
- Skip YAML frontmatter in any .md files
- Use relative dates ("today", "current")—always get actual date via bash
- Create course without user confirmation of key details

## Example Usage

**Interactive:**
```
User: /create-course PropTech Fundamentals
[Plugin prompts for duration, location, audience]
[Plugin creates structure with provided details]
```

**With arguments:**
```
User: /create-course "AI for Real Estate" --duration 1-day --location ~/workshops
[Plugin creates immediately with provided parameters]
```

**Autonomous integration:**
```
User: I want to create a 2-day course on PropTech
[curriculum-architect agent may invoke this command internally]
```

---

Create course projects that follow backward design principles, use standardized structure, and set up instructors for success with clear next steps and workflow guidance.
