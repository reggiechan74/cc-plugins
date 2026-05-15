# Phase 3: Delivery & Process — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add virtual/hybrid delivery support and stakeholder review workflow, enabling the plugin to design courses for any delivery format and facilitate organizational approval processes.

**Architecture:** Two independent workstreams — (1) delivery mode as a first-class parameter in `create-course` with a new `virtual-facilitation` skill, mode-aware defaults in `generate-outline` and `generate-lesson-plans`, and a post-hoc `adapt-for-virtual` command for converting existing courses; (2) new `generate-review-package` command for stakeholder/SME review. All follow established v0.5.0 plugin conventions.

**Tech Stack:** Markdown command/skill files with YAML frontmatter. No runtime code.

---

## Task 1: Add Delivery Mode to `create-course`

**Files:**
- Modify: `commands/create-course.md`

**Step 1: Read current file**

Read `commands/create-course.md`.

**Step 2: Update argument-hint**

Change the `argument-hint` line from:
```
argument-hint: "[Course Title] [--duration 1-day|2-day] [--location path] [--series name --level N]"
```
To:
```
argument-hint: "[Course Title] [--duration 1-day|2-day] [--mode in-person|virtual|hybrid] [--location path] [--series name --level N]"
```

**Step 3: Add --mode to argument handling**

In the "## Argument Handling" section, under "Interactive mode", add to the list of items gathered:
```
- Delivery mode: in-person (default), virtual, or hybrid
```

Under "Args-based mode", update the example:
```bash
/create-course "PropTech Fundamentals" --duration 2-day --mode virtual --location ~/courses
```

**Step 4: Add delivery mode section**

After the "## Series Integration" section (and before "## Directory Naming"), add a new section:

```markdown
## Delivery Mode

When `--mode` is provided (or selected interactively):

### In-Person (default)
No changes to existing behavior. Standard workshop design.

### Virtual
Adds the following to `course-positioning.md`:
- `deliveryMode: virtual` in YAML frontmatter
- Platform requirements section (video conferencing, digital whiteboard, chat)
- Virtual logistics section (tech check schedule, backup plans)

Sets mode-specific defaults that propagate to downstream commands:
- **Max session length:** 4 hours per day (not 6)
- **Break frequency:** Every 45 minutes (not 60)
- **Break duration:** 10 minutes (not 5-10)
- **Activity format:** Breakout rooms replace table groups; digital collaboration replaces physical materials
- **Engagement cadence:** Interaction point every 15-20 minutes (polls, chat, reactions)
- **Buffer time:** 15% (not 10%)

### Hybrid
Adds the following to `course-positioning.md`:
- `deliveryMode: hybrid` in YAML frontmatter
- Dual-experience design notes (in-room and remote participants)
- Technology requirements for both audiences
- Equity considerations section

Sets mode-specific defaults:
- Inherits virtual timing constraints (shorter sessions, more breaks)
- Adds camera/audio requirements for in-room
- Activities must work for both audiences simultaneously
- Facilitator attention split guidance

### Frontmatter Addition

When generating `course-positioning.md`, add to YAML frontmatter:
```yaml
deliveryMode: "[in-person|virtual|hybrid]"
```

And add to the "## Workshop Format" section:
```markdown
- **Delivery:** [In-person intensive workshop | Virtual workshop via [Platform] | Hybrid (in-room + remote participants)]
```
```

**Step 5: Commit**

```bash
git add course-curriculum-creator/commands/create-course.md
git commit -m "feat(commands): add --mode flag for virtual/hybrid delivery to create-course"
```

---

## Task 2: Create `virtual-facilitation` Skill

**Files:**
- Create: `skills/virtual-facilitation/SKILL.md`

**Step 1: Write the skill file**

Create `skills/virtual-facilitation/SKILL.md`:

