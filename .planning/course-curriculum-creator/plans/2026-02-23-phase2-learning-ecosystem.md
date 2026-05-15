# Phase 2: Learning Ecosystem — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add transfer-of-learning planning, Kirkpatrick L3/L4 evaluation, and differentiated instruction to transform the plugin from a course creation tool into a complete learning ecosystem.

**Architecture:** Three independent workstreams — (1) new `generate-transfer-plan` command for post-workshop application, (2) new `generate-evaluation-plan` command for multi-level evaluation, (3) differentiation layer added to existing `generate-lesson-plans` command template. All follow established plugin conventions from v0.4.0.

**Tech Stack:** Markdown command files with YAML frontmatter. No runtime code — plugin is entirely prompt-based.

---

## Task 1: Create the `generate-transfer-plan` Command

**Files:**
- Create: `commands/generate-transfer-plan.md`

**Step 1: Write the command file**

Create `commands/generate-transfer-plan.md` with this exact content:

```markdown
---
name: generate-transfer-plan
description: Generate a post-workshop transfer plan with action items, manager briefings, job aids, and follow-up touchpoints to bridge learning to workplace application
argument-hint: "[--format full|manager-brief|job-aids-only]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Skill
---

# Generate Transfer Plan Command

Create a comprehensive transfer-of-learning plan that bridges workshop learning to workplace application. Research shows 70% of training content is forgotten within 24 hours without reinforcement — this command designs the reinforcement ecosystem.

## Why This Matters

Kirkpatrick Level 3 (behavior change) is what organizations actually pay for. A workshop without transfer mechanisms is entertainment, not training. This command ensures every learning objective has a concrete path from classroom to workplace.

## Prerequisites

- Must have `01-planning/learning-objectives.md`
- Should have `02-design/lesson-plans.md` (for activity context)
- Should have `03-assessment/rubrics.md` (for success criteria)

## Staleness Check

Before generating, check if source files have changed since this file was last generated:

1. If the output file `04-materials/transfer-plan.md` already exists, read its YAML frontmatter `sourceHashes`
2. Compute current hash of each source file:
   - `md5sum 01-planning/learning-objectives.md | cut -c1-8`
   - `md5sum 02-design/lesson-plans.md | cut -c1-8` (if exists)
3. Compare hashes and warn if changed

When generating, always compute and write current source hashes to the output file's frontmatter.

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `instructor_name`: Use as workshop facilitator in follow-up materials
- `organization`: Use in manager briefing header

If settings file doesn't exist, use sensible defaults or prompt user.

## Command Behavior

1. Load `backward-design-methodology` skill for outcomes alignment
2. Read learning objectives to identify transfer targets
3. Classify each objective by transfer type:
   - **Near transfer** (Apply-level): Direct application of same skill in similar context
   - **Far transfer** (Analyze/Evaluate/Create): Adaptation of principles to new contexts
4. Generate transfer plan components based on `--format` flag
5. Write to `04-materials/transfer-plan.md`

## Format Options

### --format full (default)
Generates all components: 30/60/90-day action plan, manager briefing, job aids, follow-up schedule, performance support tools.

### --format manager-brief
Generates only the manager briefing document — suitable for sending to participants' managers before or after the workshop.

### --format job-aids-only
Generates only the quick-reference job aids — one per Apply+ level objective.

## File Output Format

### 04-materials/transfer-plan.md

```
---
title: Transfer Plan - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
courseVersion: [match]
lastUpdated: YYYY-MM-DD
sourceFiles:
  learning-objectives: "01-planning/learning-objectives.md"
  lesson-plans: "02-design/lesson-plans.md"
sourceHashes:
  learning-objectives: "[md5-first-8]"
  lesson-plans: "[md5-first-8]"
---

# Transfer of Learning Plan

## [Course Title]

**Purpose:** Bridge workshop learning to workplace application through structured reinforcement, manager support, and performance tools.

**Key Principle:** Apply new skills within 48 hours for maximum retention.

---

## Part 1: 30/60/90-Day Action Plan

### Participant Action Plan Template

**Name:** _______________
**Workshop Date:** _______________
**Manager:** _______________

#### Week 1 (Days 1-7): Immediate Application

For each Apply-level objective, provide:

| Objective | First Application Task | Success Indicator | Target Date |
|---|---|---|---|
| [Objective from learning-objectives.md] | [Specific workplace task] | [Observable outcome] | [Date] |

