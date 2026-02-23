---
name: review-curriculum
description: Validate curriculum quality, backward design alignment, and pedagogical soundness
argument-hint: "[course-code-or-path]"
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash
  - Skill
---

# Review Curriculum Command

Validate an existing curriculum for quality, backward design alignment, and pedagogical soundness using the quality-reviewer agent's methodology.

## Command Behavior

When user invokes `/review-curriculum [course-code-or-path]`:

1. **Locate the curriculum to review:**
   - If a course code is provided (e.g., `021-2-201`), search for a matching directory
   - If a path is provided, use that directory directly
   - If no argument is given, look for curriculum files in the current working directory

2. **Load pedagogical reference skills:**
   - Load the `backward-design-methodology` skill for UbD framework guidance
   - Load the `blooms-taxonomy` skill for cognitive level validation

3. **Discover curriculum files:**
   Use Glob to find all markdown files in the curriculum directory. Look for:
   - `01-planning/course-positioning.md`
   - `01-planning/learning-objectives.md`
   - `01-planning/course-description.md`
   - `02-design/course-outline.md`
   - `02-design/lesson-plans.md`
   - `03-assessment/rubrics.md`
   - Any additional files in the directory structure

4. **Perform validation across all three backward design stages:**

   **Stage 1 - Learning Outcomes:**
   - Verify each objective uses a measurable Bloom's taxonomy action verb
   - Check cognitive level distribution is appropriate for the course duration
   - Confirm objectives are achievable within the timeframe
   - Validate scaffolding progression (lower to higher Bloom's levels)

   **Stage 2 - Assessment Plan:**
   - Verify every learning objective has at least one corresponding assessment
   - Check assessment methods match cognitive levels of objectives
   - Evaluate rubric quality (clear criteria, differentiated performance levels)
   - Identify orphaned assessments (assessments without matching objectives)

   **Stage 3 - Learning Activities:**
   - Verify activities support stated objectives
   - Check activities prepare students for assessments
   - Evaluate scaffolding from guided to independent practice
   - Validate timing feasibility with breaks and buffer

   **Module Consistency:**
   - Verify module count matches between outline and lesson plans
   - Verify module titles match between outline and lesson plans
   - Check every learning objective is mapped to at least one module

   **Overall Coherence:**
   - Vertical alignment: positioning -> outcomes -> assessments -> activities
   - Terminology consistency across all documents
   - Timing analysis (total time vs. workshop duration)
   - Gap analysis (orphaned elements, untested outcomes, unprepared assessments)

   **Timing Reconciliation:**
   - Compare objective time allocations, outline module durations, and lesson plan activity totals
   - Flag discrepancies > 10% between any two sources
   - Verify total instruction time fits within workshop duration (with 10-15% buffer)

5. **Generate validation report:**

   Create a report with:
   - Executive summary with overall quality rating (EXCELLENT / GOOD / NEEDS REVISION / SIGNIFICANT ISSUES)
   - Stage-by-stage findings with PASS/FAIL status
   - Objective-assessment coverage matrix
   - Activity-objective alignment matrix
   - Quality metrics (coverage %, alignment %, timing buffer %, Bloom's distribution)
   - Prioritized action items (CRITICAL / HIGH / MEDIUM / LOW)

6. **Save and present results:**
   - Save the validation report as `VALIDATION_REPORT.md` in the curriculum directory
   - Present a concise summary to the user with:
     - Overall quality rating
     - Critical issues (if any)
     - Recommendation (ready to deliver / needs revision / needs redesign)
     - Path to full report
   - Offer to help implement recommended changes

## Quality Rating Criteria

- **EXCELLENT**: All stages PASS, no critical issues, exemplary alignment
- **GOOD**: All stages PASS, minor issues, solid backward design implementation
- **NEEDS REVISION**: 1-2 stages FAIL, moderate issues, fixable with targeted changes
- **SIGNIFICANT ISSUES**: 3+ stages FAIL, critical gaps, requires substantial redesign

## Edge Cases

- **Missing curriculum files**: Note which components are missing, flag as CRITICAL, validate what exists
- **Incomplete curriculum**: Clearly state validation is preliminary, provide feedback on completed sections
- **Non-standard structure**: Adapt validation to actual file organization, focus on alignment principles
