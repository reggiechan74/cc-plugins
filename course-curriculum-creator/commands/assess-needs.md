---
name: assess-needs
description: Conduct a training needs assessment to determine if a course is the right intervention and document the performance gap
argument-hint: "[--title 'Assessment Title'] [--skip-alternatives]"
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Edit
---

# Assess Needs Command

Conduct a structured Training Needs Assessment (TNA) before course design begins. Expert instructional design practice requires diagnostic assessment before prescription — this command guides the user through identifying the performance gap, evaluating whether training is the right intervention, and documenting the target population and success metrics. The output is a standalone TNA document that informs all downstream design decisions.

## Why This Matters

Expert L&D practice requires diagnostic assessment before prescription. Not every performance problem is a training problem. Skipping needs assessment leads to:

- **Wasted resources** building courses that don't address the real issue
- **Misaligned content** that teaches the wrong things to the wrong people
- **Unmeasurable outcomes** because success was never defined upfront
- **Missed alternatives** where job aids, process changes, or environmental fixes would be more effective

A proper TNA ensures that when training IS the right answer, it targets the actual gap with measurable outcomes. When training is NOT the answer, it saves the organization time and money by recommending the right intervention.

## Command Behavior

When user invokes `/assess-needs [--title 'Assessment Title'] [--skip-alternatives]`:

### Step 1: Gather Context

Use AskUserQuestion to collect the following (prompt for each missing piece):

1. **Stakeholder**: Who requested this training? What is their role?
2. **Business Problem**: What business outcome is not being met? What triggered this request?
3. **Current State**: What are people doing now? What does current performance look like?
4. **Desired State**: What should people be doing instead? What does success look like?
5. **Measurement**: How is the gap currently being measured or observed? What data exists?

If `--title` is provided, use it as the assessment title. Otherwise, derive a title from the business problem described.

### Step 2: Analyze Performance Gap

Based on the gathered context, classify the performance gap into one or more categories:

| Gap Type | Description | Example |
|----------|-------------|---------|
| **Skills** | People lack the ability to perform the task | Cannot use the new software tool |
| **Knowledge** | People lack information needed to perform | Don't know the updated compliance regulations |
| **Motivation** | People can perform but choose not to | Know the process but skip steps due to time pressure |
| **Environmental** | Systems, tools, or processes prevent performance | Software crashes frequently, making task impossible |
| **Resource** | People lack time, tools, or support | No access to reference materials on the job |

Present the analysis to the user and ask for confirmation or correction. A single performance problem may involve multiple gap types.

### Step 3: Recommend Intervention Type

Based on the gap analysis, recommend one of three outcomes:

**Training Appropriate** — The gap is primarily Skills or Knowledge based:
- Proceed with course design
- Document what training should cover
- Note any complementary non-training interventions needed

**Training Partial** — The gap involves Skills/Knowledge AND Motivation/Environmental/Resource factors:
- Training can address part of the problem
- Document what training CAN address
- Document what MUST be addressed through other interventions
- Flag that training alone will not close the gap

**Training Not Appropriate** — The gap is primarily Motivation, Environmental, or Resource based:
- Document why training is not the right intervention
- Recommend alternative interventions (process redesign, job aids, management coaching, tool improvements, incentive alignment)
- If `--skip-alternatives` is provided, acknowledge the finding but do not block the user from proceeding

### Step 4: Document Target Population

Use AskUserQuestion to gather:

1. **Population Size**: How many people need this intervention? (approximate range is fine)
2. **Skill Range**: What is the spread of current capability? (novice to expert, or narrow band)
3. **Learning Context**: Where will training occur? (in-person, virtual, self-paced, blended)
4. **Prior Training**: What related training have they already received?
5. **Accessibility Needs**: Are there known accessibility, language, or accommodation requirements?

### Step 5: Define Success Metrics

Use AskUserQuestion to establish measurable outcomes using Kirkpatrick's four levels:

