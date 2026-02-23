---
name: generate-objectives
description: Generate Bloom's taxonomy-aligned learning objectives for the course
argument-hint: "[--count N] [--levels cognitive-levels]"
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Edit
  - Skill
---

# Generate Objectives Command

Create measurable, Bloom's-aligned learning objectives for the course based on backward design principles.

## Prerequisites

Must be run within a course project directory (created via `/create-course`).

## Staleness Check

Before generating, check if source files have changed since this file was last generated:

1. If the output file `01-planning/learning-objectives.md` already exists, read its YAML frontmatter `sourceHashes`
2. Compute current hash of each source file: `md5sum 01-planning/course-positioning.md | cut -c1-8`
3. Compare hashes:
   - If hashes match: sources are unchanged, proceed normally
   - If hashes differ: warn the user: "⚠ Source file course-positioning.md has changed since this file was last generated. Regenerating will incorporate these changes."
   - If output file doesn't exist: skip check, proceed with generation

When generating, always compute and write current source hashes to the output file's frontmatter.

## Command Behavior

1. **Load required skills**: Load `blooms-taxonomy` and `backward-design-methodology` skills
2. **Read course positioning**: Parse `01-planning/course-positioning.md` for context
3. **Gather requirements** (if not specified):
   - Number of objectives (default from duration: 5-7 for 1-day, 8-12 for 2-day)
   - Cognitive level distribution preference
   - Target audience considerations
4. **Generate learning objectives**: Create SMART objectives with appropriate action verbs
5. **Write to file**: Save to `01-planning/learning-objectives.md`
6. **Update positioning**: Suggest updating course-positioning.md with outcomes summary

## Skill Loading

Always load these skills before generating:
```
Load blooms-taxonomy skill for action verb selection and cognitive levels
Load backward-design-methodology skill for outcomes-first approach
```

## Input Gathering

**Read from course-positioning.md:**
- Duration (1-day or 2-day)
- Target audience
- Prerequisites
- Course topic/focus

**Prompt user if needed:**
- Desired cognitive level focus (Apply-heavy, balanced, or advanced with Evaluate/Create)
- Specific skills or competencies students must achieve
- Any constraints or requirements

**Use settings defaults:**
- `default_duration` for objective count
- `default_audience_level` for cognitive complexity

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `default_duration`: Determines objective count range (5-7 for 1-day, 8-12 for 2-day)
- `default_audience_level`: Guides cognitive complexity distribution (e.g., beginner skews toward Apply, advanced includes more Evaluate/Create)

If settings file doesn't exist, use sensible defaults or prompt user.

## Objective Generation Logic

### Quantity by Duration

**1-day workshop:**
- Total objectives: 5-7
- Remember: 0-1 (minimize or pre-work)
- Understand: 1-2
- Apply: 3-4 (primary focus)
- Analyze: 0-1 (optional)
- Evaluate/Create: 0

**2-day workshop:**
- Total objectives: 8-12
- Remember: 0-1 (minimize or pre-work)
- Understand: 1-2
- Apply: 4-5
- Analyze: 2-3
- Evaluate: 1-2
- Create: 1 (capstone)

### Objective Quality Standards

Each objective must:
- Use measurable action verb from Bloom's taxonomy
- Specify what students will do (observable behavior)
- Include context or conditions
- Be achievable within workshop timeframe
- Align with course positioning and audience needs

**Format:**
```
[Action Verb] + [What] + [Context/Conditions] + [Criteria (optional)]
```

**Example:**
"Apply Porter's Five Forces framework to analyze PropTech use cases in commercial real estate, identifying all five forces with supporting evidence"

### Scaffolding

Ensure objectives progress logically:
- Start with lower cognitive levels (Understand/Apply)
- Build to higher levels (Analyze/Evaluate/Create)
- Each objective should build on or complement previous ones
- Create clear learning pathway

## File Output Format

### 01-planning/learning-objectives.md

```markdown
---
title: Learning Objectives - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
courseVersion: [match course version]
lastUpdated: YYYY-MM-DD
sourceFiles:
  course-positioning: "01-planning/course-positioning.md"
sourceHashes:
  course-positioning: "[md5-first-8]"
---

# Learning Objectives

## Course: [Course Title]

**Duration:** [1-day or 2-day]
**Target Audience:** [From course-positioning.md]

## Overview

By the end of this workshop, participants will be able to demonstrate the following competencies:

## Learning Objectives

### Objective 1: [Descriptive Title]

**Objective Statement:**
[Full SMART objective with action verb, context, criteria]

**Cognitive Level:** [Bloom's level]
**Time Allocation:** [Estimated minutes]
**Assessment Method:** [How this will be measured]
**Module:** [Which module addresses this - TBD until outline created]

**Rationale:**
[Why this objective is important, how it serves course positioning]

---

### Objective 2: [Descriptive Title]

[Repeat format for each objective]

---

## Objective Summary Table

| # | Objective | Cognitive Level | Time | Assessment |
|---|-----------|-----------------|------|------------|
| 1 | [Brief description] | [Level] | [Min] | [Method] |
| 2 | [Brief description] | [Level] | [Min] | [Method] |
| ... | | | | |

## Cognitive Level Distribution

- **Understand:** [Count] objectives ([Percentage]%)
- **Apply:** [Count] objectives ([Percentage]%)
- **Analyze:** [Count] objectives ([Percentage]%)
- **Evaluate:** [Count] objectives ([Percentage]%)
- **Create:** [Count] objectives ([Percentage]%)

**Total:** [Count] objectives, [Total time] minutes

## Scaffolding Plan

**Learning Progression:**

[Describe how objectives build on each other]

**Day 1 Focus (if 2-day):** [Cognitive levels and themes]
**Day 2 Focus (if 2-day):** [Cognitive levels and themes]

## Alignment with Course Positioning

[Brief explanation of how these objectives fulfill the value proposition and target audience needs from course-positioning.md]

## Next Steps

1. Review and refine objectives
2. Update course-positioning.md with outcomes summary
3. Design assessments aligned to objectives: `/generate-rubrics`
4. Plan learning activities: `/generate-outline` then `/generate-lesson-plans`

## Notes

- All objectives follow SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)
- Action verbs selected from appropriate Bloom's taxonomy levels
- Time allocations include instruction + practice + assessment
- Progression scaffolds from lower to higher cognitive complexity
```

