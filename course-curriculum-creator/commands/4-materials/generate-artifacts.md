---
name: generate-artifacts
description: Generate additional course materials (handouts, guides, slides, assessments)
argument-hint: "--type [handout|instructor-guide|slides|pre-assessment|post-assessment|evaluation|pre-work|post-work|all]"
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

### --type pre-work
**Pre-Course Preparation Materials**
- Reading assignments or video links for foundational concepts
- Self-assessment (current knowledge baseline)
- Preparation exercises for Day 1 readiness
- Environment/tool setup instructions (if applicable)
- Pre-reading for technical vocabulary

Derived from Remember/Understand-level objectives in `01-planning/learning-objectives.md`.
Linked to specific Day 1 morning modules from `02-design/course-outline.md`.
Output: `04-materials/pre-work.md`

### --type post-work
**Post-Course Reinforcement Materials**
- Application exercises tied to Apply+ level objectives
- Reflection prompts for each major learning outcome
- Resource compilation (further reading, tools, communities)
- Learning journal template for ongoing practice
- 30-day challenge or practice schedule

Derived from Apply/Analyze/Evaluate/Create objectives in `01-planning/learning-objectives.md`.
Linked to capstone or final module activities from `02-design/course-outline.md`.
Output: `04-materials/post-work.md`

### --type all
Generate all artifact types above (handout, instructor-guide, slides, pre-assessment, post-assessment, evaluation, pre-work, post-work)

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

## Pre-Work Structure

```markdown
---
title: Pre-Course Preparation - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
courseVersion: [match]
lastUpdated: YYYY-MM-DD
dueDate: [2 business days before workshop]
estimatedTime: [30-60 minutes]
---

# Pre-Course Preparation

## [Course Title]

**Workshop Date:** [Date]
**Please complete by:** [Due date — 2 business days before]
**Estimated time:** [30-60 minutes]

---

## Welcome

[Brief welcome explaining why pre-work matters and how it will make the workshop more effective]

---

## 1. Self-Assessment: Where Are You Now?

Rate your current confidence with these topics (1 = No experience, 5 = Very confident):

| Topic | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| [Topic from Understand-level objective 1] | | | | | |
| [Topic from Understand-level objective 2] | | | | | |
| [Topic from course positioning] | | | | | |

---

## 2. Foundational Reading

### Required Reading (15-20 minutes)

[Brief summaries or links to foundational content that maps to Remember/Understand objectives. Keep concise — focus on vocabulary and key concepts that will be built upon in the workshop.]

**Reading 1:** [Title]
[2-3 paragraph summary or link]
**Key takeaway:** [One sentence]

**Reading 2:** [Title]
[2-3 paragraph summary or link]
**Key takeaway:** [One sentence]

---

## 3. Preparation Exercise (10-15 minutes)

[A simple exercise that activates prior knowledge and prepares learners for Day 1 activities]

**Exercise:** [Description]

**Your response:**
[Space for learner to write/think]

---

## 4. Environment Setup (if applicable)

[Technical setup instructions — software installation, account creation, file downloads]

- [ ] [Setup step 1]
- [ ] [Setup step 2]
- [ ] [Verification: how to confirm setup is complete]

---

## 5. What to Bring

- [ ] Laptop (if applicable)
- [ ] This completed pre-work document
- [ ] [Domain-specific items]
- [ ] Questions or scenarios from your own work context

---

## Questions?

Contact [instructor name] at [contact method] if you have questions about the pre-work or need accommodations for the workshop.
```

## Post-Work Structure

```markdown
---
title: Post-Course Reinforcement - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
courseVersion: [match]
lastUpdated: YYYY-MM-DD
---

# Post-Course Reinforcement

## [Course Title]

**Workshop Completed:** [Date]
**Reinforcement Period:** 30 days

---

## Your Learning Journey Continues

The workshop gave you foundational skills. This guide helps you apply and deepen them over the next 30 days. Research shows that applying new skills within 48 hours dramatically improves retention.

---

## Week 1: Immediate Application (Days 1-7)

### Priority Actions

Pick ONE thing from the workshop to apply this week:

**Objective:** [From Apply-level objective]
**Exercise:** [Specific application task related to their work]
**Success indicator:** [Observable outcome]

### Reflection

After applying the skill, note:
- What worked well?
- What was harder than expected?
- What would you do differently?

---

## Week 2: Deepening Practice (Days 8-14)

**Objective:** [From Analyze-level objective, if exists]
**Exercise:** [More complex application building on Week 1]
**Success indicator:** [Observable outcome]

---

## Week 3: Integration (Days 15-21)

**Objective:** [From Evaluate/Create-level objective, if exists]
**Exercise:** [Integration task combining multiple workshop skills]
**Success indicator:** [Observable outcome]

---

## Week 4: Reflection & Planning (Days 22-30)

### Self-Assessment: Where Are You Now?

Re-rate your confidence (compare to pre-work self-assessment):

| Topic | Before | After | Growth |
|---|---|---|---|
| [Topic 1] | [pre-rating] | | |
| [Topic 2] | [pre-rating] | | |

### Continued Learning Resources

**Books/Articles:**
- [Resource 1 — brief description and why it's relevant]
- [Resource 2]

**Online Resources:**
- [Resource 1 — communities, tools, courses]
- [Resource 2]

**Practice Opportunities:**
- [Suggestion 1 for ongoing skill development]
- [Suggestion 2]

### Learning Journal Template

Use this for ongoing reflection:

**Date:** ___
**Skill practiced:** ___
**Context:** ___
**What happened:** ___
**What I learned:** ___
**Next step:** ___
```

## Post-Generation

For each artifact:
- Validate it aligns with curriculum
- Check completeness
- Ensure formatting is ready for use

Prompt: "Artifacts generated in 04-materials/. Review for completeness and alignment with curriculum."

---

Generate practical, ready-to-use materials that support effective workshop delivery and student learning.