```markdown
---
name: virtual-facilitation
description: This skill should be used when the user asks to "design a virtual workshop", "create online training", "adapt for remote delivery", "plan a hybrid session", "facilitate via Zoom/Teams/Meet", or when course-positioning.md has deliveryMode set to "virtual" or "hybrid". Provides practical guidance for designing and facilitating effective virtual and hybrid learning experiences.
version: 0.1.0
---

# Virtual Facilitation for Workshop Design

## Overview

Virtual and hybrid workshops require fundamentally different design, not just putting a camera on an in-person session. Attention spans are shorter, engagement requires active design, technology introduces failure points, and facilitators must manage both content and technology simultaneously.

This skill provides practical guidance for designing workshops that work in virtual and hybrid formats, with specific timing constraints, engagement techniques, and technology considerations.

## Virtual vs. In-Person: Key Differences

| Dimension | In-Person | Virtual | Hybrid |
|---|---|---|---|
| **Max session length** | 6 hours/day | 4 hours/day | 4 hours/day |
| **Break frequency** | Every 60 min | Every 45 min | Every 45 min |
| **Attention span per activity** | 20-30 min | 10-15 min | 10-15 min |
| **Engagement check-ins** | Every 30 min | Every 15-20 min | Every 15-20 min |
| **Group work format** | Table groups | Breakout rooms | Mixed (breakout + in-room) |
| **Materials format** | Print handouts | Digital documents, shared screens | Both digital + print |
| **Assessment method** | Written, observed, presented | Digital submission, screen share, chat | Both formats |
| **Buffer time** | 10% | 15% | 20% |
| **Setup time needed** | 15 min | 30 min (tech check) | 45 min (dual setup) |

## Virtual Workshop Design Principles

### 1. Chunk Everything Smaller

In-person modules of 90-120 minutes must be broken into 45-60 minute virtual segments:

**In-person module (90 min):**
- Instruction (25 min) → Practice (40 min) → Debrief (15 min) → Break (10 min)

**Virtual equivalent (2 × 45 min):**
- Segment A: Instruction (15 min) → Quick practice (15 min) → Check-in (5 min) → Break (10 min)
- Segment B: Deeper practice (20 min) → Share-out (10 min) → Debrief (10 min) → Break (5 min)

### 2. Front-Load Engagement

The first 5 minutes of every virtual segment must include active participation:
- Poll or survey question
- Chat waterfall ("Type one word that describes...")
- Reaction/emoji check-in
- Quick breakout room introduction

Never start with a monologue. Never start with slides.

### 3. Vary Interaction Every 10-15 Minutes

Rotate through these engagement modes:
- **Listen** (instructor presents): Max 10 minutes uninterrupted
- **Write** (individual reflection in chat or document): 2-5 minutes
- **Discuss** (breakout rooms or whole-group): 5-15 minutes
- **Do** (hands-on exercise with screen share or digital tool): 10-20 minutes
- **React** (polls, reactions, thumbs up/down): 1-2 minutes

### 4. Make Cameras Optional but Engagement Mandatory

- Don't require cameras (bandwidth, home environment, fatigue)
- DO require active participation: chat responses, polls, breakout contributions
- Use the chat as a participation equalizer (introverts often prefer it)
- Set norms at the start: "Cameras optional, participation required"

### 5. Plan for Technology Failure

Every activity must have a tech-failure backup:
- Breakout rooms fail → Large group discussion with hand-raising
- Screen share fails → Describe verbally + send link in chat
- Digital whiteboard fails → Individual reflection in chat
- Internet drops for participant → Recording available, async catch-up instructions

## Virtual Activity Substitutions

| In-Person Activity | Virtual Substitute | Notes |
|---|---|---|
| Table group discussion | Breakout rooms (3-4 people, 5-10 min) | Assign roles: facilitator, note-taker, reporter |
| Gallery walk | Virtual gallery (shared doc, Jamboard, Miro) | Async viewing + synchronous debrief |
| Post-it brainstorm | Digital whiteboard or chat waterfall | Miro, Jamboard, or just chat with emoji reactions |
| Physical demonstration | Screen share with narration | Record for replay; provide written steps |
| Pair work | Breakout rooms (2 people) | Shorter than in-person (5-7 min vs. 10-15 min) |
| Raised hand poll | Zoom poll, chat emoji, or Mentimeter | Results visible to all |
| Whiteboard diagram | Annotate on shared screen or digital whiteboard | Save and share screenshots |
| Role play | Breakout rooms with scenario cards | Provide written scenario in chat before breakout |
| Physical movement | Stretch break, off-screen reflection | "Stand up, grab water, write one thought on paper" |
| Print handouts | Shared Google Doc, PDF download, LMS | Send links in chat; confirm receipt |

## Hybrid-Specific Considerations

### The Equity Challenge

Hybrid is the hardest format because you must serve two audiences simultaneously. The default failure mode is that remote participants become passive observers.

**Equity Rules:**
1. If remote can't do it, in-room doesn't do it (or provide equivalent)
2. Facilitator addresses camera regularly (not just the room)
3. Chat is monitored continuously (assign a co-facilitator for chat)
4. In-room microphones capture all speakers (not just the facilitator)
5. Digital materials are the primary format (print is supplementary)

### Hybrid Technology Requirements

- Room camera: wide-angle showing facilitator + board/screen
- Participant camera: individual webcams for in-room participants (if possible)
- Room microphone: omnidirectional, picking up all speakers
- Screen sharing: facilitator's screen visible to both audiences
- Chat monitoring: dedicated person or second screen

### Hybrid Facilitation Model

| Role | Responsibility |
|---|---|
| **Lead facilitator** | Content delivery, in-room interaction, addresses camera |
| **Virtual co-facilitator** | Chat monitoring, breakout room management, tech troubleshooting |
| **Room support** (optional) | In-room logistics, microphone passing, time management |

## Virtual Workshop Schedule Template

### 1-Day Virtual (2 sessions × 3.5 hours)

```
Morning Session (9:00 - 12:30)
  09:00 - 09:15  Tech check + welcome
  09:15 - 09:30  Icebreaker / context setting
  09:30 - 10:15  Module 1 (45 min)
  10:15 - 10:25  Break
  10:25 - 11:10  Module 2 (45 min)
  11:10 - 11:20  Break
  11:20 - 12:05  Module 3 (45 min)
  12:05 - 12:15  Morning wrap-up + preview afternoon
  12:15 - 12:30  Buffer

