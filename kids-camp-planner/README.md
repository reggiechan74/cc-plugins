# Kids Camp Planner

A Claude Code plugin for planning and booking kids' day camps, March break programs, PA day coverage, and other school-break childcare in Ontario. Helps parents systematically research providers, build gap-free schedules, manage budgets, and draft communications with camp providers.

## Overview

This plugin helps Ontario families navigate the complex puzzle of school-break childcare coverage. It handles summer camps, March break, PA days, and fall breaks (for private schools), considering budget constraints, commute logistics, pickup/dropoff schedules, dietary/medical needs, and children's interests.

### Key Features

- **Schedule Planning**: Build gap-free coverage from last day of school through fall, including March break and PA days
- **Provider Research**: Systematically discover and document camp providers with structured comparison files
- **Budget Tracking**: Calculate costs across children, providers, and weeks with discount optimization and tax recovery estimates
- **Private School Support**: Handle calendar mismatches between private schools and public board PA day/break schedules
- **Email Drafting**: Generate inquiry, registration, waitlist, special needs, and cancellation emails
- **Pre-Saved Calendars**: Ships with TDSB and GIST calendar data; extensible to other Ontario schools

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
The camp-researcher agent will search for providers in your area and create structured comparison files.

### 3. Plan Your Summer
```
User: "Plan summer camp coverage"
```
The plan-summer skill builds a week-by-week schedule covering every day from school end to fall start.

### 4. Generate Budget
```
User: "Create a camp budget for summer"
```
The budget-optimization skill calculates total costs with discounts and tax recovery estimates.

### 5. Draft Emails
```
User: "Draft an inquiry email to YMCA about their Adventure Camp"
```
The draft-email skill generates personalized emails using your family profile and provider details.

## Components

### Skills (9)

| Skill | Purpose |
|-------|---------|
| **Setup** | Initialize research folder and family profile |
| **Camp Planning** | Ontario camp evaluation knowledge and quality indicators |
| **Budget Optimization** | Cost calculation, discount optimization, tax recovery |
| **Plan Summer** | Full summer coverage scheduling |
| **Plan March Break** | March break planning (handles 2-week private school breaks) |
| **Plan PA Days** | PA day lookup and single-day coverage |
| **Research Camps** | Provider discovery and documentation |
| **Draft Email** | Email composition for camp communications |
| **Add School Calendar** | Import school calendar from URL/PDF into reference data |

### Agents (2)

| Agent | Purpose |
|-------|---------|
| **Camp Researcher** | Autonomous web research creating provider files |
| **Schedule Optimizer** | Builds and refines schedules across constraints |

### Python Scripts (2)

| Script | Purpose |
|--------|---------|
| `budget_calculator.py` | Multi-child budget calculation with discounts |
| `summer_dates.py` | Coverage window and week-by-week date calculation |

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
- Budget (total, per-child, flexibility, care preferences)
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
- **TDSB** (2025-2026): PA days, holidays, breaks
- **German International School Toronto** (2025-2026, 2026-2027): Full calendar with public board cross-reference

See `RESEARCH-PLAN.md` for the roadmap to add more Ontario schools.

## Prerequisites

- Claude Code CLI
- Python 3.x (for budget calculator and date scripts)
- [Anthropic xlsx skill](https://github.com/anthropics/skills/blob/main/skills/xlsx/SKILL.md) (optional, for Excel budget export)
- Google Calendar connectivity via external plugin/MCP (optional, for calendar integration)

## License

MIT
