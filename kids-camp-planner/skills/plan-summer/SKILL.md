---
name: Plan Summer Camps
description: This skill should be used when the user asks to "plan summer camps", "plan summer coverage", "fill the summer schedule", "summer camp schedule", "cover the summer", "what camps for summer", "summer childcare plan", "plan from end of school to Labour Day", or needs help building a complete summer camp schedule covering the period from the last day of school through to the start of the next school year. Provides a structured workflow for gap-free summer camp coverage in Ontario.
version: 0.1.0
---

# Plan Summer Camps

## Overview

Build a complete summer camp schedule covering every weekday from the last day of school through to the day before the new school year begins (typically the day after Labour Day in Ontario). Identify coverage gaps, match camps to children's ages and interests, respect budget and logistics constraints, and produce a visual schedule.

## Planning Workflow

### Step 1: Determine the Summer Window

Read the family profile from `.claude/kids-camp-planner.local.md` for school dates. If school dates are not specified in the profile, use the **3-Tier School Calendar Lookup**:

**Tier 1 - Check internal library first:**
- Search `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/` for the family's school board/school
- If found and the school year matches, extract last day/first fall day directly

**Tier 2 - Ask the user:**
If no internal data exists, ask: "I don't have [school] calendar data saved. Do you have the school calendar URL or PDF handy?"
- If provided, extract dates and save to internal library using the add-school-calendar skill workflow

**Tier 3 - Web search:**
If the user doesn't have it, search for "[school board] school year calendar [year]"
- Download and save the PDF if one is found to `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/pdfs/`
- Extract dates and save structured data to the internal library

From the calendar data, determine:
1. **Last day of school**: For most Ontario public boards, the last day is typically the last Thursday or Friday of June.
2. **First day of fall**: Usually the day after Labour Day for public schools. **For private schools, the fall start date may differ significantly** - some start before Labour Day (e.g., German International School Toronto starts in late August). Always verify from the school's actual calendar rather than assuming Labour Day + 1.
3. **Coverage window**: First weekday after last school day through last weekday before first school day.

**Private school note:** Private schools may have a shorter or longer summer than public schools depending on their start/end dates. Always use the actual school calendar dates, not the public board defaults. Pass the exact dates to the summer_dates.py script via `--last-school-day` and `--first-fall-day`.

Run the date calculator to determine the exact window:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/plan-summer/scripts/summer_dates.py \
  --year 2025 \
  --last-school-day 2025-06-26 \
  --first-fall-day 2025-09-02
```

The script outputs: total weekdays, total weeks, and a week-by-week date range listing.

### Step 2: Map Exclusion Dates

From the family profile, identify vacation and exclusion dates. Subtract these from the coverage window to determine **weeks/days that need camp coverage**.

Present to user:
```
Summer 2025 Coverage Needs:
- Total window: June 30 - August 29 (9 weeks)
- Vacation: July 14-18 (cottage), Aug 11-15 (camping)
- Weeks needing coverage: 7 weeks
- Days needing coverage: 35 weekdays
```

### Step 3: Gather Camp Options

Check if provider files already exist in `camp-research/providers/`. If not, suggest using the research-camps skill or camp-researcher agent to find options.

For each child, filter providers by:
- Age eligibility
- Location / commute constraint
- Budget range
- Availability during needed weeks
- Program interest alignment

### Step 4: Build the Schedule

Create a week-by-week assignment considering:

**Hard constraints (must satisfy):**
- Every coverage day has a camp assigned for every child
- Camp accepts child's age group during that week
- Pickup/dropoff timing works with parent schedules
- Budget is within limits

**Soft constraints (optimize for):**
- Children's interest alignment
- Minimize provider switching (reduces transition stress)
- Sibling discounts (same provider same week)
- Proximity to home during non-work days
- Variety across the summer (mix of activities)

**Schedule format:**

```markdown
# Summer 2025 Schedule

| Week | Dates | Child 1 | Child 2 | Notes |
|------|-------|---------|---------|-------|
| 1 | Jun 30 - Jul 4 | YMCA Day Camp | YMCA Day Camp | Sibling discount |
| 2 | Jul 7 - Jul 11 | City Swim Camp | City Art Camp | Different interests |
| 3 | Jul 14 - Jul 18 | VACATION | VACATION | Cottage trip |
| ... | ... | ... | ... | ... |
```

### Step 5: Identify Gaps and Issues

After building the initial schedule, check for:
- [ ] Any uncovered weekdays
- [ ] Weeks where no suitable camp was found
- [ ] Budget overruns (run budget-optimization skill)
- [ ] Logistics conflicts (overlapping pickup times for different camps)
- [ ] Waitlisted programs that need backup plans

Flag issues clearly and suggest alternatives.

### Step 6: Generate Output Files

Create or update:
1. **`camp-research/summer-YYYY/schedule.md`** - The week-by-week schedule table
2. **`camp-research/summer-YYYY/budget.md`** - Budget summary (use budget-optimization skill)
3. **Provider files** in `camp-research/providers/` for any new providers identified

### Step 7: Present for Review

Summarize the plan for the user:
- Total weeks covered vs. vacation
- Number of providers used
- Total estimated cost vs. budget
- Key decisions that need user input (waitlists, alternatives)
- Next steps (register, draft inquiry emails, etc.)

## Handling Common Scenarios

### Popular camps are full
- Check waitlist policies and suggest adding to waitlist
- Identify alternative providers with similar programming
- Consider municipal programs as backup (usually have more capacity)

### Budget is too tight
- Trigger budget-optimization skill for cost reduction strategies
- Suggest mixing expensive specialty weeks with cheaper general camps
- Identify subsidy eligibility

### Different needs per child
- Allow different providers per child per week
- Consider camps that accept both age groups for sibling discount
- Balance individual interests with logistics simplicity

### Partial weeks
- First/last week of summer may be partial
- Some providers offer daily rates for partial weeks
- Municipal drop-in programs work well for odd days

## Additional Resources

### Scripts

- **`scripts/summer_dates.py`** - Calculate summer coverage window, weekday counts, and week-by-week date ranges given school year boundaries