--- Extended Lunch Break: 12:30 - 13:30 (60 min) ---

Afternoon Session (13:30 - 16:30)
  13:30 - 13:40  Re-engagement activity
  13:40 - 14:25  Module 4 (45 min)
  14:25 - 14:35  Break
  14:35 - 15:20  Module 5 (45 min)
  15:20 - 15:30  Break
  15:30 - 16:00  Capstone / integration activity (30 min)
  16:00 - 16:15  Wrap-up + action planning
  16:15 - 16:30  Buffer + Q&A
```

Total instruction time: ~5 hours (vs. 6 hours in-person)
Total elapsed time: 7.5 hours (vs. 7 hours in-person)
Break time: ~1.5 hours (vs. ~1 hour in-person)

### 2-Day Virtual (4 sessions × 3.5 hours)

Follow the same pattern across 4 half-day sessions over 2 days:
- Day 1 Morning: Modules 1-3
- Day 1 Afternoon: Modules 4-5
- Day 2 Morning: Modules 6-8
- Day 2 Afternoon: Modules 9-10 + Capstone

### Alternative: Multi-Day Virtual (4 × 2-hour sessions)

For audiences that can't do full-day virtual:
- Session 1 (Day 1): Modules 1-2
- Session 2 (Day 2): Modules 3-4
- Session 3 (Day 3): Modules 5-6
- Session 4 (Day 4): Review + Capstone

This spreads a 1-day workshop across 4 days, allowing practice between sessions.

## Platform-Specific Tips

### Zoom
- Use breakout room pre-assignment for repeated groups
- Polling is built-in (prepare polls in advance)
- Annotation tools work on shared screens
- Record to cloud for async review

### Microsoft Teams
- Breakout rooms require Teams Premium or manual channel creation
- Use Forms for polls (share link in chat)
- Whiteboard app integrates for collaborative diagramming
- Record to Stream/SharePoint

### Google Meet
- Breakout rooms available in Google Workspace
- Use Jamboard for collaborative whiteboarding
- Polls via embedded Google Forms
- Record to Google Drive

## Technology Checklist

### Before Workshop (1 week)
- [ ] Test all technology with a colleague
- [ ] Create breakout room assignments
- [ ] Prepare all polls/surveys
- [ ] Upload materials to shared folder
- [ ] Send tech check instructions to participants
- [ ] Confirm recording permissions

### Before Workshop (30 min)
- [ ] Open platform early
- [ ] Test screen share, breakout rooms, polls
- [ ] Verify recording is working
- [ ] Post welcome message in chat
- [ ] Open backup communication channel (email, Slack)

### During Workshop
- [ ] Monitor chat continuously
- [ ] Save chat transcript periodically
- [ ] Screenshot whiteboard/collaborative work
- [ ] Check breakout room progress (visit rooms)
- [ ] Save poll results

## Common Virtual Facilitation Mistakes

| Mistake | Problem | Fix |
|---|---|---|
| Lecturing for 20+ minutes | Participants multitask, disengage | Cap instruction at 10 min, then interact |
| Requiring cameras always on | Creates fatigue, inequity | Make participation mandatory, cameras optional |
| Not using chat | Misses participation channel | Ask chat questions every 10-15 min |
| Single facilitator for hybrid | Remote participants ignored | Assign dedicated virtual co-facilitator |
| No tech backup plan | Single failure derails the session | Pre-plan alternatives for every tech-dependent activity |
| Same timing as in-person | Exhaustion, poor retention | Reduce to 4 hrs/day, more breaks |
| Skipping tech check | Wasted first 20 minutes troubleshooting | Require tech check day before or 30 min early |
| No async component | No time for deeper reflection | Add pre-work and between-session assignments |
```

