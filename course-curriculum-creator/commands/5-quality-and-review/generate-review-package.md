---
name: generate-review-package
description: Generate a stakeholder-friendly review package for SME validation and organizational approval of curriculum before delivery
argument-hint: "[--audience sme|executive|all] [--include-rubrics]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# Generate Review Package Command

Create a stakeholder-friendly review document for SME (Subject Matter Expert) validation and organizational approval. This is different from `/export-curriculum` — it's structured for review and feedback, not information delivery.

## Why This Matters

In organizational L&D, courses go through: designer → SME review → stakeholder approval → pilot → revision → deployment. Without a structured review process, curriculum gaps survive until delivery. This command creates documents that non-designers can meaningfully review.

## Prerequisites

- Must have `01-planning/course-positioning.md`
- Must have `01-planning/learning-objectives.md`
- Should have `02-design/course-outline.md`
- Should have `03-assessment/rubrics.md`

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `instructor_name`: Use as curriculum designer
- `organization`: Use in document header

If settings file doesn't exist, use sensible defaults or prompt user.

## Command Behavior

1. Read all available curriculum files
2. Determine audience (`--audience` flag or prompt)
3. Generate review package tailored to audience
4. Include specific review questions per section
5. Write to `04-materials/review-package.md`

## Audience Options

### --audience sme (default)
Full technical review with detailed questions about content accuracy, completeness, and real-world relevance. Includes rubric review if available.

### --audience executive
High-level summary focused on business alignment, ROI potential, and resource requirements. Omits pedagogical details.

### --audience all
Generates both SME and executive sections in one document.

## File Output Format

### 04-materials/review-package.md

