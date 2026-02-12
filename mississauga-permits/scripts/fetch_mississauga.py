#!/usr/bin/env python3
"""Fetch any dataset from City of Mississauga ArcGIS Open Data portal."""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from typing import Optional

BASE_URL = "https://services6.arcgis.com/hM5ymMLbxIyWTjn2/arcgis/rest/services"
MAX_RECORD_COUNT = 2000

DIRECTION_MAP = {
    "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W",
    "NORTHEAST": "NE", "NORTHWEST": "NW",
    "SOUTHEAST": "SE", "SOUTHWEST": "SW",
}


# ---------------------------------------------------------------------------
# Dataset Registry
# ---------------------------------------------------------------------------

def load_registry() -> dict:
    """Load dataset registry from config/datasets.json."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "datasets.json")
    with open(config_path) as f:
        registry = json.load(f)
    # Strip internal comments
    return {k: v for k, v in registry.items() if not k.startswith("_")}


def get_feature_url(dataset: dict) -> str:
    """Build FeatureServer layer URL from dataset config."""
    service = dataset["service"]
    layer = dataset.get("layer", 0)
    return f"{BASE_URL}/{service}/FeatureServer/{layer}"


# ---------------------------------------------------------------------------
# Field Discovery
# ---------------------------------------------------------------------------

def discover_fields(feature_url: str) -> list[dict]:
    """Query FeatureServer metadata to get field definitions."""
    url = f"{feature_url}?f=json"
    data = _fetch_json(url)
    return data.get("fields", [])


def get_field_names(fields: list[dict]) -> list[str]:
    """Extract field names, excluding system geometry fields."""
    exclude = {"Shape", "Shape__Area", "Shape__Length", "SHAPE", "GlobalID", "FID"}
    return [f["name"] for f in fields if f["name"] not in exclude and f["type"] != "esriFieldTypeGeometry"]


def get_date_fields(fields: list[dict]) -> set[str]:
    """Identify date-type fields."""
    return {f["name"] for f in fields if f["type"] == "esriFieldTypeDate"}


def get_numeric_fields(fields: list[dict]) -> set[str]:
    """Identify numeric fields."""
    numeric_types = {"esriFieldTypeInteger", "esriFieldTypeSmallInteger",
                     "esriFieldTypeDouble", "esriFieldTypeSingle"}
    return {f["name"] for f in fields if f["type"] in numeric_types}


# ---------------------------------------------------------------------------
# Query Building
# ---------------------------------------------------------------------------

def _escape_sql(value: str) -> str:
    return value.replace("'", "''")


def _normalize_address(text: str) -> str:
    words = text.upper().split()
    return " ".join(DIRECTION_MAP.get(w, w) for w in words)


def build_where_clause(search_term: str, search_field: str, extra_where: Optional[str] = None) -> str:
    """Build WHERE clause from search term and field."""
    term = _escape_sql(_normalize_address(search_term))
    clauses = [f"UPPER({search_field}) LIKE '%{term}%'"]
    if extra_where:
        clauses.append(extra_where)
    return " AND ".join(clauses)


def build_spatial_params(lat: float, lon: float) -> dict:
    """Build spatial query parameters for point-in-polygon lookup."""
    return {
        "geometry": json.dumps({"x": lon, "y": lat, "spatialReference": {"wkid": 4326}}),
        "geometryType": "esriGeometryPoint",
        "spatialRel": "esriSpatialRelIntersects",
        "inSR": 4326,
    }


# ---------------------------------------------------------------------------
# API Calls
# ---------------------------------------------------------------------------

def _fetch_json(url: str) -> dict:
    """Fetch JSON from URL with error handling."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "mississauga-opendata-plugin/0.1.0")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"ERROR: HTTP {e.code} from ArcGIS API", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Could not reach ArcGIS API: {e.reason}", file=sys.stderr)
        sys.exit(1)