**Step 2: Commit**

```bash
git add -f course-curriculum-creator/skills/virtual-facilitation/SKILL.md
git commit -m "feat(skills): add virtual-facilitation skill for virtual/hybrid delivery"
```

---

## Task 3: Add Delivery Mode Awareness to `generate-outline`

**Files:**
- Modify: `commands/generate-outline.md`

**Step 1: Read current file**

Read `commands/generate-outline.md`.

**Step 2: Add virtual-facilitation skill loading**

In the Command Behavior section (numbered steps), add after the UDL skill loading:

```
3. If course-positioning.md has `deliveryMode: virtual` or `deliveryMode: hybrid`, load `virtual-facilitation` skill for mode-specific timing and activity guidance
```

Renumber subsequent steps.

**Step 3: Add delivery mode timing section**

After the existing "## Timing Allocation" section, add:

```markdown
## Delivery Mode Adjustments

Read `deliveryMode` from `01-planning/course-positioning.md` YAML frontmatter.

### If deliveryMode is "virtual"

Override default timing:
- **Max session length:** 3.5-4 hours (not 6)
- **Module duration:** 45-60 minutes (not 60-120)
- **Break frequency:** Every 45 minutes
- **Break duration:** 10 minutes minimum
- **Buffer time:** 15% (not 10%)
- **Total instruction time (1-day):** ~5 hours across 2 sessions with extended lunch
- **Total instruction time (2-day):** ~10 hours across 4 sessions

Apply from virtual-facilitation skill:
- Chunk large modules into 45-min segments
- Add engagement checkpoints every 15-20 minutes within modules
- Replace physical activities with virtual substitutes (breakout rooms, digital whiteboards, chat activities)
- Add tech check slot at workshop start (15 min)
- Add re-engagement activity after each break

### If deliveryMode is "hybrid"

Apply virtual timing constraints PLUS:
- Add 15 additional minutes at start for dual-setup verification
- Note co-facilitator requirement for each module
- Flag activities that need parallel in-room and remote versions
- Increase buffer to 20%

### If deliveryMode is "in-person" (or not specified)

No changes — use existing defaults.
```

