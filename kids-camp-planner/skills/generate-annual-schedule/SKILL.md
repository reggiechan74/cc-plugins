---
name: generate-annual-schedule
description: This skill should be used when the user asks to "generate annual schedule", "update annual schedule", "create year schedule", "rebuild schedule", "refresh schedule from spreadsheet", "create full-year view", "build annual camp plan", "consolidate all camp days", "combine summer and PA days", or needs to produce a consolidated annual schedule covering summer, PA days, winter break, and March break from spreadsheet data and school calendar. Generates both markdown and Excel output.
---

# Generate Annual Schedule

## Overview

Generate a consolidated annual camp schedule that combines all school-break periods into a single view. Reads summer assignments from the spreadsheet's Daily Schedule tab, looks up non-summer dates from the school calendar, applies provider assignments for PA days and breaks, and produces both a markdown schedule and an updated spreadsheet with an "Annual Schedule" tab.

## When to Use

- After the summer schedule is built (Daily Schedule tab populated)
- When PA day, winter break, or March break plans are finalized
- To refresh the annual view after any schedule changes
- To produce a full-year cost summary

## Workflow

### Step 1: Gather Inputs

Read the family profile from `.claude/kids-camp-planner.local.md` for:
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

Ask the user: "For PA days I'll use City of Toronto ($62/day) and for winter/March breaks I'll use YMCA Cedar Glen ($87/day). Want to change any of these?"

### Step 3: Run the Generator Script

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/generate-annual-schedule/scripts/generate_annual_schedule.py \
  --xlsx examples/sample-budget.xlsx \
  --calendar ${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/public-boards/tcdsb.md \
  --children "Emma,Liam" \
  --pa-day-provider "City of Toronto" \
  --break-provider "YMCA Cedar Glen" \
  --output-md camp-research/annual-schedule-2025-2026.md \
  --update-xlsx
```

**Arguments:**
- `--xlsx`: Path to the budget spreadsheet (reads Provider Comparison + Daily Schedule tabs)
- `--calendar`: Path to the school calendar markdown file
- `--children`: Comma-separated children's names (must match spreadsheet column headers)
- `--pa-day-provider`: Provider name for PA day coverage (must exist in Provider Comparison tab)
- `--break-provider`: Provider name for winter break and March break (must exist in Provider Comparison tab)
- `--output-md`: Path for the generated markdown file
- `--update-xlsx`: Flag to add/replace "Annual Schedule" tab in the spreadsheet

### Step 4: Review Output

The script produces:

**Markdown file** with:
- Period-by-period sections (Summer, each PA Day, Winter Break, March Break)
- Day-by-day tables with per-child camp assignments and costs
- Period subtotals
- Annual summary table with total days and costs

**Updated spreadsheet** with:
- New "Annual Schedule" tab covering all 59 days
- Same column layout as Daily Schedule (A-P, 16 columns)
- VLOOKUP formulas referencing Provider Comparison tab for costs
- SUM formulas for totals
- Existing 4 tabs preserved untouched

### Step 5: Present Summary

Show the user the annual summary:

```
Annual Schedule Generated:
- Summer 2025: 40 days
- PA Days: 7 days
- Winter Break: 7 days
- March Break: 5 days
- Total: 59 days

Files updated:
- camp-research/annual-schedule-2025-2026.md
- examples/sample-budget.xlsx (Annual Schedule tab added)
```

## What the Script Reads

### From Provider Comparison tab (cols A-F, rows 4-6):
- Provider names and daily rates (camp fee, before care, after care, lunch, total)

### From Daily Schedule tab (cols A, C, D, J, rows 4-43):
- Date, week number, child 1 camp name, child 2 camp name
- These are the summer assignments (40 rows)

### From school calendar markdown:
- PA day dates and purposes (from `### PA Days - Elementary` table)
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