def query_features(feature_url: str, out_fields: list[str],
                   where: str = "1=1", spatial_params: Optional[dict] = None,
                   offset: int = 0, order_by: Optional[str] = None) -> dict:
    """Query the FeatureServer with pagination support."""
    params = {
        "where": where,
        "outFields": ",".join(out_fields),
        "resultOffset": offset,
        "resultRecordCount": MAX_RECORD_COUNT,
        "f": "json",
    }
    if order_by:
        params["orderByFields"] = order_by
    if spatial_params:
        params.update(spatial_params)

    url = f"{feature_url}/query?{urllib.parse.urlencode(params)}"
    return _fetch_json(url)


def fetch_all_features(feature_url: str, out_fields: list[str],
                       where: str = "1=1", spatial_params: Optional[dict] = None,
                       order_by: Optional[str] = None) -> list[dict]:
    """Fetch all matching features with pagination."""
    all_features = []
    offset = 0

    while True:
        data = query_features(feature_url, out_fields, where, spatial_params, offset, order_by)

        if "error" in data:
            print(f"ERROR: ArcGIS API error: {data['error']}", file=sys.stderr)
            sys.exit(1)

        features = data.get("features", [])
        if not features:
            break

        all_features.extend(features)

        exceeded = data.get("exceededTransferLimit", False)
        if not exceeded or len(features) < MAX_RECORD_COUNT:
            break

        offset += len(features)
        print(f"  Fetched {len(all_features)} records so far...", file=sys.stderr)

    return all_features


# ---------------------------------------------------------------------------
# Record Processing
# ---------------------------------------------------------------------------

def epoch_ms_to_iso(epoch_ms) -> Optional[str]:
    """Convert ArcGIS epoch milliseconds to ISO 8601 date string."""
    if epoch_ms is None:
        return None
    dt = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def normalize_records(features: list[dict], field_names: list[str],
                      date_fields: set[str]) -> list[dict]:
    """Convert ArcGIS features to flat records with normalized dates."""
    records = []
    for feature in features:
        attrs = feature.get("attributes", {})
        record = {}
        for field in field_names:
            val = attrs.get(field)
            if field in date_fields and val is not None:
                val = epoch_ms_to_iso(val)
            record[field] = val
        records.append(record)
    return records


SKIP_SUMMARY_PATTERNS = {
    "OBJECTID", "FID", "GLOBALID", "SHAPE", "MSLINK", "COMPKEY", "GISKEY",
    "GRIDKEY", "ADDRKEY", "ROOMKEY", "PARENTKEY", "MAPID", "CENT_X", "CENT_Y",
    "CENT_X_3857", "CENT_Y_3857", "UTM_X", "UTM_Y", "COLOUR_CODE",
    "CREATOR", "EDITOR", "CRTBY_GIS", "UPDBY_GIS",
}


def _skip_field(field: str) -> bool:
    """Check if a field should be excluded from summary stats."""
    upper = field.upper().replace(" ", "_")
    if upper in SKIP_SUMMARY_PATTERNS:
        return True
    for pattern in ("_KEY", "_ID", "_FK", "MSLINK", "COMPKEY", "GRIDKEY",
                    "GISKEY", "ADDRKEY", "ROOMKEY", "CENT_X", "CENT_Y",
                    "UTM_X", "UTM_Y", "_GIS"):
        if pattern in upper:
            return True
    return False


def compute_summary(records: list[dict], field_names: list[str],
                    date_fields: set[str], numeric_fields: set[str]) -> dict:
    """Compute summary statistics dynamically based on field types."""
    summary = {"total_records": len(records)}

    # Summarize string fields with low cardinality (< 30 unique values)
    string_fields = [f for f in field_names
                     if f not in date_fields and f not in numeric_fields
                     and not _skip_field(f)]
    for field in string_fields:
        values = [r.get(field) for r in records if r.get(field) and str(r.get(field)).strip()]
        if values:
            counts = Counter(values)
            if len(counts) <= 30:
                summary[f"by_{field.lower()}"] = dict(counts.most_common(10))

    # Summarize numeric fields (skip internal IDs)
    for field in numeric_fields:
        if _skip_field(field):
            continue
        values = [r[field] for r in records if r.get(field) is not None]
        if values:
            summary[f"{field.lower()}_total"] = sum(values)
            summary[f"{field.lower()}_avg"] = round(sum(values) / len(values), 2)
            summary[f"{field.lower()}_min"] = min(values)
            summary[f"{field.lower()}_max"] = max(values)

    # Date range
    for field in date_fields:
        dates = [r[field] for r in records if r.get(field)]
        if dates:
            summary[f"{field.lower()}_range"] = {"earliest": min(dates), "latest": max(dates)}

    return summary