## Post-Generation Actions

After generating learning-objectives.md:

1. **Prompt user to review**: "Review the generated objectives. Would you like me to adjust cognitive levels, add/remove objectives, or modify any objectives?"

2. **Suggest course-positioning update**: "These objectives should inform your course positioning. Would you like me to update 01-planning/course-positioning.md with an outcomes summary?"

3. **Recommend next step**: "Next: Generate assessment rubrics aligned to these objectives using `/generate-rubrics`"

## Validation Checks

Before finalizing, validate:
- [ ] All objectives use Bloom's taxonomy action verbs
- [ ] Cognitive levels appropriate for workshop duration
- [ ] Total time allocation realistic (5-6 hours for 1-day, 11-12 hours for 2-day)
- [ ] Objectives progress logically from simple to complex
- [ ] Each objective is SMART (measurable, achievable, specific)
- [ ] Objectives align with course positioning audience/needs
- [ ] Prerequisites are addressed (or noted as pre-work)

## Error Handling

**Not in course directory:**
- Check for `01-planning/course-positioning.md`
- If missing: "Error: Not in a course project directory. Run `/create-course` first or navigate to course directory."

**Missing course-positioning.md:**
- "Error: course-positioning.md not found. Cannot generate objectives without course context."

**Objectives already exist:**
- Prompt: "learning-objectives.md already exists. Options: (1) Regenerate (overwrites), (2) Edit existing, (3) Cancel"
- Handle user choice

## Example Usage

**Basic (uses defaults):**
```
User: /generate-objectives
[Plugin reads context, generates appropriate objectives]
```

**With arguments:**
```
User: /generate-objectives --count 6 --levels "apply-heavy"
[Plugin generates 6 objectives with emphasis on Apply level]
```

**Autonomous integration:**
```
[curriculum-architect agent may invoke this internally]
```

## Implementation Notes

**Always use bash for dates:**
```bash
TZ='America/New_York' date '+%Y-%m-%d'
```

**Time allocation calculation:**
- Remember: 15-20 min per objective
- Understand: 30-45 min per objective
- Apply: 45-60 min per objective
- Analyze: 60-90 min per objective
- Evaluate: 90-120 min per objective
- Create: 120-180 min per objective

**Assessment method suggestions:**
- Remember/Understand: Quiz, explanation, summary
- Apply: Framework application, problem-solving
- Analyze: Case analysis, pattern identification
- Evaluate: Multi-criteria evaluation, recommendation
- Create: Design, plan, strategy development

## Incremental Update Mode

When invoked with `--update`, modify existing objectives instead of regenerating all:

### Adding Objectives

```
/generate-objectives --update "Add an Evaluate-level objective about assessing PropTech ROI"
```

**Behavior:**
1. Read existing `01-planning/learning-objectives.md`
2. Parse current objectives and cognitive level distribution
3. Generate the new objective following the same quality standards
4. Validate it doesn't duplicate existing objectives
5. Add it in the appropriate position (maintaining Bloom's level progression)
6. Update the Objective Summary Table and Cognitive Level Distribution
7. Warn about downstream staleness: "⚠ Downstream files (rubrics, outline, lesson plans) may need regeneration. Run `/generate-rubrics`, `/generate-outline`, etc. to update."

### Removing Objectives

```
/generate-objectives --update --remove 3
```

**Behavior:**
1. Read existing objectives
2. Remove objective #3
3. Renumber remaining objectives
4. Update Summary Table and Distribution
5. Warn about downstream staleness

### Modifying Objectives

```
/generate-objectives --update --modify 2 "Change to Analyze level with focus on market comparison"
```

**Behavior:**
1. Read existing objectives
2. Modify objective #2 as specified
3. Validate modified objective meets quality standards
4. Update Summary Table and Distribution
5. Warn about downstream staleness

### Validation After Update

After any incremental change:
- Revalidate cognitive level distribution is appropriate for duration
- Revalidate total time allocation is realistic
- Revalidate scaffolding progression
- Update sourceHashes in frontmatter

---

Generate learning objectives that are measurable, achievable, and appropriately scaffolded. Use Bloom's taxonomy action verbs, align with course positioning, and set foundation for assessment and activity design.
