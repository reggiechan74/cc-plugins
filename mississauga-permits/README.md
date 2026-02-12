# mississauga-permits

Claude Code plugin for querying the City of Mississauga Open Data portal. Provides on-demand access to 20 municipal datasets including building permits, parcels, land use, transit, infrastructure projects, and more.

## Prerequisites

- Python 3.9+
- No external dependencies (stdlib only)
- Internet access to reach `services6.arcgis.com`

## Installation

### As a project command (recommended for single repo)

Copy the plugin folder into your project and create command shims:

```bash
cp -r mississauga-permits /your-repo/.claude/plugins/
cp mississauga-permits/commands/fetch-permits.md /your-repo/.claude/commands/
cp mississauga-permits/commands/fetch-mississauga.md /your-repo/.claude/commands/
```

Then edit the two command shims in `.claude/commands/` to replace `${CLAUDE_PLUGIN_ROOT}` with the project-relative path `.claude/plugins/mississauga-permits`:

```
python3 .claude/plugins/mississauga-permits/scripts/fetch_permits.py ...
python3 .claude/plugins/mississauga-permits/scripts/fetch_mississauga.py ...
```

### As a Claude Code plugin

```bash
claude --plugin-dir /path/to/mississauga-permits
```

When loaded as a plugin, `${CLAUDE_PLUGIN_ROOT}` resolves automatically. No path editing needed.

## Commands

### `/fetch-permits <address> [filters]`

Specialized command for building permit lookups. Queries the Issued Building Permits dataset (32,000+ records since Jan 2018) with rich filtering options.

**Arguments:**

| Argument | Description | Example |
|----------|-------------|---------|
| `<address>` | Street address (partial match, required) | `400 Matheson Blvd E` |
| `--type` | FILE_TYPE filter | `RESIDENTIAL`, `COMMERCIAL`, `INDUSTRIAL`, `PUBLIC` |
| `--scope` | Scope filter (partial match) | `NEW BUILDING`, `ADDITION`, `INTERIOR ALTERATION` |
| `--ward` | Ward number | `5` |
| `--from` | Start date (YYYY-MM-DD) | `2024-01-01` |
| `--to` | End date (YYYY-MM-DD) | `2024-12-31` |
| `--date-field` | Which date to filter on | `APPLICATION_DATE`, `ISSUE_DATE` (default), `COMPLETE_DATE` |
| `--min-value` | Minimum estimated construction value (CAD) | `500000` |
| `--max-value` | Maximum estimated construction value (CAD) | `1000000` |
| `-o`, `--output` | Custom output file path | `results.json` |

**Examples:**

```
/fetch-permits 400 Matheson Blvd East
/fetch-permits Hurontario --type COMMERCIAL --from 2024-01-01
/fetch-permits Dundas --ward 1 --min-value 500000
/fetch-permits Burnhamthorpe --scope "NEW BUILDING" --from 2020-01-01 --to 2023-12-31
```

**Output:** JSON file with schema reference, query metadata, summary statistics, and permit records. Summary printed to console.

### `/fetch-mississauga [options] [search term]`

General-purpose command for querying any of the 20 registered City of Mississauga datasets. Supports both text search and spatial (lat/lon) queries.

**Arguments:**