**Step 4: Commit**

```bash
git add course-curriculum-creator/commands/generate-outline.md
git commit -m "feat(commands): add delivery mode awareness to generate-outline"
```

---

## Task 4: Add Delivery Mode Awareness to `generate-lesson-plans`

**Files:**
- Modify: `commands/generate-lesson-plans.md`

**Step 1: Read current file**

Read `commands/generate-lesson-plans.md`.

**Step 2: Add virtual-facilitation skill loading**

In the Command Behavior section, add after the UDL skill loading:

```
3. If course-positioning.md has `deliveryMode: virtual` or `deliveryMode: hybrid`, load `virtual-facilitation` skill for platform-specific activity design
```

Renumber subsequent steps.

**Step 3: Add delivery mode section**

After the existing "## Differentiation Guidance" section (added in Phase 2) and before the closing line, add:

```markdown
## Delivery Mode Adaptations

Read `deliveryMode` from `01-planning/course-positioning.md` YAML frontmatter.

### Virtual Mode Lesson Plan Adjustments

When generating lesson plans for virtual delivery:

**Module Flow Changes:**
- **Introduction:** Add tech check/engagement activity (poll, chat question) in first 2 minutes
- **Instruction:** Cap at 10 minutes before an interaction point (chat question, poll, or quick exercise)
- **Guided Practice:** Use breakout rooms (3-4 people, 5-10 min) instead of table groups
- **Independent Practice:** Provide digital workspace (shared doc, online tool); allow screen share for demonstration
- **Debrief:** Use chat waterfall or gallery view share-out instead of physical gallery walk

**Per-Module Additions:**
```markdown
**Virtual Facilitation Notes:**
- Platform features used: [breakout rooms, polls, shared whiteboard, annotation, chat]
- Engagement checkpoints: [every X minutes — specify the interaction type]
- Tech failure backup: [what to do if primary activity tool fails]
- Recording considerations: [what to record, privacy notes]
```

**Activity Substitution Guidance:**
For each activity in the lesson plan, if deliveryMode is virtual or hybrid, specify both:
- Primary activity (using digital tools)
- Backup activity (if technology fails)

### Hybrid Mode Lesson Plan Adjustments

Inherit all virtual adjustments PLUS:
- Note which activities run identically for both audiences vs. require parallel versions
- Specify co-facilitator responsibilities per module
- Add equity checks: "Can remote participants participate equally in this activity?"
```

**Step 4: Commit**

```bash
git add course-curriculum-creator/commands/generate-lesson-plans.md
git commit -m "feat(commands): add delivery mode adaptations to generate-lesson-plans"
```

---

## Task 5: Create `adapt-for-virtual` Command

**Files:**
- Create: `commands/adapt-for-virtual.md`

**Step 1: Write the command file**

