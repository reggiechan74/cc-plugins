# Course Curriculum Creator — Enhancement Design

**Date:** 2026-03-15
**Scope:** 10 enhancements across 3 new commands, 4 new reference files, and 3 modifications to existing files
**Approach:** Additive only — no restructuring of existing files or patterns

---

## Overview

These enhancements address gaps identified in an expert instructional design review. They add learner analysis, pre-work design, spaced practice, formative assessment guidance, accessibility specifications, affective domain objectives, co-teaching support, cultural adaptation, content curation, and series transition design.

All new files follow existing plugin conventions: YAML frontmatter, staleness checks via md5 hashes, settings integration from `.claude/course-curriculum-creator.local.md`, and AskUserQuestion-driven interactive workflows.

---

## Part 1: New Commands

### 1.1 `/generate-learner-profile` (Stage 0 — Analysis)

**File:** `commands/0-analysis/generate-learner-profile.md`

**Frontmatter:**
```yaml
name: generate-learner-profile
description: Generate a learner profile analyzing audience prior knowledge, motivational drivers, learning constraints, transfer environment, and resistance points
argument-hint: "[--from-tna]"
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Edit
```

**Behavior:**
1. Read `01-planning/course-positioning.md` (if exists) for audience context
2. Read `01-planning/training-needs-analysis.md` (if exists or `--from-tna` flag) for gap type and population data — pre-populate answers where TNA already has the data
3. Use AskUserQuestion to gather 5 dimensions interactively:
   - **Prior knowledge inventory:** What participants already know. Ask for 3-5 skills/concepts they can already do, and 3-5 they cannot. Map to prerequisites.
   - **Motivational drivers:** Why attending — voluntary vs. mandatory, career advancement vs. compliance, intrinsic curiosity vs. external requirement. Ask: "Why are participants taking this course? (a) Required by organization, (b) Self-selected for career growth, (c) Mixed/unknown, (d) Other"
   - **Learning preferences & constraints:** Team sizes, time zones, language proficiency, tech proficiency, attention span expectations. Ask: "What constraints should we design around? (tech access, language, disabilities, scheduling)"
   - **Transfer environment:** Will their workplace support applying new skills? Manager awareness? Tool access? Ask: "After the workshop, what support will participants have? (a) Manager actively reinforcing, (b) Manager aware but hands-off, (c) No manager involvement, (d) Unknown"
   - **Resistance points:** Anticipated objections, prior negative training experiences, competing priorities. Ask: "What resistance or skepticism do you anticipate?"
4. Generate "Design Implications" section — map each finding to a concrete curriculum decision:
   - High tech anxiety → Module 0 tech orientation, step-by-step screenshots
   - Mandatory attendance → Extra engagement hooks, immediate relevance connections
   - Low manager support → Stronger self-directed transfer plan, peer accountability groups
   - Mixed skill levels → Wider differentiation tiers in practice activities
5. Write to `01-planning/learner-profile.md`

**Output format:**
```markdown
---
title: Learner Profile - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
lastUpdated: YYYY-MM-DD
sourceFiles:
  course-positioning: "01-planning/course-positioning.md"
sourceHashes:
  course-positioning: "[md5-first-8]"
---

# Learner Profile

## [Course Title]

**Purpose:** Inform curriculum differentiation, example selection, and transfer planning based on audience analysis.

---

## 1. Prior Knowledge Inventory

### What Participants Can Already Do
| Skill/Concept | Confidence Level | Evidence |
|---|---|---|
| [Skill 1] | [High/Medium/Low] | [How we know] |

### What Participants Cannot Yet Do
| Skill/Concept | Gap Severity | Implication |
|---|---|---|
| [Skill 1] | [Critical/Moderate/Minor] | [Prerequisite? Pre-work? Module focus?] |

### Prerequisite Mapping
[Map prior knowledge to course prerequisites — what must be true before Day 1]

---

## 2. Motivational Drivers

| Factor | Finding | Design Response |
|---|---|---|
| Attendance type | [Voluntary/Mandatory/Mixed] | [Engagement strategy] |
| Primary motivation | [Career/Compliance/Curiosity/Other] | [Relevance framing] |
| Expected ROI | [What participants hope to gain] | [Value prop emphasis] |

---

## 3. Learning Preferences & Constraints

| Constraint | Details | Accommodation |
|---|---|---|
| Technology proficiency | [Level] | [Tech orientation needed?] |
| Language considerations | [Primary languages] | [Glossary, pacing, visual aids] |
| Accessibility needs | [Known or anticipated] | [Specific UDL measures] |
| Schedule constraints | [Time zones, availability] | [Session timing] |
| Group size | [Expected N] | [Activity format implications] |

---

## 4. Transfer Environment

| Factor | Assessment | Risk Level |
|---|---|---|
| Manager support | [Active/Aware/None/Unknown] | [High/Medium/Low] |
| Tool/resource access | [Available/Partial/None] | [High/Medium/Low] |
| Competing priorities | [Description] | [High/Medium/Low] |
| Organizational culture | [Supports learning?] | [High/Medium/Low] |

**Transfer risk summary:** [Overall assessment of how likely participants are to apply learning post-workshop]

---

## 5. Resistance Points

| Anticipated Resistance | Source | Mitigation Strategy |
|---|---|---|
| [Resistance 1] | [Why they feel this way] | [How to address in curriculum] |

---

## 6. Design Implications

**Priority adjustments based on this profile:**

| Finding | Curriculum Impact | Action |
|---|---|---|
| [Finding 1] | [What to change] | [Specific file/command affected] |
| [Finding 2] | [What to change] | [Specific file/command affected] |

**Differentiation guidance:**
- Floor tier should assume: [baseline capability]
- Extension tier should challenge: [stretch capability]
- Scaffolding emphasis: [where extra support is needed]
```

**Integration points:**
- `generate-lesson-plans` reads learner profile for differentiation tier calibration and example domain selection
- `generate-transfer-plan` reads transfer environment section to calibrate manager briefing depth and self-directed vs. supported action plans
- `generate-pre-work` reads prior knowledge inventory to determine pre-work depth
- `quality-reviewer` agent checks learner profile exists and flags if differentiation tiers don't match profile findings
- `curriculum-architect` agent adds learner profile generation as Phase 3.5 (after course initialization, before objectives)

**Error handling:**
- No course directory: save as `learner-profile-YYYY-MM-DD.md` in current directory (same pattern as standalone TNA)
- Course positioning missing: proceed without pre-population, gather all data interactively
- User skips sections: mark as "[Not assessed — skipped by user]", still generate document

---

### 1.2 `/generate-pre-work` (Stage 3 — Learning Plan)

**File:** `commands/3-learning-plan/generate-pre-work.md`

**Frontmatter:**
```yaml
name: generate-pre-work
description: Design pre-workshop micro-learning units to cover prerequisites and free Day 1 for Apply+ activities
argument-hint: "[--format full|micro-only|emails-only]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Skill
```

**Behavior:**
1. Load `blooms-taxonomy` skill for cognitive level identification
2. Read `01-planning/learning-objectives.md` — identify:
   - Remember-level objectives → candidates for full pre-work coverage
   - Understand-level objectives → candidates for introduction/preview in pre-work
   - Apply+ objectives → extract implied prerequisites not covered by explicit objectives
