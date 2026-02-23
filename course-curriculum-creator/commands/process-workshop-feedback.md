---
name: process-workshop-feedback
description: Process workshop feedback and generate improvement report
argument-hint: "[feedback-file-or-notes]"
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
---

# Process Workshop Feedback Command

Analyze post-workshop feedback and generate an actionable improvement report.

## Prerequisites

- Must be in a course project directory
- Need feedback data (file, pasted notes, or survey results)

## Command Behavior

When user invokes `/process-workshop-feedback [feedback-source]`:

1. **Gather feedback data:**
   - If a file path is provided, read the feedback file
   - If no argument, prompt user: "How would you like to provide feedback? (1) Paste evaluation notes, (2) Provide path to feedback file, (3) Summarize key observations verbally"
   - Accept multiple feedback sources if provided

2. **Read curriculum context:**
   - `01-planning/learning-objectives.md` for objective achievement context
   - `02-design/course-outline.md` for module structure context
   - `03-assessment/rubrics.md` for assessment criteria context

3. **Analyze feedback** across dimensions (see analysis framework below)

4. **Generate debrief report:** `04-materials/workshop-debrief-report.md`

## Feedback Analysis Framework

### Dimension 1: Content Effectiveness
- Which modules received highest/lowest ratings?
- Were learning objectives perceived as achieved?
- Was content depth appropriate (too basic / too advanced)?
- Were examples relevant to the audience?

### Dimension 2: Delivery & Pacing
- Was timing appropriate for each module?
- Were activities engaging?
- Was the balance of lecture vs. practice appropriate?
- Were there energy dips or engagement peaks?

### Dimension 3: Materials & Resources
- Were handouts useful?
- Were exercises clear and well-structured?
- Were any materials missing or unnecessary?
- Was technology reliable?

### Dimension 4: Instructor Effectiveness
- Was instruction clear?
- Was the instructor responsive to questions?
- Was the learning environment supportive?

### Dimension 5: Overall Impact
- Would participants recommend the workshop?
- What was the most valuable takeaway?
- What would participants change?
- Net Promoter Score (if available)

## Output Format

```markdown
---
title: Workshop Debrief Report - [Course Title]
workshopDate: [date of workshop, if known]
reportDate: YYYY-MM-DD
feedbackSources: [list of sources]
respondentCount: [N, if known]
---

# Workshop Debrief Report

## Course: [Course Title]
**Workshop Date:** [date]
**Report Generated:** [current date]
**Feedback Sources:** [description of feedback data]

---

## Executive Summary

[2-3 sentence overview of feedback themes, overall satisfaction, and primary action items]

**Overall Rating:** [if quantitative data available]
**Net Promoter Score:** [if available]
**Would Recommend:** [percentage if available]

---

## Feedback Summary by Dimension

### Content Effectiveness
**Rating:** [if available]

**Strengths:**
- [Positive feedback theme 1]
- [Positive feedback theme 2]

**Areas for Improvement:**
- [Issue 1 with supporting evidence]
- [Issue 2 with supporting evidence]

**Specific Module Feedback:**
| Module | Rating/Feedback | Suggested Change |
|--------|----------------|-----------------|
| [Module 1] | [Summary] | [Change if needed] |
| [Module 2] | [Summary] | [Change if needed] |

### Delivery & Pacing
[Same structure as above]

### Materials & Resources
[Same structure as above]

### Instructor Effectiveness
[Same structure as above]

### Overall Impact
[Same structure as above]

---

## Suggested Revisions

Based on feedback analysis, these curriculum changes are recommended:

### High Priority (Before Next Delivery)

1. **[Revision 1]**
   - **Source:** [Which feedback theme]
   - **File to modify:** [Specific curriculum file]
   - **Change:** [What to change]

2. **[Revision 2]**
   - **Source:** [Which feedback theme]
   - **File to modify:** [Specific curriculum file]
   - **Change:** [What to change]

### Medium Priority (Improves Quality)

[Same format]

### Low Priority (Nice to Have)

[Same format]

---

## Improvement Priorities

Ranked list of improvement actions:

| Priority | Action | Impact | Effort | Target |
|----------|--------|--------|--------|--------|
| 1 | [Action] | High | Low | Next delivery |
| 2 | [Action] | High | Medium | Next delivery |
| 3 | [Action] | Medium | Low | Future update |

---

## Version Control Recommendation

Based on the scope of suggested changes:
- **No version change needed** (minor wording/timing tweaks)
- **Patch version** (v1.0.x): Small fixes, timing adjustments
- **Minor version** (v1.x.0): New modules, significant content changes
- **Major version** (vX.0.0): Complete restructuring

**Recommended:** [version change level] - [brief rationale]

---

## Raw Feedback Data

[If provided, include or reference the original feedback data for archival]
```

## Error Handling

**No feedback provided:**
- Prompt user for feedback input method
- If user has no formal feedback, offer: "I can help you create a structured self-reflection based on your observations. Would you like to answer some guided questions?"

**Incomplete curriculum files:**
- Proceed with available context
- Note which curriculum files were unavailable for cross-referencing

---

Transform raw workshop feedback into structured, actionable improvement plans that drive continuous curriculum quality improvement.
