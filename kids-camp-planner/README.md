# Kids Camp Planner

A Claude Code plugin for planning and booking kids' day camps, March break programs, PA day coverage, and other school-break childcare in Ontario. Helps parents systematically research providers, build gap-free day-by-day schedules, manage budgets, and draft communications with camp providers.

## Overview

This plugin helps Ontario families navigate the complex puzzle of school-break childcare coverage. It handles summer camps, March break, PA days, and fall breaks (for private schools), considering budget constraints, commute logistics, pickup/dropoff schedules, dietary/medical needs, and children's interests.

### Key Features

- **Daily Scheduling**: Day-by-day schedule as the primary unit, with weekly summaries derived automatically
- **Full-Year Coverage**: Plan across all school-break periods — summer, PA days, winter break, March break — in one annual view
- **Schedule Planning**: Build gap-free coverage from last day of school through fall, including March break and PA days
- **Provider Research**: Systematically discover and document camp providers with structured comparison files (daily and weekly rates)
- **Budget Tracking**: Calculate costs across children, providers, and days/weeks with discount optimization and tax recovery estimates
- **Private School Support**: Handle calendar mismatches between private schools and public board PA day/break schedules
- **Email Drafting**: Generate inquiry, registration, waitlist, special needs, and cancellation emails
- **Pre-Saved Calendars**: Ships with TDSB, TCDSB, GIST, and KCS calendar data; extensible to other Ontario schools

## Installation

### From Marketplace
```bash
cc plugin install kids-camp-planner
```

### Local Development
```bash
cp -r kids-camp-planner ~/.claude/plugins/
cc plugin enable kids-camp-planner
```

## Quick Start

### 1. Set Up Your Family Profile
```
User: "Set up camp planner"
```
The setup skill will guide you through creating your family profile with children's details, school information, budget, and constraints.

### 2. Research Camp Providers
```
User: "Research summer camps near me"
```
The camp-researcher agent will search for providers in your area and create structured comparison files with daily and weekly rates.

### 3. Plan Your Summer
```
User: "Plan summer camp coverage"
```
The plan-summer skill builds a day-by-day schedule covering every weekday from school end to fall start. Each day gets a camp assignment per child, with costs looked up automatically from provider rates.

### 4. Generate Budget
```
User: "Create a camp budget for summer"
```
The budget-optimization skill calculates total costs with discounts and tax recovery estimates. Supports both daily and weekly rate calculations.

### 5. Draft Emails
```
User: "Draft an inquiry email to YMCA about their Adventure Camp"
```
The draft-email skill generates personalized emails using your family profile and provider details.

## How Daily Scheduling Works

The plugin uses **day-level scheduling** as its primary unit rather than weekly blocks. This supports real-world scenarios where parents book by the day (PA days, partial weeks, drop-in programs).

### Spreadsheet Structure

The sample budget spreadsheet (`examples/sample-budget.xlsx`) has four tabs:

| Tab | Role |
|-----|------|
| **Provider Comparison** | Camp rates with both daily and weekly columns, Total/Day and Total/Week formulas |
| **Daily Schedule** | Source of truth — one row per weekday with VLOOKUP formulas pulling costs from Provider Comparison |
| **Weekly Schedule** | Derived from Daily Schedule via SUMIF formulas |
| **Budget Summary** | All cost totals (camp fees, care, lunch, per-provider breakdown) derived from Daily Schedule |

Users only fill in four columns per row in the Daily Schedule: **date**, **week number**, and **camp name** per child. All costs are formula-driven.

### Annual Schedule

The sample annual schedule (`examples/sample-annual-schedule.md`) demonstrates full-year coverage across all school-break periods for a TCDSB elementary family:

| Period | Days |
|--------|------|
| Summer 2025 | 40 weekdays (8 weeks) |
| PA Days | 7 individual days |
| Winter Break | 7 camp-eligible days |
| March Break | 5 weekdays |
| **Total** | **59 days** |

## Components

### Skills (10)

| Skill | Purpose |
|-------|---------|
| **Setup** | Initialize research folder and family profile (including per-day budget target) |
| **Camp Planning** | Ontario camp evaluation knowledge and quality indicators (daily/weekly rate comparison) |
| **Budget Optimization** | Cost calculation with daily and weekly rate modes, discount optimization, tax recovery |
| **Plan Summer** | Day-by-day summer coverage scheduling with `--output-days` support |
| **Plan March Break** | March break planning with daily cost notes (handles 2-week private school breaks) |
| **Plan PA Days** | PA day lookup, single-day coverage, and daily rate budgeting |
| **Research Camps** | Provider discovery with daily rate ($/Day) column in comparison tables |
| **Draft Email** | Email composition including daily rate availability inquiries |
| **Add School Calendar** | Import school calendar from URL/PDF into reference data |
| **Generate Annual Schedule** | Consolidate summer, PA days, winter break, and March break into one annual view with markdown + xlsx output |

