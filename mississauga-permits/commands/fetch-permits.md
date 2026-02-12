---
description: Fetch Mississauga building permits by street address
argument-hint: <address> [--type TYPE] [--from DATE] [--to DATE] [--ward N] [--scope SCOPE] [--min-value N] [--max-value N]
allowed-tools: Bash(python3:*)
---

Fetch building permit data from the City of Mississauga Open Data portal for the given address.

**Parse the user's arguments from:** `$ARGUMENTS`

The address is the first positional argument (may contain spaces — everything before the first `--` flag). All other arguments are optional flags.

**Available filters:**
- `--type` — FILE_TYPE filter: RESIDENTIAL, COMMERCIAL, INDUSTRIAL, PUBLIC
- `--from` / `--to` — Date range in YYYY-MM-DD format
- `--date-field` — Which date to filter: APPLICATION_DATE, ISSUE_DATE (default), COMPLETE_DATE
- `--scope` — Scope filter (partial match): e.g., "NEW BUILDING", "ADDITION", "INTERIOR ALTERATION"
- `--ward` — Ward number (integer)
- `--min-value` / `--max-value` — Estimated construction value range in CAD
- `--output` / `-o` — Custom output file path

**Execute the script:**

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_permits.py <parsed arguments>
```

Build the command from the parsed arguments. Quote the address argument. Pass flags exactly as provided.

**After execution:**
1. Read the stderr output for the summary statistics
2. Present the summary to the user in a clean format
3. Mention the output file path so they know where the JSON was saved
4. If no results were found, suggest broadening the search (shorter address string, removing filters)
