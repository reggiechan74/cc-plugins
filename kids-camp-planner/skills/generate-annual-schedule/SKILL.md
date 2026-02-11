---
name: Generate Annual Schedule
description: This skill should be used when the user asks to "generate annual schedule", "update annual schedule", "create year schedule", "rebuild schedule", "refresh schedule from spreadsheet", "create full-year view", "build annual camp plan", "consolidate all camp days", "combine summer and PA days", or needs to produce a consolidated annual schedule covering summer, PA days, winter break, and March break from spreadsheet data and school calendar. Generates both markdown and Excel output.
version: 0.1.0
---

# Generate Annual Schedule

## Overview

**Locate research directory:** Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path (default: `camp-research`). All user data paths below are relative to this directory. The family profile is at `<research_dir>/family-profile.md`.

Generate a consolidated annual camp schedule that combines all school-break periods into a single view. Reads summer assignments from the spreadsheet's Daily Schedule tab, looks up non-summer dates from the school calendar, applies provider assignments for PA days and breaks, and produces both a markdown schedule and an updated spreadsheet with an "Annual Schedule" tab.

## When to Use

- After the summer schedule is built (Daily Schedule tab populated)
- When PA day, winter break, or March break plans are finalized
- To refresh the annual view after any schedule changes
- To produce a full-year cost summary

## Workflow

### Step 1: Gather Inputs

Read the family profile from `<research_dir>/family-profile.md` for:
- Children's names
- School board

Locate the required files:
- **Spreadsheet**: The budget xlsx (e.g., `examples/sample-budget.xlsx`) with Provider Comparison and Daily Schedule tabs
- **School calendar**: The school board's calendar file in `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/`

### Step 2: Confirm Non-Summer Assignments

The summer schedule comes from the spreadsheet. For non-summer periods, confirm or accept defaults:

| Period | Default Provider | Override? |
|--------|-----------------|-----------|
| PA Days | City of Toronto | Ask user if different |
| Winter Break | YMCA Cedar Glen | Ask user if different |
| March Break | YMCA Cedar Glen | Ask user if different |
| Fall Break | Same as --break-provider | Ask user if different |

Ask the user: "For PA days I'll use City of Toronto ($62/day) and for winter/March/fall breaks I'll use YMCA Cedar Glen ($87/day). Want to change any of these?"

If children need **different providers** on specific days (e.g., Emma does Science Camp for a PA day while Liam does YMCA), create an overrides JSON file. Every day can have a different provider per child — see the `--overrides` argument below.