def sanitize_filename(text: str) -> str:
    clean = re.sub(r"[^\w\s-]", "", text.strip())
    clean = re.sub(r"\s+", "_", clean)
    return clean.lower()[:60]


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def print_summary(dataset_name: str, search_desc: str, records: list[dict],
                  summary: dict, outpath: str) -> None:
    """Print human-readable summary to stderr."""
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Mississauga Open Data — {dataset_name}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"  Query: {search_desc}", file=sys.stderr)
    print(f"  Records found: {len(records)}", file=sys.stderr)

    for key, val in summary.items():
        if key == "total_records":
            continue
        if key.startswith("by_"):
            field_label = key[3:].replace("_", " ").title()
            print(f"\n  By {field_label}:", file=sys.stderr)
            for k, v in val.items():
                print(f"    {k}: {v}", file=sys.stderr)
        elif key.endswith("_range"):
            field_label = key[:-6].replace("_", " ").title()
            print(f"  {field_label} range: {val['earliest']} to {val['latest']}", file=sys.stderr)
        elif key.endswith("_total"):
            field_label = key[:-6].replace("_", " ").title()
            print(f"  {field_label} total: {val:,.2f}", file=sys.stderr)
        elif key.endswith("_avg"):
            field_label = key[:-4].replace("_", " ").title()
            print(f"  {field_label} avg: {val:,.2f}", file=sys.stderr)

    print(f"\n  Saved to: {outpath}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)


def print_dataset_list(registry: dict) -> None:
    """Print available datasets grouped by category."""
    by_cat = {}
    for name, ds in registry.items():
        cat = ds.get("category", "other")
        by_cat.setdefault(cat, []).append((name, ds))

    print("\nAvailable datasets:\n", file=sys.stderr)
    for cat in sorted(by_cat):
        print(f"  [{cat.upper()}]", file=sys.stderr)
        for name, ds in sorted(by_cat[cat]):
            spatial = " (spatial)" if ds.get("spatial") else ""
            search = f" [search: {ds['search_field']}]" if ds.get("search_field") else ""
            print(f"    {name:30s} {ds['description']}{spatial}{search}", file=sys.stderr)
        print(file=sys.stderr)

    print("  Use: --dataset <name> <search-term>", file=sys.stderr)
    print("  Spatial datasets accept: --lat <lat> --lon <lon>", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fetch data from City of Mississauga Open Data portal"
    )
    parser.add_argument("search", nargs="*", help="Search term (text query against the dataset's search field)")
    parser.add_argument("--dataset", "-d", default="building-permits",
                        help="Dataset to query (default: building-permits). Use --list to see all.")
    parser.add_argument("--list", action="store_true", help="List all available datasets")
    parser.add_argument("--lat", type=float, help="Latitude for spatial query")
    parser.add_argument("--lon", type=float, help="Longitude for spatial query")
    parser.add_argument("--where", help="Raw WHERE clause (advanced — overrides search term)")
    parser.add_argument("--search-field", dest="search_field", help="Override which field to search")
    parser.add_argument("--limit", type=int, help="Limit number of records returned")
    parser.add_argument("--output", "-o", help="Output file path (default: auto-generated)")

    args = parser.parse_args()

    registry = load_registry()

    if args.list:
        print_dataset_list(registry)
        return

    # Resolve dataset
    if args.dataset not in registry:
        print(f"ERROR: Unknown dataset '{args.dataset}'", file=sys.stderr)
        print(f"Available: {', '.join(sorted(registry.keys()))}", file=sys.stderr)
        sys.exit(1)

    ds = registry[args.dataset]
    feature_url = get_feature_url(ds)
    search_term = " ".join(args.search) if args.search else None

    # Determine query mode
    is_spatial = args.lat is not None and args.lon is not None
    search_field = args.search_field or ds.get("search_field")

    if not search_term and not is_spatial and not args.where:
        print(f"ERROR: Provide a search term, --lat/--lon, or --where", file=sys.stderr)
        if ds.get("spatial"):
            print(f"  This dataset supports spatial queries: --lat <lat> --lon <lon>", file=sys.stderr)
        if search_field:
            print(f"  Or text search on field '{search_field}': <search term>", file=sys.stderr)
        sys.exit(1)

    if search_term and not search_field and not is_spatial:
        print(f"ERROR: Dataset '{args.dataset}' has no default search field.", file=sys.stderr)
        print(f"  Use --lat/--lon for spatial query, or --search-field to specify a field.", file=sys.stderr)
        sys.exit(1)

    # Discover fields
    print(f"Discovering fields for '{args.dataset}'...", file=sys.stderr)
    fields = discover_fields(feature_url)
    if not fields:
        print(f"ERROR: Could not retrieve field metadata from {feature_url}", file=sys.stderr)
        sys.exit(1)

    field_names = get_field_names(fields)
    date_fields = get_date_fields(fields)
    numeric_fields = get_numeric_fields(fields)

    # Validate search field exists
    if search_term and search_field and search_field not in field_names:
        print(f"ERROR: Field '{search_field}' not found in dataset.", file=sys.stderr)
        print(f"  Available fields: {', '.join(field_names[:20])}", file=sys.stderr)
        sys.exit(1)

    # Build query
    where = "1=1"
    spatial_params = None
    search_desc = ""

    if args.where:
        where = args.where
        search_desc = f"WHERE {where}"
    elif search_term and search_field:
        where = build_where_clause(search_term, search_field)
        search_desc = f"{search_field} ~ '{search_term}'"
    elif is_spatial:
        search_desc = f"lat={args.lat}, lon={args.lon}"

    if is_spatial:
        spatial_params = build_spatial_params(args.lat, args.lon)
        if search_desc and not search_desc.startswith("lat="):
            search_desc += f" + spatial({args.lat}, {args.lon})"

    # Determine sort order (use first date field if available)
    order_by = None
    for df in ["ISSUE_DATE", "APPLICATION_DATE", "CREATED_DATE", "DATE_"]:
        matches = [f for f in date_fields if df in f]
        if matches:
            order_by = f"{matches[0]} DESC"
            break

    print(f"Querying: {where}" + (f" + spatial" if spatial_params else ""), file=sys.stderr)

    # Fetch
    features = fetch_all_features(feature_url, field_names, where, spatial_params, order_by)

    if args.limit and len(features) > args.limit:
        features = features[:args.limit]

    records = normalize_records(features, field_names, date_fields)

    if not records:
        print(f"No records found.", file=sys.stderr)
        empty = {"metadata": {
            "source": f"City of Mississauga Open Data — {ds['description']}",
            "dataset": args.dataset,
            "query": search_desc,
            "total_records": 0,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }, "records": []}
        print(json.dumps(empty))
        return

    summary = compute_summary(records, field_names, date_fields, numeric_fields)

    output = {
        "metadata": {
            "source": f"City of Mississauga Open Data — {ds['description']}",
            "dataset": args.dataset,
            "api_endpoint": feature_url,
            "query": search_desc,
            "fields": field_names,
            "total_records": len(records),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
        },
        "records": records,
    }

    slug = sanitize_filename(search_term or f"{args.lat}_{args.lon}" if is_spatial else args.dataset)
    outpath = args.output or f"mississauga_{args.dataset}_{slug}.json"
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)

    print_summary(ds["description"], search_desc, records, summary, outpath)


if __name__ == "__main__":
    main()