3. Read `01-planning/learner-profile.md` (if exists) — calibrate:
   - High prior knowledge → shorter pre-work, quiz-only fast track
   - Low prior knowledge → fuller explanations, more examples
   - Tech constraints → text-based pre-work over video
4. Design micro-learning units:
   - Maximum 3 units, maximum 30 minutes total completion time
   - Each unit: 10-15 minutes, single concept focus, one self-check question at end
   - Two paths per unit:
     - **Fast track:** Already familiar — read 2-sentence summary, take self-check quiz, done (2-3 min)
     - **Full path:** Concept explanation + 1-2 examples + self-check quiz (10-15 min)
   - Units ordered by dependency (if concept B requires concept A, unit A comes first)
5. Generate readiness self-assessment: 5-8 questions matching prerequisites, with answer key and "if you got <60%, complete the full path for units X and Y"
6. Generate reminder email templates:
   - T-7 days: Welcome + pre-work instructions + estimated time + link to materials
   - T-2 days: Reminder + "complete before [date]" + quick link to self-assessment
7. Write to `04-materials/pre-work.md`
8. Staleness check on source objectives

**Format options:**
- `--format full` (default): All components — micro-learning units, self-assessment, email templates
- `--format micro-only`: Just the micro-learning units
- `--format emails-only`: Just the email templates (for when pre-work content already exists)

**Output format:**
```markdown
---
title: Pre-Work Materials - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
courseVersion: [match]
lastUpdated: YYYY-MM-DD
totalEstimatedTime: "[N] minutes (fast track: [M] minutes)"
sourceFiles:
  learning-objectives: "01-planning/learning-objectives.md"
  learner-profile: "01-planning/learner-profile.md"
sourceHashes:
  learning-objectives: "[md5-first-8]"
  learner-profile: "[md5-first-8]"
---

# Pre-Work Materials

## [Course Title]

**Purpose:** Prepare participants with foundational knowledge before the workshop, freeing Day 1 for hands-on application.

**Total Time:** [N] minutes (full path) | [M] minutes (fast track)

**Instructions for Participants:**
Complete these materials before [workshop date]. If you're already familiar with a topic, use the Fast Track option to verify your knowledge quickly.

---

## Unit 1: [Concept Title]

**Prerequisite for:** Module [N] — [Module Title]
**Estimated Time:** [N] min (full) | [M] min (fast track)

### Fast Track
[2-3 sentence summary of the concept]

**Quick Check:** [Single question to verify understanding]

If you answered correctly, skip to Unit 2. If not, complete the Full Path below.

### Full Path

[Concept explanation — clear, concise, with concrete example]

**Example 1:** [Domain-relevant example]

**Example 2:** [Different context example for transfer]

**Self-Check:** [Question matching the prerequisite level]
- Answer: [With brief explanation]

---

[Repeat for each unit]

---

## Readiness Self-Assessment

**Instructions:** Answer these questions to verify you're ready for the workshop. You should be able to answer at least 6 of 8 correctly.

1. [Question targeting prerequisite concept 1]
2. [Question targeting prerequisite concept 2]
...

### Answer Key
[Answers with brief explanations]

### Score Interpretation
- 8/8 or 7/8: You're well prepared. The workshop will build on these foundations.
- 5/8 or 6/8: Review the units for questions you missed.
- Below 5/8: Complete all pre-work units in full path mode before attending.

---

## Email Templates

### T-7 Days: Welcome & Pre-Work Instructions

**Subject:** Prepare for [Course Title] — [Date]

[Email body with welcome, pre-work link, estimated time, contact for questions]

### T-2 Days: Reminder

**Subject:** Reminder: Complete pre-work for [Course Title] — [Date]

[Email body with reminder, direct link to self-assessment, support contact]
```

