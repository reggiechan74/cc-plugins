---
name: generate-evaluation-plan
description: Generate a comprehensive evaluation plan covering all four Kirkpatrick levels to measure training effectiveness and business impact
argument-hint: "[--levels 1,2,3,4|all] [--roi]"
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Edit
  - Skill
---

# Generate Evaluation Plan Command

Create a comprehensive evaluation plan covering Kirkpatrick's four levels of training evaluation. Moves beyond "did they like it?" (Level 1) to "did it change their behavior and impact the business?" (Levels 3-4).

## Why This Matters

L&D managers are increasingly accountable for demonstrating ROI. Reaction surveys (L1) and quiz scores (L2) don't answer the question stakeholders actually ask: "Was this worth the investment?" This command designs measurement at all four levels during the design phase — not as an afterthought when data comes in.

## Prerequisites

- Must have `01-planning/learning-objectives.md`
- Should have `03-assessment/rubrics.md` (for L2 alignment)
- Should have `04-materials/transfer-plan.md` (for L3 integration)
- Recommended: `01-planning/training-needs-analysis.md` (for L4 baseline metrics)

## Staleness Check

Before generating, check if source files have changed since this file was last generated:

1. If the output file `03-assessment/evaluation-plan.md` already exists, read its YAML frontmatter `sourceHashes`
2. Compute current hash of source files and compare
3. Warn if changed

When generating, always compute and write current source hashes to the output file's frontmatter.

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `instructor_name`: Use as evaluator
- `organization`: Use in plan header

If settings file doesn't exist, use sensible defaults or prompt user.

## Command Behavior

1. Load `backward-design-methodology` skill for assessment alignment
2. Read learning objectives and TNA (if exists) for evaluation context
3. Determine which levels to generate (default: all four)
4. For each level, create specific instruments and timelines
5. Write to `03-assessment/evaluation-plan.md`

## Level Selection

### --levels all (default)
Generate evaluation instruments for all four Kirkpatrick levels.

### --levels 1,2
Generate only Level 1 and Level 2 (common for low-stakes workshops).

### --levels 1,2,3,4
Same as `all`.

### --roi
Add ROI calculation section (Phillips Level 5) to Level 4.

## File Output Format

### 03-assessment/evaluation-plan.md