```markdown
---
name: adapt-for-virtual
description: Adapt an existing in-person curriculum for virtual or hybrid delivery by adjusting timing, substituting activities, and adding technology requirements
argument-hint: "[--mode virtual|hybrid] [--platform zoom|teams|meet]"
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Edit
  - Skill
---

# Adapt for Virtual Command

Convert an existing in-person curriculum to virtual or hybrid delivery. This is a post-hoc adaptation command for courses designed as in-person — for new courses, use `--mode virtual` with `/create-course` instead.

## Why This Matters

An in-person curriculum cannot be delivered virtually without significant adaptation. A 6-hour in-person day becomes a 4-hour virtual day. Activities that work in a room don't work on a screen. This command systematically adapts every component while preserving pedagogical integrity.

## Prerequisites

- Must be run within a course project directory
- Must have `02-design/course-outline.md`
- Must have `02-design/lesson-plans.md`
- Recommended: `01-planning/learning-objectives.md`

## Command Behavior

1. Load `virtual-facilitation` skill for mode-specific guidance
2. Load `universal-design-for-learning` skill for accessibility
3. Read current course-positioning.md, outline, and lesson plans
4. Analyze each module for virtual adaptation needs
5. Generate adaptation report with specific changes
6. Optionally apply changes to existing files

## Adaptation Process

### Step 1: Assess Current Curriculum

For each module in the outline, classify activities:
- **Direct transfer**: Works as-is virtually (e.g., individual reflection, reading)
- **Needs substitution**: Requires a virtual equivalent (e.g., table discussion → breakout room)
- **Needs redesign**: Cannot be done virtually (e.g., physical lab work, room-based activities)

### Step 2: Adjust Timing

Using the virtual-facilitation skill timing constraints:
- Recalculate total available instruction time (4 hrs/day virtual vs. 6 hrs/day)
- If content doesn't fit: recommend splitting across more days or moving content to pre-work
- Break 90+ minute modules into 45-minute segments
- Add engagement checkpoints every 15-20 minutes
- Add tech check time at start
- Increase buffer from 10% to 15% (virtual) or 20% (hybrid)

### Step 3: Substitute Activities

For each activity needing substitution, recommend:

| Current Activity | Virtual Substitute | Platform Feature | Setup Needed |
|---|---|---|---|
| [Activity] | [Replacement] | [Zoom/Teams/Meet feature] | [What to prepare] |

### Step 4: Add Technology Requirements

Generate a technology requirements section:
- Platform features needed (breakout rooms, polls, whiteboard, recording)
- Participant requirements (internet speed, dual monitor recommended, headset)
- Facilitator requirements (second screen, backup internet, co-facilitator for hybrid)
- Pre-session tech check plan

### Step 5: Generate Adaptation Report

Write to `02-design/virtual-adaptation.md`:

```
---
title: Virtual Adaptation Report - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
originalMode: in-person
targetMode: [virtual|hybrid]
platform: [zoom|teams|meet|unspecified]
lastUpdated: YYYY-MM-DD
---

# Virtual Adaptation Report

## Summary

**Original format:** In-person, [X] day(s), [Y] hours instruction
**Adapted format:** [Virtual/Hybrid], [X] day(s), [Y] hours instruction
**Key changes:** [Count] activities substituted, [Count] modules restructured, [X] hours moved to pre-work

## Timing Changes

| Component | Original | Adapted | Change |
|---|---|---|---|
| Total instruction time | [X] hrs | [Y] hrs | [Delta] |
| Max session length | [X] hrs | [Y] hrs | [Delta] |
| Break frequency | Every [X] min | Every [Y] min | [Delta] |
| Buffer time | [X]% | [Y]% | [Delta] |

## Module-by-Module Adaptations

### Module [N]: [Title]

**Original timing:** [X] minutes
**Adapted timing:** [Y] minutes (or split into [A] + [B] minutes)

| Activity | Original | Virtual Adaptation | Notes |
|---|---|---|---|
| [Activity 1] | [Description] | [Virtual version] | [Why changed] |
| [Activity 2] | [Description] | [Virtual version] | [Why changed] |

### [Repeat for each module]

## Technology Requirements

### Platform: [Name]

**Required features:**
- [ ] [Feature 1]
- [ ] [Feature 2]

**Participant requirements:**
- [ ] [Requirement 1]
- [ ] [Requirement 2]

**Facilitator setup:**
- [ ] [Setup item 1]
- [ ] [Setup item 2]

## Content Moved to Pre-Work

[If instruction time was reduced, list content moved to asynchronous pre-work]

