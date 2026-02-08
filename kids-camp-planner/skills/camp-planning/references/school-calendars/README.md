# School Calendars Reference Data

Pre-saved school calendar information for Ontario schools. Used by the camp planner to quickly determine PA days, breaks, and coverage windows without requiring web searches for known schools.

## Directory Structure

```
school-calendars/
├── public-boards/       # Ontario public school boards (extracted markdown)
│   └── tdsb.md          # Toronto District School Board
├── private-schools/     # Ontario private/independent schools (extracted markdown)
│   └── gist.md          # German International School Toronto
└── pdfs/                # Original source PDFs (downloaded or user-provided)
    ├── gist/            # German International School Toronto
    ├── kcs/             # Kingsway College School
    └── tdsb/            # Toronto District School Board
```

## How This Data Is Used

All planning skills use the **3-Tier School Calendar Lookup** pattern:
1. **Tier 1 - Internal library**: Check this directory for pre-saved data (fastest)
2. **Tier 2 - Ask user**: If not found, ask the user for a URL or PDF
3. **Tier 3 - Web search**: If the user doesn't have it, search the web; download and save any PDF found to `pdfs/`, extract to markdown

Skills that perform this lookup:
- **Setup skill**: Populates the library during initial family profile creation
- **Add-school-calendar skill**: Dedicated skill for importing school calendars
- **Plan-PA-days skill**: Looks up PA day dates, cross-references against nearest public board
- **Plan-summer skill**: Gets school start/end dates for coverage window calculation
- **Plan-march-break skill**: Determines break duration (1 week vs 2 weeks)

## File Format

Each school has two possible artifacts:
- **Markdown file** (in `public-boards/` or `private-schools/`): Structured extracted data containing school metadata, per-year sections with key dates, PA days, holidays/breaks, cross-references (private schools), early dismissal dates, summer coverage window calculations, and planning notes
- **PDF file** (in `pdfs/`): Original source document, if available. Named `[abbreviation]-[YYYY-YYYY].pdf`. Kept as the authoritative source for verification.

## Contributing New Schools

Use the **add-school-calendar** skill, which automates the full workflow:
1. Checks if the school already exists in the internal library
2. Accepts a PDF path, URL, or conducts a web search
3. Downloads and saves the original PDF to `pdfs/` (if available)
4. Extracts all key dates to structured markdown
5. For private schools, cross-references PA days against the nearest public board
6. Saves the markdown file to `public-boards/` or `private-schools/`

To add manually, follow the format of existing files (see `tdsb.md` or `gist.md`).

## Data Currency

School calendars change annually. Each file includes:
- `Last updated` date at the bottom
- `Source` citations
- Specific school year headers

When using this data, always verify the school year matches. If only older data is available, use it as a starting point but confirm current dates via web search.

## Phase 2 Research Plan

See `RESEARCH-PLAN.md` for the plan to systematically add more Ontario schools.
