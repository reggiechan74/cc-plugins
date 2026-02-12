---
description: Query any City of Mississauga open dataset (permits, parcels, land use, POI, transit, etc.)
argument-hint: [--dataset NAME] <search> [--lat N --lon N] [--list] [--where CLAUSE] [--limit N]
allowed-tools: Bash(python3:*)
---

Query the City of Mississauga Open Data portal. Supports 20+ datasets with text search and spatial queries.

**Parse the user's arguments from:** `$ARGUMENTS`

**Argument rules:**
- `--dataset <name>` or `-d <name>` selects the dataset (default: building-permits)
- `--list` shows all available datasets and exits
- Text after flags = search term (partial match on dataset's default search field)
- `--lat <lat> --lon <lon>` = spatial point-in-polygon query (for parcels, land use, wards, etc.)
- `--search-field <FIELD>` overrides which field to text-search
- `--where <clause>` = raw ArcGIS SQL WHERE clause (advanced)
- `--limit <N>` caps the number of records
- `--output <path>` or `-o <path>` = custom output file

**Execute the script:**

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_mississauga.py <parsed arguments>
```

Quote multi-word search terms. Pass flags exactly as provided.

**Example invocations:**
- `--list` → show all datasets
- `--dataset building-permits 400 Matheson` → building permits at address
- `--dataset parcels --lat 43.6258 --lon -79.6573` → parcel info at coordinates
- `--dataset land-use --lat 43.6258 --lon -79.6573` → zoning designation
- `--dataset city-poi Library` → find libraries
- `--dataset bus-stops Square One` → transit stops near Square One
- `--dataset wards --lat 43.59 --lon -79.65` → which ward a location is in

**After execution:**
1. Read the stderr output for the summary statistics
2. Present the summary to the user in a clean, readable format
3. Mention the output file path
4. If no results, suggest broadening search or trying spatial query
5. If the dataset has many fields, highlight the most interesting/relevant ones rather than dumping everything