- **Level 1 — Reaction**: How will learner satisfaction be measured?
- **Level 2 — Learning**: What knowledge or skill will be tested? How?
- **Level 3 — Behavior**: What observable on-the-job behavior change is expected? Over what timeline?
- **Level 4 — Results**: What business metric should improve? By how much? Over what period?

Guide the user to define at least one metric beyond Level 1 (satisfaction surveys alone are insufficient). Ask for:

- **Timeline**: When should results be measurable? (e.g., 30/60/90 days post-training)
- **Baseline Data**: What is the current measurement? (needed to calculate improvement)

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if it exists:
- `instructor_name`: Use as analyst name in the output document
- `organization`: Use as organization in the output document

If settings file doesn't exist, ask the user for analyst name and organization during Step 1.

## Output Location

Determine where to save the TNA document:

**Standalone mode** (before create-course, no course directory exists):
- Save as `training-needs-analysis-YYYY-MM-DD.md` in the current working directory
- This is the typical flow: assess needs first, then decide whether to create a course

**Inside course directory** (01-planning/ directory exists in current working directory):
- Save as `01-planning/training-needs-analysis.md`
- This supports running the assessment after a course directory has already been created

## File Output Format

Generate the TNA document with the following structure:

```markdown
---
title: Training Needs Assessment - [Title or Topic]
date: YYYY-MM-DD
version: 0.1.0
status: draft
analyst: [From settings or user input]
organization: [From settings or user input]
lastUpdated: YYYY-MM-DD
recommendation: [training-appropriate|training-partial|training-not-appropriate]
---

# Training Needs Assessment: [Title or Topic]

## 1. Business Context

**Stakeholder:** [Name and role]
**Date of Request:** [Date]
**Business Problem:** [Description of the business outcome not being met]
**Trigger:** [What prompted this training request]

## 2. Performance Gap Analysis

### Current State

[Description of what people are currently doing — observed behaviors, performance data]

### Desired State

[Description of what people should be doing — target behaviors, performance targets]

### Gap Description

[Clear articulation of the difference between current and desired state]

### Gap Type Classification

| Gap Type | Present? | Evidence |
|----------|----------|----------|
| Skills | [Yes/No] | [Supporting evidence] |
| Knowledge | [Yes/No] | [Supporting evidence] |
| Motivation | [Yes/No] | [Supporting evidence] |
| Environmental | [Yes/No] | [Supporting evidence] |
| Resource | [Yes/No] | [Supporting evidence] |

**Primary Gap Type:** [The dominant gap type driving the performance issue]

### Root Cause Analysis

[Analysis of why the gap exists — not just what the gap is, but what caused it]

## 3. Intervention Recommendation

**Recommendation:** [Training Appropriate | Training Partial | Training Not Appropriate]

**Rationale:** [Why this recommendation follows from the gap analysis]

**What Training Can Address:**
- [Specific skills or knowledge gaps that training will target]

**What Training Cannot Address:**
- [Factors that require non-training interventions]

**Complementary Interventions Needed:**
- [Job aids, process changes, management actions, tool improvements, etc.]

## 4. Target Population

| Attribute | Details |
|-----------|---------|
| Population Size | [Number or range] |
| Current Skill Range | [Novice/Intermediate/Advanced or spread description] |
| Learning Context | [In-person/Virtual/Self-paced/Blended] |
| Prior Related Training | [What they've already completed] |
| Accessibility Needs | [Known requirements or "None identified"] |

## 5. Success Metrics

### Kirkpatrick Evaluation Levels

- [ ] **Level 1 — Reaction**: [How satisfaction will be measured]
- [ ] **Level 2 — Learning**: [What will be tested and how]
- [ ] **Level 3 — Behavior**: [Observable behavior change expected]
- [ ] **Level 4 — Results**: [Business metric improvement expected]

**Measurement Timeline:** [When results should be measurable — e.g., 30/60/90 days]

**Baseline Data:**
- [Current metric]: [Current value]
- [Target metric]: [Target value]
- [Measurement method]: [How improvement will be tracked]

## 6. Constraints and Considerations

- [Budget constraints]
- [Timeline constraints]
- [Technology or platform constraints]
- [Organizational or cultural considerations]
- [Regulatory or compliance requirements]

## 7. Next Steps

[Based on recommendation — either proceed to course design or pursue alternative interventions]
```

