# Phase 1: Professional Foundations — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add Training Needs Assessment, Universal Design for Learning (UDL), and Pre-work/Post-work artifact types to bring the plugin to professional L&D standards.

**Architecture:** Three parallel workstreams — (1) new `assess-needs` command + TNA skill, (2) new `universal-design-for-learning` skill + modifications to existing commands and quality-reviewer agent, (3) two new artifact types added to `generate-artifacts` command. Each workstream is independent and can be built in any order. All follow existing plugin conventions: YAML frontmatter, `${CLAUDE_PLUGIN_ROOT}` references, staleness hashing, prerequisite hooks.

**Tech Stack:** Markdown command/skill/agent files with YAML frontmatter. JSON hooks. No runtime code — plugin is entirely prompt-based.

---

## Task 1: Create the `assess-needs` Command

**Files:**
- Create: `commands/assess-needs.md`

**Step 1: Write the command file**

Create `commands/assess-needs.md` following the exact frontmatter pattern from `create-course.md`:

```markdown
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

Conduct a structured training needs assessment (TNA) before course design. Determines whether training is the right intervention and documents the performance gap that the course must close.

## Why This Matters

Expert L&D practice requires diagnostic assessment before prescription. This command prevents the most expensive mistake in curriculum design: building a beautifully designed course that solves the wrong problem.

## Command Behavior

When user invokes `/assess-needs`:

1. **Gather context** through structured questions (use AskUserQuestion):
   - Who is the requesting stakeholder?
   - What business problem or opportunity triggered this request?
   - What is the current state (what people do now)?
   - What is the desired state (what people should do)?
   - How is the gap currently measured?

2. **Analyze the performance gap**:
   - Skills gap (they don't know how) → Training IS appropriate
   - Knowledge gap (they don't know what) → Training IS appropriate
   - Motivation gap (they don't want to) → Training alone is NOT sufficient
   - Environmental gap (systems/processes prevent it) → Training is NOT the solution
   - Resource gap (they lack tools/time) → Training is NOT the solution

3. **Recommend intervention type**:
   - If skills/knowledge gap: "Training is an appropriate intervention. Proceed with course design."
   - If motivation gap: "Training may help with awareness, but also requires management/incentive changes."
   - If environmental/resource gap: "Training alone will not solve this. Recommend process/tooling changes first."
   - If mixed: Document each component and recommend a blended approach.

4. **Document target population**:
   - How many people need this?
   - What is their current skill level (range)?
   - What is their learning context (voluntary vs. mandatory, on-the-job vs. classroom)?
   - What prior training have they received?
   - Are there accessibility requirements?

5. **Define success metrics**:
   - What observable behavior change indicates success?
   - How will it be measured? (Kirkpatrick levels)
   - What is the timeline for expected results?
   - What baseline data exists?

6. **Generate output file**

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `instructor_name`: Use as analyst name
- `organization`: Use in report header

If settings file doesn't exist, use sensible defaults or prompt user.

## Output Location

**If run before `/create-course`** (standalone TNA):
- Write to current directory as `training-needs-analysis-YYYY-MM-DD.md`
- The file can be referenced later when creating the course

**If run inside an existing course directory** (course directory detected by presence of `01-planning/`):
- Write to `01-planning/training-needs-analysis.md`

## File Output Format

### training-needs-analysis.md

```
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

# Training Needs Assessment

## 1. Business Context

**Requesting Stakeholder:** [Name/role]
**Business Problem:** [Description of the trigger]
**Organizational Impact:** [Why this matters to the organization]

## 2. Performance Gap Analysis

### Current State
[What people do now — observable behaviors]

### Desired State
[What people should do — observable behaviors]

### Gap Description
[The specific delta between current and desired]

### Gap Type Classification

| Gap Component | Type | Training Addressable? |
|---|---|---|
| [Component 1] | Skills / Knowledge / Motivation / Environmental / Resource | Yes / Partial / No |
| [Component 2] | ... | ... |