**Validation checks:**
- Total pre-work time does not exceed 30 minutes (warn if it does — completion rates drop sharply)
- Every pre-work unit maps to a specific objective or prerequisite
- Self-assessment questions match prerequisite concepts, not workshop content
- Fast track path exists for every unit (don't force experienced participants through full content)

**Integration points:**
- `generate-lesson-plans` checks if `04-materials/pre-work.md` exists:
  - If yes, adjust Day 1 Module 1: skip foundation content already covered in pre-work, add brief "pre-work review" activity (5-10 min recap + Q&A) instead of full instruction
  - Reference pre-work in module prerequisites
- `generate-workshop-prep` includes pre-work distribution in T-2 weeks checklist:
  - T-14 days: Finalize pre-work materials
  - T-7 days: Send welcome email with pre-work
  - T-2 days: Send reminder email
  - T-1 day: Check completion rates (if LMS tracking available)
- `curriculum-architect` agent adds pre-work generation as Phase 7.5 (after lesson plans, before description)

**Error handling:**
- Missing learning objectives: "Error: learning-objectives.md not found. Cannot identify prerequisites. Run `/generate-objectives` first."
- No Remember/Understand objectives found: "Advisory: No Remember/Understand-level objectives found. Pre-work will focus on implied prerequisites for Apply+ objectives."
- Pre-work already exists: Prompt with overwrite/update/cancel options

---

### 1.3 `/generate-spaced-practice` (Stage 6 — Delivery)

**File:** `commands/6-delivery/generate-spaced-practice.md`

**Frontmatter:**
```yaml
name: generate-spaced-practice
description: Generate a post-workshop spaced retrieval practice sequence to combat the forgetting curve with scheduled questions at expanding intervals
argument-hint: "[--format email|flashcards|lms|all] [--intervals custom]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Skill
```

**Behavior:**
1. Load `blooms-taxonomy` skill for cognitive level matching
2. Read `01-planning/learning-objectives.md` — extract objectives per module
3. Read `02-design/lesson-plans.md` — identify core content taught per module
4. Read `03-assessment/rubrics.md` — calibrate question difficulty to match assessment expectations
5. For each module, generate 3-5 retrieval questions:
   - Match Bloom's level of the module's objective (not just Remember-level recall)
   - Include brief answer keys with 1-2 sentence explanations
   - Mix question formats:
     - Remember/Understand: multiple choice, fill-in-the-blank, true/false with correction
     - Apply: short scenario + "what would you do?"
     - Analyze: "given this data/situation, what pattern do you see?"
     - Evaluate: "which option is best and why?"
   - No questions should test content not covered in lesson plans
6. Schedule questions at expanding intervals (default): Day 1, Day 3, Day 7, Day 14, Day 30
   - Each practice session: 3-5 questions, max 5 minutes to complete
   - Questions cycle through modules so each module is revisited multiple times
   - Later sessions mix questions from different modules (interleaving for deeper retention)
7. Format based on `--format` flag
8. Write to `04-materials/spaced-practice.md`
9. Staleness check on source files

**Format options:**
- `--format email` (default): Self-contained questions embedded in email body with "reveal answer" sections
- `--format flashcards`: Question/answer pairs, one per card, suitable for Anki or physical flashcard export
- `--format lms`: Structured quiz format with correct answer flagged, suitable for LMS import
- `--format all`: All three formats in one document

**Intervals:** `--intervals custom` prompts user for custom schedule. Default is Day 1, 3, 7, 14, 30.

**Output format:**
```markdown
---
title: Spaced Practice Sequence - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
courseVersion: [match]
lastUpdated: YYYY-MM-DD
format: [email|flashcards|lms|all]
intervals: [1, 3, 7, 14, 30]
totalQuestions: [N]
sourceFiles:
  learning-objectives: "01-planning/learning-objectives.md"
  lesson-plans: "02-design/lesson-plans.md"
  rubrics: "03-assessment/rubrics.md"
sourceHashes:
  learning-objectives: "[md5-first-8]"
  lesson-plans: "[md5-first-8]"
  rubrics: "[md5-first-8]"
---

# Spaced Practice Sequence

## [Course Title]

**Purpose:** Combat the forgetting curve through scheduled retrieval practice at expanding intervals. Research shows spaced retrieval can double long-term retention compared to single post-workshop assessment.

**Schedule:** 5 practice sessions over 30 days (Day 1, 3, 7, 14, 30)
**Time per session:** 3-5 minutes
**Total questions:** [N] across all sessions

---

## Question Bank

### Module 1: [Title] — [Bloom's Level]

**Q1.1:** [Question text]
- **Format:** [Multiple choice / Scenario / Short answer]
- **Answer:** [Correct answer]
- **Explanation:** [1-2 sentence explanation of why]
- **Scheduled:** Day [N]

**Q1.2:** [Question text]
...

[Repeat for each module]

---

## Practice Sessions

### Day 1 — Immediate Retrieval

**Time:** 5 minutes | **Questions:** 5

1. [Q1.1] — Module 1
2. [Q2.1] — Module 2
3. [Q3.1] — Module 3
4. [Q4.1] — Module 4
5. [Q5.1] — Module 5

### Day 3 — Early Reinforcement

**Time:** 4 minutes | **Questions:** 4

[Questions drawn from different modules than Day 1 where possible]

### Day 7 — First Interval

**Time:** 5 minutes | **Questions:** 5

[Mix of new questions and revisited concepts from Day 1/3]

### Day 14 — Consolidation

**Time:** 4 minutes | **Questions:** 4

[Interleaved questions across all modules — tests connections between concepts]

### Day 30 — Long-Term Check

**Time:** 5 minutes | **Questions:** 5

[Higher-level questions — Apply/Analyze scenarios that combine multiple modules]

---

## Email Format (if --format email or all)

### Day [N] Email

**Subject:** [Course Title] — Quick Practice ([N] minutes)

**Body:**

Hi [Name],

Here's your Day [N] practice for [Course Title]. Takes about [N] minutes.

**Question 1:** [Question text]

<details>
<summary>Reveal Answer</summary>
[Answer + explanation]
</details>

[Repeat for each question]

---

## Flashcard Format (if --format flashcards or all)

### Card [N]
**Front:** [Question]
**Back:** [Answer + brief explanation]
**Tags:** [Module], [Bloom's level], [Day scheduled]

---

## LMS Format (if --format lms or all)

### Quiz: Day [N] Practice
**Time limit:** 5 minutes
**Passing score:** 70%
**Attempts:** Unlimited

| # | Question | Type | Correct Answer | Distractors | Points |
|---|----------|------|---------------|-------------|--------|
| 1 | [Text] | [MC/TF/SA] | [Answer] | [If MC: options] | 1 |
```

**Validation checks:**
- Every module has at least 2 retrieval questions
- No questions test content not covered in lesson plans
- Question Bloom's level matches module objective level (no recall questions for Analyze objectives)
- Each practice session is completable in under 5 minutes
- All modules are represented across the 30-day schedule (no module forgotten)
- Answer explanations are present for every question

**Integration points:**
- `generate-transfer-plan` references spaced practice schedule in follow-up touchpoint table:
  - Merge Day 1/3/7 practice emails into existing follow-up schedule
  - Note: spaced practice complements (does not replace) transfer application tasks
- `generate-evaluation-plan` can use spaced practice completion rates as supplementary L2 retention data
- `curriculum-architect` agent adds spaced practice generation as Phase 9e (after evaluation plan)

**Error handling:**
- Missing learning objectives: "Error: learning-objectives.md not found. Run `/generate-objectives` first."
- Missing lesson plans: "Warning: lesson-plans.md not found. Questions will be based on objectives only (less specific). Generate lesson plans first for better question quality."
- Spaced practice already exists: Prompt with overwrite/update/cancel options

---

## Part 2: New Reference Files

### 2.1 Formative Assessment Techniques

**File:** `skills/backward-design-methodology/references/formative-assessment-techniques.md`

**Content structure:**

```markdown
# Formative Assessment Techniques for Intensive Workshops

## Purpose

A structured menu of formative assessment techniques for checking understanding during workshops. Use these to insert meaningful checkpoints into lesson plans — not just "any questions?" but techniques that reveal whether students actually understood.

## Technique Catalog by Cognitive Level

### Remember / Understand Level

| Technique | Time | Group Size | Description | What to Look For | Virtual Equivalent |
|---|---|---|---|---|---|
| **Signal Cards** | 1-2 min | Any | Students hold up colored cards (green=got it, yellow=shaky, red=lost) | Distribution of colors — if >30% yellow/red, re-teach | Emoji reactions or poll (green check / yellow circle / red X) |
| **Muddiest Point** | 3-5 min | Any | Students write the one thing they're most confused about | Common themes — cluster similar confusions | Chat waterfall: "Type your muddiest point" |
| **Think-Pair-Share** | 5-8 min | Any | Think individually (1 min), discuss with partner (2-3 min), share with group (2-3 min) | Quality of pair discussion; misconceptions surfaced in share-out | Breakout rooms (2 people, 3 min) + whole-group share |
| **Minute Paper** | 3-5 min | Any | Write for 1 minute: "What is the most important thing you learned?" and "What question do you still have?" | Depth of response; gap between stated learning and objectives | Shared doc or chat response |
| **Concept Check Poll** | 2-3 min | Any | Multiple-choice question targeting a common misconception | Percentage selecting the misconception option vs. correct answer | Platform poll feature |
| **Vocabulary Spot-Check** | 2-3 min | Any | Flash a term; students write or say definition in own words | Whether definitions are accurate vs. memorized vs. confused | Chat: "Define [term] in your own words — no looking at notes" |

### Apply / Analyze Level

| Technique | Time | Group Size | Description | What to Look For | Virtual Equivalent |
|---|---|---|---|---|---|
| **Error Analysis** | 5-10 min | Individual or pairs | Present a worked example with a deliberate error; students identify and correct it | Whether they catch the error AND explain why it's wrong | Screen share worked example; students respond in chat |
| **Worked Example Critique** | 8-12 min | Small groups | Show a completed application of the framework; groups evaluate quality using rubric criteria | Whether groups can distinguish good from mediocre application | Breakout rooms with shared doc for annotations |
| **Case Snippet** | 5-8 min | Individual | Present a brief scenario (3-4 sentences); students apply the current framework/tool | Whether application is correct and reasoning is sound | Individual response in shared doc or chat |
| **Peer Explanation** | 5-8 min | Pairs | Student A explains the concept/procedure to Student B, then swap | Whether the explainer uses accurate terminology and logical sequence | Breakout rooms (2 people, 4 min each direction) |
| **Diagram Labeling** | 3-5 min | Individual | Provide an incomplete diagram or framework; students fill in missing elements | Accuracy and completeness of labels; common omissions | Annotation on shared screen or digital whiteboard |
| **Two-Minute Application** | 3-5 min | Individual | "Apply [concept] to your own work context — write one specific example" | Whether example demonstrates genuine application vs. surface restatement | Chat or shared doc |

### Evaluate / Create Level

| Technique | Time | Group Size | Description | What to Look For | Virtual Equivalent |
|---|---|---|---|---|---|
| **Defense Questioning** | 5-10 min | Small groups | Present a recommendation or design; peers ask "why?" questions the author must defend | Quality of justification; whether criteria are applied consistently | Breakout rooms with structured questioning protocol |
| **Criteria Application** | 8-12 min | Individual or pairs | Given evaluation criteria and two options, students rank and justify | Whether justification references criteria (not just preference) | Individual written response in shared doc |
| **Rapid Prototype Review** | 10-15 min | Small groups | Groups review each other's in-progress work against rubric criteria | Whether feedback is specific, criteria-referenced, and actionable | Breakout rooms rotate through shared docs |
| **Priority Ranking** | 5-8 min | Individual then pairs | Rank 4-5 options by a given criterion; compare rankings with partner and resolve differences | Whether ranking criteria are applied consistently; quality of negotiation | Individual ranking in chat, then breakout for comparison |

## Instructor Decision Rules

Use these rules to act on formative assessment results in real time:

| Signal | Meaning | Action |
|---|---|---|
| >80% correct/confident | Class is ready to move on | Proceed to next activity; offer extension challenge for fast finishers |
| 50-80% correct | Partial understanding — some gaps | Brief re-teach (5 min) targeting the specific misconception; re-check with a second technique |
| <50% correct | Fundamental misunderstanding | Stop and re-teach the core concept from a different angle; do not proceed until >70% correct |
| Bimodal (strong cluster at correct AND incorrect) | Mixed readiness | Split: advanced group gets extension task; struggling group gets guided re-teach with instructor |
| Students can DO it but can't EXPLAIN it | Procedural knowledge without conceptual understanding | Add a "why does this work?" reflection; pair with a Peer Explanation activity |
| Students can EXPLAIN it but can't DO it | Conceptual knowledge without procedural skill | Add more guided practice with step-by-step support; slow down the procedure |

## Technique Selection Guide

When inserting formative assessment into a lesson plan, select based on:

1. **Cognitive level of the objective** — match technique to the level being assessed
2. **Time available** — use quick techniques (1-3 min) between activities, longer techniques (5-15 min) at module transitions
3. **Information needed** — polls give distribution data; written responses give qualitative depth
4. **Energy level** — movement-based or social techniques after low-energy periods; quiet techniques when group is focused

## Integration with Lesson Plans

When using this reference in `/generate-lesson-plans`:
- Insert at least one formative check per module (after instruction, before independent practice)
- Name the specific technique (not just "check understanding")
- Include the decision rule: "If <50% correct on the concept check, re-teach using [alternative explanation] before proceeding to guided practice"
- For virtual delivery, always specify the virtual equivalent
```

---

### 2.2 Accessibility Specifications

**File:** `skills/universal-design-for-learning/references/accessibility-specifications.md`

**Content structure:**

```markdown
# Accessibility Specifications for Training Materials

## Purpose

Translate UDL principles into actionable WCAG 2.1 AA technical specifications. Use this reference when generating artifacts, handouts, slides, and digital materials.

## Color & Contrast

### WCAG 2.1 AA Requirements
- **Normal text** (under 18pt or 14pt bold): minimum 4.5:1 contrast ratio
- **Large text** (18pt+ or 14pt+ bold): minimum 3:1 contrast ratio
- **Non-text elements** (icons, chart elements, form borders): minimum 3:1 contrast ratio
- **Focus indicators**: minimum 3:1 contrast against adjacent colors

### Compliant Color Combinations
| Background | Text Color | Ratio | Use For |
|---|---|---|---|
| White (#FFFFFF) | Dark gray (#333333) | 12.6:1 | Body text — preferred over pure black for reduced eye strain |
| White (#FFFFFF) | Dark blue (#1A365D) | 11.4:1 | Headings, links |
| Light gray (#F7F7F7) | Dark gray (#333333) | 10.9:1 | Alternate row backgrounds |
| Dark blue (#1A365D) | White (#FFFFFF) | 11.4:1 | Slide headers, emphasis blocks |

### Color Usage Rules
- Never use color as the sole carrier of meaning (always pair with labels, patterns, or icons)
- In charts: use patterns/textures in addition to color; label data directly when possible
- Test all materials with a color blindness simulator (e.g., Coblis, Sim Daltonism)
- Provide a color legend with text labels for any color-coded content

### Contrast Checking Tools
- WebAIM Contrast Checker: webaim.org/resources/contrastchecker
- Colour Contrast Analyser (desktop app): TPGi
- Built-in: macOS Accessibility Inspector, Chrome DevTools

## Typography

### Recommended Accessible Fonts
| Font | Type | Why Accessible | Best For |
|---|---|---|---|
| **Atkinson Hyperlegible** | Sans-serif | Designed specifically for low vision; distinct letterforms (Il1, O0) | Handouts, worksheets |
| **Source Sans Pro** | Sans-serif | Open-source, excellent x-height, clear at small sizes | Digital materials, slides |
| **Open Sans** | Sans-serif | Wide letterforms, good screen rendering | Projected slides, handouts |

### Minimum Sizes by Context
| Context | Minimum Size | Recommended |
|---|---|---|
| Projected slides (body text) | 18pt | 24pt |
| Projected slides (titles) | 28pt | 36pt |
| Printed handouts (body text) | 12pt | 13-14pt |
| Printed handouts (headings) | 14pt | 16-18pt |
| Digital documents (body) | 12pt / 1rem | 14pt / 1.125rem |
| Captions/footnotes | 10pt | 11pt |

### Spacing & Layout
- **Line spacing:** 1.5 for body text (minimum 1.15 for dense reference materials)
- **Paragraph spacing:** At least 1.5x the line spacing
- **Line length:** 50-75 characters per line (prevents tracking errors)
- **Alignment:** Left-aligned (never justified — uneven word spacing impairs reading)
- **White space:** Generous margins (1 inch minimum for print)

## Document Accessibility Checklist

### Structure
- [ ] Heading hierarchy is logical (H1 → H2 → H3, no skipped levels)
- [ ] Headings describe content (not "Section 1" but "Learning Objectives")
- [ ] Lists use proper list markup (not manually typed bullets)
- [ ] Tables have header rows marked as headers
- [ ] Reading order matches visual layout (test by tabbing through)

### Images & Visual Content
- [ ] All images have alt text describing content and purpose
- [ ] Decorative images have empty alt text (alt="")
- [ ] Complex diagrams have long descriptions or text alternatives
- [ ] Charts include data tables as alternatives
- [ ] Screenshots include text descriptions of key elements

### Text Content
- [ ] Plain language used (8th-grade reading level for general audiences)
- [ ] Acronyms defined at first use
- [ ] Links are descriptive (not "click here" — use "download the worksheet")
- [ ] Instructions don't rely on sensory characteristics ("click the red button" → "click the Submit button")

### PDF Specific
- [ ] PDF is tagged (not scanned image)
- [ ] Reading order is correct (test with screen reader)
- [ ] Form fields have labels
- [ ] Document language is set
- [ ] Title is set in document properties

## Slide Accessibility Checklist

- [ ] Every slide has a unique, descriptive title
- [ ] Text is not embedded in images (use text boxes)
- [ ] Animations are minimal and non-essential (content accessible without animation)
- [ ] Alt text on all non-decorative images
- [ ] Slide reading order is set correctly (check in Accessibility Checker)
- [ ] Font size meets minimums (18pt+ body, 28pt+ title)
- [ ] High contrast between text and background
- [ ] Speaker notes contain full narrative (usable as transcript)
- [ ] No auto-advancing slides (participants control pace)

## Video & Audio Requirements

### Captions
- **Synchronized captions** required for all video content
- **Accuracy:** 99%+ (auto-generated captions must be edited)
- **Formatting:** Max 2 lines, 32 characters per line, 1-second minimum display
- **Speaker identification** when multiple speakers

### Transcripts
- **Full text transcript** for all audio and video content
- Include speaker identification, relevant sound effects, and visual descriptions
- Provide as separate downloadable document

### Audio Description
- **Audio description** for visual-only content (diagrams drawn on screen, physical demonstrations)
- Alternative: provide verbal narration of all visual content as standard practice

## Quick Compliance Check (5-Minute Pre-Delivery Audit)

Run through these 10 items before delivering any training materials:

1. [ ] Slide fonts are 18pt+ body, 28pt+ title
2. [ ] Handout fonts are 12pt+ with 1.5 line spacing
3. [ ] Color is never the only way information is conveyed
4. [ ] All images have alt text
5. [ ] Headings are used for structure (not just bold text)
6. [ ] Links are descriptive (no "click here")
7. [ ] Videos have captions
8. [ ] Materials available in digital format (not print-only)
9. [ ] Reading order makes sense when read linearly
10. [ ] Acronyms defined at first use

**Score:** 10/10 = ready. <8/10 = fix before delivery. <6/10 = significant accessibility barriers.
```

---

### 2.3 Cultural Adaptation

**File:** `skills/universal-design-for-learning/references/cultural-adaptation.md`

**Content structure:**

```markdown
# Cultural Adaptation Guide for Training Materials

## Purpose

Guidance for adapting curricula across cultural contexts. Use this reference when designing workshops for international audiences or adapting existing curricula for delivery in new regions.

## Examples & Case Studies

### Selection Principles
- Use examples from industries/domains common across cultures (technology, healthcare, logistics) rather than culture-specific contexts
- When using region-specific examples, provide 2-3 variants so participants from different regions can connect
- Avoid examples that assume specific regulatory environments (e.g., US tax law, EU GDPR) unless the course is regulation-specific — if regulation is relevant, name it explicitly and note jurisdictional scope
- Test examples with someone from the target culture before delivery

### What to Avoid in Examples
| Avoid | Why | Instead |
|---|---|---|
| Sports metaphors (baseball, cricket, American football) | Not universal | Use workplace or general process metaphors |
| Pop culture references (TV shows, celebrities) | Regional and generational | Use universal scenarios (travel, cooking, building) |
| Humor based on wordplay or idioms | Doesn't translate | Use visual humor or situational humor that transcends language |
| Business practices assumed universal (tipping, at-will employment, credit scores) | Vary dramatically by country | Name the practice explicitly and note it's context-specific |
| Currency-specific examples ($100K salary) | Meaningless across economies | Use ratios, percentages, or relative comparisons |
| Holiday or calendar references | Vary by culture and religion | Use "Q1/Q2" or "first half of year" instead of "after Thanksgiving" |

### Case Study Adaptation
When adapting case studies for a new region:
1. Change company names and locations to local equivalents
2. Adjust financial figures to local currency and economic scale
3. Replace regulatory references with local equivalents
4. Verify that the business scenario is realistic in the target market
5. Have a local reviewer check for cultural plausibility

## Communication Norms

### Feedback & Participation Styles
| Dimension | Range | Design Implications |
|---|---|---|
| **Direct vs. indirect feedback** | Some cultures give direct critique; others preserve harmony | Provide anonymous feedback options alongside verbal; use "I notice..." framing for critiques |
| **Individual vs. group identity** | Some cultures emphasize individual achievement; others prioritize group consensus | Offer both individual and group assessment options; don't force individual public performance in group-oriented cultures |
| **Power distance** | Some cultures expect hierarchy between instructor and student; others prefer equality | In high power-distance cultures, instructor modeling is more effective than peer learning; adjust accordingly |
| **Uncertainty avoidance** | Some cultures want clear rules and structure; others are comfortable with ambiguity | Provide explicit rubrics and step-by-step guides for high uncertainty-avoidance groups; allow more open exploration for low |
| **Face-saving** | Public failure is deeply uncomfortable in some cultures | Never single out incorrect answers publicly; use anonymous polling; provide private feedback channels |

### Adjusting Activities
- **Think-pair-share:** Works universally but adjust share-out — in face-saving cultures, have pairs share their partner's idea (not their own), reducing personal exposure
- **Group presentations:** In hierarchy-sensitive cultures, assign the most senior person as presenter (they'll be uncomfortable if a junior presents "for" them)
- **Debate/argument activities:** May be uncomfortable in harmony-oriented cultures — reframe as "exploring different perspectives" rather than "defending a position"
- **Self-assessment:** In cultures where self-criticism is norm-violating, use comparative assessment ("rate this work sample" rather than "rate yourself")

## Time & Pacing

| Factor | Consideration | Adaptation |
|---|---|---|
| **Punctuality norms** | Vary from strict to flexible across cultures | Build 10-15 min buffer at start; don't penalize latecomers in early activities |
| **Break expectations** | Some cultures expect longer meal breaks; others prefer shorter, more frequent | Ask participants about preferences on Day 1; offer flexibility |
| **Pace of discourse** | Some cultures value deliberation; others prefer quick exchanges | Allow longer think-time before responses (5 seconds minimum); don't interpret silence as disengagement |
| **Meeting duration** | Full-day workshops are normal in some cultures, unusual in others | For unfamiliar audiences, default to half-day sessions |

## Localization Checklist

When adapting an existing curriculum for a new region, verify each item:

### Content
- [ ] Currency in examples matches target region (or uses relative values)
- [ ] Regulatory references updated to local equivalents
- [ ] Date formats match local convention (DD/MM/YYYY vs. MM/DD/YYYY)
- [ ] Units of measurement match local standards (metric vs. imperial)
- [ ] Company names and scenarios are plausible in target market
- [ ] Technology tools referenced are available in target region
- [ ] Images show diverse representation relevant to target audience

### Language
- [ ] Idioms and colloquialisms replaced with plain language
- [ ] Acronyms expanded and explained (don't assume global recognition)
- [ ] Reading level appropriate for non-native speakers (if applicable)
- [ ] Technical terminology consistent with local industry usage
- [ ] Glossary provided for domain-specific terms

### Facilitation
- [ ] Activities reviewed for cultural appropriateness (public speaking, debate, self-disclosure)
- [ ] Feedback mechanisms include anonymous options
- [ ] Group work structure accounts for hierarchy and face-saving norms
- [ ] Timing includes buffer for language processing and cultural pace differences
- [ ] Co-facilitator or local contact identified for cultural guidance during delivery
```

---

### 2.4 Content Curation

**File:** `skills/backward-design-methodology/references/content-curation.md`

**Content structure:**

```markdown
# Content Curation Guide for Course Development

## Purpose

Guidance for selecting, evaluating, and integrating third-party content into training curricula. Complements the content-sources.md licensing tracker with quality evaluation criteria.

## RARBA Evaluation Framework

Evaluate every third-party source against five criteria before incorporating:

| Criterion | Question | Red Flag | Green Flag |
|---|---|---|---|
| **Recency** | When was this published or last updated? | >5 years old for fast-moving fields; >10 years for stable fields | Published within 2 years; actively maintained |
| **Authority** | Who created this? What are their credentials? | Anonymous source; no credentials listed; vendor marketing | Named expert; peer-reviewed; recognized institution |
| **Relevance** | Does this directly serve a learning objective? | Tangentially interesting but doesn't advance specific outcomes | Directly supports a named objective; fills a specific gap |
| **Bias** | Does this present a balanced perspective? | Single vendor perspective; cherry-picked data; advocacy disguised as analysis | Multiple perspectives acknowledged; methodology transparent |
| **Accessibility** | Can all participants access and engage with this? | Paywalled; requires specific software; only available in one language | Open access; multiple formats; plain language |

### Using RARBA
- Score each criterion: 1 (poor) to 3 (strong)
- Total score 13-15: Include confidently
- Total score 10-12: Include with caveats or minor adaptation
- Total score 7-9: Consider alternatives; include only if no better source exists
- Total score below 7: Do not include

## Case Study Selection

### Real vs. Fictional Case Studies

| Type | When to Use | Advantages | Risks |
|---|---|---|---|
| **Real (named company)** | When authenticity drives learning; when outcome is public knowledge | Credibility; participants can research further; motivating | Dated quickly; participants may have preconceptions; legal considerations |
| **Real (anonymized)** | When illustrating sensitive situations; when using client data | Authenticity without exposure; flexible detail level | Participants may guess the company; still may be sensitive |
| **Fictional** | When you need to control variables; when teaching a framework | Can design the perfect teaching example; no legal risk; can adjust complexity | Less credible; participants may disengage if it feels unrealistic |
| **Participant-generated** | When transfer is the primary goal; when audience expertise is high | Maximum relevance; high engagement; immediate application | Unpredictable quality; privacy concerns; may derail timing |

### Adapting Published Case Studies
1. Verify licensing allows adaptation (check case publisher's terms)
2. Update data and context to current conditions
3. Simplify to focus on the specific learning objective (remove tangential complexity)
4. Add discussion questions that map to your assessment criteria
5. Provide instructor notes with key teaching points and common student responses
6. Credit the original source in content-sources.md

## Framework Attribution

### Common Frameworks and Citation Practice
| Framework | Creator | Minimum Attribution | Notes |
|---|---|---|---|
| Porter's Five Forces | Michael Porter | "Porter's Five Forces (Porter, 1979)" | Widely taught; no permission needed for educational use |
| SWOT Analysis | Albert Humphrey (attributed) | "SWOT Analysis" (no formal citation needed) | Origin disputed; treated as general knowledge |
| Bloom's Taxonomy | Benjamin Bloom; revised by Anderson & Krathwohl | "Bloom's Revised Taxonomy (Anderson & Krathwohl, 2001)" | Widely used in education; no permission needed |
| Design Thinking | Stanford d.school / IDEO | "Design Thinking (Stanford d.school)" | Specific visualizations may be trademarked; concepts are free to teach |
| Agile/Scrum | Various | "Scrum Guide (Schwaber & Sutherland, 2020)" | Scrum Guide is freely available; specific certifications are trademarked |
| Kirkpatrick Model | Donald Kirkpatrick | "Kirkpatrick's Four Levels (Kirkpatrick, 1994)" | The four levels are general knowledge; specific tools may be trademarked |

### Citation Style for Training Materials
Training materials use a simplified citation style (not full APA/MLA):
- **In-text:** "Using Porter's Five Forces (Porter, 1979), we analyze..."
- **Slide footer:** "Adapted from Porter's Five Forces Framework"
- **Handout reference list:** Author. (Year). Title. Publisher. [URL if applicable]
- **When in doubt:** More attribution is always safer than less

## Source Types Comparison

| Source Type | Credibility | Recency | Best For | Watch Out For |
|---|---|---|---|---|
| **Academic research** | High | Variable (may be dated) | Theoretical foundations, evidence-based claims | Jargon, limited practical application |
| **Industry reports** (Gartner, McKinsey, Deloitte) | High | Current | Market data, trends, benchmarks | May require purchase; vendor bias possible |
| **Trade publications** | Medium | Current | Practitioner perspectives, real-world examples | Less rigorous methodology; may be opinion |
| **News articles** | Medium | Very current | Current events, recent examples | May lack depth; can become dated quickly |
| **Practitioner blogs** | Variable | Current | Practical how-to, real experience | No peer review; quality varies widely |
| **Vendor materials** | Low (biased) | Current | Product-specific training only | Marketing bias; not suitable for general teaching |
| **Wikipedia** | Medium (for overview) | Current | Quick reference, starting point | Not a primary source; verify claims elsewhere |

## Red Flags Checklist

Before including any third-party content, check for these warning signs:

- [ ] **Single source claims:** "Studies show..." without naming the study
- [ ] **Outdated data:** Statistics or market data more than 3 years old in fast-moving fields
- [ ] **Vendor marketing:** Content that consistently favors one product or company
- [ ] **No author attribution:** Cannot identify who created the content
- [ ] **Circular citations:** Sources that cite each other without independent verification
- [ ] **Survivorship bias:** Case studies that only show successes, never failures
- [ ] **Absolute claims:** "Always," "never," "the only way" — real expertise acknowledges nuance
- [ ] **Paywalled sources:** Content participants cannot access for follow-up study
- [ ] **Copyrighted images:** Stock photos, diagrams, or screenshots without license
- [ ] **Outdated UI screenshots:** Software interface screenshots that no longer match current versions
```

---

## Part 3: Enhancements to Existing Files

### 3.1 Affective Domain — Bloom's Taxonomy Skill

**File:** `skills/blooms-taxonomy/SKILL.md`

**Change:** Append a new section titled `## Affective Domain (Krathwohl's Taxonomy)` after the existing `## Scaffolding Strategies` section and before `## Intensive Workshop Considerations`.

**Content to append:**

```markdown
## Affective Domain (Krathwohl's Taxonomy)

### When to Use Affective Objectives

Many workshops aim to change attitudes and values, not just skills — "embrace data-driven decision making," "value inclusive design," "adopt a security-first mindset." These goals require affective objectives alongside cognitive ones.

**Signals that you need affective objectives:**
- User says "I want them to appreciate/value/embrace/adopt..."
- The real goal is behavior change driven by attitude shift, not just skill acquisition
- Prior training taught the skill but participants aren't using it (motivation gap, not skill gap)
- The TNA identified a motivation-type gap

**When NOT to use affective objectives:**
- The goal is purely procedural skill acquisition
- The workshop is compliance training with no attitude change goal
- Time is too short (affective change is slower than cognitive learning)

### The Five Affective Levels

#### Level 1: Receiving (Awareness)
**Definition:** Being aware of and willing to attend to new ideas or perspectives

**Action verbs:** Acknowledge, attend, listen, notice, observe, recognize, be aware of

**Example objectives:**
- "Acknowledge the role of data analytics in modern real estate decision-making"
- "Recognize how unconscious bias affects hiring decisions"

**Instructional strategies:** Compelling stories, surprising data, guest perspectives, video testimonials
**Assessment:** Attendance to content, willingness to engage (participation observation, not testing)

#### Level 2: Responding (Reaction)
**Definition:** Actively participating in and reacting to new ideas

**Action verbs:** Participate, contribute, discuss, volunteer, engage, respond, comply, follow

**Example objectives:**
- "Participate in discussions about ethical implications of AI in real estate"
- "Contribute personal examples of data-driven decision successes and failures"

**Instructional strategies:** Structured discussions, reflection prompts, peer sharing, case study discussions
**Assessment:** Quality and frequency of participation, depth of reflection responses

#### Level 3: Valuing (Commitment)
**Definition:** Attaching worth to an idea, behavior, or practice; demonstrating commitment

**Action verbs:** Appreciate, value, justify, advocate, prioritize, commit, support, prefer

**Example objectives:**
- "Justify the importance of accessibility testing in product development"
- "Prioritize data-backed evidence over intuition when evaluating PropTech solutions"

**Instructional strategies:** Values clarification exercises, debate/discussion, commitment statements, "when would you NOT do this?" scenarios
**Assessment:** Commitment statements, justification quality, behavioral intention surveys

#### Level 4: Organizing (Integration)
**Definition:** Integrating new values with existing value system; resolving conflicts between values

**Action verbs:** Integrate, reconcile, balance, formulate, organize, synthesize, relate

**Example objectives:**
- "Integrate risk awareness into existing decision-making processes without creating paralysis"
- "Balance innovation goals with compliance requirements"

**Instructional strategies:** Value conflict scenarios, priority-setting exercises, personal philosophy development
**Assessment:** Quality of integration reasoning, resolution of value conflicts in case studies

**Workshop note:** Organizing-level change typically requires more than a 1-2 day workshop. Include as a stretch goal or post-workshop development objective.

#### Level 5: Characterizing (Identity)
**Definition:** Acting consistently with new values as part of one's identity and worldview

**Action verbs:** Embody, exemplify, internalize, consistently demonstrate, be characterized by

**Example objectives:**
- "Consistently apply ethical considerations when recommending technology solutions"

**Workshop note:** Characterizing-level change cannot be achieved in a workshop. This level represents long-term behavioral change that workshops can initiate but not complete. Use only in course series or ongoing development programs as an aspirational outcome.

### Pairing Cognitive and Affective Objectives

Effective workshops often pair a cognitive objective with a related affective objective in the same module:

| Cognitive Objective | Paired Affective Objective | Why the Pairing Works |
|---|---|---|
| Apply risk assessment framework to PropTech investments (Apply) | Value proactive risk identification as essential to investment decisions (Valuing) | Skill without motivation leads to unused knowledge |
| Analyze accessibility barriers in digital products (Analyze) | Advocate for accessibility testing as a standard development practice (Valuing) | Understanding barriers intellectually doesn't guarantee action |
| Evaluate vendor proposals using due diligence criteria (Evaluate) | Prioritize evidence-based evaluation over relationship-driven decisions (Valuing) | Cognitive skill exists but organizational habits override it |

### Workshop Considerations for Affective Objectives

**Quantity:** Limit to 1-2 affective objectives per workshop. Attitude change is slower than cognitive learning and requires reflection time.

**Level ceiling:** Focus on Receiving, Responding, and Valuing levels. Organizing and Characterizing require sustained practice far beyond a workshop timeframe.

**Assessment approach:** Affective outcomes cannot be assessed with quizzes. Use:
- Self-reflection journals or prompts
- Behavioral intention surveys (pre/post)
- Commitment statements ("I will... because...")
- Observation of discussion quality and engagement depth
- Attitude scales (Likert-type, pre/post workshop comparison)

**Avoid:** Do not grade or score affective outcomes. Affective assessment is formative (informing facilitation adjustments) not summative (passing/failing participants).

**Integration with `/generate-objectives`:** When a user's stated goal sounds affective ("I want them to appreciate..." / "They need to buy in to..."), offer to formulate an explicit affective objective alongside the cognitive one. Present both and let the user choose whether to include the affective objective.
```

---

### 3.2 Co-Facilitation Support — generate-lesson-plans

**File:** `commands/3-learning-plan/generate-lesson-plans.md`

**Change:** Append a new section titled `## Co-Facilitation Support` after the existing `## Delivery Mode Adaptations` section and before the final `---` separator.

**Content to append:**

```markdown
## Co-Facilitation Support

When generating lesson plans for team-taught workshops, add co-facilitation structure to each module.

### Argument

`--facilitators N` (default: 1)

When N > 1, add the following to each module's lesson plan:

### Per-Module Role Table

Add after the module header and before "### Overview":

```
### Facilitation Roles

| Role | Facilitator | Responsibilities |
|---|---|---|
| **Lead** | [Name/TBD] | Content delivery, demonstrations, main instruction |
| **Support** | [Name/TBD] | Q&A monitoring, time management, circulating during practice, breakout room visits (virtual) |
| **Observer** (if 3+) | [Name/TBD] | Assessment observation, note-taking on student progress, identifying struggling learners |
```

### Role Rotation

Rotate lead and support roles across modules to:
- Keep both facilitators engaged and energized
- Leverage each facilitator's strengths for relevant modules
- Prevent one facilitator from becoming a passive observer

Default rotation: alternate lead role every 2-3 modules. Group module assignments by facilitator expertise if known.

### Handoff Protocol

Add between each module pair:

```
### Module Transition: [Module N] → [Module N+1]

**Outgoing Lead briefs Incoming Lead (2-3 min during break):**
- Timing status: [on time / X minutes behind / ahead]
- Student energy: [high / moderate / flagging]
- Unresolved questions: [list any questions parked for later]
- Struggling learners: [note anyone needing extra support]
- Key misconception surfaced: [if any]
```

### Split Instructor Notes

Where the standard template has `**Instructor Notes:**`, split to:

```
**Lead Notes:**
- [Content delivery guidance, pacing, key emphases]

**Support Notes:**
- [What to monitor during this section]
- [When to intervene vs. let the lead handle]
- [Specific students or groups to watch]
- [Chat/Q&A management instructions (virtual)]
```

### Co-Facilitation Planning Checklist

Add to the Instructor Preparation Checklist at the end of lesson plans:

```
### Co-Facilitation Preparation
- [ ] Role assignments confirmed for each module
- [ ] Handoff protocol reviewed by both facilitators
- [ ] Shared signals agreed (time warnings, need-help, take-over)
- [ ] Communication channel established (text, Slack, hand signals)
- [ ] Pre-workshop dry run: practice at least one handoff
- [ ] Backup plan: if one facilitator is unavailable, which modules can be solo-delivered?
```
```

---

### 3.3 Inter-Course Transition Design — design-series

**File:** `commands/0-analysis/design-series.md`

**Change:** Append a new section titled `## Inter-Course Transition Design` after the existing `## Output Format` section (before `## Settings Integration`).

**Content to append:**

```markdown
## Inter-Course Transition Design

After defining the series structure, design the transitions between course levels to address retention decay and readiness verification.

### Retention Bridge

For each course transition (101→201, 201→301, etc.), generate:

#### Review Module
- **Duration:** 15-20 minutes at the start of the higher-level course
- **Content:** Recap of the prior course's 3-5 handoff outcomes
- **Format:** Not a re-teach — a rapid activation exercise:
  - Quick-fire concept check (5 questions, 5 minutes)
  - Pair discussion: "How have you applied [prior course skill] since the workshop?" (5 minutes)
  - Instructor recap of key frameworks with visual reference (5-10 minutes)
- **Instructor note:** If >30% of participants struggle with the review, consider whether they have the prerequisite knowledge for this level

#### Prerequisite Concept Map
For each transition, list:

| Concept from Level N | Required for (Level N+1 Module) | How It's Used |
|---|---|---|
| [Handoff outcome 1] | Module [X]: [Title] | [Foundation for / Builds directly on / Assumed prerequisite for] |

This maps exactly which prior knowledge feeds into which later module, so the review module can prioritize the most critical prerequisites.

#### Recommended Time Gaps
| Gap | Suitability | Notes |
|---|---|---|
| 1-4 weeks | Ideal | Skills still fresh; brief review sufficient |
| 1-3 months | Acceptable | Moderate review needed; include pre-work refresher |
| 3-6 months | Requires intervention | Significant review module or pre-work required |
| 6+ months | Re-assessment recommended | Consider requiring placement assessment before enrollment |

### Placement Assessment

Generate a short skills assessment for each transition that allows learners to skip a level:

- **Length:** 5-8 questions covering the prior course's Apply+ objectives
- **Format:** Scenario-based questions at the prior course's highest Bloom's level
- **Passing threshold:** 80% (must demonstrate solid mastery, not just familiarity)
- **Result interpretation:**
  - 80%+: May enroll directly in the higher-level course
  - 60-79%: Recommended to take the prior course or complete bridge pre-work
  - Below 60%: Should complete the prior course before enrolling

#### Placement Assessment Template

For each transition in the series, generate a section in the series plan:

```
### Placement: Skip [Level N] → Enroll Directly in [Level N+1]

**Instructions:** Complete this assessment to determine if you can skip [Level N]. You should be able to answer at least [M] of [N] questions correctly.

1. [Scenario-based question targeting handoff outcome 1]
2. [Scenario-based question targeting handoff outcome 2]
...

**Answer Key:** [Provided separately to administrator]

**Score Interpretation:**
- [M+]/[N]: You may skip [Level N] and enroll in [Level N+1]
- [Below M]/[N]: We recommend completing [Level N] first
```

### Bridge Assignments

Optional between-course activities that maintain skills during the gap between courses:

#### Post-[Level N] / Pre-[Level N+1] Activities

For each transition, generate 2-3 bridge activities:

| Activity | Purpose | Time | Deadline |
|---|---|---|---|
| [Practice task using Level N skills in workplace] | Maintain procedural skill | 30-60 min | 2 weeks post-Level N |
| [Reading or self-study on Level N+1 preview topics] | Prime for new content | 20-30 min | 1 week pre-Level N+1 |
| [Self-assessment checklist for Level N+1 readiness] | Identify gaps before enrollment | 10 min | Before enrollment |

**Bridge Activity Design Principles:**
- Activities should use skills from Level N in realistic workplace contexts (not academic exercises)
- Preview activities for Level N+1 should build curiosity, not teach the content (that's the next course's job)
- Total bridge time should not exceed 2 hours between courses
- All activities are optional but recommended — never gate enrollment on bridge completion

### Series Plan Output Addition

When generating the series plan, add after the `## Series Coherence Summary` section:

```
## Inter-Course Transitions

### Transition: 101 → 201

**Review module (15-20 min at start of 201):**
- Concepts to review: [list from 101 handoff outcomes]
- Review format: [Quick-fire check + pair discussion + visual recap]

**Placement assessment:**
- [N] questions covering [101 handoff outcomes]
- Passing threshold: 80%

**Bridge activities (optional):**
1. [Activity 1]
2. [Activity 2]

**Recommended gap:** [Ideal: X weeks | Maximum: Y months]

---

[Repeat for each transition]
```
```

---

## Part 4: Integration Updates

These are minor updates to existing files to reference the new additions. Each is a small, targeted change.

### 4.1 curriculum-architect agent

**File:** `agents/curriculum-architect.md`

**Changes:**
- Add Phase 3.5 (after course initialization, before objectives): "If sufficient audience information is available, generate learner profile using `/generate-learner-profile`"
- Add Phase 7.5 (after lesson plans, before description): "If Remember/Understand prerequisites exist, generate pre-work using `/generate-pre-work`"
- Add Phase 9e (after evaluation plan): "Generate spaced practice sequence using `/generate-spaced-practice`"
- Update Phase 10 deliverables list to include new files

### 4.2 quality-reviewer agent

**File:** `agents/quality-reviewer.md`

**Changes:**
- In Stage 3 Validation (Learning Activities), add check: "If `01-planning/learner-profile.md` exists, verify differentiation tiers align with profile findings"
- In Section 5 (Overall Coherence Check), add: "If affective objectives exist in learning-objectives.md, validate they are paired with cognitive objectives and use appropriate assessment methods (not quizzes)"
- Add Section 5e: "Pre-Work Validation" — if pre-work exists, verify it maps to specific objectives/prerequisites and total time is under 30 minutes

### 4.3 README.md

**File:** `README.md`

**Changes:**
- Add new commands to command reference sections
- Update feature list
- Add reference files to skills reference

---

## File Inventory

### New Files (7)
| File | Type | Location |
|---|---|---|
| `generate-learner-profile.md` | Command | `commands/0-analysis/` |
| `generate-pre-work.md` | Command | `commands/3-learning-plan/` |
| `generate-spaced-practice.md` | Command | `commands/6-delivery/` |
| `formative-assessment-techniques.md` | Reference | `skills/backward-design-methodology/references/` |
| `accessibility-specifications.md` | Reference | `skills/universal-design-for-learning/references/` |
| `cultural-adaptation.md` | Reference | `skills/universal-design-for-learning/references/` |
| `content-curation.md` | Reference | `skills/backward-design-methodology/references/` |

### Modified Files (5)
| File | Change Type |
|---|---|
| `skills/blooms-taxonomy/SKILL.md` | Append affective domain section |
| `commands/3-learning-plan/generate-lesson-plans.md` | Append co-facilitation section |
| `commands/0-analysis/design-series.md` | Append inter-course transition section |
| `agents/curriculum-architect.md` | Add new phases for new commands |
| `agents/quality-reviewer.md` | Add validation checks for new artifacts |

### Updated Files (1)
| File | Change Type |
|---|---|
| `README.md` | Add new commands and features |

**Total: 7 new files, 6 modified files**