```
---
title: Curriculum Review Package - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: pending-review
courseVersion: [match]
lastUpdated: YYYY-MM-DD
reviewAudience: [sme|executive|all]
reviewDeadline: [Suggest: 2 weeks from generation date]
---

# Curriculum Review Package

## [Course Title]

**Prepared by:** [Instructor/designer name]
**Review requested by:** [Date + 2 weeks]
**Review type:** [SME Technical Review / Executive Approval / Both]

---

## How to Use This Document

1. Read through the curriculum summary below
2. For each section, respond to the review questions in the **Reviewer Feedback** boxes
3. Flag any concerns as: CRITICAL (blocks delivery), IMPORTANT (should fix), MINOR (nice to have)
4. Return completed review by [deadline]

---

## Part 1: Executive Summary

**Business Need:**
[From course-positioning.md or TNA — why this course exists]

**Target Audience:**
[From course-positioning.md — who it's for, how many, prerequisites]

**Expected Outcomes:**
[From learning-objectives.md — what participants will be able to do]

**Format:**
[Duration, delivery mode, schedule overview]

**Resource Requirements:**
- Instructor time: [Development + delivery hours estimate]
- Participant time: [Workshop hours + pre/post-work]
- Materials: [What needs to be produced/purchased]
- Venue/technology: [Physical space or platform requirements]

> **Reviewer Feedback — Executive:**
> - Does this address a real business need? (Yes/No/Needs revision)
> - Is the target audience correct and sized appropriately?
> - Are resource requirements acceptable?
> - Approval status: APPROVED / APPROVED WITH CHANGES / NOT APPROVED
> - Comments: ___

---

## Part 2: Learning Objectives Review

For each learning objective:

### Objective [N]: [Title]

**Statement:** [Full objective from learning-objectives.md]
**Cognitive Level:** [Bloom's level]
**Time Allocated:** [Minutes]
**Assessment Method:** [From rubrics.md]

> **Reviewer Feedback — SME:**
> - Is this objective relevant to the target audience's actual work? (Yes/No)
> - Is the cognitive level appropriate? (Too basic / Just right / Too advanced)
> - Is the time allocation realistic for this content? (Yes/No)
> - Suggested changes: ___

[Repeat for each objective]

---

## Part 3: Course Structure Review

### Schedule Overview

[From course-outline.md — module titles, timing, sequence]

| Module | Title | Duration | Key Topics |
|---|---|---|---|
| 1 | [Title] | [Time] | [Topics] |
| 2 | [Title] | [Time] | [Topics] |

> **Reviewer Feedback — SME:**
> - Is the topic sequence logical for this audience?
> - Are any critical topics missing?
> - Are any topics unnecessary or better covered elsewhere?
> - Is the time allocation per module realistic?
> - Comments: ___

---

## Part 4: Content Accuracy Review (SME Only)

For each module, list the key claims, frameworks, or examples used:

### Module [N]: [Title]

**Key concepts taught:**
- [Concept 1]
- [Concept 2]

**Examples/case studies used:**
- [Example 1]
- [Example 2]

**Frameworks/models referenced:**
- [Framework 1]

> **Reviewer Feedback — SME:**
> - Are the concepts accurate and current? (Yes/No)
> - Are the examples realistic and relevant? (Yes/No)
> - Are any frameworks outdated or misapplied?
> - Are there better examples from our organization?
> - Specific corrections needed: ___

[Repeat for each module]

---

## Part 5: Assessment Review (if --include-rubrics)

### Assessment Strategy Summary

[From rubrics.md — how learning will be measured]

| Objective | Assessment Method | Criteria Summary |
|---|---|---|
| [Obj 1] | [Method] | [Key criteria] |

> **Reviewer Feedback — SME:**
> - Do assessments actually test what the objectives promise?
> - Are assessment methods practical for this audience?
> - Are rubric criteria specific enough to evaluate fairly?
> - Comments: ___

---

## Part 6: Sign-Off

### SME Sign-Off

| Reviewer | Role | Date | Status | Signature |
|---|---|---|---|---|
| [Name] | [Role] | [Date] | [Approved/Changes Needed/Rejected] | ___ |

### Executive Sign-Off

| Reviewer | Role | Date | Status | Signature |
|---|---|---|---|---|
| [Name] | [Role] | [Date] | [Approved/Changes Needed/Rejected] | ___ |

### Action Items from Review

| # | Finding | Priority | Action Required | Owner | Deadline |
|---|---|---|---|---|---|
| 1 | [Issue] | [CRITICAL/IMPORTANT/MINOR] | [What to do] | [Who] | [When] |

---

## Review Timeline

| Step | Action | Date |
|---|---|---|
| 1 | Review package distributed | [Today's date] |
| 2 | SME review deadline | [+2 weeks] |
| 3 | Executive review deadline | [+3 weeks] |
| 4 | Revisions completed | [+4 weeks] |
| 5 | Final approval | [+5 weeks] |
```

## Post-Generation Actions

1. **Summarize**: "Review package generated for [audience]. Includes [N] objectives, [M] modules, and [P] review questions."
2. **Recommend distribution**: "Send to reviewers with the deadline [date + 2 weeks]. Follow up at 1 week if no response."
3. **After review returns**: "Use `/generate-objectives --update` and related commands to implement reviewer feedback."

## Validation Checks

- [ ] Every learning objective has a reviewer feedback section
- [ ] Executive summary covers business need, audience, outcomes, resources
- [ ] Module structure review includes complete schedule
- [ ] Sign-off section has space for all reviewer types
- [ ] Review timeline is realistic (not same-day turnaround)

## Error Handling

**Missing core files:**
- "Error: Cannot generate review package without course-positioning.md and learning-objectives.md."

**Partial curriculum:**
- "Warning: Course outline and rubrics not yet generated. Review package will cover positioning and objectives only. Generate remaining components first for a complete review."

## Implementation Notes

**Date retrieval:**
```bash
TZ='America/New_York' date '+%Y-%m-%d'
```

**Review deadline calculation:**
```bash
TZ='America/New_York' date -d "+14 days" '+%Y-%m-%d'
```

**DO NOT:**
- Include raw pedagogical jargon (explain Bloom's levels in plain language for executives)
- Generate a review package that's longer than the curriculum itself
- Skip the reviewer feedback prompts (they are the whole point)
- Make the sign-off section optional (organizational accountability requires it)

---

Create review packages that make it easy for non-designers to give meaningful, structured feedback on curriculum quality and relevance.
