#!/usr/bin/env python3
"""Fetch building permits from City of Mississauga ArcGIS FeatureServer."""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from typing import Optional

FEATURE_SERVER = (
    "https://services6.arcgis.com/hM5ymMLbxIyWTjn2"
    "/arcgis/rest/services/Issued_Building_Permits/FeatureServer/0"
)
MAX_RECORD_COUNT = 2000
DATE_FIELDS = {"APPLICATION_DATE", "ISSUE_DATE", "COMPLETE_DATE"}
ALL_FIELDS = [
    "OBJECTID", "BP_NO", "STATUS", "ADDRESS", "UNIT_NO", "DESCRIPTION",
    "SCOPE", "FILE_TYPE", "BLDG_TYPE", "APP_DETAIL", "APPL_AREA", "STOREYS",
    "EST_CON_VALUE", "RES_UNITS", "DEMO", "POSTAL_CODE", "BLDG_NO", "WARD",
    "ZAREA", "LATITUDE", "LONGITUDE", "APPLICATION_DATE", "ISSUE_DATE",
    "COMPLETE_DATE",
]


DIRECTION_MAP = {
    "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W",
    "NORTHEAST": "NE", "NORTHWEST": "NW",
    "SOUTHEAST": "SE", "SOUTHWEST": "SW",
}


def _escape_sql(value: str) -> str:
    """Escape single quotes for ArcGIS SQL WHERE clauses."""
    return value.replace("'", "''")


def _normalize_address(address: str) -> str:
    """Normalize direction words to abbreviations used in municipal GIS data."""
    words = address.upper().split()
    return " ".join(DIRECTION_MAP.get(w, w) for w in words)


def build_where_clause(args: argparse.Namespace) -> str:
    """Build SQL WHERE clause from CLI arguments."""
    addr = _escape_sql(_normalize_address(args.address))
    clauses = [f"UPPER(ADDRESS) LIKE '%{addr}%'"]

    if args.type:
        clauses.append(f"FILE_TYPE = '{_escape_sql(args.type.upper())}'")
    if args.scope:
        clauses.append(f"UPPER(SCOPE) LIKE '%{_escape_sql(args.scope.upper())}%'")
    if args.ward is not None:
        clauses.append(f"WARD = {args.ward}")
    if args.min_value is not None:
        clauses.append(f"EST_CON_VALUE >= {args.min_value}")
    if args.max_value is not None:
        clauses.append(f"EST_CON_VALUE <= {args.max_value}")

    date_field = args.date_field
    if args.date_from:
        clauses.append(f"{date_field} >= DATE '{args.date_from}'")
    if args.date_to:
        clauses.append(f"{date_field} <= DATE '{args.date_to}'")

    return " AND ".join(clauses)


def epoch_ms_to_iso(epoch_ms) -> Optional[str]:
    """Convert ArcGIS epoch milliseconds to ISO 8601 date string."""
    if epoch_ms is None:
        return None
    dt = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def query_features(where: str, offset: int = 0) -> dict:
    """Query the ArcGIS FeatureServer with pagination support."""
    params = {
        "where": where,
        "outFields": ",".join(ALL_FIELDS),
        "resultOffset": offset,
        "resultRecordCount": MAX_RECORD_COUNT,
        "orderByFields": "ISSUE_DATE DESC",
        "f": "json",
    }
    url = f"{FEATURE_SERVER}/query?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url)
    req.add_header("User-Agent", "mississauga-permits-plugin/0.1.0")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"ERROR: HTTP {e.code} from ArcGIS API", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Could not reach ArcGIS API: {e.reason}", file=sys.stderr)
        sys.exit(1)


def fetch_all_permits(where: str) -> list[dict]:
    """Fetch all matching permits, handling pagination."""
    all_features = []
    offset = 0

    while True:
        data = query_features(where, offset)

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


def normalize_record(feature: dict) -> dict:
    """Convert ArcGIS feature to flat record with normalized dates."""
    attrs = feature.get("attributes", {})
    record = {}
    for field in ALL_FIELDS:
        val = attrs.get(field)
        if field in DATE_FIELDS and val is not None:
            val = epoch_ms_to_iso(val)
        record[field] = val
    return record


