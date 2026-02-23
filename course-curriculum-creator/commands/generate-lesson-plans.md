---
name: generate-lesson-plans
description: Generate detailed module-level lesson plans with activities and timing
argument-hint: "[--module N]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Skill
---

# Generate Lesson Plans Command

Create detailed lesson plans for each module with activities, timing, materials, and instructor notes.

## Prerequisites

- Must have `02-design/course-outline.md`
- Must have `01-planning/learning-objectives.md`
- Should have `03-assessment/rubrics.md`

## Staleness Check

Before generating, check if source files have changed since this file was last generated:

1. If the output file `02-design/lesson-plans.md` already exists, read its YAML frontmatter `sourceHashes`
2. Compute current hash of each source file:
   - `md5sum 02-design/course-outline.md | cut -c1-8`
   - `md5sum 01-planning/learning-objectives.md | cut -c1-8`
3. Compare hashes:
   - If hashes match: sources are unchanged, proceed normally
   - If hashes differ: warn the user: "⚠ Source file [name] has changed since this file was last generated. Regenerating will incorporate these changes."
   - If output file doesn't exist: skip check, proceed with generation

When generating, always compute and write current source hashes to the output file's frontmatter.

## Command Behavior

1. Load `backward-design-methodology` skill for Stage 3 guidance
2. Load universal-design-for-learning skill for accessibility and inclusive design
3. Read course outline for module structure
4. Read objectives and rubrics for alignment
5. Generate detailed plans for each module
6. Write to `02-design/lesson-plans.md`

## Lesson Plan Detail Level

**Module-level detail** (not minute-by-minute):
- Major activity blocks (15-30 min segments)
- Key teaching points
- Practice exercises with context
- Assessment checkpoints
- Instructor facilitation notes

## Module Lesson Plan Template

For each module:

```markdown
## Module X: [Title]

**Duration:** [Minutes]
**Learning Objective(s):** [From learning-objectives.md]
**Cognitive Level:** [Bloom's level]
**Assessment:** [From rubrics.md]

### Overview

[Brief description of what this module accomplishes and how it connects to prior/subsequent modules]

### Materials Needed

**Instructor:**
- [Presentation slides/materials]
- [Examples, case studies]
- [Assessment rubrics]

**Students:**
- [Handouts, worksheets]
- [Tools, templates]
- [Reference materials]

### Module Flow

#### Introduction (5-10 min)

**Purpose:** Orient students, activate prior knowledge, preview learning

**Activities:**
- Review previous module connections
- Present learning objective
- Provide overview and relevance

**Instructor Notes:**
- [Key points to emphasize]
- [Common questions to anticipate]

---

#### Instruction (20-30 min)

**Purpose:** Introduce concepts, frameworks, or procedures

**Content:**
- [Key concept 1 with explanation]
- [Key concept 2 with explanation]
- [Worked example demonstration]

**Teaching Strategies:**
- Use [specific examples relevant to audience]
- Check understanding with [formative assessment method]
- Provide [visual aids, diagrams]

**Instructor Notes:**
- [Common misconceptions to address]
- [Pacing guidance]

---

#### Guided Practice (25-35 min)

**Purpose:** Students practice with support

**Activity:** [Name and description]

**Setup:**
- [How to structure activity]
- [Groups, materials, timeframe]

**Instructions to Students:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Instructor Role:**
- Circulate and observe
- Provide corrective feedback
- Note common struggles for debrief

**Success Indicators:**
- Students can [observable behavior]
- [Specific outputs or demonstrations]

**Instructor Notes:**
- [Common errors to watch for]
- [Intervention strategies]

---

#### Independent Practice (30-50 min)

**Purpose:** Students apply independently or in groups

**Activity:** [Name and description aligned to assessment]

**Setup:**
- [Individual or group work]
- [Resources provided]
- [Time allocation]

**Task:**
[Clear task description that mirrors assessment rubric criteria]

**Assessment:**
- Use Rubric X (from rubrics.md)
- [Formative or summative]
- [Self/peer/instructor assessment]

**Differentiation:**
- **Struggling students:** [Support strategy]
- **Advanced students:** [Extension challenge]

**Instructor Notes:**
- [What to monitor]
- [When to intervene vs. let struggle productively]

---

#### Debrief & Assessment (10-15 min)

**Purpose:** Consolidate learning, provide feedback, transition to next module

**Activities:**
- Share-out or gallery walk
- Address common issues observed
- Connect to next module
- Exit ticket: [Prompt]

**Key Takeaways:**
- [Point 1]
- [Point 2]
- [Point 3]

**Instructor Notes:**
- [How to handle if running behind]
- [Preview for next module]

---

### Timing Summary

| Activity Block | Duration | Cumulative |
|----------------|----------|------------|
| Introduction | 10 min | 10 min |
| Instruction | 25 min | 35 min |
| Guided Practice | 30 min | 65 min |
| Independent Practice | 40 min | 105 min |
| Debrief | 15 min | 120 min |

**Total:** 120 minutes

### Alignment Check

- ✓ Activities prepare students for assessment (Rubric X)
- ✓ Cognitive level matches objective ([Level])
- ✓ Scaffolding from guided to independent practice
- ✓ Formative assessment embedded (guided practice, exit ticket)

**Accessibility & UDL Notes:**
- Representation modes used: [list — e.g., verbal instruction, visual slides, written handout]
- Engagement options: [any learner choice in this module]
- Expression alternatives: [how learners can demonstrate learning — e.g., written, verbal, diagram]
- Accommodation reminders: [any specific notes — e.g., "Provide written instructions for Exercise 2.1 in addition to verbal walkthrough"]

```

