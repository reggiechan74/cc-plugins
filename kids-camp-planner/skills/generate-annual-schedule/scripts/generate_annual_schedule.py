#!/usr/bin/env python3
"""
Annual Schedule Generator

Reads summer assignments from a budget spreadsheet's Daily Schedule tab,
combines with PA days, winter break, and March break from a school calendar,
and generates a consolidated annual schedule as markdown and/or an xlsx tab.

Usage:
    # Basic: same provider for all children per period type
    python3 generate_annual_schedule.py \
      --xlsx examples/sample-budget.xlsx \
      --calendar skills/camp-planning/references/school-calendars/public-boards/tcdsb.md \
      --children "Emma,Liam" \
      --pa-day-provider "City of Toronto" \
      --break-provider "YMCA Cedar Glen" \
      --output-md camp-research/annual-schedule-2025-2026.md \
      --update-xlsx

    # Per-child, per-day overrides via JSON file
    python3 generate_annual_schedule.py \
      --xlsx examples/sample-budget.xlsx \
      --calendar skills/camp-planning/references/school-calendars/public-boards/tcdsb.md \
      --children "Emma,Liam" \
      --pa-day-provider "City of Toronto" \
      --break-provider "YMCA Cedar Glen" \
      --overrides overrides.json \
      --output-md camp-research/annual-schedule-2025-2026.md

Overrides JSON format (per-child, per-date provider assignments):
    {
      "2025-09-26": {"Emma": "Science Camp Toronto", "Liam": "City of Toronto"},
      "2025-12-22": {"Emma": "City of Toronto"},
      "2026-03-16": {"Emma": "Science Camp Toronto", "Liam": "Science Camp Toronto"}
    }
    Any child not listed for a date falls back to the period default
    (--pa-day-provider or --break-provider). Summer days from the
    spreadsheet can also be overridden.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from calendar_parser import parse_calendar, parse_date_flexible, resolve_calendars
from rate_resolver import resolve_period_rate
from schedule_builder import build_annual_days, build_annual_days_multi
from xlsx_handler import (
    read_provider_rates, read_summer_assignments, update_xlsx,
    calculate_total_cols, get_child_col_offsets, validate_child_count,
)
from renderer import render_markdown


def main():
    parser = argparse.ArgumentParser(description="Annual Schedule Generator")
    parser.add_argument("--xlsx", required=True,
                        help="Path to budget spreadsheet (reads Provider Comparison + Daily Schedule)")
    parser.add_argument("--calendar", required=True, action="append",
                        help="School calendar markdown. Single: path. Multi: 'Child:path' per entry")
    parser.add_argument("--children", required=True,
                        help="Comma-separated children's names (e.g., 'Emma,Liam')")
    parser.add_argument("--pa-day-provider", default="City of Toronto",
                        help="Provider for PA day coverage")
    parser.add_argument("--break-provider", default="YMCA Cedar Glen",
                        help="Provider for winter and March break coverage")
    parser.add_argument("--fall-break-provider",
                        help="Provider for fall break coverage (default: same as --break-provider)")
    parser.add_argument("--overrides",
                        help="JSON file with per-child, per-date provider overrides. "
                             "Format: {\"YYYY-MM-DD\": {\"ChildName\": \"Provider\"}}")
    parser.add_argument("--output-md",
                        help="Path for output markdown file")
    parser.add_argument("--update-xlsx", action="store_true",
                        help="Add/replace Annual Schedule tab in the xlsx")

    args = parser.parse_args()
    children = [c.strip() for c in args.children.split(",")]

    validate_child_count(len(children))

    # Read inputs
    provider_rates = read_provider_rates(args.xlsx)
    summer_days = read_summer_assignments(args.xlsx, children)

    # Load overrides
    overrides = {}
    if args.overrides:
        with open(args.overrides) as f:
            overrides = json.load(f)
        print(f"Loaded {len(overrides)} date overrides from {args.overrides}")

    # Validate all providers exist (defaults + every provider in overrides)
    all_providers = {args.pa_day_provider, args.break_provider}
    for date_key, child_map in overrides.items():
        for child_name, provider_name in child_map.items():
            all_providers.add(provider_name)
    missing = [p for p in all_providers if p not in provider_rates]
    if missing:
        print(f"Error: Provider(s) not found in Provider Comparison tab: {', '.join(sorted(missing))}", file=sys.stderr)
        print(f"Available providers: {', '.join(sorted(provider_rates.keys()))}", file=sys.stderr)
        sys.exit(1)

    # Resolve calendars and build unified schedule
    if len(args.calendar) == 1 and ":" not in args.calendar[0]:
        # Single calendar mode (backward compatible)
        calendar_data = parse_calendar(args.calendar[0])
        annual_days = build_annual_days(
            summer_days, calendar_data,
            args.pa_day_provider, args.break_provider, children,
            overrides=overrides,
            fall_break_provider=args.fall_break_provider,
        )
    else:
        # Multi-calendar mode
        cal_map = resolve_calendars(args.calendar, children)
        per_child_cals = {child: parse_calendar(path) for child, path in cal_map.items()}
        annual_days = build_annual_days_multi(
            summer_days, per_child_cals,
            args.pa_day_provider, args.break_provider, children,
            overrides=overrides,
            fall_break_provider=args.fall_break_provider,
        )

    # Summary stats
    period_counts = {}
    for d in annual_days:
        p = d["period"]
        period_counts[p] = period_counts.get(p, 0) + 1
    total_days = len(annual_days)

    print(f"Annual schedule: {total_days} days")
    for p, c in sorted(period_counts.items()):
        print(f"  {p}: {c} days")

    # Generate markdown
    if args.output_md:
        ctx = {
            "pa_provider": args.pa_day_provider,
            "break_provider": args.break_provider,
            "has_overrides": bool(overrides),
        }
        md = render_markdown(annual_days, provider_rates, children, render_context=ctx)
        with open(args.output_md, "w") as f:
            f.write(md)
        print(f"Markdown written to {args.output_md}")

    # Update xlsx
    if args.update_xlsx:
        update_xlsx(args.xlsx, annual_days, children, provider_count=len(provider_rates))
        print(f"Annual Schedule tab added to {args.xlsx}")


if __name__ == "__main__":
    main()