**Instructions to participant:**
- Pick your highest-priority skill from the workshop
- Apply it to a real work task within 48 hours
- Note what worked and what was difficult
- Share results with your manager using the talking points below

#### Month 1 (Days 8-30): Deepening Practice

For each Analyze/Evaluate-level objective:

| Objective | Practice Task | Complexity Level | Support Available |
|---|---|---|---|
| [Objective] | [More complex application] | [Building on Week 1] | [Resources, contacts] |

**Instructions to participant:**
- Build on your Week 1 application
- Tackle a more complex scenario
- Use the job aids provided for reference
- Schedule a check-in with your manager

#### Month 2-3 (Days 31-90): Integration & Independence

For Create-level objectives (if applicable):

| Objective | Integration Project | Expected Outcome | Review Date |
|---|---|---|---|
| [Objective] | [Original work combining skills] | [Deliverable] | [Date] |

**Instructions to participant:**
- Combine multiple workshop skills in a real project
- Self-assess using the workshop rubrics
- Document lessons learned
- Share with peers who attended the workshop

---

## Part 2: Manager Briefing

### For: Managers of Workshop Participants
### Re: [Course Title] — Supporting Your Employee's Learning

**Workshop Overview:**
[2-3 sentence summary derived from course-positioning.md]

**What Your Employee Learned:**

| Skill Area | What They Can Now Do | How You Can Reinforce |
|---|---|---|
| [From Objective 1] | [Observable capability] | [Specific manager action] |
| [From Objective 2] | [Observable capability] | [Specific manager action] |

**Your Role in Transfer Success:**

1. **Week 1**: Ask about the workshop within 2 days. Use: "What's one thing you learned that you want to apply this week?"
2. **Month 1**: Assign a task that uses workshop skills. Provide feedback on application.
3. **Month 2-3**: Include workshop skills in performance conversations. Recognize application.

**Warning Signs Transfer Is Failing:**
- Employee hasn't mentioned applying anything after 2 weeks
- No visible change in work approach
- Employee says "the workshop was good but doesn't apply to my work"

**If Transfer Is Failing:**
- Schedule 15-minute conversation about application barriers
- Ask: "What's preventing you from using [specific skill]?"
- Common barriers: time pressure, conflicting processes, lack of confidence
- Contact [instructor/L&D team] for coaching support

---

## Part 3: Job Aids

### Quick Reference Cards

For each Apply+ level objective, create a one-page job aid:

#### Job Aid: [Objective Title]

**When to use this:** [Workplace trigger — what situation calls for this skill]

**Steps:**
1. [Step 1 — action verb + what to do]
2. [Step 2]
3. [Step 3]
4. [Step 4]

**Common Mistakes:**
- [Mistake 1] → [What to do instead]
- [Mistake 2] → [What to do instead]

**Quality Check:** [How to verify you did it correctly]

**Need Help?** [Resource or contact]

---

[Repeat for each Apply+ objective]

---

## Part 4: Follow-Up Touchpoint Schedule

| Timing | Channel | Content | Owner |
|---|---|---|---|
| Day 1 post-workshop | Email | Thank you + action plan reminder + job aids attached | Instructor |
| Day 7 | Email | "How's your first application going?" + quick tip | Instructor |
| Day 14 | Survey (2 min) | Application progress check + barrier identification | L&D team |
| Day 30 | Email | Month 1 practice task reminder + peer learning invite | Instructor |
| Day 60 | Survey (5 min) | Kirkpatrick L3 behavior assessment | L&D team |
| Day 90 | Email | Integration project prompt + continued resources | Instructor |

## Part 5: Performance Support Tools

### Decision Trees

For complex skills (Analyze/Evaluate objectives), create decision trees:

#### Decision Tree: [Skill Name]

```
[Situation] → Ask: [First question]
  ├── Yes → [Action A]
  └── No → Ask: [Second question]
       ├── Yes → [Action B]
       └── No → [Action C]
```

### Checklists

For procedural skills (Apply objectives), create checklists:

#### Checklist: [Procedure Name]

- [ ] [Step 1]
- [ ] [Step 2]
- [ ] [Step 3]
- [ ] Verify: [Quality check]

---

## Transfer Success Metrics

