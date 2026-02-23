---
name: generate-workshop-prep
description: Generate a dated preparation checklist for workshop delivery
argument-hint: "[--date YYYY-MM-DD]"
allowed-tools:
  - Bash
  - Read
  - Write
---

# Generate Workshop Prep Command

Generate a comprehensive, time-phased preparation checklist for delivering the workshop.

## Prerequisites

- Must be in a course project directory
- Should have lesson plans (`02-design/lesson-plans.md`) and artifacts (`04-materials/`)
- Workshop date should be known (provided as argument or prompted)

## Command Behavior

When user invokes `/generate-workshop-prep [--date YYYY-MM-DD]`:

1. **Get workshop date:**
   - Use `--date` argument if provided
   - Otherwise prompt: "When is the workshop scheduled? (YYYY-MM-DD)"

2. **Read curriculum files:**
   - `02-design/lesson-plans.md` for materials and activity requirements
   - `02-design/course-outline.md` for module structure and timing
   - `04-materials/` directory for available materials
   - `01-planning/course-positioning.md` for audience and logistics context

3. **Generate dated checklist** with specific dates calculated from workshop date

4. **Write output:** `04-materials/workshop-prep-checklist.md`

## Output Format

```markdown
---
title: Workshop Preparation Checklist - [Course Title]
workshopDate: YYYY-MM-DD
generatedDate: YYYY-MM-DD
status: active
---

# Workshop Preparation Checklist

## Course: [Course Title]
**Workshop Date:** [date]
**Duration:** [1-day or 2-day]
**Expected Participants:** [from positioning or TBD]

---

## T-2 Weeks ([calculated date])

### Content Preparation
- [ ] Review and finalize all lesson plans
- [ ] Customize examples and case studies for this specific audience
- [ ] Update any dated references or statistics
- [ ] Review learning objectives for clarity

### Logistics
- [ ] Confirm venue booking and room setup requirements
- [ ] Send pre-workshop communication to participants
- [ ] Send pre-assessment (if using `/generate-artifacts --type pre-assessment`)
- [ ] Confirm A/V equipment availability

### Materials
- [ ] Review student handout for completeness
- [ ] Review instructor guide for accuracy
- [ ] Identify any materials that need printing
- [ ] Prepare digital materials for distribution

---

## T-1 Week ([calculated date])

### Content Finalization
- [ ] Do a dry run of key activities (especially hands-on exercises)
- [ ] Prepare opening remarks and icebreaker
- [ ] Review timing for each module (use lesson plan timing summaries)
- [ ] Prepare backup activities for modules that might run short/long

### Materials Production
- [ ] Print student handouts ([N] copies + [buffer] extras)
- [ ] Print rubrics for assessment activities
- [ ] Prepare any digital templates or files students will need
- [ ] Create name badges or tent cards (if applicable)

### Logistics
- [ ] Send reminder to participants with logistics details
- [ ] Confirm catering for breaks and lunch
- [ ] Test all technology (projector, WiFi, software)
- [ ] Prepare sign-in sheet

---

## T-2 Days ([calculated date])

### Final Preparation
- [ ] Review participant list and any special requirements
- [ ] Finalize seating arrangement (tables for group work recommended)
- [ ] Organize materials by module (labeled folders or sections)
- [ ] Charge devices, test adapters

### Mental Preparation
- [ ] Review lesson plans one final time
- [ ] Note key transitions between modules
- [ ] Prepare for common questions (see instructor guide)
- [ ] Review pre-assessment results (if available)

---

## Day of Workshop ([workshop date])

### Setup (60-90 minutes before start)
- [ ] Arrive early to set up room
- [ ] Test projector, WiFi, microphone
- [ ] Distribute handouts to each seat
- [ ] Write WiFi credentials on whiteboard
- [ ] Set up any technology students will need
- [ ] Put up directional signs if needed
- [ ] Prepare facilitator station (notes, timer, water)

### Module Materials Ready
[For each module from course outline:]
- [ ] Module 1 ([title]): [specific materials from lesson plan]
- [ ] Module 2 ([title]): [specific materials from lesson plan]
- [ ] [Continue for all modules]

### During Workshop
- [ ] Start on time with welcome and agenda overview
- [ ] Use timer app for activity blocks
- [ ] Circulate during practice activities
- [ ] Take notes on what works and what doesn't
- [ ] Collect feedback during breaks
- [ ] Monitor energy levels, adjust pacing as needed

### Post-Workshop (same day)
- [ ] Collect evaluation forms or send digital survey
- [ ] Note immediate reflections while fresh
- [ ] Thank participants
- [ ] Collect any leftover materials
- [ ] Take photos of whiteboard notes, group work outputs

---

## Post-Workshop (within 1 week)

- [ ] Send post-assessment (if using)
- [ ] Send thank-you email with additional resources
- [ ] Process evaluation feedback: `/process-workshop-feedback`
- [ ] Update lesson plans with improvements noted
- [ ] Archive workshop materials and participant work
- [ ] Update course version if significant changes needed
```

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `instructor_name`: For checklist personalization

If settings file doesn't exist, use generic references.

## Error Handling

**Missing lesson plans:**
- Warn: "Lesson plans not found. Checklist will use generic material references. Generate lesson plans first with `/generate-lesson-plans` for a complete checklist."

**No workshop date provided:**
- Prompt user for date
- If user declines, use placeholder dates: "T-2 weeks", "T-1 week", etc. without specific dates

---

Generate practical, actionable preparation checklists that help instructors deliver polished workshops without forgetting critical preparation steps.