def compute_summary(permits: list[dict]) -> dict:
    """Compute aggregate summary statistics."""
    values = [p["EST_CON_VALUE"] for p in permits if p.get("EST_CON_VALUE")]
    dates = []
    for p in permits:
        for df in ("ISSUE_DATE", "APPLICATION_DATE"):
            if p.get(df):
                dates.append(p[df])

    file_types = Counter(p.get("FILE_TYPE") or "UNKNOWN" for p in permits)
    scopes = Counter(p.get("SCOPE") or "UNKNOWN" for p in permits)
    statuses = Counter(p.get("STATUS") or "UNKNOWN" for p in permits)

    return {
        "total_estimated_value": sum(values) if values else None,
        "average_estimated_value": round(sum(values) / len(values)) if values else None,
        "date_range": {
            "earliest": min(dates) if dates else None,
            "latest": max(dates) if dates else None,
        },
        "by_file_type": dict(file_types.most_common()),
        "by_scope": dict(scopes.most_common()),
        "by_status": dict(statuses.most_common()),
    }


def sanitize_filename(address: str) -> str:
    """Create safe filename from address string."""
    clean = re.sub(r"[^\w\s-]", "", address.strip())
    clean = re.sub(r"\s+", "_", clean)
    return clean.lower()[:60]


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Mississauga building permits by address"
    )
    parser.add_argument("address", help="Street address to search (partial match)")
    parser.add_argument("--type", help="Filter by FILE_TYPE (RESIDENTIAL, COMMERCIAL, INDUSTRIAL, PUBLIC)")
    parser.add_argument("--scope", help="Filter by SCOPE (partial match)")
    parser.add_argument("--ward", type=int, help="Filter by ward number")
    parser.add_argument("--min-value", type=int, dest="min_value", help="Minimum estimated construction value")
    parser.add_argument("--max-value", type=int, dest="max_value", help="Maximum estimated construction value")
    parser.add_argument("--from", dest="date_from", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="date_to", help="End date (YYYY-MM-DD)")
    parser.add_argument("--date-field", dest="date_field", default="ISSUE_DATE",
                        choices=["APPLICATION_DATE", "ISSUE_DATE", "COMPLETE_DATE"],
                        help="Which date field to filter on (default: ISSUE_DATE)")
    parser.add_argument("--output", "-o", help="Output file path (default: auto-generated)")

    args = parser.parse_args()

    where = build_where_clause(args)
    print(f"Querying: {where}", file=sys.stderr)

    features = fetch_all_permits(where)
    permits = [normalize_record(f) for f in features]

    if not permits:
        print(f"No permits found matching '{args.address}'", file=sys.stderr)
        print(json.dumps({"metadata": {
            "source": "City of Mississauga Open Data - Issued Building Permits",
            "query_address": args.address,
            "total_records": 0,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }, "permits": []}))
        return

    summary = compute_summary(permits)

    output = {
        "$schema": "./schemas/building_permit.schema.json",
        "metadata": {
            "source": "City of Mississauga Open Data - Issued Building Permits",
            "api_endpoint": FEATURE_SERVER,
            "query_address": args.address,
            "filters_applied": {
                "date_field": args.date_field,
                "date_from": args.date_from,
                "date_to": args.date_to,
                "file_type": args.type,
                "scope": args.scope,
                "ward": args.ward,
                "min_value": args.min_value,
                "max_value": args.max_value,
            },
            "total_records": len(permits),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
        },
        "permits": permits,
    }

    outpath = args.output or f"building_permits_{sanitize_filename(args.address)}.json"
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)

    # Print summary to stderr for Claude to read
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Mississauga Building Permits — Results", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"  Address search: {args.address}", file=sys.stderr)
    print(f"  Records found:  {len(permits)}", file=sys.stderr)
    if summary["total_estimated_value"]:
        print(f"  Total est. value: ${summary['total_estimated_value']:,.0f}", file=sys.stderr)
        print(f"  Avg est. value:   ${summary['average_estimated_value']:,.0f}", file=sys.stderr)
    if summary["date_range"]["earliest"]:
        print(f"  Date range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}", file=sys.stderr)
    print(f"\n  By Type:", file=sys.stderr)
    for k, v in summary["by_file_type"].items():
        print(f"    {k}: {v}", file=sys.stderr)
    print(f"\n  By Scope:", file=sys.stderr)
    for k, v in list(summary["by_scope"].items())[:10]:
        print(f"    {k}: {v}", file=sys.stderr)
    print(f"\n  Saved to: {outpath}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)


if __name__ == "__main__":
    main()
