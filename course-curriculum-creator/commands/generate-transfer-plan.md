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
