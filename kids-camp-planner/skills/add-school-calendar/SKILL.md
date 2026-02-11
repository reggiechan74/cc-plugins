---
name: Add School Calendar
description: This skill should be used when the user asks to "add a school calendar", "import school calendar", "save school calendar", "import PA day dates", "import PA days from PDF", "add a school to the planner", "save school dates", "load school calendar from URL", "import school year", or provides a school calendar PDF or URL and wants it saved as reference data for camp planning. Extracts and saves structured calendar data from school board or private school sources.
version: 0.1.0
---

# Add School Calendar

## Overview

**Locate research directory:** Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path (default: `camp-research`). All user data paths below are relative to this directory. The family profile is at `<research_dir>/family-profile.md`.

Extract school calendar data from a URL, PDF, or web search and save it as a structured reference file in the school-calendars directory. This makes the data instantly available to all planning skills (plan-summer, plan-march-break, plan-pa-days) without requiring web searches for known schools.

All planning skills use the **School Calendar Lookup** pattern (see below) before asking the user or searching the web. This skill is what populates the internal library that those lookups check first.

## School Calendar Lookup (3-Tier)

This is the standard lookup pattern used by all planning skills in the plugin. When any skill needs school calendar data:

### Tier 1: Check Internal Library

Search the plugin's pre-saved calendar data:
- Public boards: `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/public-boards/`
- Private schools: `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/private-schools/`

Use Glob to find files matching the school name or abbreviation. If a matching file exists and covers the required school year, use it directly. Inform the user: "Found [school] calendar data in the internal library for [year]."

If data exists but is for a different school year, inform the user and proceed to Tier 2.

### Tier 2: Ask the User

If no internal data is found, ask the user:
"I don't have [school name] calendar data saved. Do you have the school calendar available? You can provide:"
- A PDF file path
- A URL to the school calendar page
- Or I can search the web for it

### Tier 3: Web Search

If the user doesn't have the calendar handy, conduct a web search:
1. Search for "[school name] school year calendar [YYYY-YYYY]" or "[school board] PA days [YYYY-YYYY]"
2. **Prioritize the official school/board website** - avoid third-party aggregator sites
3. **Ensure the correct school year** is retrieved (verify dates match the expected year)
4. If a **PDF is found**: download it using Bash (`curl -L -o`) and save to `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/pdfs/[abbreviation]/[abbreviation]-[YYYY-YYYY].pdf`, then read the PDF to extract data
5. If the information is **only on a webpage**: extract directly to markdown (no PDF to save)

After extracting data from any tier, proceed to the extraction and saving workflow below.

## Workflow

### Step 1: Identify the School

Collect the following (skip any the user has already provided):
- **School name** (full name)
- **Abbreviation** for the filename (e.g., TDSB, GIST, UCC, BSS)
- **School type**: public board, Catholic board, or private/independent. Note: Catholic boards (e.g., TCDSB, DPCDSB) are treated as separate public boards with their own PA day schedules, not as private schools.
- **Region** (e.g., Toronto, York Region, Peel Region)
- **School year(s)** being added (e.g., 2025-2026)

Then run the 3-Tier Lookup above. If Tier 1 finds existing data and the user just wants to verify it, show them the saved data and offer to update it.

### Step 2: Extract Calendar Data

Read the source (PDF via Read tool, URL via WebFetch, or web search results) and extract all of the following. If a field cannot be found, mark it as "Not specified" rather than guessing.

#### Required Fields
| Field | Example |
|-------|---------|
| First instructional day | September 2, 2025 |
| Last instructional day (elementary) | June 25, 2026 |
| Last instructional day (secondary) | June 24, 2026 |
| PA days with dates and day-of-week | Sep 26 (Fri), Oct 10 (Fri)... |
| March break dates | March 16-20, 2026 |
| Winter/Christmas break dates | December 22 - January 2 |
| Summer break start | Day after last instructional day |

#### Optional Fields (extract if available)
| Field | Example |
|-------|---------|
| Fall break dates | November 3-7, 2025 |
| Early dismissal dates | June 26 (1:15pm) |
| Exam periods | January 26-29 |
| PA day purposes | "Parent Teacher Conferences" |
| Special events affecting scheduling | "Camp Pine Crest Sep 16-19" |
| Next year start date | August 31, 2026 |