```
---
title: Evaluation Plan - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
courseVersion: [match]
lastUpdated: YYYY-MM-DD
levelsIncluded: [1, 2, 3, 4]
sourceFiles:
  learning-objectives: "01-planning/learning-objectives.md"
  rubrics: "03-assessment/rubrics.md"
  transfer-plan: "04-materials/transfer-plan.md"
  training-needs-analysis: "01-planning/training-needs-analysis.md"
sourceHashes:
  learning-objectives: "[md5-first-8]"
  rubrics: "[md5-first-8]"
  transfer-plan: "[md5-first-8]"
  training-needs-analysis: "[md5-first-8]"
---

# Evaluation Plan

## [Course Title]

**Purpose:** Measure training effectiveness across all four Kirkpatrick levels to demonstrate value and inform continuous improvement.

**Evaluation Timeline:**

| Level | What It Measures | When | Instrument |
|---|---|---|---|
| 1 - Reaction | Satisfaction, perceived relevance | End of workshop | Survey |
| 2 - Learning | Knowledge/skill acquisition | Pre + post workshop | Assessment |
| 3 - Behavior | On-the-job application | 30-60 days post | Observation/survey |
| 4 - Results | Business impact | 60-90 days post | Metrics analysis |

---

## Level 1: Reaction

**Question:** Did participants find the training valuable, engaging, and relevant?

**When:** Immediately after workshop (last 10 minutes)

**Instrument: End-of-Workshop Survey**

Rate each item 1-5 (1=Strongly Disagree, 5=Strongly Agree):

| Item | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| The workshop content was relevant to my work | | | | | |
| The pace was appropriate for the material | | | | | |
| The activities helped me understand the concepts | | | | | |
| I feel confident applying what I learned | | | | | |
| The instructor was effective and engaging | | | | | |
| I would recommend this workshop to a colleague | | | | | |

**Open-ended questions:**
1. What was the most valuable part of the workshop?
2. What would you change about the workshop?
3. What additional topics would you like to explore?

**Success Threshold:** Average rating >= 4.0, NPS >= 40

**Data Collection:** [Paper forms / digital survey / LMS]
**Analysis Timeline:** Within 1 week of workshop

---

## Level 2: Learning

**Question:** Did participants acquire the intended knowledge and skills?

**When:** Pre-workshop (baseline) + end of workshop (post)

**Instrument: Pre/Post Knowledge & Skills Assessment**

For each learning objective, design a matched assessment item:

| Objective | Bloom's Level | Pre-Assessment Item | Post-Assessment Item | Measurement |
|---|---|---|---|---|
| [Objective 1] | [Level] | [Question/task matching cognitive level] | [Parallel question/task] | Score comparison |
| [Objective 2] | [Level] | [Question/task] | [Parallel question/task] | Score comparison |

**Assessment Design Principles:**
- Pre and post items must be parallel (same difficulty, different content)
- Assessment method must match cognitive level (no multiple choice for Analyze-level objectives)
- Include both knowledge items (Understand) and performance items (Apply+)
- Use rubrics from `03-assessment/rubrics.md` for Apply+ assessment

**Confidence Ratings:**
For each objective, also ask:
"How confident are you in your ability to [objective verb] [objective content]?"
(1=Not at all confident, 5=Very confident)

Compare pre/post confidence alongside pre/post performance.

**Success Threshold:**
- Knowledge gain: >= 20% improvement from pre to post
- Skill demonstration: >= 80% of participants meet rubric criteria at "Proficient" or above
- Confidence gain: >= 1.0 point average increase

**Note:** Level 2 assessment is largely covered by existing `/generate-artifacts --type pre-assessment` and `--type post-assessment`. This section adds the evaluation framework and success thresholds around those instruments.

---

## Level 3: Behavior

**Question:** Are participants applying what they learned on the job?

**When:** 30 days and 60 days post-workshop

**Instrument A: Participant Self-Report Survey (Day 30)**

For each Apply+ objective:

| Skill | Have You Applied This? | How Often? | Confidence | Barriers? |
|---|---|---|---|---|
| [Objective 1] | Yes/No/Partially | Daily/Weekly/Monthly/Not yet | 1-5 | [Open text] |
| [Objective 2] | Yes/No/Partially | ... | ... | ... |

**Additional questions:**
1. Describe a specific situation where you applied a workshop skill. What happened?
2. What has prevented you from applying other skills? (Select all: Time, Competing priorities, Lack of confidence, Process doesn't allow it, Forgot how, Not relevant to my role, Other)
3. What additional support would help you apply what you learned?

**Instrument B: Manager Observation Checklist (Day 60)**

For managers of workshop participants:

| Behavior | Not Observed | Sometimes | Consistently | N/A |
|---|---|---|---|---|
| [Observable behavior from Objective 1] | | | | |
| [Observable behavior from Objective 2] | | | | |

**Manager questions:**
1. Have you noticed changes in your employee's work approach since the workshop?
2. Has the employee discussed applying workshop concepts?
3. Would you recommend this workshop for other team members?

**Success Threshold:**
- Application rate: >= 70% report applying at least one skill within 30 days
- Sustained behavior: >= 50% report consistent application at 60 days
- Manager observation: >= 60% of managers observe behavior change

**Integration with Transfer Plan:**
L3 measurement should align with the follow-up touchpoints in `04-materials/transfer-plan.md`. The Day 30 survey replaces the Day 14 survey in the transfer schedule. The Day 60 manager checklist is a new touchpoint.

---

## Level 4: Results

**Question:** Did the training impact business outcomes?

**When:** 60-90 days post-workshop

**Step 1: Identify Business Metrics**

Connect learning objectives to business outcomes:

| Objective | Expected Business Impact | Metric | Baseline | Target |
|---|---|---|---|---|
| [Objective 1] | [What business outcome improves] | [Measurable KPI] | [Current value] | [Goal value] |
| [Objective 2] | [What business outcome improves] | [Measurable KPI] | [Current value] | [Goal value] |

**If TNA exists:** Pull baseline metrics from `01-planning/training-needs-analysis.md` Section 5 (Success Metrics).

**If TNA doesn't exist:** Prompt user for baseline metrics using AskUserQuestion:
- "What business metrics should improve as a result of this training?"
- "What are the current values for these metrics?"

**Step 2: Measurement Plan**

For each metric:
- **Data source:** Where does this data come from? (CRM, performance reviews, project tracking, customer surveys)
- **Collection method:** Who collects it and how?
- **Comparison method:** Pre/post, trained group vs. untrained group, or trend analysis
- **Confounding factors:** What else could explain changes? (seasonal trends, new tools, market changes)
- **Attribution method:** How to isolate training's contribution (manager estimates, control group, trend analysis)

**Step 3: Results Report Template**

```
## Training Impact Report: [Course Title]

**Evaluation Period:** [Date range]
**Participants Evaluated:** [N]

### Business Metrics

| Metric | Baseline | Post-Training | Change | Attribution to Training |
|---|---|---|---|---|
| [Metric 1] | [Value] | [Value] | [+/- %] | [% attributed] |
| [Metric 2] | [Value] | [Value] | [+/- %] | [% attributed] |