### Root Cause Analysis
[Why the gap exists — not just symptoms]

## 3. Intervention Recommendation

**Primary Recommendation:** [Training / Process Change / Tool Change / Blended]

**Rationale:**
[Why this intervention type based on gap analysis]

**If training is recommended:**
- Suggested format: [Workshop / E-learning / On-the-job / Mentoring]
- Suggested duration: [Based on gap scope]
- Priority level: [High / Medium / Low]

**If non-training interventions needed:**
- [Specific process/tool/management recommendations]
- [How these complement or replace training]

## 4. Target Population

**Population Size:** [Number]
**Current Skill Range:** [Novice to Expert distribution]
**Learning Context:** [Voluntary/Mandatory, On-site/Remote, During work/After hours]
**Prior Training:** [Relevant previous training received]
**Accessibility Requirements:** [Known accommodations needed]
**Language/Cultural Considerations:** [If applicable]

## 5. Success Metrics

| Metric | Baseline | Target | Measurement Method | Timeline |
|---|---|---|---|---|
| [Behavior/outcome 1] | [Current] | [Goal] | [How measured] | [When] |
| [Behavior/outcome 2] | ... | ... | ... | ... |

**Kirkpatrick Evaluation Levels Planned:**
- [ ] Level 1 (Reaction): Post-training survey
- [ ] Level 2 (Learning): Pre/post assessment
- [ ] Level 3 (Behavior): [Observation method + timeline]
- [ ] Level 4 (Results): [Business metric + timeline]

## 6. Constraints and Considerations

**Budget:** [If known]
**Timeline:** [When training must be delivered]
**Logistics:** [Venue, technology, scheduling constraints]
**Stakeholder Expectations:** [What stakeholders expect to see]

## 7. Next Steps

1. [If training appropriate] Create course project: `/create-course "[Title]"`
2. [If blended approach] Document non-training interventions separately
3. [If training not appropriate] Present alternative recommendations to stakeholder
```

## Post-Generation Actions

After generating the TNA:

1. **Summarize recommendation**: "Based on the needs assessment, [training is/is not] the appropriate intervention because [reason]."

2. **If training recommended**: "Ready to proceed with course design. Run `/create-course` to initialize the project. The TNA will inform your course positioning and objectives."

3. **If training not recommended**: "Recommend discussing alternative interventions with stakeholders before proceeding with course design."

## Validation Checks

Before finalizing, validate:
- [ ] Gap type is classified (not just described)
- [ ] Recommendation logically follows from gap analysis
- [ ] Success metrics are measurable (not vague)
- [ ] Target population is characterized enough to inform design
- [ ] At least one Kirkpatrick level beyond L1 is planned

## Error Handling

**No context provided:**
- Guide user through questions interactively using AskUserQuestion
- Minimum viable TNA requires: business problem, current state, desired state

**User wants to skip TNA:**
- Acknowledge: "Proceeding without needs assessment. You can always run `/assess-needs` later."
- Do NOT block course creation (the hook uses --skip-tna)

## Implementation Notes

**Date retrieval:**
Always use bash to get current date:
```bash
TZ='America/New_York' date '+%Y-%m-%d'
```

---

Ensure every training intervention starts with clear diagnostic reasoning. The TNA prevents the most expensive L&D mistake: solving the wrong problem with the right pedagogy.
```

**Step 2: Verify the file renders correctly**

Run: `head -5 commands/assess-needs.md`
Expected: YAML frontmatter starting with `---`

**Step 3: Commit**

```bash
git add -f course-curriculum-creator/commands/assess-needs.md
git commit -m "feat(commands): add /assess-needs for training needs assessment"
```

---

## Task 2: Add TNA Hook to Enforce Prerequisites

**Files:**
- Modify: `hooks/hooks.json`

**Step 1: Read current hooks file**

Read `hooks/hooks.json` to get current content.

**Step 2: Add TNA prerequisite check to the existing prompt**

Add a new check to the existing PreToolUse Write hook prompt. Insert this BEFORE the existing checks:

```
- If file_path ends with '01-planning/course-positioning.md' AND a course directory already exists (the parent directory contains 01-planning/, 02-design/, etc.): Check if 'training-needs-analysis.md' exists in either '01-planning/' subdirectory or the parent of the course directory. This is an ADVISORY check only — if the TNA doesn't exist, respond with: {"decision":"approve"} but include a note in the reason: "Note: No training needs assessment found. Consider running /assess-needs to validate that training is the right intervention." Do NOT block — only advise.
```

**IMPORTANT:** This is advisory, not blocking. The design doc recommends `--skip-tna` support, but the simplest approach that maintains the plugin's usability is a soft warning. The TNA is a professional best practice, not a hard dependency.

**Step 3: Verify JSON is valid**

Run: `python3 -c "import json; json.load(open('course-curriculum-creator/hooks/hooks.json'))"`
Expected: No output (valid JSON)

**Step 4: Commit**

```bash
git add course-curriculum-creator/hooks/hooks.json
git commit -m "feat(hooks): add advisory TNA check to PreToolUse hook"
```

---

## Task 3: Create Universal Design for Learning (UDL) Skill

**Files:**
- Create: `skills/universal-design-for-learning/SKILL.md`

**Step 1: Write the UDL skill file**

Create `skills/universal-design-for-learning/SKILL.md` following the exact frontmatter pattern from `backward-design-methodology/SKILL.md`:

```markdown
---
name: universal-design-for-learning
description: This skill should be used when the user asks to "design accessible curriculum", "apply UDL", "accommodate diverse learners", "create inclusive workshops", "ensure accessibility", or references Universal Design for Learning. Also applies when generating lesson plans, outlines, or activities to ensure multiple means of representation, engagement, and expression. Provides practical guidance for creating inclusive, accessible learning experiences in 1-2 day workshop contexts.
version: 0.1.0
---

# Universal Design for Learning (UDL) for Workshop Design

## Overview

Universal Design for Learning (UDL) is a framework for designing learning experiences that are accessible and effective for ALL learners from the start — not retrofitted for "special needs" after the fact. UDL is based on neuroscience research showing that learners vary in how they perceive information, engage with content, and express what they know.

For intensive workshops, UDL prevents a common failure mode: designing for the "average" learner and losing participants at both ends. When you design for the margins (learners with the most barriers), you improve the experience for everyone.

## The Three UDL Principles

### Principle 1: Multiple Means of Representation (The "What" of Learning)

Present information in more than one format so all learners can perceive and comprehend it.

**Workshop Application:**

| Instead of Only... | Also Include... | Why |
|---|---|---|
| Verbal lecture | Visual slides, written handout | Some learners process visual information better |
| Text-heavy slides | Diagrams, flowcharts, concept maps | Reduces cognitive load for complex relationships |
| Live demo only | Step-by-step written guide | Learners can reference at their own pace |
| Single example | Multiple examples from different domains | Helps learners who don't relate to one context |
| English-only jargon | Glossary of key terms, plain language alternatives | Supports non-native speakers and novices |

**Minimum Standard for Workshops:**
Every module should present key concepts through at least 2 different representation modes (e.g., verbal + visual, demo + written guide, diagram + explanation).

**Checklist per Module:**
- [ ] Key concepts available in both verbal and visual/written form
- [ ] Complex processes shown as diagrams or flowcharts (not only described verbally)
- [ ] Technical terms defined when first introduced
- [ ] Examples drawn from multiple contexts when possible
- [ ] Handout or reference sheet available for self-paced review

### Principle 2: Multiple Means of Engagement (The "Why" of Learning)

Provide different ways to motivate learners and sustain their effort.

**Workshop Application:**

| Strategy | Implementation | Addresses |
|---|---|---|
| Choice in practice activities | Offer 2-3 exercise options at same cognitive level | Autonomy, relevance |
| Relevance connections | Ask learners to connect concepts to their own work context | Motivation, transfer |
| Collaborative AND individual options | Mix pair work, small group, and solo activities | Social preference variation |
| Low-stakes practice before assessment | Ungraded exercises before evaluated performance | Psychological safety |
| Progress visibility | Checkpoint summaries, skills-applied tracker | Self-regulation |
| Varied challenge levels | Core exercise + extension for advanced learners | Appropriate challenge |

**Minimum Standard for Workshops:**
Each half-day should include at least one activity where learners have choice in how they engage (topic selection, partner vs. solo, which scenario to work on).

**Checklist per Module:**
- [ ] At least one activity offers learner choice
- [ ] Activities connect to real-world contexts learners recognize
- [ ] Mix of individual, pair, and group work across the day
- [ ] Low-stakes practice precedes any evaluated performance
- [ ] Learners can see their progress (checkpoint, summary, or self-check)

### Principle 3: Multiple Means of Action & Expression (The "How" of Learning)

Allow learners to demonstrate what they know in different ways.

**Workshop Application:**

| Instead of Only... | Also Accept... | Why |
|---|---|---|
| Written response | Verbal explanation, diagram, demo | Motor/writing differences, language barriers |
| Timed exercise | Flexible pacing with core + extension | Processing speed variation |
| Solo presentation | Written submission, pair presentation, group work product | Anxiety, introversion |
| Single correct format | Multiple valid approaches to same problem | Creativity, diverse problem-solving styles |
| Handwriting on worksheets | Digital input option, verbal response | Physical accessibility |

**Minimum Standard for Workshops:**
At least one major assessment or practice activity per day should offer learners a choice in how they demonstrate their learning.

**Checklist per Module:**
- [ ] Assessments allow at least 2 response formats where feasible
- [ ] Timed activities have guidance for what to prioritize if time runs short
- [ ] Physical activities have seated alternatives
- [ ] Technology-dependent activities have non-tech fallbacks
- [ ] Learners are not penalized for format choice (rubrics assess content, not medium)

## Accommodation Planning

### Pre-Workshop Accommodation Process

When designing the course (during `/create-course` or `/generate-lesson-plans`):

1. **Include accommodation prompt in registration/enrollment materials**
   - "Do you have any accessibility requirements or learning accommodations we should plan for?"
   - Common categories: visual, auditory, motor/physical, cognitive/processing, language

2. **Build flexibility into the design** (proactive, not reactive)
   - All materials available digitally AND in print
   - Microphone for instructor in groups larger than 15
   - Seating arrangement allows wheelchair access
   - Font size minimum 14pt on slides, 12pt on handouts
   - Color is never the ONLY way to convey information (use labels + color)

3. **Plan for common accommodations without requiring disclosure**
   - Extended time built into schedule (buffer time serves everyone)
   - Materials available in advance for pre-reading
   - Breaks every 45-60 minutes (standard for intensive workshops)
   - Multiple input methods for exercises

### Common Workshop Accommodations

| Need | Proactive Design (Built In) | Reactive Accommodation (If Requested) |
|---|---|---|
| Visual impairment | Large fonts, high contrast, verbal descriptions of visuals | Screen reader compatible materials, braille |
| Hearing impairment | Written instructions for all verbal tasks, visual cues for transitions | Sign language interpreter, captioning |
| Motor/physical | Digital alternatives to handwriting, flexible seating | Adaptive equipment, scribe |
| Processing speed | Buffer time, written instructions to reference | Extended time, simplified materials |
| Attention/focus | Frequent breaks, varied activities, movement opportunities | Preferential seating, fidget tools |
| Language barriers | Plain language, glossary, visual aids | Translated materials, bilingual support |
| Anxiety/introversion | Low-stakes practice, pair work before group, opt-in participation | Private assessment option, written alternatives to verbal |

## UDL Integration Points in the Curriculum Workflow

### During `/generate-outline`
- Check each module for representation variety (not all lecture, not all text)
- Verify activity types rotate (individual → pair → group → individual)
- Confirm breaks are scheduled appropriately (every 45-60 min for intensive workshops)
- Ensure transition times are included (3-5 min between activities)

### During `/generate-lesson-plans`
- Each module's activities should engage at least 2 UDL principles
- Materials list should include both digital and physical options
- Facilitation notes should include accommodation reminders
- Exercise instructions should specify multiple valid response formats

### During `/generate-artifacts --type handout`
- Use clear, readable formatting (headers, whitespace, consistent structure)
- Include visual organizers (tables, diagrams) alongside text
- Provide structured workspace (not just blank space)
- Include reference sections for key terms and frameworks

### During `/generate-rubrics`
- Assess CONTENT and SKILL, not format or medium
- Rubric criteria should not penalize for response format choices
- Include "demonstrates understanding through..." (not "writes a paragraph about...")

### During `/review-curriculum` (Quality Reviewer)
- Add UDL validation dimension:
  - Representation: Does each module use 2+ representation modes?
  - Engagement: Does each half-day include learner choice?
  - Expression: Do assessments allow flexible response formats?
  - Accommodation: Are proactive accommodations built into the design?

## Common UDL Pitfalls in Workshop Design

| Pitfall | Problem | Fix |
|---|---|---|
| "We'll accommodate if someone asks" | Reactive = too late for many learners | Build flexibility in from the start |
| All activities require handwriting | Excludes motor impairments, slow writers | Offer digital input option |
| Timed exercises with no guidance | Punishes processing speed differences | State priorities: "If short on time, focus on X" |
| Only verbal instructions | Learners can't reference later | Provide written instructions always |
| Color-coded without labels | Excludes color-blind learners (8% of males) | Always use labels + color together |
| "Everyone present to the group" | Penalizes introverts and anxious learners | Offer written or pair alternatives |
| Single example domain | Alienates learners outside that domain | Use 2-3 diverse examples |
| No pre-reading materials | Disadvantages slow processors | Share materials 48h before |

## UDL Validation Checklist

Use this checklist when reviewing any curriculum component:

### Representation (The "What")
- [ ] Key concepts presented in 2+ formats per module
- [ ] Visual aids supplement verbal/text content
- [ ] Technical vocabulary defined at first use
- [ ] Complex processes have visual representations (diagrams, flowcharts)
- [ ] Examples drawn from multiple contexts

### Engagement (The "Why")
- [ ] Learner choice available in at least 1 activity per half-day
- [ ] Activities connect to real-world application
- [ ] Mix of individual, pair, and group work
- [ ] Low-stakes practice before assessed performance
- [ ] Progress checkpoints visible to learners

### Action & Expression (The "How")
- [ ] 2+ response formats accepted for major assessments
- [ ] Timed activities include prioritization guidance
- [ ] Physical activities have alternatives
- [ ] Technology activities have fallbacks
- [ ] Rubrics assess content, not medium

### Proactive Accommodation
- [ ] Materials available digitally and in print
- [ ] Font sizes meet minimum (14pt slides, 12pt handouts)
- [ ] Color never sole information carrier
- [ ] Breaks every 45-60 minutes
- [ ] Buffer time built into schedule
- [ ] Pre-reading materials available 48h before
```

