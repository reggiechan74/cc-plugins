---
name: generate-outline
description: Generate course outline with module structure and timing
argument-hint: "[--modules N]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# Generate Outline Command

Create high-level course structure with modules, timing, and topics following backward design Stage 3.

## Prerequisites

- Must have `01-planning/learning-objectives.md`
- Should have `03-assessment/rubrics.md` (recommended)

## Staleness Check

Before generating, check if source files have changed since this file was last generated:

1. If the output file `02-design/course-outline.md` already exists, read its YAML frontmatter `sourceHashes`
2. Compute current hash of each source file: `md5sum 01-planning/learning-objectives.md | cut -c1-8`
3. Compare hashes:
   - If hashes match: sources are unchanged, proceed normally
   - If hashes differ: warn the user: "⚠ Source file learning-objectives.md has changed since this file was last generated. Regenerating will incorporate these changes."
   - If output file doesn't exist: skip check, proceed with generation

When generating, always compute and write current source hashes to the output file's frontmatter.

## Command Behavior

1. Read learning objectives and time allocations
2. Group objectives into logical modules
3. Allocate timing for instruction, practice, breaks
4. Generate structured outline
5. Write to `02-design/course-outline.md`

## Module Structure Logic

**1-day workshop:** 4-6 modules
**2-day workshop:** 8-10 modules

**Module duration:** 60-120 minutes each

**Module components:**
- Learning objective(s) addressed
- Key topics/concepts
- Activities (high-level)
- Timing breakdown

## Timing Allocation

**Total available:**
- 1-day: 6 hours (360 minutes) instruction
- 2-day: 12 hours (720 minutes) instruction

**Account for:**
- Breaks: 15 min every 90-120 min
- Lunch: 60 min (if full day)
- Transitions: 5 min between modules
- Buffer: 10-15% for overruns

**Module timing split:**
- Instruction: 20-30%
- Guided practice: 25-35%
- Independent practice: 30-40%
- Assessment/debrief: 10-15%

## File Output

```markdown
---
title: Course Outline - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
courseVersion: [match]
lastUpdated: YYYY-MM-DD
sourceFiles:
  learning-objectives: "01-planning/learning-objectives.md"
sourceHashes:
  learning-objectives: "[md5-first-8]"
---

# Course Outline

## [Course Title]

**Duration:** [1-day or 2-day]
**Total Instruction Time:** [Hours]

---

## Day 1 [if 2-day]

### Module 1: [Title] (Time: 9:00-10:30, Duration: 90 min)

**Learning Objective(s):**
- [Objective from learning-objectives.md]

**Key Topics:**
- [Topic 1]
- [Topic 2]

**Activities:**
- Introduction and objective preview (5 min)
- Concept instruction with examples (20 min)
- Guided practice exercise (30 min)
- Independent application task (25 min)
- Debrief and Q&A (10 min)

**Assessment:** [Formative method]

**Materials Needed:**
- [List materials]

---

### Break (10:30-10:45, 15 min)

---

### Module 2: [Title] (Time: 10:45-12:15, Duration: 90 min)

[Repeat format]

---

[Continue for all modules with breaks, lunch]

---

## Schedule Summary

### Day 1

| Time | Module | Duration | Type |
|------|--------|----------|------|
| 9:00-10:30 | Module 1: [Title] | 90 min | Instruction/Practice |
| 10:30-10:45 | Break | 15 min | - |
| 10:45-12:15 | Module 2: [Title] | 90 min | Instruction/Practice |
| 12:15-1:15 | Lunch | 60 min | - |
| 1:15-2:45 | Module 3: [Title] | 90 min | Practice-heavy |
| 2:45-3:00 | Break | 15 min | - |
| 3:00-4:30 | Module 4: [Title] | 90 min | Assessment/Synthesis |

**Total Day 1 Instruction:** 360 minutes (6 hours)

[Repeat for Day 2 if applicable]

---

## Next Steps

1. Review outline for logical flow and realistic timing
2. Generate detailed lesson plans for each module: `/generate-lesson-plans`
3. Ensure all learning objectives are addressed across modules
```

## Post-Generation

Prompt: "Review the outline. Would you like me to adjust module timing, regroup objectives, or modify the sequence?"

Next: "Generate detailed lesson plans using `/generate-lesson-plans`"

## Incremental Update Mode

When invoked with `--update`, modify existing outline instead of regenerating:

### Adding a Module

```
/generate-outline --update "Add a module on Advanced Analytics after Module 3"
```

**Behavior:**
1. Read existing `02-design/course-outline.md`
2. Insert new module at specified position
3. Renumber subsequent modules
4. Recalculate timing (adjust break/lunch schedule if needed)
5. Assign relevant learning objectives to the new module
6. Warn about downstream staleness: "⚠ Lesson plans need regeneration to include the new module. Run `/generate-lesson-plans` to update."

### Removing a Module

```
/generate-outline --update --remove 4
```

**Behavior:**
1. Remove module 4
2. Renumber subsequent modules
3. Recalculate timing
4. Warn if removed module was the only one covering certain objectives
5. Warn about downstream staleness

### Reordering Modules

```
/generate-outline --update --move 5 --to 2
```

**Behavior:**
1. Move module 5 to position 2
2. Renumber all modules
3. Recalculate timing
4. Validate Bloom's level progression still makes sense (warn if not)

### Adjusting Module Timing

```
/generate-outline --update --resize 3 120
```

**Behavior:**
1. Change module 3 duration to 120 minutes
2. Recalculate schedule (break/lunch/transition times)
3. Warn if total time exceeds workshop duration

### Validation After Update

After any incremental change:
- Verify all learning objectives are still covered by at least one module
- Verify total time fits within workshop duration (with buffer)
- Verify Bloom's level progression is maintained
- Update sourceHashes in frontmatter

---

Create structured outlines that scaffold learning, allocate time realistically, and prepare for detailed lesson planning.
