---
name: Camp Planner Setup
description: This skill should be used when the user asks to "set up camp planner", "initialize camp planning", "create family profile", "configure camp planner", "start camp planning", "set up kids camp", or mentions needing to configure their family details, children info, school board, or budget for camp planning. Provides guided setup workflow for the kids-camp-planner plugin.
version: 0.2.0
---

# Camp Planner Setup

## Overview

Initialize the kids-camp-planner workspace by creating the research folder structure, seeding it with templates and examples, collecting the family profile, and configuring API keys. This is typically the first step before any camp planning activity.

**Locate research directory:** Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path (default: `camp-research`). All user data paths below are relative to this directory. The family profile is at `<research_dir>/family-profile.md`.

## Setup Workflow

### Step 0: Choose Research Directory Name

Ask the user what they'd like to name their research directory using AskUserQuestion:
- Default: `camp-research` (recommended)
- The user may choose a custom name (e.g., `camps`, `camp-planning`, `kids-camps`)
- This directory will hold all camp research data: providers, schedules, budgets, drafts, etc.

Store the chosen name — it will be written to `.claude/kids-camp-planner.local.md` as `research_dir` in Step 3.

### Step 1: Create Research Folder Structure and Seed Files

Create the following directory structure in the user's current working directory, using the research directory name chosen in Step 0:

```
<research_dir>/
├── family-profile.md             # Full family profile (seeded from plugin, filled in Step 2)
├── providers/                    # Individual camp provider files
├── templates/
│   └── provider-template.md      # Provider file template for reference
├── examples/
│   ├── ymca-cedar-glen.md        # YMCA Cedar Glen example
│   └── boulderz-etobicoke.md     # Boulderz Climbing example
├── drafts/                       # Draft emails
├── school-calendars/             # Saved school calendar data for this family
├── summer-YYYY/                  # Summer period planning
├── march-break-YYYY/             # March break planning
├── fall-break-YYYY/              # Fall break planning (private schools)
└── pa-days-YYYY-YYYY/            # PA day coverage
```

**Seed files from plugin:** Copy the following files from the plugin into the research directory so the user has templates and examples visible in their project:

| Source (plugin) | Destination (research dir) |
|----------------|---------------------------|
| `${CLAUDE_PLUGIN_ROOT}/examples/family-profile.md` | `<research_dir>/family-profile.md` |
| `${CLAUDE_PLUGIN_ROOT}/skills/research-camps/references/provider-template.md` | `<research_dir>/templates/provider-template.md` |
| `${CLAUDE_PLUGIN_ROOT}/skills/research-camps/examples/ymca-cedar-glen.md` | `<research_dir>/examples/ymca-cedar-glen.md` |
| `${CLAUDE_PLUGIN_ROOT}/skills/research-camps/examples/boulderz-etobicoke.md` | `<research_dir>/examples/boulderz-etobicoke.md` |

Read each source file with the Read tool and write it to the destination with the Write tool.

**Notes:**
- The `fall-break-YYYY/` folder is only created if the school has a fall break (common in private schools, uncommon in Ontario public boards). If unsure, create it — it's harmless to have an empty folder.
- The `school-calendars/` folder stores the user's specific school calendar data. Before web searching, check if pre-saved data exists in the plugin's reference data at `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/`. If found, copy the relevant data to the user's folder and confirm it matches the current year.
- Use the current year for folder names. For PA days, use the current school year span (e.g., `pa-days-2025-2026`).

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
- Target per child per day (for PA days, partial weeks, drop-in programs)
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

Write the collected profile to `<research_dir>/family-profile.md` in YAML frontmatter format. Reference the seed template already copied in Step 1 for the expected format. Include a markdown body section titled "Family Notes" for any additional context the user provides.

### Step 3: Configure API Keys and Write Thin Config

Collect optional API keys:

**Geoapify API key (optional):**
- Enables automated commute calculations via the commute-matrix skill
- Free tier is sufficient (3,000 requests/day) for all camp planning needs
- Link: https://myprojects.geoapify.com/
- Skip if user doesn't want to set up now — commute calculations can be added later

Write the thin config file to `.claude/kids-camp-planner.local.md` with:
- `research_dir`: The directory name chosen in Step 0
- `apis.geoapify_api_key`: The API key collected (or empty string if skipped)

Reference the template at `${CLAUDE_PLUGIN_ROOT}/examples/kids-camp-planner.local.md` for the expected format.

### Step 4: Confirm and Summarize

Present a summary of the setup to the user:
- Research directory location and what was seeded into it
- Number of children and their ages
- School board and type
- Budget overview
- Key constraints (commute, care hours, dietary)
- Vacation dates noted
- API keys configured (or skipped)
- Files created:
  - `<research_dir>/family-profile.md` — full family profile
  - `.claude/kids-camp-planner.local.md` — thin config (research_dir pointer + API keys)
  - Seed files in `<research_dir>/templates/` and `<research_dir>/examples/`

Invite the user to review and edit the family profile directly at `<research_dir>/family-profile.md` if any corrections are needed. Mention that API keys can be updated in `.claude/kids-camp-planner.local.md`.

## Re-Running Setup

If a `.claude/kids-camp-planner.local.md` file already exists:
1. Read it to get the `research_dir` path
2. Read `<research_dir>/family-profile.md` for existing family data
3. Ask the user whether to:
   - Update specific fields (preserve existing data)
   - Start fresh (replace entirely)
   - Cancel (keep existing profile)

If `research_dir` points to a directory that doesn't exist, treat it as a fresh setup starting from Step 1.

## Profile Validation

After generating the profile, verify:
- [ ] At least one child is listed with DOB
- [ ] School information is provided (board or school name)
- [ ] At least one parent/guardian with schedule
- [ ] Home address is provided
- [ ] Budget has at least one constraint specified
- [ ] Research folder structure was created successfully
- [ ] Seed files were copied (family-profile.md, provider-template.md, ymca-cedar-glen.md, boulderz-etobicoke.md)
- [ ] Thin config `.claude/kids-camp-planner.local.md` has correct `research_dir` value
