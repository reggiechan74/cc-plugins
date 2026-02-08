#!/usr/bin/env python3
"""
Summer Dates Calculator

Calculate the summer coverage window between end of school and start of fall,
accounting for weekends and providing week-by-week breakdowns.

Usage:
    # Basic usage with explicit dates
    python3 summer_dates.py --year 2025 \
        --last-school-day 2025-06-26 --first-fall-day 2025-09-02

    # Auto-calculate Labour Day for fall start
    python3 summer_dates.py --year 2025 --last-school-day 2025-06-26

    # With exclusion dates (vacations)
    python3 summer_dates.py --year 2025 \
        --last-school-day 2025-06-26 \
        --exclude 2025-07-14:2025-07-18 \
        --exclude 2025-08-11:2025-08-15

    # JSON output
    python3 summer_dates.py --year 2025 \
        --last-school-day 2025-06-26 --format json
"""

import argparse
import json
from datetime import date, datetime, timedelta


def find_labour_day(year):
    """Find Labour Day (first Monday in September) for a given year."""
    sept_1 = date(year, 9, 1)
    # Monday is weekday 0
    days_until_monday = (7 - sept_1.weekday()) % 7
    if sept_1.weekday() == 0:
        return sept_1
    return sept_1 + timedelta(days=days_until_monday)


def get_weekdays(start_date, end_date):
    """Get all weekdays between two dates (inclusive)."""
    weekdays = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Monday=0 through Friday=4
            weekdays.append(current)
        current += timedelta(days=1)
    return weekdays


def get_weeks(start_date, end_date):
    """Break a date range into Monday-Friday weeks."""
    weeks = []
    current = start_date

    # Find the first Monday on or after start_date
    while current.weekday() != 0:
        current += timedelta(days=1)

    # Handle partial first week if start_date is not a Monday
    if start_date < current:
        first_friday = current - timedelta(days=1)
        # Find the Friday of the partial week
        temp = start_date
        while temp.weekday() != 4 and temp < current:
            temp += timedelta(days=1)
        first_week_end = min(temp, first_friday)
        weekdays = get_weekdays(start_date, first_week_end)
        if weekdays:
            weeks.append({
                "monday": start_date.isoformat(),
                "friday": first_week_end.isoformat(),
                "start": start_date.isoformat(),
                "end": first_week_end.isoformat(),
                "weekdays": len(weekdays),
                "partial": True,
            })

    # Full weeks
    while current + timedelta(days=4) <= end_date:
        friday = current + timedelta(days=4)
        weeks.append({
            "monday": current.isoformat(),
            "friday": friday.isoformat(),
            "start": current.isoformat(),
            "end": friday.isoformat(),
            "weekdays": 5,
            "partial": False,
        })
        current += timedelta(days=7)

    # Handle partial last week
    if current <= end_date:
        last_friday = min(current + timedelta(days=4), end_date)
        weekdays = get_weekdays(current, last_friday)
        if weekdays:
            weeks.append({
                "monday": current.isoformat(),
                "friday": last_friday.isoformat(),
                "start": current.isoformat(),
                "end": last_friday.isoformat(),
                "weekdays": len(weekdays),
                "partial": len(weekdays) < 5,
            })

    return weeks


