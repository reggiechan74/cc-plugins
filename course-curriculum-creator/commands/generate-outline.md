---
name: generate-outline
description: Generate course outline with module structure and timing
argument-hint: ""
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

---

Create structured outlines that scaffold learning, allocate time realistically, and prepare for detailed lesson planning.