### Step 3: Run the Generator Script

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/generate-annual-schedule/scripts/generate_annual_schedule.py \
  --xlsx examples/sample-budget.xlsx \
  --calendar ${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/public-boards/tcdsb.md \
  --children "Emma,Liam" \
  --pa-day-provider "City of Toronto" \
  --break-provider "YMCA Cedar Glen" \
  --output-md <research_dir>/annual-schedule-2025-2026.md \
  --update-xlsx
```

For per-child, per-day provider assignments, add an overrides file:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/generate-annual-schedule/scripts/generate_annual_schedule.py \
  --xlsx examples/sample-budget.xlsx \
  --calendar ${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/public-boards/tcdsb.md \
  --children "Emma,Liam" \
  --pa-day-provider "City of Toronto" \
  --break-provider "YMCA Cedar Glen" \
  --overrides <research_dir>/schedule-overrides.json \
  --output-md <research_dir>/annual-schedule-2025-2026.md \
  --update-xlsx
```

**Arguments:**
- `--xlsx`: Path to the budget spreadsheet (reads Provider Comparison + Daily Schedule tabs)
- `--calendar`: Path to the school calendar markdown file
- `--children`: Comma-separated children's names (must match spreadsheet column headers)
- `--pa-day-provider`: Default provider for PA day coverage (must exist in Provider Comparison tab)
- `--break-provider`: Default provider for winter break and March break (must exist in Provider Comparison tab)
- `--fall-break-provider`: Default provider for fall break coverage (defaults to same as `--break-provider`; must exist in Provider Comparison tab)
- `--overrides`: Optional JSON file with per-child, per-date provider overrides (see below)
- `--output-md`: Path for the generated markdown file
- `--update-xlsx`: Flag to add/replace "Annual Schedule" tab in the spreadsheet

**Overrides JSON format:**

The overrides file lets you assign different providers to each child on any date. Children not listed for a date fall back to the period default (`--pa-day-provider` or `--break-provider`). Summer dates can also be overridden (replacing the spreadsheet assignment for that child).

```json
{
  "2025-09-26": {"Emma": "Science Camp Toronto", "Liam": "YMCA Cedar Glen"},
  "2025-10-10": {"Liam": "YMCA Cedar Glen"},
  "2025-12-22": {"Emma": "City of Toronto"},
  "2026-03-16": {"Emma": "Science Camp Toronto", "Liam": "City of Toronto"}
}
```

All provider names in the overrides file must exist in the Provider Comparison tab.

**Multi-school families:** If children attend different schools, pass per-child calendars:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/generate-annual-schedule/scripts/generate_annual_schedule.py \
  --xlsx examples/sample-budget.xlsx \
  --calendar "Emma:${CLAUDE_PLUGIN_ROOT}/.../tdsb.md" \
  --calendar "Liam:${CLAUDE_PLUGIN_ROOT}/.../gist.md" \
  --children "Emma,Liam" \
  --pa-day-provider "City of Toronto" \
  --break-provider "YMCA Cedar Glen" \
  --output-md <research_dir>/annual-schedule-2025-2026.md \
  --update-xlsx
```

On days where only some children are off school, the others show "In school" with $0 cost.

### Step 4: Review Output

The script produces:

**Markdown file** with:
- Period-by-period sections (Summer, each PA Day, School Holidays, Fall Break, Winter Break, March Break)
- Day-by-day tables with per-child camp assignments and costs
- Period subtotals
- Annual summary table with total days and costs

**Updated spreadsheet** with:
- New "Annual Schedule" tab covering all ~64 days
- Dynamic column layout matching Daily Schedule: 3 prefix + (N x 6 child block) + 1 daily total (supports 1-4 children)
- VLOOKUP formulas referencing Provider Comparison tab for costs
- SUM formulas for totals
- Existing 4 tabs preserved untouched

### Step 5: Present Summary

Show the user the annual summary:

```
Annual Schedule Generated:
- Summer 2025: 40 days
- PA Days: 7 days
- School Holidays: 5 days
- Winter Break: 7 days
- March Break: 5 days
- Total: 64 days

Files updated:
- <research_dir>/annual-schedule-2025-2026.md
- examples/sample-budget.xlsx (Annual Schedule tab added)
```

## What the Script Reads

### From Provider Comparison tab (cols A-M, rows 4+):
- Provider names and daily rates (camp fee, before care, after care, lunch, total)
- Supports up to 3 rate sections: Summer, PA Day, and Break (Winter/March/Fall)
- PA Day and Break columns are optional; when empty, summer rates are used as fallback

### From Daily Schedule tab (dynamic columns, rows 4-43):
- Date, week number, and camp name per child (up to 4 children)
- Column layout: 3 prefix cols (Date, Day, Week#) + 6 cols per child + 1 Daily Total
- For 2 children: cols A-P (16 cols); for 3: cols A-V (22 cols); for 4: cols A-AB (28 cols)
- These are the summer assignments (40 rows)

### From school calendar markdown:
- PA day dates and purposes (from `### PA Days - Elementary` table)
- School holidays — single-day holidays like Thanksgiving, Family Day, Good Friday, Easter Monday, Victoria Day (from `### Holidays & Breaks`)
- Fall break dates, if applicable (from `Fall Break` row in `### Holidays & Breaks`)
- Winter break dates (from `Christmas Break` row in `### Holidays & Breaks`)
- March break dates (from `Mid-Winter Break (March Break)` row)

## Output Format

See `${CLAUDE_PLUGIN_ROOT}/examples/sample-annual-schedule.md` for the complete output format.

## Additional Resources

### Scripts

- **`scripts/generate_annual_schedule.py`** - Read spreadsheet + calendar, generate annual schedule markdown and xlsx tab. Supports `--update-xlsx` to add Annual Schedule tab to existing spreadsheet.

### Related Skills

- **Plan Summer**: Build the summer daily schedule that feeds into the annual view
- **Plan PA Days**: Look up PA day dates and find coverage programs
- **Plan March Break**: Plan March break camp coverage
- **Budget Optimization**: Calculate costs and apply discounts
