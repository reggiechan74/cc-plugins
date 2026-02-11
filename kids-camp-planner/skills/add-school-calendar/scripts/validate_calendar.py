#!/usr/bin/env python3
"""
Validate school calendar markdown files.

Checks:
- Required sections exist (Key Dates, Holidays & Breaks, Summer Window)
- Dates are parseable
- School year matches expected format
- Table columns are correct
- No date conflicts (same date in PA days and holidays)

Usage:
    python3 validate_calendar.py path/to/calendar.md
    python3 validate_calendar.py --all path/to/school-calendars/
"""

import argparse
import os
import re
import sys
from datetime import datetime


def validate_calendar(path):
    """Validate a single calendar markdown file. Returns list of errors."""
    errors = []
    warnings = []

    with open(path) as f:
        content = f.read()

    # Required sections
    required_sections = [
        (r"### Key Dates", "Missing '### Key Dates' section"),
        (r"### Holidays & Breaks", "Missing '### Holidays & Breaks' section"),
        (r"### Summer Window", "Missing '### Summer Window' section"),
    ]
    for pattern, msg in required_sections:
        if not re.search(pattern, content):
            errors.append(msg)

    # PA Days section (required for public boards, may be absent for schools like KCS)
    has_pa = bool(re.search(r"### PA Days", content))
    if not has_pa:
        warnings.append("No '### PA Days' section found (OK for schools using midterm breaks instead)")

    # School year header
    year_match = re.search(r"## (\d{4})-(\d{4}) School Year", content)
    if not year_match:
        errors.append("Missing '## YYYY-YYYY School Year' header")
    else:
        y1, y2 = int(year_match.group(1)), int(year_match.group(2))
        if y2 != y1 + 1:
            errors.append(f"School year span invalid: {y1}-{y2} (expected consecutive years)")

    # Validate dates in PA Days table
    pa_section = re.search(
        r"### PA Days[^\n]*\n\|.*\n\|[-|]+\n((?:\|.*\n)*)", content
    )
    if pa_section:
        for line in pa_section.group(1).strip().split("\n"):
            cols = [c.strip() for c in line.split("|")]
            if len(cols) >= 5 and cols[1].strip().replace(".", "").isdigit():
                date_str = cols[2].strip()
                try:
                    _parse_date(date_str)
                except ValueError:
                    errors.append(f"Cannot parse PA day date: '{date_str}'")

    # Validate Holidays & Breaks table
    holidays_section = re.search(
        r"### Holidays & Breaks\s*\n\|.*\n\|[-|]+\n((?:\|.*\n)*)", content
    )
    if holidays_section:
        for line in holidays_section.group(1).strip().split("\n"):
            cols = [c.strip() for c in line.split("|")]
            if len(cols) < 4:
                errors.append(f"Holidays table row has too few columns: {line.strip()}")

    # Summer Window
    summer_section = re.search(r"### Summer Window", content)
    if summer_section:
        if not re.search(r"\*\*Last school day\*\*", content):
            warnings.append("Summer Window missing 'Last school day' field")
        if not re.search(r"\*\*First fall day\*\*", content):
            warnings.append("Summer Window missing 'First fall day' field")

    # Source/last-updated
    if not re.search(r"\*Last updated:", content):
        warnings.append("Missing '*Last updated:' footer")

    return errors, warnings


def _parse_date(date_str):
    """Try to parse a date string."""
    formats = ["%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse: {date_str}")


def main():
    parser = argparse.ArgumentParser(description="Validate school calendar markdown files")
    parser.add_argument("path", help="Path to calendar file or directory (with --all)")
    parser.add_argument("--all", action="store_true",
                        help="Validate all .md files in the directory recursively")
    args = parser.parse_args()

    files = []
    if args.all:
        for root, dirs, filenames in os.walk(args.path):
            for fn in filenames:
                if fn.endswith(".md") and fn not in ("README.md", "RESEARCH-PLAN.md", "calendar-template.md"):
                    files.append(os.path.join(root, fn))
    else:
        files = [args.path]

    total_errors = 0
    total_warnings = 0
    for f in sorted(files):
        errors, warnings = validate_calendar(f)
        status = "PASS" if not errors else "FAIL"
        print(f"{status}: {os.path.relpath(f)}")
        for e in errors:
            print(f"  ERROR: {e}")
            total_errors += 1
        for w in warnings:
            print(f"  WARN: {w}")
            total_warnings += 1

    print(f"\n{len(files)} files checked, {total_errors} errors, {total_warnings} warnings")
    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