**Step 2: Verify file structure**

Run: `head -5 skills/universal-design-for-learning/SKILL.md`
Expected: YAML frontmatter starting with `---`

**Step 3: Commit**

```bash
git add -f course-curriculum-creator/skills/universal-design-for-learning/SKILL.md
git commit -m "feat(skills): add universal-design-for-learning (UDL) skill"
```

---

## Task 4: Modify `generate-outline` to Include UDL Checkpoints

**Files:**
- Modify: `commands/generate-outline.md`

**Step 1: Read current file**

Read `commands/generate-outline.md` fully.

**Step 2: Add UDL skill loading**

In the section where skills are loaded (look for existing skill loading instructions like `Load blooms-taxonomy skill`), add:

```
Load universal-design-for-learning skill for accessibility and inclusive design guidance
```

**Step 3: Add UDL validation to post-generation checks**

Find the validation/post-generation section. Add a new subsection:

```markdown
### UDL Validation (Post-Generation)

After generating the outline, validate each module against UDL minimums:

- **Representation**: Does each module use at least 2 representation modes? (e.g., not all lecture, not all reading)
  - Flag modules that rely on a single modality
- **Engagement**: Does each half-day include at least one activity with learner choice?
  - Flag half-days without choice opportunities
- **Activity variety**: Do activity types rotate across the day? (individual → pair → group → individual)
  - Flag sequences of 3+ same-format activities
- **Breaks**: Are breaks scheduled every 45-60 minutes during instruction?
  - Flag gaps longer than 60 minutes without breaks

If any check fails, add a note to the outline: "⚠ UDL Note: [specific recommendation]"
```

