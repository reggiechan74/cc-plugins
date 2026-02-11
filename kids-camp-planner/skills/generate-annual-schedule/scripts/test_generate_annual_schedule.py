"""Tests for generate_annual_schedule.py."""

import json
import os
import sys
import tempfile
from datetime import date
from unittest.mock import patch

import pytest

# Add script directory to path
sys.path.insert(0, os.path.dirname(__file__))
from generate_annual_schedule import (
    parse_calendar,
    parse_date_flexible,
    build_annual_days,
    get_weekdays_between,
    get_summer_holidays,
    find_civic_holiday,
    _group_into_sections,
    render_markdown,
    read_provider_rates,
)


# --- Fixtures: calendar markdown content ---

TCDSB_CALENDAR = """\
# Toronto Catholic District School Board (TCDSB)

## 2025-2026 School Year

### Key Dates
| Item | Date(s) |
|------|---------|
| First day of school | September 2, 2025 |
| Last day of classes (elementary) | June 25, 2026 |

### PA Days - Elementary
| # | Date | Day | Purpose |
|---|------|-----|---------|
| 1 | September 26, 2025 | Friday | Provincial Education Priorities |
| 2 | October 10, 2025 | Friday | Provincial Education Priorities |
| 3 | November 14, 2025 | Friday | Parent-Teacher Conferences |
| 4 | January 16, 2026 | Friday | Assessment, Evaluation and Reporting |
| 5 | February 13, 2026 | Friday | Parent-Teacher Conferences |
| 6 | June 5, 2026 | Friday | Assessment, Evaluation and Reporting |
| 7 | June 26, 2026 | Friday | Provincial Education Priorities |

### Holidays & Breaks
| Holiday/Break | Date(s) | Weekdays Off |
|---------------|---------|-------------|
| Labour Day | September 1, 2025 | 1 |
| Thanksgiving | October 13, 2025 | 1 |
| Christmas Break | December 22, 2025 - January 2, 2026 | 8 |
| Family Day | February 16, 2026 | 1 |
| Mid-Winter Break (March Break) | March 16-20, 2026 | 5 |
| Good Friday | April 3, 2026 | 1 |
| Easter Monday | April 6, 2026 | 1 |
| Victoria Day | May 18, 2026 | 1 |
"""

GIST_CALENDAR = """\
# German International School Toronto (GIST)

## 2025-2026 School Year

### PA Days
| # | Date | Day | Purpose |
|---|------|-----|---------|
| 1 | October 24, 2025 | Friday | Kindergarten only |
| 2 | November 21, 2025 | Friday | Learning Development Meetings |
| 3 | January 30, 2026 | Friday | No classes |
| 4 | May 29, 2026 | Friday | No classes |

### Holidays & Breaks
| Holiday/Break | Date(s) | Weekdays Off | TDSB Equivalent |
|---------------|---------|-------------|-----------------|
| Labour Day | September 1, 2025 | 1 | Same |
| National Day for Truth & Reconciliation | September 30, 2025 | 1 | Same |
| Thanksgiving | October 13, 2025 | 1 | Same |
| Fall Break | November 3-7, 2025 | 5 | None - TDSB has no fall break |
| Remembrance Day | November 11, 2025 | 1 | Same |
| Christmas Break | December 22, 2025 - January 2, 2026 | 8 | Same |
| Family Day | February 16, 2026 | 1 | Same |
| March Break | March 16-27, 2026 | 10 | March 16-20 only (5 days) |
| Good Friday | April 3, 2026 | 1 | Same |
| Easter Monday | April 6, 2026 | 1 | Same |
| Victoria Day | May 18, 2026 | 1 | Same |
"""

