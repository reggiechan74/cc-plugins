---
name: generate-artifacts
description: Generate additional course materials (handouts, guides, slides, assessments)
argument-hint: "--type [handout|instructor-guide|slides|pre-assessment|post-assessment|evaluation|all]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# Generate Artifacts Command

Create supporting course materials beyond core curriculum documents.

## Prerequisites

- Depends on artifact type
- Most artifacts need lesson-plans.md and objectives.md

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `instructor_name`: Use as facilitator name in instructor guide header and preparation checklists

If settings file doesn't exist, use sensible defaults or prompt user.

## Artifact Types

### --type handout
**Student Workbook/Handout**
- Exercise worksheets
- Reference guides
- Templates and frameworks
- Note-taking spaces
Output: `04-materials/student-handout.md`

### --type instructor-guide
**Facilitator Guide**
- Facilitation tips
- Answer keys
- Time management guidance
- Troubleshooting common issues
Output: `04-materials/instructor-guide.md`

### --type slides
**Slide Deck Outline**
- Markdown outline for slides
- Key visuals and talking points
- Ready for conversion to PowerPoint/Google Slides
Output: `04-materials/slide-deck-outline.md`

### --type pre-assessment
**Pre-Workshop Assessment**
- Baseline knowledge check
- Confidence ratings
- Learning goals survey
Output: `04-materials/pre-assessment.md`

### --type post-assessment
**Post-Workshop Assessment**
- Learning gains measurement
- Confidence ratings (compare to pre)
- Workshop evaluation
- Application planning
Output: `04-materials/post-assessment.md`

### --type evaluation
**Course Evaluation Form**
- Module ratings
- Instructor feedback
- Content relevance
- Improvement suggestions
Output: `04-materials/course-evaluation.md`

### --type all
Generate all artifact types above

## Student Handout Structure

```markdown
---
title: Student Workbook - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
courseVersion: [match]
lastUpdated: YYYY-MM-DD
---

# [Course Title]
## Student Workbook

**Instructor:** [Name]
**Duration:** [1-day or 2-day]

---

## Welcome

[Brief welcome and how to use this workbook]

---

## Learning Objectives

By the end of this workshop, you will:

- [Objective 1]
- [Objective 2]
[...]

---

## Module 1: [Title]

### Key Concepts

[Reference material for this module]

### Exercise 1.1: [Title]

**Objective:** [What you'll practice]

**Instructions:**
[Step-by-step guidance]

**Workspace:**

[Structured space for student work - tables, diagrams, text boxes]

**Reflection:**
[Prompts for thinking about application]

---

[Repeat for each module and exercise]

---

## Resources

### Frameworks Reference

[Quick reference for frameworks taught]

### Action Verb Guide

[Bloom's taxonomy verbs for self-assessment]

### Additional Reading

[Optional resources for continued learning]

---

## Post-Workshop Action Plan

**What I will apply first:**

**By when:**

**Success indicators:**

**Obstacles and solutions:**
```

## Instructor Guide Structure

```markdown
---
title: Instructor Guide - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
courseVersion: [match]
lastUpdated: YYYY-MM-DD
---

# Instructor Facilitation Guide
## [Course Title]

---

## Pre-Workshop Preparation

### 2 Weeks Before

- [ ] Finalize enrollment
- [ ] Send pre-assessment to participants
- [ ] Confirm venue and logistics

### 1 Week Before

- [ ] Review and customize examples
- [ ] Print materials
- [ ] Test technology

### Day Before

- [ ] Final logistics check
- [ ] Review lesson plans
- [ ] Prepare opening remarks

---

## Workshop Delivery Guidance

### Module-by-Module Tips

#### Module 1: [Title]

**Common Student Struggles:**
- [Issue 1 and how to address]
- [Issue 2 and how to address]

**Answer Key for Exercise 1.1:**
[Model answers or rubric application]

**Timing Tips:**
- If running behind: [What to compress]
- If ahead: [Extension activities]

**Differentiation:**
- For struggling students: [Support strategies]
- For advanced students: [Challenge extensions]

---

[Repeat for each module]

---

## Facilitation Best Practices

### Creating Psychological Safety

- [Tips specific to this audience]

### Managing Different Experience Levels

- [Strategies for mixed-level groups]

### Handling Common Questions

**Q:** [Frequent question]
**A:** [Recommended response]

[Repeat for common questions]

---

## Troubleshooting

### Technical Issues

[Common tech problems and solutions]

### Timing Problems

[How to adjust if behind/ahead]

### Group Dynamics

[How to handle challenging situations]

---

## Post-Workshop

### Follow-Up

- Send post-assessment within 24 hours
- Share additional resources
- Provide contact for questions

### Continuous Improvement

- Review what worked/didn't
- Update lesson plans
- Note for next delivery
```

## Post-Generation

For each artifact:
- Validate it aligns with curriculum
- Check completeness
- Ensure formatting is ready for use

Prompt: "Artifacts generated in 04-materials/. Review for completeness and alignment with curriculum."

---

Generate practical, ready-to-use materials that support effective workshop delivery and student learning.
