---
name: Plan March Break
description: This skill should be used when the user asks to "plan March break", "plan March break camps", "March break coverage", "March break childcare", "what to do for March break", "book March break camp", or needs help finding and scheduling camp programs for the Ontario March break week. Provides a structured workflow for March break camp planning.
version: 0.1.0
---

# Plan March Break

## Overview

Plan camp coverage for the Ontario March break week (typically the third week of March). March break is a single week, making it simpler than summer planning but with its own considerations: limited availability, different provider landscape, and shorter planning window.

## Planning Workflow

### Step 1: Confirm March Break Dates

Ontario March break is set by the Ministry of Education. Determine the exact dates using the **3-Tier School Calendar Lookup**:

1. Read the family profile from `.claude/kids-camp-planner.local.md` for school board/school info
2. **Tier 1 - Check internal library**: Search `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/` for the family's school. If found, extract March break dates directly.
3. **Tier 2 - Ask the user**: If no internal data, ask: "Do you have the school calendar URL or PDF handy?" If provided, extract dates and save to internal library.
4. **Tier 3 - Web search**: If the user doesn't have it, search for "[school board] March break [year]". Download and save any PDF found. Extract dates and save to internal library.
5. For private schools, note that break dates may differ significantly from public boards.

**Typical pattern:** Third Monday through Friday in March, but confirm annually as it occasionally shifts.

**Private school extended breaks (CRITICAL):**
Some private schools have a longer March break than the public board. For example, German International School Toronto has a 2-week March break compared to TDSB's 1-week break. When the private school break is longer:
- **Week 1** (overlapping with public board March break): March break camp programs will be widely available from all providers
- **Week 2** (private school only, public schools in session): March break-specific programs will NOT be running. Fall back to:
  - General day camp operators offering weekly programs year-round
  - Before/after school care programs that accept drop-ins
  - PA day-style single-day programs (if any are running)
  - Parent/family coverage
- Present this split clearly to the user: "Week 1 has full March break program availability. Week 2 will have limited options since public schools are in session."
- Budget separately for each week since costs and provider types may differ significantly

### Step 2: Check Family Availability

From the family profile, determine:
- Is the full week needed, or are parents taking time off for part of it?
- Any family trips planned during March break?
- Budget allocated for March break specifically

Present coverage needs:
```
March Break 2026: March 16-20
- Days needing coverage: [X] of 5
- Children needing coverage: [list]
- Budget for this period: $[X]
```

### Step 3: Research March Break Programs

March break programs differ from summer camps:

**Where to look:**
- Municipal recreation departments (registration typically opens November-January)
- YMCA/YWCA March break camps
- Museums and science centres (ROM, Ontario Science Centre, local museums)
- Sports facilities and clubs
- Arts organizations (theatre companies, art galleries)
- Private camp operators (many summer camps run March break programs)
- Ski/outdoor recreation programs

**March break considerations:**
- Capacity is more limited than summer (fewer providers run March break programs)
- Registration opens earlier relative to the break (November-January)
- Costs may be higher per day than equivalent summer programs
- Indoor programming is more important (weather is unpredictable in March)
- Some programs offer half-week options

### Step 4: Evaluate and Compare

For each March break option, collect:
- Full-week vs. daily registration available
- Hours (core hours, before/after care)
- Indoor vs. outdoor activity ratio
- Lunch included or bring-your-own
- Cost for the full week
- Location and commute time

Use the camp-planning skill's evaluation criteria for quality assessment.

### Step 5: Build the Schedule

March break is a single week, so the schedule is simpler:

```markdown
# March Break 2026 Schedule (March 16-20)

| Day | Child 1 | Child 2 | Dropoff | Pickup |
|-----|---------|---------|---------|--------|
| Mon | City Science Camp | City Science Camp | Parent 1, 8:30am | Parent 2, 4:30pm |
| Tue | City Science Camp | City Science Camp | Parent 1, 8:30am | Parent 2, 4:30pm |
| Wed | City Science Camp | City Science Camp | Parent 1, 8:30am | Grandparent, 3:00pm |
| Thu | City Science Camp | City Science Camp | Parent 1, 8:30am | Parent 2, 4:30pm |
| Fri | City Science Camp | City Science Camp | Parent 1, 8:30am | Parent 1, 4:00pm |
```

### Step 6: Generate Output Files

Create or update:
1. **`camp-research/march-break-YYYY/schedule.md`** - Daily schedule
2. **`camp-research/march-break-YYYY/budget.md`** - Cost breakdown (use budget-optimization skill)
3. **Provider files** in `camp-research/providers/` for any new providers

### Step 7: Registration Reminders

March break programs fill quickly. Advise the user on:
- Registration deadlines for selected programs
- Backup options if first choice is full
- Waitlist strategies
- Whether to draft inquiry emails (use draft-email skill)

## Key Differences from Summer Planning

| Aspect | Summer | March Break |
|--------|--------|-------------|
| Duration | 8-9 weeks | 1 week |
| Provider availability | High | Limited |
| Registration timing | Jan-Feb | Nov-Jan |
| Weather factor | Outdoor-heavy | Indoor important |
| Cost per week | Standard | Sometimes higher |
| Half-week options | Rare | More common |
| Mixing providers | Common | Usually one provider |

## Additional Resources

For detailed private school March break test cases (including 2-week break scenarios with real GIST vs TDSB data), consult `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/private-school-test-cases.md` (see Test Case 2: Extended March Break).