## File Output

```markdown
---
title: Lesson Plans - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
courseVersion: [match]
lastUpdated: YYYY-MM-DD
sourceFiles:
  course-outline: "02-design/course-outline.md"
  learning-objectives: "01-planning/learning-objectives.md"
sourceHashes:
  course-outline: "[md5-first-8]"
  learning-objectives: "[md5-first-8]"
---

# Detailed Lesson Plans

## [Course Title]

**Purpose:** These lesson plans provide module-level guidance for delivering the workshop. Each plan includes learning objectives, activities, timing, materials, and instructor notes.

**How to Use:**
- Review plans before workshop
- Adjust examples to audience
- Use timing as guide, not rigid constraint
- Refer to rubrics during student practice

---

[Module 1 lesson plan]

---

[Module 2 lesson plan]

---

[Continue for all modules]

---

## Instructor Preparation Checklist

### Before Workshop

- [ ] Review all lesson plans
- [ ] Customize examples for audience
- [ ] Prepare all materials (slides, handouts, templates)
- [ ] Test any technology or tools
- [ ] Print rubrics for reference

### Day Before

- [ ] Final review of timing
- [ ] Prepare opening remarks
- [ ] Organize materials by module
- [ ] Set up room/space

### During Workshop

- [ ] Start each module with objective preview
- [ ] Monitor timing (use phone timer for major blocks)
- [ ] Circulate during practice activities
- [ ] Take notes on what works/struggles
- [ ] Adjust pacing based on student progress

### After Workshop

- [ ] Debrief: what worked, what didn't
- [ ] Note improvements for next delivery
- [ ] Update lesson plans with refinements

---

## Next Steps

1. Review lesson plans for clarity and completeness
2. Generate supporting materials: `/generate-artifacts --type handout` and `/generate-artifacts --type instructor-guide`
3. Validate full curriculum alignment: use quality-reviewer agent
```

## Post-Generation

Validate alignment:
```
For each module:
- Objective → Activity → Assessment chain is clear
- Cognitive level appropriate for stage in workshop
- Timing realistic (compare to past workshops if available)
- Materials are specified
- Instructor notes address common issues
```

Prompt: "Review lesson plans. Would you like me to adjust any module's activities, timing, or instructional strategies?"

Next: "Generate student and instructor materials using `/generate-artifacts`"

## Timing Reconciliation

After generating lesson plans, perform timing reconciliation across all curriculum documents:

1. **Collect time data from three sources:**
   - **Objectives**: Read time allocations from each objective in `01-planning/learning-objectives.md`
   - **Outline**: Read module durations from `02-design/course-outline.md`
   - **Lesson Plans**: Sum activity block durations from each module in the generated lesson plans

2. **Compare and validate:**
   - Sum objective time allocations → should equal total instruction time
   - Sum outline module durations → should equal total instruction time
   - Sum lesson plan phase totals → should equal module durations from outline

3. **Flag discrepancies:**
   - If any source differs by more than 10% from another, warn the user:
     "⚠ Timing discrepancy detected: [source A] allocates [X] minutes but [source B] allocates [Y] minutes ([Z]% difference). Review and reconcile before delivery."
   - List specific modules/objectives where discrepancies occur

4. **Reconciliation guidance:**
   - Objective times are the source of truth for what's pedagogically needed
   - Outline times are the source of truth for scheduling
   - Lesson plan times must fit within outline times
   - If lesson plan activities exceed outline module time, suggest compressing or splitting

## Module Validation

After generating lesson plans, validate module count and titles against the course outline:

1. **Count modules**: Count the number of modules in `02-design/course-outline.md` and compare to the number of module sections generated in lesson plans. They must match exactly.

2. **Validate titles**: Each module title in lesson plans must match the corresponding module title in course-outline.md exactly (or with only minor clarifying additions).

3. **Check objective mapping**: Every learning objective should appear in at least one module's lesson plan. List any unmapped objectives as warnings.

If mismatches are found:
- "⚠ Module count mismatch: outline has [X] modules but lesson plans have [Y] modules."
- "⚠ Module title mismatch: outline Module [N] is '[title A]' but lesson plan Module [N] is '[title B]'."

---

Create detailed, practical lesson plans that instructors can follow while maintaining flexibility for audience needs and pacing adjustments.