## Post-Generation Actions

After generating the TNA document:

1. **Summarize the recommendation** to the user in plain language:
   - If **Training Appropriate**: "The analysis supports building a course. The primary gap is [type], which training can directly address."
   - If **Training Partial**: "Training can address part of this problem ([skills/knowledge gap]), but [other factors] also need non-training interventions to fully close the gap."
   - If **Training Not Appropriate**: "The analysis suggests training is not the primary solution. The gap is driven by [type], which is better addressed through [alternative]."

2. **Suggest next steps** based on the outcome:
   - **Training Appropriate**: "Next: Run `/create-course` to initialize the course project, then `/generate-objectives` to define learning outcomes aligned with this assessment."
   - **Training Partial**: "Next: Document the non-training interventions with the stakeholder. For the training component, run `/create-course` to proceed with course design."
   - **Training Not Appropriate**: "Next: Share this assessment with the stakeholder to discuss alternative interventions. If they still want training, the TNA document captures the rationale and risks."

## Validation Checks

Before finalizing the TNA document, verify:

- [ ] **Gap type classified**: At least one gap type is marked as present with supporting evidence
- [ ] **Recommendation follows from analysis**: If gap is Skills/Knowledge, recommendation is training-appropriate; if mixed, training-partial; if Motivation/Environmental/Resource only, training-not-appropriate
- [ ] **Metrics are measurable**: Success metrics include specific, observable criteria (not vague aspirations)
- [ ] **Population characterized**: All five target population attributes are documented
- [ ] **At least one Kirkpatrick level beyond L1**: Success metrics include at least Level 2 or Level 3 measurement (satisfaction surveys alone are insufficient)

If any validation check fails, flag it to the user and offer to revisit that section.

## Error Handling

**No context provided (user runs command with no information):**
- Guide through all questions interactively using AskUserQuestion
- Start with Step 1 and proceed sequentially
- Provide examples to help the user articulate the problem

**User wants to skip sections:**
- Acknowledge and don't block — mark skipped sections as "[Not assessed — skipped by user]"
- Still generate the document with available information
- Note in the document which sections were skipped and why

**User disagrees with recommendation:**
- Accept the user's judgment — they may have context not captured in the assessment
- Document the disagreement: "Note: Analyst recommendation was [X] but stakeholder elected to proceed with [Y]."
- Continue with the user's chosen direction

**Settings file not found:**
- Prompt user for analyst name and organization
- Suggest: "Tip: Create `.claude/course-curriculum-creator.local.md` to set default preferences."

## Implementation Notes

**Date retrieval:**
Always use bash to get current date:
```bash
TZ='America/New_York' date '+%Y-%m-%d'
```

**Path handling:**
- Check for `01-planning/` directory in current working directory to determine output mode
- Use absolute paths in success messages
- Expand ~ to full path if applicable

**YAML frontmatter:**
- All dates in YYYY-MM-DD format
- Version starts at 0.1.0 (semantic versioning)
- Status starts as "draft"
- Recommendation field uses kebab-case values: `training-appropriate`, `training-partial`, `training-not-appropriate`

**DO NOT:**
- Skip the gap analysis and jump straight to course creation
- Assume training is always the answer
- Use relative dates ("today", "current") — always get actual date via bash
- Generate a TNA without user input on business context
- Mark all Kirkpatrick levels as "N/A" — push for at least L1 + one higher level

---

Ensure every training intervention starts with clear diagnostic reasoning.