| Metric | Measurement Method | Target | Timeline |
|---|---|---|---|
| Application rate | Day 14 survey | 80% applied at least one skill | 2 weeks |
| Manager awareness | Manager survey | 70% aware of employee's new skills | 1 month |
| Behavior change | Day 60 L3 survey | 60% sustained behavior change | 2 months |
| Business impact | Performance data | Measurable improvement in [KPI] | 3 months |
```

## Post-Generation Actions

After generating the transfer plan:

1. **Summarize components**: "Transfer plan generated with [N] job aids, manager briefing, 30/60/90-day action plan, and follow-up schedule."

2. **Recommend distribution**: "Distribute the manager briefing 1 week before the workshop. Send the action plan and job aids to participants on Day 1 post-workshop."

3. **Suggest next step**: "Generate evaluation plan to measure transfer effectiveness: `/generate-evaluation-plan`"

## Validation Checks

Before finalizing, validate:
- [ ] Every Apply+ objective has a corresponding job aid
- [ ] Action plan covers all three phases (Week 1, Month 1, Month 2-3)
- [ ] Manager briefing is actionable (specific behaviors, not vague encouragement)
- [ ] Follow-up touchpoints have realistic timing and clear ownership
- [ ] Success metrics are measurable with specific targets

## Error Handling

**Missing learning objectives:**
- "Error: learning-objectives.md not found. Cannot generate transfer plan without objectives. Run `/generate-objectives` first."

**No Apply+ level objectives:**
- "Warning: No Apply-level or higher objectives found. Transfer plans are most effective for skills-based learning. Generating a simplified version focused on knowledge retention."

**Transfer plan already exists:**
- Prompt: "transfer-plan.md already exists. Options: (1) Regenerate (overwrites), (2) Update specific sections, (3) Cancel"

## Implementation Notes

**Date retrieval:**
```bash
TZ='America/New_York' date '+%Y-%m-%d'
```

**Transfer type mapping:**
- Remember/Understand objectives → Knowledge retention aids (summary sheets, glossaries)
- Apply objectives → Near transfer (job aids, checklists, step-by-step guides)
- Analyze/Evaluate objectives → Far transfer (decision trees, frameworks, case libraries)
- Create objectives → Generative transfer (project templates, innovation prompts)

**DO NOT:**
- Generate generic "keep practicing!" advice — every recommendation must be specific
- Create job aids for Remember-level objectives (these are reference materials, not transfer tools)
- Assume the manager attended the workshop — briefing must be self-contained
- Skip follow-up touchpoints — they are the primary transfer mechanism

---

Generate transfer plans that turn workshop learning into sustained workplace behavior change. Every objective deserves a concrete path from classroom to workplace.
```

**Step 2: Verify YAML frontmatter**

Run: `head -7 commands/generate-transfer-plan.md`
Expected: Valid YAML frontmatter

**Step 3: Commit**

```bash
git add -f course-curriculum-creator/commands/generate-transfer-plan.md
git commit -m "feat(commands): add /generate-transfer-plan for post-workshop learning transfer"
```

---

## Task 2: Create the `generate-evaluation-plan` Command

**Files:**
- Create: `commands/generate-evaluation-plan.md`

**Step 1: Write the command file**

Create `commands/generate-evaluation-plan.md`:

```markdown
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
```

**Step 2: Verify YAML frontmatter**

Run: `head -7 commands/generate-evaluation-plan.md`
Expected: Valid YAML frontmatter

**Step 3: Commit**

```bash
git add -f course-curriculum-creator/commands/generate-evaluation-plan.md
git commit -m "feat(commands): add /generate-evaluation-plan for Kirkpatrick L1-L4 evaluation"
```

---

## Task 3: Add Differentiation Layer to Lesson Plan Template

**Files:**
- Modify: `commands/generate-lesson-plans.md`

**Step 1: Read current file**

Read `commands/generate-lesson-plans.md` (post-Phase 1, currently at ~370 lines).

**Step 2: Enhance the existing Differentiation section in the template**

In the per-module lesson plan template, find the existing `**Differentiation:**` block within the `#### Independent Practice` section. It currently reads:

```markdown
**Differentiation:**
- **Struggling students:** [Support strategy]
- **Advanced students:** [Extension challenge]
```

Replace it with this expanded version:

```markdown
**Differentiation Strategy:**

| Tier | Learners | Approach | Activity Modification |
|---|---|---|---|
| **Floor (all learners)** | Everyone | Core exercise with essential requirements | Complete [core task] using provided template/guide |
| **Support scaffold** | Learners needing more guidance | Additional structure, worked examples, peer pairing | Same task with: step-by-step checklist, worked example to reference, or partner work option |
| **Extension challenge** | Advanced learners finishing early | Deeper complexity, fewer constraints, mentoring role | [Extended version]: remove template, add constraint, or mentor a peer |

**Instructor Decision Guide:**
- If >30% of class is struggling: Pause, re-teach key concept, provide additional worked example
- If >30% of class finishes early: Introduce extension challenge to whole class as optional
- If mixed: Pair advanced learners with struggling learners for guided practice portion
```

**Step 3: Add differentiation guidance section**

After the existing `## Module Validation` section (near the end of the file, before the closing line), add a new section:

```markdown
## Differentiation Guidance

When generating lesson plans, design each module's practice activities with three tiers:

### Floor Activities (Required for All)
- Define the minimum successful completion that demonstrates the learning objective
- Must be achievable by ALL learners within the allotted time
- Provide sufficient scaffolding: templates, step-by-step guides, worked examples
- This is what rubric criteria assess — the core expectation

### Support Scaffolds (For Learners Who Struggle)
- Same task, with additional structure: checklists, partially completed examples, peer support
- Do NOT reduce the learning objective — reduce the barriers to achieving it
- Common scaffolds: simplified vocabulary, visual guides, partner work, extended time
- Remove scaffolds gradually as learner gains confidence

### Extension Challenges (For Advanced Learners)
- Same domain, higher complexity: remove constraints, add variables, require justification
- Or: mentoring role — advanced learners help teach concepts to peers (deepens their own understanding)
- Should be genuinely challenging, not just "do more of the same"
- Extension work is optional — never penalize for not completing it

### Instructor Decision Points
- Build decision points into each practice activity
- At the 50% mark: check class progress, decide if adjustment needed
- Signals to watch: body language, question frequency, pace of work, error patterns
- Default assumption: mixed-level audience until evidence suggests otherwise
```

**Step 4: Commit**

```bash
git add course-curriculum-creator/commands/generate-lesson-plans.md
git commit -m "feat(commands): add differentiated instruction tiers to lesson plan template"
```

---

## Task 4: Add Differentiation Validation to Quality Reviewer

**Files:**
- Modify: `agents/quality-reviewer.md`

**Step 1: Read current file**

Read `agents/quality-reviewer.md` (post-Phase 1).

**Step 2: Add differentiation check to Stage 3 validation**

In section "## 4. Stage 3 Validation: Learning Activities", find the "### Engagement and Variety" subsection. After it, add:

```markdown
### Differentiation
- Do practice activities include floor (core), support scaffold, and extension tiers?
- Are support scaffolds focused on reducing barriers (not reducing expectations)?
- Are extension challenges genuinely more complex (not just "do more")?
- Are instructor decision points built into practice activities?
```

**Step 3: Commit**

```bash
git add course-curriculum-creator/agents/quality-reviewer.md
git commit -m "feat(agents): add differentiation validation to quality-reviewer Stage 3"
```

---

## Task 5: Add Prerequisite Hook for Transfer Plan

**Files:**
- Modify: `hooks/hooks.json`

**Step 1: Read current file**

Read `hooks/hooks.json`.

**Step 2: Add advisory check for transfer plan**

Add an advisory check (same pattern as the TNA advisory) to the PreToolUse Write prompt. Insert after the TNA advisory check:

```
- If file_path ends with '04-materials/transfer-plan.md': Check that '01-planning/learning-objectives.md' exists in the same course directory. If it doesn't exist, respond with: {"decision":"block","reason":"Cannot generate transfer plan without learning objectives. Run /generate-objectives first."}
```

Note: This one is a BLOCK (not advisory) because the transfer plan is derived directly from objectives.

**Step 3: Verify JSON is valid**

Run: `python3 -c "import json; json.load(open('course-curriculum-creator/hooks/hooks.json'))"`

**Step 4: Commit**

```bash
git add course-curriculum-creator/hooks/hooks.json
git commit -m "feat(hooks): add transfer-plan prerequisite check"
```

---