| Content | Original Location | Pre-Work Format | Est. Time |
|---|---|---|---|
| [Topic] | Module [N] | [Reading/video/exercise] | [X] min |

## Hybrid-Specific Notes (if --mode hybrid)

- Co-facilitator responsibilities per module
- Activities requiring parallel versions
- Equity checks for remote participants
- Technology setup for room + remote
```

## Post-Generation Actions

1. **Present summary**: "[N] modules adapted. [X] activities substituted, [Y] modules split. Total instruction time adjusted from [A] to [B] hours."
2. **Offer to apply changes**: "Would you like me to update the course-outline.md and lesson-plans.md with these adaptations? (This will modify existing files)"
3. **If applying**: Update course-positioning.md frontmatter with `deliveryMode`, update outline timing, update lesson plan activities. Mark all as version increment.

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `instructor_name`: Use in adaptation report
- No mode-specific settings at this time

## Validation Checks

- [ ] Total virtual instruction time ≤ 4 hours per day
- [ ] No module exceeds 60 minutes without a break
- [ ] Every physical activity has a virtual substitute
- [ ] Engagement checkpoints appear every 15-20 minutes
- [ ] Tech failure backup exists for every tech-dependent activity
- [ ] Pre-work additions (if any) are realistic (≤ 60 min total)

## Error Handling

**Not in course directory:**
- "Error: Not in a course project directory. Run this command from within a course created by `/create-course`."

**Missing outline or lesson plans:**
- "Error: Cannot adapt without course outline and lesson plans. Run `/generate-outline` and `/generate-lesson-plans` first."

**Already virtual:**
- "This course is already designed for [virtual/hybrid] delivery. No adaptation needed."

## Implementation Notes

**Date retrieval:**
```bash
TZ='America/New_York' date '+%Y-%m-%d'
```

**DO NOT:**
- Simply shorten timings without substituting activities
- Assume all activities transfer directly to virtual
- Ignore hybrid equity challenges
- Skip tech failure backups
- Move more than 25% of content to pre-work (defeats the purpose of the workshop)

---

Adapt thoughtfully — virtual is a different medium, not a lesser version of in-person. Every activity should be designed for the screen, not just tolerated on it.
```

**Step 2: Commit**

```bash
git add -f course-curriculum-creator/commands/adapt-for-virtual.md
git commit -m "feat(commands): add /adapt-for-virtual for converting in-person curricula"
```

---

## Task 6: Create `generate-review-package` Command

**Files:**
- Create: `commands/generate-review-package.md`

**Step 1: Write the command file**

```markdown
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
```

**Step 2: Commit**

```bash
git add -f course-curriculum-creator/commands/generate-review-package.md
git commit -m "feat(commands): add /generate-review-package for stakeholder/SME review"
```

---

## Task 7: Add Delivery Mode Validation to Quality Reviewer

**Files:**
- Modify: `agents/quality-reviewer.md`

**Step 1: Read current file**

Read `agents/quality-reviewer.md`.

**Step 2: Add virtual facilitation skill loading**

In section "## 1. Curriculum Discovery and Loading", after the UDL skill loading, add:

```
- If course has `deliveryMode: virtual` or `deliveryMode: hybrid` in positioning frontmatter, also load `virtual-facilitation` skill
```

**Step 3: Add delivery mode validation**

After the existing "## 5b. UDL & Accessibility Validation" section, add:

```markdown
## 5c. Delivery Mode Validation (if virtual or hybrid)

**Check curriculum for delivery mode compliance:**

### Virtual Timing
- Are sessions capped at 4 hours per day?
- Are breaks scheduled every 45 minutes?
- Are modules 60 minutes or less?
- Is buffer time at least 15%?

### Virtual Activities
- Do all activities have virtual equivalents (no physical-only activities)?
- Are engagement checkpoints present every 15-20 minutes?
- Do activities use appropriate platform features (breakout rooms, polls, chat)?
- Is there a tech failure backup for each tech-dependent activity?

### Hybrid Equity (if hybrid)
- Can remote participants participate equally in every activity?
- Is a co-facilitator role defined for virtual audience management?
- Are materials available in both digital and physical formats?

**Document findings:**
- Rate delivery mode readiness: READY / NEEDS ADJUSTMENTS / NOT ADAPTED
- Flag activities that won't work in the specified delivery mode
- Note missing technology requirements
```

