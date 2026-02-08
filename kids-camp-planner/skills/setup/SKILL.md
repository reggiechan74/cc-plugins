---
name: Camp Planner Setup
description: This skill should be used when the user asks to "set up camp planner", "initialize camp planning", "create family profile", "configure camp planner", "start camp planning", "set up kids camp", or mentions needing to configure their family details, children info, school board, or budget for camp planning. Provides guided setup workflow for the kids-camp-planner plugin.
version: 0.1.0
---

# Camp Planner Setup

## Overview

Initialize the kids-camp-planner workspace by creating the research folder structure and collecting the family profile. This is typically the first step before any camp planning activity.

## Setup Workflow

### Step 1: Create Research Folder Structure

Create the following directory structure in the user's current working directory:

```
camp-research/
├── providers/            # Individual camp provider files
├── drafts/               # Draft emails
├── school-calendars/     # Saved school calendar data for this family
│   ├── school-name.md    # Extracted dates, PA days, breaks
│   └── public-board.md   # Nearest public board for cross-reference
├── summer-YYYY/          # Summer period planning
│   ├── schedule.md
│   └── budget.md
├── march-break-YYYY/     # March break planning
│   ├── schedule.md
│   └── budget.md
├── fall-break-YYYY/      # Fall break planning (private schools)
│   ├── schedule.md
│   └── budget.md
└── pa-days-YYYY-YYYY/    # PA day coverage
    ├── dates.md
    └── coverage.md
```

**Notes:**
- The `fall-break-YYYY/` folder is only created if the school has a fall break (common in private schools, uncommon in Ontario public boards).
- The `school-calendars/` folder stores the user's specific school calendar data. Before web searching, check if pre-saved data exists in the plugin's reference data at `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/`. If found, copy the relevant data to the user's folder and confirm it matches the current year.

Use the current year for folder names. For PA days, use the current school year span (e.g., `pa-days-2025-2026`).

### Step 2: Collect Family Profile

Guide the user through providing their family information using AskUserQuestion. Collect information in logical groups to avoid overwhelming the user:

**Group 1 - Children:**
- Name, date of birth, interests/hobbies
- Allergies, dietary restrictions, medical notes
- Special accommodations needed

**Group 2 - School Information:**
- Public or private school
- School board name (e.g., TDSB, YRDSB, PDSB, OCDSB, DPCDSB, DDSB, HDSB)
- School name
- After collecting the school name/board, run the **3-Tier School Calendar Lookup**:
  1. Check `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/` for existing data
  2. If not found, ask if the user has the school calendar URL or PDF
  3. If not, conduct a web search, download any PDF found, and save both the PDF and extracted markdown data to the internal library
- This ensures calendar data is saved early for use by all other planning skills

**Group 3 - Parents/Guardians:**
- Name, work address, work schedule
- Pickup/dropoff availability and time constraints
- Earliest dropoff time, latest pickup time

**Group 4 - Location & Commute:**
- Home address
- Maximum commute time (minutes)

**Group 5 - Budget:**
- Total budget for summer / per period
- Target per child per week
- Budget flexibility (strict / moderate / flexible)
- Before-care and after-care willingness
- Lunch preference (pack / buy / either)

**Group 6 - Vacation & Exclusion Dates:**
- Family trips, vacations, dates camps are not needed
- Each with start date, end date, and description

**Group 7 - School Year Dates (optional overrides):**
- Last day of school (if known)
- First day of fall (if not the day after Labour Day)
- March break start and end dates (especially for private schools with extended breaks)
- Fall break dates (some private schools have a full week in Oct/Nov; public boards typically do not)
- Any other non-standard breaks or early dismissal dates

### Step 3: Generate the .local.md File

Write the collected profile to `.claude/kids-camp-planner.local.md` in YAML frontmatter format. Reference the example template at `${CLAUDE_PLUGIN_ROOT}/examples/kids-camp-planner.local.md` for the expected format.

Include a markdown body section titled "Family Notes" for any additional context the user provides (e.g., "Child 1 loved YMCA last year", "Grandparent available Wednesdays").

### Step 4: Confirm and Summarize

Present a summary of the created profile back to the user:
- Number of children and their ages
- School board and type
- Budget overview
- Key constraints (commute, care hours, dietary)
- Vacation dates noted
- Research folder location

Invite the user to review and edit the `.local.md` file directly if any corrections are needed.

## Re-Running Setup

If a `.claude/kids-camp-planner.local.md` file already exists, read it first and ask the user whether to:
1. Update specific fields (preserve existing data)
2. Start fresh (replace entirely)
3. Cancel (keep existing profile)

## Profile Validation

After generating the profile, verify:
- [ ] At least one child is listed with DOB
- [ ] School information is provided (board or school name)
- [ ] At least one parent/guardian with schedule
- [ ] Home address is provided
- [ ] Budget has at least one constraint specified
- [ ] Research folder structure was created successfully