def parse_date(date_str):
    """Parse a date string in YYYY-MM-DD format."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def main():
    parser = argparse.ArgumentParser(description="Summer Dates Calculator")
    parser.add_argument("--year", type=int, required=True, help="Summer year")
    parser.add_argument("--last-school-day", required=True,
                        help="Last day of school (YYYY-MM-DD)")
    parser.add_argument("--first-fall-day",
                        help="First day of fall school (YYYY-MM-DD). "
                             "Defaults to day after Labour Day.")
    parser.add_argument("--exclude", action="append", default=[],
                        help="Exclude date range START:END (YYYY-MM-DD:YYYY-MM-DD). "
                             "Can be specified multiple times.")
    parser.add_argument("--format", choices=["text", "json", "markdown"],
                        default="text", help="Output format")

    args = parser.parse_args()

    last_school = parse_date(args.last_school_day)

    if args.first_fall_day:
        first_fall = parse_date(args.first_fall_day)
    else:
        labour_day = find_labour_day(args.year)
        first_fall = labour_day + timedelta(days=1)

    # Coverage window: first weekday after last school day to last weekday before first fall day
    coverage_start = last_school + timedelta(days=1)
    while coverage_start.weekday() >= 5:
        coverage_start += timedelta(days=1)

    coverage_end = first_fall - timedelta(days=1)
    while coverage_end.weekday() >= 5:
        coverage_end -= timedelta(days=1)

    # Exclude Labour Day from coverage (statutory holiday, no camp programs run)
    labour_day = find_labour_day(args.year)
    if coverage_end == labour_day:
        coverage_end = labour_day - timedelta(days=3)  # Friday before Labour Day weekend

    # All weekdays in coverage window
    all_weekdays = get_weekdays(coverage_start, coverage_end)

    # Parse exclusion dates
    excluded_days = set()
    exclusion_ranges = []
    for exc in args.exclude:
        parts = exc.split(":")
        if len(parts) == 2:
            exc_start = parse_date(parts[0])
            exc_end = parse_date(parts[1])
            exclusion_ranges.append({"start": parts[0], "end": parts[1]})
            current = exc_start
            while current <= exc_end:
                if current.weekday() < 5:
                    excluded_days.add(current)
                current += timedelta(days=1)

    coverage_days = [d for d in all_weekdays if d not in excluded_days]

    # Week breakdown
    weeks = get_weeks(coverage_start, coverage_end)

    # Number weeks
    for i, w in enumerate(weeks, 1):
        w["week_number"] = i
        # Check if week overlaps with exclusions
        week_start = parse_date(w["start"])
        week_end = parse_date(w["end"])
        week_weekdays = get_weekdays(week_start, week_end)
        excluded_in_week = [d for d in week_weekdays if d in excluded_days]
        w["excluded_days"] = len(excluded_in_week)
        w["coverage_days"] = len(week_weekdays) - len(excluded_in_week)
        if len(excluded_in_week) == len(week_weekdays):
            w["status"] = "VACATION"
        elif len(excluded_in_week) > 0:
            w["status"] = "PARTIAL"
        else:
            w["status"] = "NEEDS COVERAGE"

    result = {
        "year": args.year,
        "last_school_day": last_school.isoformat(),
        "first_fall_day": first_fall.isoformat(),
        "coverage_start": coverage_start.isoformat(),
        "coverage_end": coverage_end.isoformat(),
        "total_weekdays": len(all_weekdays),
        "excluded_weekdays": len(excluded_days),
        "coverage_weekdays": len(coverage_days),
        "total_weeks": len(weeks),
        "exclusions": exclusion_ranges,
        "weeks": weeks,
    }

    if args.format == "json":
        print(json.dumps(result, indent=2))
    elif args.format == "markdown":
        print(f"# Summer {args.year} Coverage Window\n")
        print(f"- **Last school day:** {last_school.isoformat()}")
        print(f"- **First fall day:** {first_fall.isoformat()}")
        print(f"- **Coverage start:** {coverage_start.isoformat()}")
        print(f"- **Coverage end:** {coverage_end.isoformat()}")
        print(f"- **Total weekdays:** {len(all_weekdays)}")
        if excluded_days:
            print(f"- **Vacation/excluded days:** {len(excluded_days)}")
        print(f"- **Days needing coverage:** {len(coverage_days)}")
        print(f"- **Total weeks:** {len(weeks)}")
        print()
        if exclusion_ranges:
            print("## Exclusion Dates\n")
            for exc in exclusion_ranges:
                print(f"- {exc['start']} to {exc['end']}")
            print()
        print("## Week-by-Week Breakdown\n")
        print("| Week | Monday | Friday | Days | Status |")
        print("|-----:|--------|--------|-----:|--------|")
        for w in weeks:
            partial_note = " (partial)" if w["partial"] else ""
            print(f"| {w['week_number']} | {w['monday']} | {w['friday']} | {w['coverage_days']}{partial_note} | {w['status']} |")
    else:
        print(f"Summer {args.year} Coverage Window")
        print(f"{'='*40}")
        print(f"Last school day:    {last_school.isoformat()}")
        print(f"First fall day:     {first_fall.isoformat()}")
        print(f"Coverage start:     {coverage_start.isoformat()}")
        print(f"Coverage end:       {coverage_end.isoformat()}")
        print(f"Total weekdays:     {len(all_weekdays)}")
        if excluded_days:
            print(f"Excluded days:      {len(excluded_days)}")
        print(f"Coverage days:      {len(coverage_days)}")
        print(f"Total weeks:        {len(weeks)}")
        print()
        if exclusion_ranges:
            print("Exclusion Dates:")
            for exc in exclusion_ranges:
                print(f"  {exc['start']} to {exc['end']}")
            print()
        print("Week-by-Week:")
        print(f"{'Week':<6} {'Monday':<12} {'Friday':<12} {'Days':<6} {'Status'}")
        print("-" * 50)
        for w in weeks:
            print(f"{w['week_number']:<6} {w['monday']:<12} {w['friday']:<12} {w['coverage_days']:<6} {w['status']}")


if __name__ == "__main__":
    main()