### ROI Calculation (if --roi flag used)

**Benefits:** [Monetary value of improvements]
**Costs:** [Workshop development + delivery + participant time + materials]
**ROI:** (Benefits - Costs) / Costs × 100 = [X]%

**Conservative estimate:** [Lower bound using most conservative attribution]
**Optimistic estimate:** [Upper bound using full attribution]
```

**Success Threshold:**
- At least 1 business metric shows measurable improvement
- Improvement is plausible attributable to training (not solely external factors)
- Stakeholders agree the results demonstrate value

---

## Evaluation Administration Plan

| Task | Owner | Timeline | Notes |
|---|---|---|---|
| Design L1 survey | Instructor/L&D | Before workshop | Finalize during curriculum design |
| Design L2 pre/post assessment | Instructor/L&D | Before workshop | Align with objectives and rubrics |
| Administer L1 survey | Instructor | Last 10 min of workshop | Paper or digital |
| Administer L2 post-assessment | Instructor | Final module of workshop | Built into lesson plan |
| Send L3 participant survey | L&D team | Day 30 post-workshop | Automated email |
| Send L3 manager checklist | L&D team | Day 60 post-workshop | Email to managers |
| Collect L4 business data | L&D team + stakeholders | Day 60-90 | Pull from business systems |
| Compile evaluation report | L&D team | Day 90 | Full Kirkpatrick report |
| Present to stakeholders | L&D lead | Day 100 | Focus on L3/L4 results |

---

## Continuous Improvement Integration

**How evaluation data feeds back into curriculum design:**

| Evaluation Finding | Action | Command |
|---|---|---|
| L1: Low relevance scores | Update course positioning and examples | `/create-course` (revise positioning) |
| L1: Pacing issues | Adjust module timing | `/generate-outline --update` |
| L2: Specific objectives not met | Revise activities for those objectives | `/generate-lesson-plans --module N` |
| L3: Low application rate | Strengthen transfer plan, add job aids | `/generate-transfer-plan` |
| L3: Barriers identified | Address environmental/process issues | `/assess-needs` (re-evaluate) |
| L4: No business impact | Re-examine needs analysis and objective alignment | `/assess-needs` + `/generate-objectives` |
```

## Post-Generation Actions

After generating the evaluation plan:

1. **Summarize scope**: "Evaluation plan generated covering Kirkpatrick Levels [X]. Includes [N] instruments with administration timeline."

2. **Highlight dependencies**: "Level 3 measurement integrates with the transfer plan follow-up schedule. Level 4 requires baseline business metrics — [available from TNA / need to gather]."

3. **Recommend next step**: "Review evaluation instruments with stakeholders to confirm metrics and success thresholds."

## Validation Checks

Before finalizing, validate:
- [ ] Every learning objective has a corresponding L2 assessment item
- [ ] L2 assessment methods match Bloom's cognitive levels
- [ ] L3 instruments reference observable behaviors (not feelings)
- [ ] L4 metrics are connected to business outcomes from TNA (if available)
- [ ] Administration timeline is realistic with clear ownership
- [ ] Success thresholds are specified for each level

## Error Handling

**Missing learning objectives:**
- "Error: learning-objectives.md not found. Cannot generate evaluation plan without objectives. Run `/generate-objectives` first."

**No TNA available (for L4):**
- "Advisory: No training needs analysis found. Level 4 evaluation will be limited without baseline business metrics. Consider running `/assess-needs` or providing metrics manually."
- Proceed with L1-L3 and prompt user for L4 metrics via AskUserQuestion

**Evaluation plan already exists:**
- Prompt: "evaluation-plan.md already exists. Options: (1) Regenerate (overwrites), (2) Add/update specific levels, (3) Cancel"

## Implementation Notes

**Date retrieval:**
```bash
TZ='America/New_York' date '+%Y-%m-%d'
```

**Assessment-level matching for L2:**
- Remember → Multiple choice, matching
- Understand → Explain, compare (written or verbal)
- Apply → Perform, demonstrate (hands-on task)
- Analyze → Case analysis, pattern identification
- Evaluate → Critique, recommend with justification
- Create → Design, produce original work

**DO NOT:**
- Create evaluation instruments that don't map to specific objectives
- Use only self-report for L3 — include manager observation
- Promise ROI without acknowledging attribution challenges
- Skip the confounding factors analysis for L4
- Design L2 items at the wrong cognitive level (no multiple choice for Analyze objectives)

---

Design evaluation plans during curriculum creation, not after delivery. The best time to plan measurement is when you're defining what success looks like.
