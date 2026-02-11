# Contributing to Kids Camp Planner

## Adding School Calendar Data

The most impactful contribution is adding school calendar data for Ontario schools.

### Submission Format

Calendar files must follow the template at `skills/add-school-calendar/references/calendar-template.md`.

#### Required sections:
- School metadata header (name, type, region, website)
- `## YYYY-YYYY School Year` with source citation
- `### Key Dates` table
- `### PA Days - Elementary` table (or note if school uses midterm breaks)
- `### Holidays & Breaks` table
- `### Summer Window` with last school day, first fall day, coverage needed

#### For private schools, also include:
- PA day alignment table comparing against nearest public board
- Coverage challenges ranked by difficulty
- Planning notes section

### Quality Checklist

Before submitting:
- [ ] All dates verified against official school/board publication
- [ ] School year matches (2025-2026 not previous year)
- [ ] PA day count matches board's stated total
- [ ] Holidays & Breaks includes all Ontario statutory holidays
- [ ] Summer window calculation is correct (weekday count)
- [ ] Source citation includes document name and date
- [ ] `*Last updated:` footer with current date
- [ ] Passes validation: `python3 skills/add-school-calendar/scripts/validate_calendar.py path/to/file.md`

### Validation

Run the validator before submitting:

```bash
python3 skills/add-school-calendar/scripts/validate_calendar.py path/to/new-calendar.md
```

### File Locations

- Public boards: `skills/camp-planning/references/school-calendars/public-boards/[abbreviation].md`
- Private schools: `skills/camp-planning/references/school-calendars/private-schools/[abbreviation].md`
- PDFs (if downloaded): `skills/camp-planning/references/school-calendars/pdfs/[abbreviation]/`

### Priority Schools

See `skills/camp-planning/references/school-calendars/RESEARCH-PLAN.md` for the full priority list. Tier 3 (private schools) and Tier 4 (French/international) still need contributors.