# Calendar with no fall break (public board)
TDSB_CALENDAR = """\
# Toronto District School Board (TDSB)

## 2025-2026 School Year

### PA Days - Elementary
| # | Date | Day | Purpose |
|---|------|-----|---------|
| 1 | September 26, 2025 | Friday | Professional Development |
| 2 | October 10, 2025 | Friday | Professional Development |
| 3 | November 14, 2025 | Friday | Parent Teacher Conferences |
| 4 | January 16, 2026 | Friday | Assessment and Reporting |
| 5 | February 13, 2026 | Friday | Parent Teacher Conferences |
| 6 | June 5, 2026 | Friday | Assessment and Reporting |
| 7 | June 26, 2026 | Friday | Professional Development |

### Holidays & Breaks
| Holiday/Break | Date(s) | Weekdays Off |
|---------------|---------|-------------|
| Labour Day | September 1, 2025 | 1 |
| Thanksgiving | October 13, 2025 | 1 |
| Winter Break | December 22, 2025 - January 2, 2026 | 8 |
| Family Day | February 16, 2026 | 1 |
| Mid-Winter Break (March Break) | March 16-20, 2026 | 5 |
| Good Friday | April 3, 2026 | 1 |
| Easter Monday | April 6, 2026 | 1 |
| Victoria Day | May 18, 2026 | 1 |
"""


def _write_temp_calendar(content):
    """Write calendar content to a temp file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
    f.write(content)
    f.close()
    return f.name


# --- Existing functionality tests (regression) ---

class TestParseDateFlexible:
    def test_full_month_name(self):
        assert parse_date_flexible("September 26, 2025") == date(2025, 9, 26)

    def test_iso_format(self):
        assert parse_date_flexible("2025-09-26") == date(2025, 9, 26)

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            parse_date_flexible("not a date")


class TestGetWeekdaysBetween:
    def test_single_week(self):
        days = get_weekdays_between(date(2025, 7, 7), date(2025, 7, 11))
        assert len(days) == 5
        assert all(d.weekday() < 5 for d in days)

    def test_with_exclusion(self):
        days = get_weekdays_between(
            date(2025, 7, 7), date(2025, 7, 11),
            exclude_dates={date(2025, 7, 9)}
        )
        assert len(days) == 4
        assert date(2025, 7, 9) not in days


class TestFindCivicHoliday:
    def test_2025(self):
        assert find_civic_holiday(2025) == date(2025, 8, 4)

    def test_2026(self):
        assert find_civic_holiday(2026) == date(2026, 8, 3)


class TestGetSummerHolidays:
    def test_returns_canada_day_and_civic(self):
        holidays = get_summer_holidays(2025)
        assert date(2025, 7, 1) in holidays
        assert holidays[date(2025, 7, 1)] == "Canada Day"
        civic = find_civic_holiday(2025)
        assert civic in holidays


class TestParseCalendarExisting:
    """Regression tests for existing parse_calendar behavior."""

    def test_tcdsb_pa_days(self):
        path = _write_temp_calendar(TCDSB_CALENDAR)
        try:
            result = parse_calendar(path)
            assert len(result["pa_days"]) == 7
            assert result["pa_days"][0]["date_str"] == "September 26, 2025"
        finally:
            os.unlink(path)

    def test_tcdsb_winter_break(self):
        path = _write_temp_calendar(TCDSB_CALENDAR)
        try:
            result = parse_calendar(path)
            assert result["winter_break"]["start_str"] == "December 22, 2025"
            assert result["winter_break"]["end_str"] == "January 2, 2026"
        finally:
            os.unlink(path)

    def test_tcdsb_march_break(self):
        path = _write_temp_calendar(TCDSB_CALENDAR)
        try:
            result = parse_calendar(path)
            assert result["march_break"]["start_str"] == "March 16, 2026"
            assert result["march_break"]["end_str"] == "March 20, 2026"
        finally:
            os.unlink(path)

    def test_tdsb_winter_break_label(self):
        """TDSB uses 'Winter Break' instead of 'Christmas Break'."""
        path = _write_temp_calendar(TDSB_CALENDAR)
        try:
            result = parse_calendar(path)
            assert result["winter_break"] is not None
            assert result["winter_break"]["start_str"] == "December 22, 2025"
        finally:
            os.unlink(path)
