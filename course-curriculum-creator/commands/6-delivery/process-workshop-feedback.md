---
name: process-workshop-feedback
description: Process workshop feedback and generate improvement report
argument-hint: "[feedback-file-or-notes] [--pilot]"
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

## Pilot Mode (--pilot flag)

When invoked with `--pilot`, this command activates enhanced feedback collection designed for first-run deliveries. A pilot is fundamentally different from steady-state delivery — the goal is to validate the curriculum design itself, not just the instructor's delivery.

### Additional Pilot Dimensions

In addition to the standard 5 dimensions above, pilot mode adds:

### Dimension 6: Timing Accuracy (Pilot Only)
- Did each module finish within its allocated time?
- Which modules ran over? By how much?
- Which modules had excess time?
- Were breaks adequate?
- Was the overall workshop duration appropriate?

### Dimension 7: Activity Effectiveness (Pilot Only)
- For each practice activity: Did students achieve the intended outcome?
- Were instructions clear enough for students to begin without extra clarification?
- Was the scaffolding (guided → independent) progression smooth?
- Did differentiation tiers (floor/scaffold/extension) work as designed?
- Which activities should be kept, modified, or replaced?

### Dimension 8: Content Gaps (Pilot Only)
- Were there moments where students needed knowledge not yet covered?
- Were there topics included that turned out to be unnecessary?
- Did prerequisite assumptions hold (did students have the expected prior knowledge)?
- Were examples relevant and resonant with the actual audience?

### Dimension 9: Facilitation Difficulty (Pilot Only)
- Which sections were hardest to facilitate? Why?
- Were instructor notes sufficient?
- Were there unexpected questions the instructor wasn't prepared for?
- Did any transitions between modules feel abrupt or confusing?

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

## Pilot Iteration Plan Output (--pilot only)

When `--pilot` is used, generate an additional file `04-materials/pilot-iteration-plan.md`:

```markdown
---
title: Pilot Iteration Plan - [Course Title]
pilotDate: [date of pilot, if known]
reportDate: YYYY-MM-DD
version: 0.1.0
status: action-required
iterationTarget: [date of next delivery, if known]
---

# Pilot Iteration Plan

## Course: [Course Title]
**Pilot Date:** [date]
**Generated:** [current date]
**Next Delivery Target:** [if known, or "TBD"]

---

## Pilot Summary

**Overall pilot assessment:** [READY FOR DELIVERY / NEEDS MINOR REVISIONS / NEEDS MAJOR REVISIONS / NEEDS REDESIGN]

**Key finding:** [1-2 sentence summary of the most important discovery from the pilot]

---

## Timing Reconciliation

| Module | Planned Duration | Actual Duration | Delta | Action |
|--------|-----------------|-----------------|-------|--------|
| Module 1: [Title] | [X] min | [Y] min | [+/- Z] min | [Keep / Adjust to [N] min / Split] |
| Module 2: [Title] | [X] min | [Y] min | [+/- Z] min | [Keep / Adjust to [N] min / Split] |

**Total planned:** [X] min | **Total actual:** [Y] min | **Delta:** [+/- Z] min

**Timing verdict:** [On track / Needs adjustment — specify which modules]

---

## Activity-by-Activity Assessment

### Module [N]: [Title]

| Activity | Effectiveness | Issue | Revision |
|----------|--------------|-------|----------|
| [Activity 1] | [Effective / Partially effective / Ineffective] | [What went wrong, if anything] | [Keep / Modify: specific change / Replace: with what] |
| [Activity 2] | [Effective / Partially effective / Ineffective] | [What went wrong, if anything] | [Keep / Modify: specific change / Replace: with what] |

[Repeat for each module]

---

## Content Gap Analysis

### Knowledge Gaps Discovered
| Gap | Where It Surfaced | Recommended Fix |
|-----|------------------|-----------------|
| [Missing concept] | [Module N, during activity X] | [Add to Module N instruction / Add as prerequisite / Add as pre-work] |

### Unnecessary Content
| Content | Why Unnecessary | Recommended Action |
|---------|----------------|-------------------|
| [Topic] | [Reason — audience already knew, not relevant, etc.] | [Remove / Condense / Move to extension challenge] |

---

## Facilitation Notes for Next Delivery

### Sections Requiring Extra Preparation
1. [Module/activity] — [Why it was difficult and what to prepare]
2. [Module/activity] — [Why it was difficult and what to prepare]

### Unexpected Questions to Prepare For
1. [Question] — [Suggested answer or resource]
2. [Question] — [Suggested answer or resource]

### Instructor Notes to Add/Update
1. [Location in lesson plans] — [Note to add]
2. [Location in lesson plans] — [Note to add]

---

## Prioritized Revision Plan

### Before Next Delivery (MUST DO)

| # | Revision | File to Modify | Effort |
|---|----------|---------------|--------|
| 1 | [Change] | [File path] | [Low/Medium/High] |
| 2 | [Change] | [File path] | [Low/Medium/High] |

### Before Next Delivery (SHOULD DO)

| # | Revision | File to Modify | Effort |
|---|----------|---------------|--------|
| 1 | [Change] | [File path] | [Low/Medium/High] |

### Future Iteration (NICE TO HAVE)

| # | Revision | File to Modify | Effort |
|---|----------|---------------|--------|
| 1 | [Change] | [File path] | [Low/Medium/High] |

---

## Version Recommendation

Based on pilot findings:
- **Recommended version bump:** [Patch / Minor / Major]
- **Rationale:** [Brief explanation]
- **Estimated revision effort:** [X hours]
```

## Error Handling

**No feedback provided:**
- Prompt user for feedback input method
- If user has no formal feedback, offer: "I can help you create a structured self-reflection based on your observations. Would you like to answer some guided questions?"

**Incomplete curriculum files:**
- Proceed with available context
- Note which curriculum files were unavailable for cross-referencing

**Pilot mode without sufficient data:**
- If `--pilot` is used but feedback doesn't include timing or activity-level detail, warn: "⚠ Pilot mode works best with detailed per-module feedback. Missing: [timing data / activity-level observations / content gap notes]. The iteration plan will be generated with available data, but consider collecting more detailed feedback for the next pilot."

---

Transform raw workshop feedback into structured, actionable improvement plans that drive continuous curriculum quality improvement.