## Task 6: Update Curriculum Architect Agent

**Files:**
- Modify: `agents/curriculum-architect.md`

**Step 1: Read current file**

Read `agents/curriculum-architect.md`.

**Step 2: Add Phase 9b and 9c to the autonomous workflow**

The curriculum-architect has a 10-phase workflow. Find the phase for quality validation (Phase 9) and the deliverables summary (Phase 10). Between them (or update the flow to include), add references to the new commands:

After the existing quality validation phase, add:

```markdown
### Phase 9b: Transfer Planning

Generate the transfer-of-learning plan using `/generate-transfer-plan`:
- 30/60/90-day action plans derived from Apply+ objectives
- Manager briefing for reinforcement support
- Job aids for each Apply+ objective
- Follow-up touchpoint schedule

### Phase 9c: Evaluation Planning

Generate the evaluation plan using `/generate-evaluation-plan`:
- Kirkpatrick Level 1-4 instruments
- Pre/post assessment alignment with objectives
- Level 3 behavior observation instruments
- Level 4 business metric connections (from TNA if available)
```

**Step 3: Update the deliverables summary**

In Phase 10 (deliverables), add the new outputs to the list of generated files.

**Step 4: Commit**

```bash
git add course-curriculum-creator/agents/curriculum-architect.md
git commit -m "feat(agents): add transfer and evaluation planning to curriculum-architect workflow"
```

---

## Task 7: Update README and Bump Version to 0.5.0

**Files:**
- Modify: `README.md`
- Modify: `.claude-plugin/plugin.json`

**Step 1: Update plugin.json**

Change `"version": "0.4.0"` to `"version": "0.5.0"`.

**Step 2: Update README.md**

Add to the appropriate sections:

**a) Commands table**: Add `generate-transfer-plan` and `generate-evaluation-plan` with descriptions.

**b) What's New section**: Add v0.5.0 entry:

```
### v0.5.0 - Learning Ecosystem
- New: `/generate-transfer-plan` command for post-workshop learning transfer (action plans, manager briefings, job aids)
- New: `/generate-evaluation-plan` command for Kirkpatrick L1-L4 evaluation design
- Enhanced: Differentiated instruction (floor/scaffold/extension tiers) in lesson plan template
- Enhanced: Quality reviewer validates differentiation in activities
- Enhanced: Curriculum architect includes transfer and evaluation planning
- Enhanced: Transfer plan prerequisite hook
```

**Step 3: Commit**

```bash
git add course-curriculum-creator/README.md course-curriculum-creator/.claude-plugin/plugin.json
git commit -m "docs: update README and bump version to 0.5.0 for Phase 2 features"
```

---

## Task 8: Final Integration Verification

**Step 1: Verify all new files exist**

```bash
ls -la course-curriculum-creator/commands/generate-transfer-plan.md
ls -la course-curriculum-creator/commands/generate-evaluation-plan.md
```

**Step 2: Verify JSON validity**

```bash
python3 -c "import json; json.load(open('course-curriculum-creator/hooks/hooks.json')); print('VALID')"
```

**Step 3: Verify version**

```bash
python3 -c "import json; d=json.load(open('course-curriculum-creator/.claude-plugin/plugin.json')); print(d['version'])"
```
Expected: `0.5.0`

**Step 4: Verify YAML frontmatter**

```bash
head -7 course-curriculum-creator/commands/generate-transfer-plan.md
head -7 course-curriculum-creator/commands/generate-evaluation-plan.md
```

**Step 5: Review git log**

```bash
git log --oneline -10
```

---

## Summary of Phase 2 Deliverables

| # | Deliverable | Type | Files |
|---|---|---|---|
| 1 | `/generate-transfer-plan` command | New command | `commands/generate-transfer-plan.md` |
| 2 | `/generate-evaluation-plan` command | New command | `commands/generate-evaluation-plan.md` |
| 3 | Differentiated instruction tiers | Command modification | `commands/generate-lesson-plans.md` |
| 4 | Differentiation validation | Agent modification | `agents/quality-reviewer.md` |
| 5 | Transfer plan prerequisite hook | Hook modification | `hooks/hooks.json` |
| 6 | Transfer + evaluation in architect | Agent modification | `agents/curriculum-architect.md` |
| 7 | README + version bump to 0.5.0 | Documentation | `README.md`, `plugin.json` |
