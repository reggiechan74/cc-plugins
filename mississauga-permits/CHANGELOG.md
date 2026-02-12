# Changelog

All notable changes to the **mississauga-permits** plugin are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-12

Initial release. Full-featured City of Mississauga Open Data plugin with two commands, 20 datasets, and zero external dependencies.

### Added

#### Core Infrastructure
- Plugin manifest (`.claude-plugin/plugin.json`) with name, version, description, and author metadata
- Registry-driven dataset configuration (`config/datasets.json`) — add new datasets with a JSON entry, no code changes
- JSON Schema (`schemas/building_permit.schema.json`) for validating building permit output against 24 typed fields

#### Building Permits Command (`/fetch-permits`)
- Street address search with partial matching (SQL `LIKE '%address%'`)
- Address normalization: compass directions automatically abbreviated to match municipal GIS conventions (EAST→E, WEST→W, NORTH→N, SOUTH→S, plus NE/NW/SE/SW)
- Date range filtering (`--from`, `--to`) on configurable date fields (APPLICATION_DATE, ISSUE_DATE, COMPLETE_DATE)
- Permit type filtering (`--type`): RESIDENTIAL, COMMERCIAL, INDUSTRIAL, PUBLIC
- Scope filtering (`--scope`): partial match on scope description (e.g., "NEW BUILDING", "ADDITION")
- Ward filtering (`--ward`): filter by municipal ward number
- Construction value range filtering (`--min-value`, `--max-value`)
- Summary statistics: total/average estimated construction value, date range, breakdowns by file type, scope, and status
- Automatic pagination for result sets exceeding 2,000 records (ArcGIS API limit)
- Date conversion from ArcGIS epoch milliseconds to ISO 8601 strings
- Sanitized output filenames derived from search address
- Custom output path support (`-o`, `--output`)

#### General Dataset Command (`/fetch-mississauga`)
- Support for 20 City of Mississauga datasets across 7 categories:
  - **Property** (3): parcels, addresses, building-footprints
  - **Development** (1): building-permits
  - **Planning** (3): land-use, character-areas, policy-codes
  - **Infrastructure** (9): city-poi, streets, bus-stops, trails, construction-plans, stormwater-projects, road-projects, winter-maintenance, planimetric-points
  - **Administrative** (1): wards
  - **Demographics** (1): census-2016
  - **Safety** (1): speed-cameras
- Text search mode: partial-match queries on dataset-specific search fields
- Spatial query mode: point-in-polygon/intersection queries using WGS84 coordinates (`--lat`, `--lon`)
- Combined text + spatial queries
- Raw ArcGIS SQL WHERE clause support (`--where`) for advanced queries
- Runtime field auto-discovery from FeatureServer metadata endpoint — datasets can update their schema without breaking the plugin
- Dynamic summary statistics with intelligent field filtering (excludes internal GIS fields like OBJECTID, MSLINK, COMPKEY, coordinate fields, and creator/editor tracking fields)
- Dataset listing (`--list`) grouped by category with descriptions
- Configurable search field override (`--search-field`)
- Record limit cap (`--limit`)
- Custom output path support (`-o`, `--output`)

#### Plugin Portability
- All command files use `${CLAUDE_PLUGIN_ROOT}` for path resolution
- Project-level command shims in `.claude/commands/` for auto-discovery without plugin installation
- Zero external dependencies — Python stdlib only (`urllib`, `json`, `argparse`, `collections`, `datetime`, `re`, `os`, `sys`, `typing`)
- Config file resolution via `__file__` — no hardcoded paths anywhere

#### Security
- SQL injection prevention via single-quote escaping in all user-supplied WHERE clause parameters
- Input validation on date formats, numeric ranges, and dataset names
- No authentication tokens, API keys, or credentials required (public ArcGIS REST API)

### Technical Notes

- **ArcGIS Org ID:** `hM5ymMLbxIyWTjn2`
- **API Base URL:** `https://services6.arcgis.com/hM5ymMLbxIyWTjn2/arcgis/rest/services`
- **Spatial Reference:** WGS 1984 Web Mercator (EPSG:3857) for storage; WGS84 (EPSG:4326) for queries
- **Building Permits Coverage:** January 2018 to present (~32,000+ records)
- **Python Compatibility:** 3.9+ (uses `Optional[str]` instead of `str | None` union syntax)
- **Max Records Per Request:** 2,000 (ArcGIS API limit); pagination handles larger result sets automatically
