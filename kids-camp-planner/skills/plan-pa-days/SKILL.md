---
name: Plan PA Days
description: This skill should be used when the user asks to "plan PA days", "find PA day programs", "PA day coverage", "PD day camps", "professional activity day", "what to do on PA days", "look up PA days", "school PA day schedule", or needs help finding PA day dates and arranging single-day childcare coverage for Ontario Professional Activity days. Provides a workflow for looking up PA days and finding programs.
version: 0.1.0
---

# Plan PA Days

## Overview

**Locate research directory:** Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path (default: `camp-research`). All user data paths below are relative to this directory. The family profile is at `<research_dir>/family-profile.md`.

Professional Activity (PA) days are single days during the Ontario school year when students stay home while teachers participate in professional development. Plan coverage by first identifying PA day dates from the school board calendar, then finding suitable single-day programs. PA days are also called PD days (Professional Development days) in some boards.

## PA Day Lookup Workflow

### Step 1: Identify PA Day Dates

Use the **3-Tier School Calendar Lookup** to find PA day dates:

**Tier 1 - Check internal library first:**
- Read the school board/name from `<research_dir>/family-profile.md`
- Search `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/` for a matching file
- If found and the school year matches, extract PA day dates directly. Inform the user: "Found [school] PA days in the internal library."

**Tier 2 - Ask the user:**
If no internal data exists, ask: "I don't have [school] calendar data saved. Do you have the school calendar URL or PDF handy?"
- If the user provides a URL or PDF, read the document to extract PA day dates
- Save the extracted data to the internal library using the add-school-calendar skill workflow

**Tier 3 - Web search:**
If the user doesn't have it, conduct a web search for "[school board name] school year calendar [current school year]"
- **Ensure the correct school year is retrieved** (e.g., 2025-2026, not previous year)
- Look for the official board website result, not third-party aggregators
- If a PDF is found, download and save it to `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/pdfs/`
- Extract all PA day dates from the calendar and save the structured data to the internal library

**Common Ontario school boards and typical PA day patterns:**
- Most boards have 6-7 PA days per school year
- Typically: 1-2 in September/October, 1 in November, 1 in January/February, 1-2 in April/May/June
- The first day of school in September is often a PA day (staggered entry)
- PA days are board-wide; individual school PA days may also exist (less common)

**Multi-board families:** If children attend different schools, look up PA days per school. Cross-reference to identify:
- **Both off**: All children need coverage (standard PA day)
- **Partial**: Only some children off (mark others "In school")
Present the merged PA day table showing which children are off each day.

**For private schools (CRITICAL - different handling required):**
- Ask the user for their school's specific calendar URL or PDF
- Private schools may call these "in-service days", "faculty days", or "professional development days"
- Dates will almost certainly differ from the local public board calendar
- **Provider availability problem**: Most PA day program providers (municipal rec centres, YMCA, etc.) schedule their PA day programs to align with the local public school board calendar, NOT private school calendars. This means:
  - On a private school PA day that is NOT a public board PA day, dedicated PA day programs may not be running
  - Fall back to: before/after school care programs that run all school days, general day camp operators that offer drop-in days, or parent/family coverage
  - On a public board PA day when the private school IS in session, no coverage is needed (but good to note for carpooling awareness)
- **Strategy for private school families**: Cross-reference private school PA days against the local public board PA days. Categorize each private school PA day as:
  - **Aligned**: Same date as public board PA day (easy - programs available)
  - **Misaligned**: Only private school is off (harder - fewer program options)
  - Present this comparison to the user so they can plan accordingly

### Step 2: Present PA Day Dates

Create a clear listing:

```markdown
# PA Days [School Year]
## [School Board Name]

| # | Date | Day of Week | Notes |
|---|------|-------------|-------|
| 1 | Sep 2, 2025 | Tuesday | First day - staggered entry |
| 2 | Oct 10, 2025 | Friday | Before Thanksgiving weekend |
| 3 | Nov 21, 2025 | Friday | |
| 4 | Jan 30, 2026 | Friday | |
| 5 | Apr 17, 2026 | Friday | |
| 6 | Jun 5, 2026 | Friday | |
```

