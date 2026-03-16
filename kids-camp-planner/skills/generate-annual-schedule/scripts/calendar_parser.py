"""Calendar parsing functions for annual schedule generation."""

import os
import re
import sys
from datetime import date, datetime, timedelta


def parse_calendar(calendar_path):
    """Parse school calendar markdown for PA days, breaks, holidays.

    Returns {
        pa_days: [{date_str, purpose}],
        winter_break: {start_str, end_str} or None,
        march_break: {start_str, end_str} or None,
        school_holidays: [{name, date_str}],
        fall_break: {start_str, end_str} or None,
    }
    """
    with open(calendar_path) as f:
        content = f.read()

    # Strip bold markers from table cells so regexes match uniformly
    content = content.replace("**", "")

    # Parse PA Days table (matches "PA Days - Elementary" or just "PA Days")
    # Format: | # | Date | Day | Purpose |
    pa_days = []
    pa_section = re.search(
        r"### PA Days(?:\s*-\s*Elementary)?\s*\n\|.*\n\|[-|]+\n((?:\|.*\n)*)",
        content,
    )
    if pa_section:
        for line in pa_section.group(1).strip().split("\n"):
            cols = [c.strip() for c in line.split("|")]
            # cols[0] is empty (before first |), cols[1]=#, cols[2]=date, cols[3]=day, cols[4]=purpose
            if len(cols) >= 5 and cols[1].strip().isdigit():
                date_str = cols[2].strip()
                purpose = cols[4].strip() if len(cols) > 4 else ""
                pa_days.append({"date_str": date_str, "purpose": purpose})

    # Parse winter break (Christmas Break or Winter Break) from Holidays & Breaks table
    # Format: | Christmas Break | December 22, 2025 - January 2, 2026 | 8 |
    winter_break = None
    winter_match = re.search(
        r"\|\s*(?:Christmas|Winter) Break\s*\|\s*(.+?)\s*\|\s*\d+\s*\|",
        content,
    )
    if winter_match:
        date_range = winter_match.group(1).strip()
        parts = date_range.split(" - ")
        if len(parts) == 2:
            winter_break = {"start_str": parts[0].strip(), "end_str": parts[1].strip()}

    # Parse March Break from Holidays & Breaks table
    # Matches "Mid-Winter Break (March Break)" or standalone "March Break"
    march_break = None
    march_match = re.search(
        r"\|\s*(?:Mid-Winter Break \(March Break\)|March Break)\s*\|\s*(.+?)\s*\|\s*\d+\s*\|",
        content,
    )
    if march_match:
        date_range = march_match.group(1).strip()
        # Format: "March 16-20, 2026"
        m = re.match(r"(\w+)\s+(\d+)-(\d+),\s*(\d+)", date_range)
        if m:
            month_name, start_day, end_day, year = m.groups()
            march_break = {
                "start_str": f"{month_name} {start_day}, {year}",
                "end_str": f"{month_name} {end_day}, {year}",
            }

    # Parse single-day school holidays from Holidays & Breaks table
    # These are entries with Weekdays Off = 1 that aren't Christmas/March break
    school_holidays = []
    holidays_section = re.search(
        r"### Holidays & Breaks\s*\n\|.*\n\|[-|]+\n((?:\|.*\n)*)",
        content,
    )
    if holidays_section:
        for line in holidays_section.group(1).strip().split("\n"):
            cols = [c.strip() for c in line.split("|")]
            # cols: ['', name, date(s), weekdays_off, ...]
            if len(cols) < 4:
                continue
            name = cols[1].strip()
            date_str = cols[2].strip()
            weekdays_off_str = cols[3].strip()

            # Skip multi-day breaks (already handled as winter_break, march_break, fall_break)
            try:
                weekdays_off = int(weekdays_off_str)
            except ValueError:
                continue
            if weekdays_off != 1:
                continue

            # Skip if this is a break we already parse (Christmas, March, Winter)
            if any(skip in name.lower() for skip in ["christmas", "march break", "mid-winter", "winter break"]):
                continue

            school_holidays.append({
                "name": name,
                "date_str": date_str,
            })

    # Parse fall break (multi-day, typically private schools)
    # Match "Fall Break" or "Midterm break" with Weekdays Off > 1 in Oct/Nov
    fall_break = None
    fall_match = re.search(
        r"\|\s*(?:Fall Break|Midterm [Bb]reak)\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|",
        content,
    )
    if fall_match:
        date_range = fall_match.group(1).strip()
        weekdays_off = int(fall_match.group(2))
        if weekdays_off > 1:
            # Parse date range: "November 3-7, 2025" or "November 3, 2025 - November 7, 2025"
            # Short form: "Month DD-DD, YYYY"
            m = re.match(r"(\w+)\s+(\d+)-(\d+),\s*(\d+)", date_range)
            if m:
                month_name, start_day, end_day, year = m.groups()
                fall_break = {
                    "start_str": f"{month_name} {start_day}, {year}",
                    "end_str": f"{month_name} {end_day}, {year}",
                }
            else:
                # Long form: "Month DD, YYYY - Month DD, YYYY"
                parts = date_range.split(" - ")
                if len(parts) == 2:
                    fall_break = {
                        "start_str": parts[0].strip(),
                        "end_str": parts[1].strip(),
                    }

    return {
        "pa_days": pa_days,
        "winter_break": winter_break,
        "march_break": march_break,
        "school_holidays": school_holidays,
        "fall_break": fall_break,
    }


def parse_date_flexible(date_str):
    """Parse dates in various formats: 'September 26, 2025', 'March 16, 2026', etc."""
    formats = ["%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {date_str}")


def get_weekdays_between(start, end, exclude_dates=None):
    """Get all weekdays between start and end (inclusive), excluding specific dates."""
    exclude = set(exclude_dates or [])
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5 and current not in exclude:
            days.append(current)
        current += timedelta(days=1)
    return days


def find_civic_holiday(year):
    """Find Ontario Civic Holiday (first Monday in August)."""
    aug_1 = date(year, 8, 1)
    days_until_monday = (7 - aug_1.weekday()) % 7
    if aug_1.weekday() == 0:
        return aug_1
    return aug_1 + timedelta(days=days_until_monday)


def get_summer_holidays(year):
    """Return Ontario summer statutory/civic holidays that most camps close for.

    Returns dict of {date: holiday_name}.
    """
    return {
        date(year, 7, 1): "Canada Day",
        find_civic_holiday(year): "Civic Holiday",
    }


def resolve_calendars(calendar_arg, children):
    """Resolve calendar argument(s) to per-child calendar paths.

    Accepts either:
      - A single path string (applies to all children)
      - A list of "ChildName:path" strings (per-child)

    Returns: {child_name: calendar_path}
    """
    if isinstance(calendar_arg, str):
        return {child: calendar_arg for child in children}

    calendars = {}
    for entry in calendar_arg:
        if ":" not in entry:
            raise ValueError(f"Multi-calendar entry must be 'ChildName:path', got: {entry}")
        child, path = entry.split(":", 1)
        calendars[child.strip()] = path.strip()

    for child in children:
        if child not in calendars:
            raise ValueError(f"No calendar specified for child: {child}")
    return calendars