#### Holidays (extract all with dates)
Standard Ontario holidays to look for:
- Labour Day
- National Day for Truth & Reconciliation (Sep 30)
- Thanksgiving
- Remembrance Day
- Family Day
- Good Friday
- Easter Monday
- Victoria Day

### Step 3: Cross-Reference (Private Schools Only)

For private/independent schools, identify the **nearest public board** (typically TDSB for Toronto schools) and create a comparison:

1. **PA day alignment table**: Compare each private school PA day against the public board's PA days. Count how many overlap.
2. **Break differences**: Note any breaks that differ (extended March break, fall break, early starts).
3. **Coverage challenge ranking**: Rank unique coverage gaps by difficulty (see the GIST file at `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/private-schools/gist.md` for the format).

To cross-reference, check if the public board's calendar is already saved (Tier 1 lookup). If not saved, offer to add it first or note that cross-referencing will need the public board data later.

### Step 4: Calculate Summer Coverage Window

Compute the summer coverage window:
- **Coverage start**: First weekday after last instructional day
- **Coverage end**: Last weekday before the fall start date
- If fall start date is unknown, use the day after Labour Day as the default
- Run the summer dates calculator for precise numbers:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/plan-summer/scripts/summer_dates.py \
  --year YYYY --last-school-day YYYY-MM-DD --first-fall-day YYYY-MM-DD --format text
```

If the script is unavailable, calculate manually: count all weekdays (Mon-Fri) between the day after the last instructional day and the day before the fall start date, excluding Labour Day.

- Note the total weekdays and approximate weeks

### Step 5: Save the Calendar File

Save the structured markdown data following the established format.

**Markdown file location:**
- Public boards: `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/public-boards/[abbreviation].md`
- Private schools: `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/private-schools/[abbreviation].md`

**PDF file location** (if a PDF was downloaded in Tier 3):
- `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/pdfs/[abbreviation]/[abbreviation]-[YYYY-YYYY].pdf`

**File structure**: Use the full template at `references/calendar-template.md`. Key sections:
- Header metadata (name, type, region, website, contact info)
- Key Dates table
- PA Days tables (elementary and secondary)
- PA day alignment table (private schools only - compare against nearest public board)
- Holidays & Breaks table (private schools add public board comparison column)
- Early Dismissal Days
- Summer Window calculation
- Planning Notes and Coverage Challenges (private schools only)

### Step 6: Confirm and Update References

After saving:
1. Confirm the file was created and show a summary of what was extracted
2. If a PDF was downloaded, note the saved PDF path for reference
3. List any fields that were marked "Not specified" - ask if the user can fill them in
4. If this school is used in the family profile (`<research_dir>/family-profile.md`), inform the user that other skills will now automatically use this data via Tier 1 lookup
5. Offer to add another school year or another school

## Handling Ambiguous or Incomplete Sources

- **PDF won't parse**: Ask the user to open the PDF and paste the key dates manually, or try reading it with the Read tool
- **Dates are unclear**: Present what was extracted and ask the user to confirm before saving
- **Multiple calendar versions**: Ask which version to use (draft vs final, revised vs original)
- **Missing PA days**: Some schools release PA days later. Save what's available and note "PA days TBD - check [source] for updates"
- **Web search returns wrong year**: Refine the search with explicit year. Check the source document for revision dates.

## Additional Resources

### Templates

- **`references/calendar-template.md`** - Blank template matching the established file format

### Existing Calendar Files

Reference these for format consistency:
- `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/public-boards/tdsb.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/camp-planning/references/school-calendars/private-schools/gist.md`

### Scripts

- **`scripts/scrape_board_calendar.py`** - HTML calendar page scraper. Produces draft-quality markdown from school board websites. Requires human/agent review. Use for boards with HTML calendar pages; PDF-only boards still need manual extraction.
- **`scripts/validate_calendar.py`** - Calendar file validator. Checks required sections, parseable dates, school year format. Use `--all` to validate an entire directory.