Ask the user to confirm these dates are correct before planning coverage.

### Step 3: Determine Coverage Needs

For each PA day, check:
- Is it adjacent to a weekend or holiday (making a long weekend)?
- Does it fall during a period already covered (e.g., March break)?
- Can a parent take the day off? (check work schedules from profile)
- Is it a "staggered entry" day where only some grades are off?

Categorize each PA day:
- **Needs coverage**: No parent available
- **Covered by parent**: Parent taking off or working from home
- **Adjacent to break**: Already handled by break planning
- **TBD**: Need to check with user

### Step 4: Find PA Day Programs

PA day programs are different from weekly camps:

**Where to look:**
- Municipal recreation centres (most reliable for PA day programs)
- YMCA/YWCA locations
- Private camp operators (many offer PA day drop-ins)
- School-run extended care programs (if available)
- Local community centres
- Sports facilities (skating, swimming, gymnastics one-day programs)

**PA day program considerations:**
- Registration often opens 2-4 weeks before the PA day
- Municipal programs are typically the most affordable ($30-60/day)
- Some providers require advance registration; others accept drop-ins
- Hours may differ from regular camp hours
- Lunch is usually bring-your-own for single-day programs

**Search strategy:**
- Web search for "[municipality] PA day programs [year]" or "[municipality] PD day camp"
- Check municipal recreation registration portals
- Look for YMCA PA day programs in the area
- Ask if the school's before/after care program runs on PA days

### Step 5: Build PA Day Coverage Plan

For each PA day needing coverage:

```markdown
# PA Day Coverage Plan [School Year]

| Date | Provider | Hours | Cost | Dropoff | Pickup | Lunch |
|------|----------|-------|------|---------|--------|-------|
| Oct 10 | City Rec Centre | 9am-4pm | $45/child | Parent 1 | Parent 2 | Pack |
| Nov 21 | YMCA Day Program | 7:30am-6pm | $55/child | Parent 1 | Parent 1 | Pack |
| Jan 30 | School Extended Care | 7am-6pm | $35/child | Parent 2 | Parent 1 | Pack |
```

### Step 6: Generate Output Files

Create or update:
1. **`<research_dir>/pa-days-YYYY-YYYY/dates.md`** - All PA day dates with status
2. **`<research_dir>/pa-days-YYYY-YYYY/coverage.md`** - Coverage plan for each PA day
3. **Provider files** in `<research_dir>/providers/` for PA day program providers

### Step 7: Set Up Reminders

PA day program registration is time-sensitive. Advise the user:
- Set calendar reminders 3-4 weeks before each PA day to check registration
- Bookmark municipal recreation portals for quick access
- Keep a list of reliable PA day providers for repeat use
- Check if school extended care program automatically covers PA days

## Tips for PA Day Planning

### Batch Planning
- At the start of each school year, look up all PA days at once
- Register for municipal programs as early as possible
- Identify 2-3 reliable PA day providers to rotate between

### Cost Efficiency
- Municipal programs: $30-60/day (best value)
- YMCA programs: $40-65/day (good quality, sliding scale)
- Private programs: $50-90/day (specialty activities)
- School extended care: $25-45/day (if available, most convenient)

PA days are inherently daily — use the budget calculator's `--daily-rate` flag for accurate single-day costing:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/budget-optimization/scripts/budget_calculator.py \
  --kids 2 --days 1 --daily-rate 45 --before-care-daily 8 --after-care-daily 8 \
  --format markdown
```

### Friday PA Days
Most PA days fall on Fridays, creating long weekends. Consider:
- Parent taking a flex day (if work allows)
- Grandparent or family member coverage
- Combining with a mini family outing
- Half-day program + parent afternoon off

## Related Skills

- **Generate Annual Schedule** - After identifying PA day coverage, use the generate-annual-schedule skill to consolidate all school-break periods (summer, PA days, winter break, March break) into one annual view.