### Agents (2)

| Agent | Purpose |
|-------|---------|
| **Camp Researcher** | Autonomous web research creating provider files with daily and weekly rates |
| **Schedule Optimizer** | Builds and refines day-level schedules across constraints |

### Python Scripts (3)

| Script | Purpose |
|--------|---------|
| `budget_calculator.py` | Multi-child budget calculation with daily/weekly rates and discounts |
| `summer_dates.py` | Coverage window, week-by-week, and day-by-day date calculation |
| `generate_annual_schedule.py` | Consolidate spreadsheet + school calendar into annual schedule markdown and xlsx tab |

**Daily rate examples:**

```bash
# Day-by-day listing of summer coverage window
python3 skills/plan-summer/scripts/summer_dates.py \
  --year 2025 --last-school-day 2025-06-26 --output-days --format markdown

# Budget with daily rates (e.g., 7 PA days)
python3 skills/budget-optimization/scripts/budget_calculator.py \
  --kids 2 --days 7 --daily-rate 45 \
  --before-care-daily 8 --after-care-daily 8 --lunch-daily 6 \
  --format markdown

# Budget with weekly rates (backward compatible)
python3 skills/budget-optimization/scripts/budget_calculator.py \
  --kids 2 --weeks 8 --base-cost 300 \
  --before-care 50 --after-care 50 --lunch 35 \
  --sibling-discount 10 --format markdown
```

### Examples (3)

| File | Description |
|------|-------------|
| `sample-budget.xlsx` | Excel budget template with Provider Comparison, Daily Schedule, Weekly Schedule, and Budget Summary tabs |
| `sample-annual-schedule.md` | Full 2025-2026 TCDSB annual camp schedule (59 days across all periods) |
| `kids-camp-planner.local.md` | Example family profile with per-week and per-day budget targets |

## Configuration

### Family Profile

Copy the example profile to your project:
```bash
cp examples/kids-camp-planner.local.md .claude/kids-camp-planner.local.md
```

Or use the setup skill to create it interactively.

The profile includes:
- Children (names, DOB, interests, allergies, medical needs)
- School info (board, school name, public/private, calendar URL)
- Parents/guardians (work schedules, pickup/dropoff availability)
- Budget (total, per-child per-week, per-child per-day, flexibility, care preferences)
- Vacation/exclusion dates
- School year dates (overrides for private schools)

### Research Folder Structure

The plugin creates and maintains:
```
camp-research/
├── providers/            # Individual camp provider markdown files
├── school-calendars/     # Your school's calendar data
├── drafts/               # Draft emails
├── summer-YYYY/          # Summer schedule and budget
├── march-break-YYYY/     # March break schedule and budget
├── fall-break-YYYY/      # Fall break (private schools)
└── pa-days-YYYY-YYYY/    # PA day dates and coverage
```

## Private School Support

The plugin includes specific handling for private schools whose calendars don't align with Ontario public boards:

- **PA Day Misalignment**: Cross-references private school PA days against public board to identify when dedicated PA day programs won't be available
- **Extended March Break**: Handles 2-week breaks (e.g., GIST) where week 2 has no March break programs running
- **Fall Break**: Plans coverage for fall breaks that public boards don't have
- **Non-Standard School Start**: Supports schools starting before Labour Day

### Pre-Saved Calendar Data

Ships with calendar data for:
- **TDSB** (2025-2026): Toronto District School Board — PA days, holidays, breaks
- **TCDSB** (2025-2026): Toronto Catholic District School Board — PA days, holidays, breaks
- **GIST** (2025-2026, 2026-2027): German International School Toronto — full calendar with public board cross-reference
- **KCS** (2025-2026): Kingsway College School

See `RESEARCH-PLAN.md` for the roadmap to add more Ontario schools.

## Prerequisites

- Claude Code CLI
- Python 3.x (for budget calculator and date scripts)
- openpyxl (for Excel spreadsheet generation)
- [Anthropic xlsx skill](https://github.com/anthropics/skills/blob/main/skills/xlsx/SKILL.md) (optional, for Excel budget export)
- Google Calendar connectivity via external plugin/MCP (optional, for calendar integration)

## License

MIT