| Argument | Description | Example |
|----------|-------------|---------|
| `--list` | Show all available datasets | |
| `-d`, `--dataset` | Dataset to query (default: `building-permits`) | `parcels`, `land-use`, `city-poi` |
| `<search term>` | Text search (partial match on dataset's default field) | `Library`, `Square One` |
| `--lat` | Latitude for spatial query | `43.6258` |
| `--lon` | Longitude for spatial query | `-79.6573` |
| `--search-field` | Override which field to search | `LANDMARKNAME` |
| `--where` | Raw ArcGIS SQL WHERE clause (advanced) | `"WARD = 5 AND STATUS = 'OPEN'"` |
| `--limit` | Cap the number of records returned | `10` |
| `-o`, `--output` | Custom output file path | `results.json` |

**Examples:**

```
/fetch-mississauga --list
/fetch-mississauga -d parcels --lat 43.6258 --lon -79.6573
/fetch-mississauga -d land-use --lat 43.6258 --lon -79.6573
/fetch-mississauga -d wards --lat 43.59 --lon -79.65
/fetch-mississauga -d city-poi Library
/fetch-mississauga -d bus-stops Square One
/fetch-mississauga -d construction-plans Hurontario
/fetch-mississauga -d speed-cameras Dundas
/fetch-mississauga -d building-permits 100 City Centre --limit 20
```

**Output:** JSON file with dataset metadata, auto-discovered field list, summary statistics, and records. Summary printed to console.

## Available Datasets

### Property

| Dataset | Search | Description |
|---------|--------|-------------|
| `parcels` | spatial | Tax parcel boundaries for property analysis |
| `addresses` | text (FULLNAME) | Civic address points, updated monthly |
| `building-footprints` | spatial | Building footprint polygons from 2023 imagery |

### Development

| Dataset | Search | Description |
|---------|--------|-------------|
| `building-permits` | text (ADDRESS) | Building permits issued since Jan 2018 |

### Planning

| Dataset | Search | Description |
|---------|--------|-------------|
| `land-use` | spatial | Official Plan land use designations |
| `character-areas` | spatial | Designated character area classifications |
| `policy-codes` | spatial | ELU policy code zones and designations |

### Infrastructure

| Dataset | Search | Description |
|---------|--------|-------------|
| `city-poi` | text (LANDMARKNAME) | 200+ landmark types (parks, schools, hospitals) |
| `streets` | text (FULLNAME) | Street network data |
| `bus-stops` | text (stp_descri) | Mississauga transit stop locations |
| `trails` | text (TRAILNAME1) | Multi-use trails and engineered walkways |
| `construction-plans` | text (Location) | Active municipal construction projects |
| `stormwater-projects` | text (stormwater_exceltotable_street_) | Stormwater infrastructure projects |
| `road-projects` | text (Street_Name) | Road construction and improvement projects |
| `winter-maintenance` | spatial | Salt and plow routes |
| `planimetric-points` | spatial | Feature points (antennas, hydrants, poles, trees) |

### Administrative

| Dataset | Search | Description |
|---------|--------|-------------|
| `wards` | spatial | 11 city ward/electoral boundaries |

### Demographics

| Dataset | Search | Description |
|---------|--------|-------------|
| `census-2016` | spatial | 2016 Census demographics by neighbourhood |

### Safety

| Dataset | Search | Description |
|---------|--------|-------------|
| `speed-cameras` | text (LOCATION) | Automated Speed Enforcement camera locations |

## Query Modes

### Text Search

Datasets with a `search_field` support partial-match text queries. The search term is matched using SQL `LIKE '%term%'` against the field, case-insensitive.

```bash
python3 scripts/fetch_mississauga.py --dataset city-poi Library
# Queries: UPPER(LANDMARKNAME) LIKE '%LIBRARY%'
```

### Spatial Query

Datasets marked `spatial` accept latitude/longitude coordinates. The query finds all features (polygons, points) that intersect the given point using WGS84 (EPSG:4326).

```bash
python3 scripts/fetch_mississauga.py --dataset parcels --lat 43.6258 --lon -79.6573
# Returns the parcel polygon containing that point
```

### Combined

Text and spatial queries can be combined:

```bash
python3 scripts/fetch_mississauga.py --dataset city-poi Library --lat 43.59 --lon -79.65
# Text match on LANDMARKNAME + spatial intersection
```

### Raw WHERE Clause

For advanced queries, use `--where` to pass a raw ArcGIS SQL expression:

```bash
python3 scripts/fetch_mississauga.py --dataset building-permits \
  --where "WARD = 5 AND FILE_TYPE = 'COMMERCIAL' AND EST_CON_VALUE > 1000000"
```

## Address Normalization

Compass directions in search terms are automatically normalized to match municipal GIS conventions:

| Input | Normalized |
|-------|-----------|
| `EAST` | `E` |
| `WEST` | `W` |
| `NORTH` | `N` |
| `SOUTH` | `S` |
| `NORTHEAST` | `NE` |
| `NORTHWEST` | `NW` |
| `SOUTHEAST` | `SE` |
| `SOUTHWEST` | `SW` |

Example: `400 Matheson Blvd East` becomes `400 MATHESON BLVD E` before querying.

## Output Format

### Building Permits (`fetch_permits.py`)

Outputs JSON with a `$schema` reference to `schemas/building_permit.schema.json`:

```json
{
  "$schema": "./schemas/building_permit.schema.json",
  "metadata": {
    "source": "City of Mississauga Open Data - Issued Building Permits",
    "api_endpoint": "https://services6.arcgis.com/.../FeatureServer/0",
    "query_address": "400 Matheson",
    "filters_applied": { ... },
    "total_records": 3,
    "fetched_at": "2026-02-12T19:39:54.719064+00:00",
    "summary": {
      "total_estimated_value": 414000,
      "average_estimated_value": 138000,
      "date_range": { "earliest": "2020-03-27", "latest": "2023-04-21" },
      "by_file_type": { "INDUSTRIAL": 3 },
      "by_scope": { "ALTERATION TO EXISTING BLDG": 3 },
      "by_status": { "COMPLETED -ALL INSP SIGNED OFF": 2, "ISSUED PERMIT": 1 }
    }
  },
  "permits": [
    {
      "OBJECTID": 20609,
      "BP_NO": "BP 3ALT 23-5671",
      "STATUS": "ISSUED PERMIT",
      "ADDRESS": "400 MATHESON BLVD E",
      "DESCRIPTION": "INTERIOR ALTERATIONS - PROPOSED OFFICE",
      "EST_CON_VALUE": 162000,
      "ISSUE_DATE": "2023-04-21",
      ...
    }
  ]
}
```

### General Datasets (`fetch_mississauga.py`)

Outputs JSON with auto-discovered fields and dynamic summary statistics:

```json
{
  "metadata": {
    "source": "City of Mississauga Open Data -- Official Plan land use designations",
    "dataset": "land-use",
    "api_endpoint": "https://services6.arcgis.com/.../FeatureServer/0",
    "query": "lat=43.62575, lon=-79.65726",
    "fields": ["OBJECTID", "MOP_CODE", "MOP_DESCRIPTION", ...],
    "total_records": 1,
    "fetched_at": "2026-02-12T...",
    "summary": { ... }
  },
  "records": [
    {
      "MOP_CODE": "BE",
      "MOP_DESCRIPTION": "Business Employment",
      ...
    }
  ]
}
```

Fields are auto-discovered from the FeatureServer metadata at query time. Date fields are converted from ArcGIS epoch milliseconds to ISO 8601 strings. Internal system fields (OBJECTID, Shape, etc.) are excluded from summary statistics.

## Architecture

```
mississauga-permits/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── commands/
│   ├── fetch-permits.md         # Building permits command (specialized)
│   └── fetch-mississauga.md     # General dataset command (20 datasets)
├── config/
│   └── datasets.json            # Dataset registry (service URLs, search fields)
├── schemas/
│   └── building_permit.schema.json  # JSON Schema for permit output
└── scripts/
    ├── fetch_permits.py         # Permits-specific fetcher (24 hardcoded fields)
    └── fetch_mississauga.py     # General fetcher (auto-discovers fields)
```

### Design Decisions

**Two scripts, not one.** `fetch_permits.py` is specialized for building permits with hardcoded fields, a typed JSON Schema, and permit-specific summary stats (construction value, scope breakdown). `fetch_mississauga.py` is general-purpose with dynamic field discovery. The specialized script produces cleaner, more predictable output for the most common use case.

**Auto-discovery over hardcoding.** The general script queries each FeatureServer's metadata endpoint to discover field names, types, and aliases at runtime. This means datasets can change their schema without breaking the plugin. The tradeoff is one extra API call per query (~2KB metadata response).

**Registry-driven configuration.** Adding a new dataset requires only a JSON entry in `config/datasets.json` with the service name, search field, and category. No code changes needed.

**Zero external dependencies.** Both scripts use only Python stdlib (`urllib`, `json`, `argparse`, `collections`, `datetime`). No `pip install`, no `requirements.txt`, no virtual environment needed.

**Summary stats filter.** Internal GIS fields (OBJECTID, MSLINK, COMPKEY, coordinate fields, creator/editor fields) are automatically excluded from summary statistics to keep output meaningful.

## Data Source

All data comes from the City of Mississauga Open Data portal, powered by Esri ArcGIS Hub.

- **Portal:** https://data.mississauga.ca
- **ArcGIS Org ID:** `hM5ymMLbxIyWTjn2`
- **Base URL:** `https://services6.arcgis.com/hM5ymMLbxIyWTjn2/arcgis/rest/services`
- **API:** ArcGIS REST FeatureServer (public, no authentication required)
- **Coverage:** Varies by dataset. Building permits: Jan 2018 to present (~32,000 records).
- **Spatial Reference:** WGS 1984 Web Mercator (EPSG:3857) for storage; WGS84 (EPSG:4326) for spatial queries.

## Adding New Datasets

1. Find the service name at the [ArcGIS REST services directory](https://services6.arcgis.com/hM5ymMLbxIyWTjn2/arcgis/rest/services)
2. Add an entry to `config/datasets.json`:

```json
"my-dataset": {
  "service": "Service_Name_From_ArcGIS",
  "layer": 0,
  "description": "Brief description of the dataset",
  "search_field": "FIELD_NAME",
  "category": "property"
}
```

For spatial-only datasets (polygons with no useful text search field):

```json
"my-spatial-dataset": {
  "service": "Service_Name",
  "layer": 0,
  "description": "Description",
  "search_field": null,
  "spatial": true,
  "category": "planning"
}
```

3. Test: `python3 scripts/fetch_mississauga.py --dataset my-dataset <search-term>`

To discover available fields for a dataset:

```bash
curl -s "https://services6.arcgis.com/hM5ymMLbxIyWTjn2/arcgis/rest/services/SERVICE_NAME/FeatureServer/0?f=json" | python3 -c "import sys,json; [print(f['name'], f['type']) for f in json.load(sys.stdin)['fields']]"
```

## Limitations

- **Rate limits:** No formal rate limit documented, but the ArcGIS API caps each request at 2,000 records. Pagination handles larger result sets automatically.
- **Coverage:** Building permits only go back to January 2018. Census data is from 2016.
- **Address formats:** Municipal GIS uses abbreviated directions (E/W/N/S). Auto-normalization handles full words, but other address quirks (e.g., `ST` vs `STREET`) are not normalized.
- **Spatial precision:** Point-in-polygon queries use exact intersection. If your coordinates are on a parcel boundary, results may vary.

## License

MIT