**Step 4: Commit**

```bash
git add course-curriculum-creator/commands/generate-outline.md
git commit -m "feat(commands): add UDL skill loading and validation to generate-outline"
```

---

## Task 5: Modify `generate-lesson-plans` to Include UDL Considerations

**Files:**
- Modify: `commands/generate-lesson-plans.md`

**Step 1: Read current file**

Read `commands/generate-lesson-plans.md` fully.

**Step 2: Add UDL skill loading**

In the skill loading section, add:

```
Load universal-design-for-learning skill for accessibility and inclusive design
```

**Step 3: Add UDL section to the per-module lesson plan template**

Find the lesson plan template structure (the per-module format). Add after the existing "Materials Needed" or "Debrief" section:

```markdown
**Accessibility & UDL Notes:**
- Representation modes used: [list — e.g., verbal instruction, visual slides, written handout]
- Engagement options: [any learner choice in this module]
- Expression alternatives: [how learners can demonstrate learning — e.g., written, verbal, diagram]
- Accommodation reminders: [any specific notes — e.g., "Provide written instructions for Exercise 2.1 in addition to verbal walkthrough"]
```

**Step 4: Commit**

```bash
git add course-curriculum-creator/commands/generate-lesson-plans.md
git commit -m "feat(commands): add UDL considerations to generate-lesson-plans template"
```

---

## Task 6: Modify `generate-rubrics` to Include UDL-Aligned Criteria Guidance

**Files:**
- Modify: `commands/generate-rubrics.md`

**Step 1: Read current file**

Read `commands/generate-rubrics.md` fully.

**Step 2: Add UDL principle to rubric criteria guidance**

Find the section that describes how rubric criteria should be written. Add this guidance:

```markdown
### UDL-Aligned Criteria

When writing rubric criteria, follow UDL Principle 3 (Multiple Means of Action & Expression):

- **Assess content and skill, not format**: Use "Demonstrates understanding of..." not "Writes a paragraph about..."
- **Allow multiple response formats**: Unless format IS the skill being assessed (e.g., "write a SQL query"), accept verbal, written, diagrammatic, or demonstrated responses
- **Criteria should be format-neutral**: "Identifies all five forces with supporting evidence" works whether the learner writes, diagrams, or presents verbally
```

**Step 3: Commit**

```bash
git add course-curriculum-creator/commands/generate-rubrics.md
git commit -m "feat(commands): add UDL-aligned criteria guidance to generate-rubrics"
```

---

## Task 7: Add UDL Validation Dimension to Quality Reviewer Agent

**Files:**
- Modify: `agents/quality-reviewer.md`

**Step 1: Read current file**

Read `agents/quality-reviewer.md` fully (already read above, but re-read for exact insertion points).

**Step 2: Add UDL skill to the skill loading section**

In the "Curriculum Discovery and Loading" section (section 1), after the existing skill loads, add:

```
- `universal-design-for-learning` skill (provides UDL framework and accessibility validation guidance)
```

**Step 3: Add UDL validation stage**

After the existing "5. Overall Coherence Check" section, add a new section:

```markdown
## 5b. UDL & Accessibility Validation

**Check curriculum for Universal Design for Learning compliance:**

### Representation (The "What")
- Does each module present key concepts in 2+ formats?
- Are visual aids used alongside verbal/text content?
- Are technical terms defined at first use?
- Do complex processes have visual representations?

### Engagement (The "Why")
- Does each half-day include at least one activity with learner choice?
- Is there a mix of individual, pair, and group work across the day?
- Do low-stakes practice activities precede assessed performance?

### Action & Expression (The "How")
- Do assessments allow 2+ response formats for major tasks?
- Do timed activities include prioritization guidance?
- Do rubrics assess content/skill rather than response format?

### Proactive Accommodation
- Are materials specified as available in digital and print formats?
- Do slides meet minimum font size (14pt)?
- Is color never the sole information carrier?
- Are breaks scheduled every 45-60 minutes?
- Is buffer time built into the schedule?

**Document findings:**
- Rate each UDL principle: STRONG / ADEQUATE / NEEDS IMPROVEMENT
- Flag specific modules that lack representation variety
- Flag assessments that penalize response format
- Note accommodation gaps
```

**Step 4: Add UDL to the report template**

In the "6. Generate Validation Report" section, add after "Overall Coherence Analysis":

```markdown
### UDL & Accessibility Validation
**Status**: PASS / FAIL

- Representation analysis (per-module modality count)
- Engagement analysis (choice opportunities per half-day)
- Expression analysis (assessment format flexibility)
- Accommodation readiness
- Specific issues found with recommendations
```

**Step 5: Update the PASS criteria**

In the "Quality Standards" section, add:

```
- **UDL & Accessibility**: Each module uses 2+ representation modes, each half-day includes learner choice, assessments accept multiple formats, proactive accommodations designed in
```

**Step 6: Commit**

```bash
git add course-curriculum-creator/agents/quality-reviewer.md
git commit -m "feat(agents): add UDL validation dimension to quality-reviewer"
```

---

## Task 8: Add Pre-work and Post-work Artifact Types to `generate-artifacts`

**Files:**
- Modify: `commands/generate-artifacts.md`

**Step 1: Read current file**

Read `commands/generate-artifacts.md` (already read above, but re-read for exact insertion points).

**Step 2: Update the frontmatter argument-hint**

Change the `argument-hint` line from:
```
argument-hint: "--type [handout|instructor-guide|slides|pre-assessment|post-assessment|evaluation|all]"
```
To:
```
argument-hint: "--type [handout|instructor-guide|slides|pre-assessment|post-assessment|evaluation|pre-work|post-work|all]"
```

**Step 3: Add pre-work artifact type**

After the `### --type evaluation` section and before `### --type all`, add:

```markdown
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
```

**Step 4: Update the `--type all` description**

Change:
```
### --type all
Generate all artifact types above
```
To:
```
### --type all
Generate all artifact types above (handout, instructor-guide, slides, pre-assessment, post-assessment, evaluation, pre-work, post-work)
```

**Step 5: Add pre-work template structure**

After the existing "Instructor Guide Structure" section (after the instructor guide code block), add:

```markdown
## Pre-Work Structure

```
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

```
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
```

**Step 6: Commit**

```bash
git add course-curriculum-creator/commands/generate-artifacts.md
git commit -m "feat(commands): add pre-work and post-work artifact types to generate-artifacts"
```

---

## Task 9: Register New Skill in Plugin Manifest (if needed) and Update README

**Files:**
- Modify: `README.md`
- Check: `.claude-plugin/plugin.json`

**Step 1: Check if plugin.json needs skill registration**

Read `.claude-plugin/plugin.json`. Claude Code plugins auto-discover skills from the `skills/` directory, so the manifest may not need changes. Verify by checking if existing skills are explicitly listed.

If skills are NOT explicitly listed (auto-discovery): No change needed.
If skills ARE explicitly listed: Add `universal-design-for-learning` to the list.

**Step 2: Update README.md**

Read `README.md` fully. Add the new components to the appropriate sections:

1. **Commands section**: Add `assess-needs` with description
2. **Skills section**: Add `universal-design-for-learning` with description
3. **Artifact types section**: Add `pre-work` and `post-work` to the generate-artifacts listing
4. **Version**: Bump to `0.4.0`

Match the existing formatting exactly (heading levels, bullet styles, table format if used).

**Step 3: Update plugin.json version**

Change `"version": "0.3.0"` to `"version": "0.4.0"` in `.claude-plugin/plugin.json`.

**Step 4: Commit**

```bash
git add course-curriculum-creator/README.md course-curriculum-creator/.claude-plugin/plugin.json
git commit -m "docs: update README and bump version to 0.4.0 for Phase 1 features"
```

---

## Task 10: Add UDL Example File

**Files:**
- Create: `skills/universal-design-for-learning/examples/example-udl-1day-workshop.md`

**Step 1: Write the example file**

Create a concrete example showing UDL applied to a 1-day workshop. Model it after `skills/backward-design-methodology/examples/example-backward-design-1day.md` in structure.

The example should show:
- A sample 1-day workshop module schedule
- Each module annotated with UDL principles applied
- Representation modes per module (visual + verbal + written)
- Engagement choices offered per half-day
- Expression alternatives for the main assessment
- Built-in accommodations (break schedule, font sizes, digital + print materials)
- Before/after comparison: "Without UDL" vs. "With UDL" for one module

Keep it practical and concise (not theoretical). Show what changes in the actual lesson plan when UDL is applied.

**Step 2: Commit**

```bash
git add -f course-curriculum-creator/skills/universal-design-for-learning/examples/example-udl-1day-workshop.md
git commit -m "docs(skills): add UDL worked example for 1-day workshop"
```

---

## Task 11: Final Integration Verification

**Step 1: Verify all files exist**

Run:
```bash
ls -la course-curriculum-creator/commands/assess-needs.md
ls -la course-curriculum-creator/skills/universal-design-for-learning/SKILL.md
ls -la course-curriculum-creator/skills/universal-design-for-learning/examples/example-udl-1day-workshop.md
```
Expected: All three files exist

**Step 2: Verify hooks JSON is valid**

Run: `python3 -c "import json; json.load(open('course-curriculum-creator/hooks/hooks.json'))"`
Expected: No output (valid JSON)

**Step 3: Verify YAML frontmatter on all new/modified files**

Run:
```bash
head -6 course-curriculum-creator/commands/assess-needs.md
head -6 course-curriculum-creator/skills/universal-design-for-learning/SKILL.md
```
Expected: Both start with `---` and have proper YAML fields

**Step 4: Verify plugin.json version**

Run: `python3 -c "import json; d=json.load(open('course-curriculum-creator/.claude-plugin/plugin.json')); print(d['version'])"`
Expected: `0.4.0`

**Step 5: Review git log for all Phase 1 commits**

Run: `git log --oneline -12`
Expected: All Phase 1 commits visible in chronological order

**Step 6: Final commit summary**

No additional commit needed — this is verification only.

---

## Summary of Phase 1 Deliverables

| # | Deliverable | Type | Files |
|---|---|---|---|
| 1 | `/assess-needs` command | New command | `commands/assess-needs.md` |
| 2 | TNA advisory hook | Hook modification | `hooks/hooks.json` |
| 3 | UDL skill | New skill | `skills/universal-design-for-learning/SKILL.md` |
| 4 | UDL in outline generation | Command modification | `commands/generate-outline.md` |
| 5 | UDL in lesson plan generation | Command modification | `commands/generate-lesson-plans.md` |
| 6 | UDL in rubric generation | Command modification | `commands/generate-rubrics.md` |
| 7 | UDL validation in quality reviewer | Agent modification | `agents/quality-reviewer.md` |
| 8 | Pre-work & post-work artifacts | Command modification | `commands/generate-artifacts.md` |
| 9 | README + version bump | Documentation | `README.md`, `.claude-plugin/plugin.json` |
| 10 | UDL worked example | New example | `skills/universal-design-for-learning/examples/example-udl-1day-workshop.md` |