**Step 4: Add to report template**

In section "## 6. Generate Validation Report", after the UDL section, add:

```markdown
### Delivery Mode Validation (if applicable)
**Status**: PASS / FAIL / N/A

- Timing compliance for virtual/hybrid constraints
- Activity compatibility with delivery mode
- Technology requirements completeness
- Hybrid equity assessment (if applicable)
```

**Step 5: Commit**

```bash
git add course-curriculum-creator/agents/quality-reviewer.md
git commit -m "feat(agents): add delivery mode validation to quality-reviewer"
```

---

## Task 8: Update README and Bump Version to 0.6.0

**Files:**
- Modify: `README.md`
- Modify: `.claude-plugin/plugin.json`

**Step 1: Update plugin.json**

Change `"version": "0.5.0"` to `"version": "0.6.0"`.

**Step 2: Update README.md**

Add to the appropriate sections:

**a) Commands table**: Add `adapt-for-virtual` and `generate-review-package` with descriptions.

**b) Skills section**: Add `virtual-facilitation` with description.

**c) What's New section**: Add v0.6.0 entry:

```markdown
### v0.6.0 - Delivery & Process
- New: `/adapt-for-virtual` command for converting in-person curricula to virtual/hybrid
- New: `/generate-review-package` command for stakeholder/SME review workflow
- New: `virtual-facilitation` skill with platform-specific guidance
- Enhanced: `--mode` flag in `/create-course` for virtual/hybrid from the start
- Enhanced: Delivery mode awareness in `/generate-outline` and `/generate-lesson-plans`
- Enhanced: Quality reviewer validates delivery mode compliance
```

**Step 3: Commit**

```bash
git add course-curriculum-creator/README.md course-curriculum-creator/.claude-plugin/plugin.json
git commit -m "docs: update README and bump version to 0.6.0 for Phase 3 features"
```

---

## Task 9: Final Integration Verification

**Step 1: Verify all new files exist**

```bash
ls -la course-curriculum-creator/skills/virtual-facilitation/SKILL.md
ls -la course-curriculum-creator/commands/adapt-for-virtual.md
ls -la course-curriculum-creator/commands/generate-review-package.md
```

**Step 2: Verify JSON and version**

```bash
python3 -c "import json; json.load(open('course-curriculum-creator/hooks/hooks.json')); print('hooks: VALID')"
python3 -c "import json; d=json.load(open('course-curriculum-creator/.claude-plugin/plugin.json')); print(f'version: {d[\"version\"]}')"
```
Expected: hooks VALID, version 0.6.0

**Step 3: Review git log**

```bash
git log --oneline 376a13e..HEAD
git diff --stat 376a13e..HEAD
```

---

## Summary of Phase 3 Deliverables

| # | Deliverable | Type | Files |
|---|---|---|---|
| 1 | `--mode` flag in create-course | Command modification | `commands/create-course.md` |
| 2 | `virtual-facilitation` skill | New skill | `skills/virtual-facilitation/SKILL.md` |
| 3 | Delivery mode in outline | Command modification | `commands/generate-outline.md` |
| 4 | Delivery mode in lesson plans | Command modification | `commands/generate-lesson-plans.md` |
| 5 | `/adapt-for-virtual` command | New command | `commands/adapt-for-virtual.md` |
| 6 | `/generate-review-package` command | New command | `commands/generate-review-package.md` |
| 7 | Delivery mode validation in reviewer | Agent modification | `agents/quality-reviewer.md` |
| 8 | README + version bump to 0.6.0 | Documentation | `README.md`, `plugin.json` |
