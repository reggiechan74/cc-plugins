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
