"""Tests for generate_annual_schedule.py."""

import json
import os
import sys
import tempfile
from datetime import date
from unittest.mock import patch

import openpyxl
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
    update_xlsx,
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


class TestParseCalendarSchoolHolidays:
    """Tests for new school_holidays parsing."""

    def test_tcdsb_school_holidays_parsed(self):
        path = _write_temp_calendar(TCDSB_CALENDAR)
        try:
            result = parse_calendar(path)
            assert "school_holidays" in result
            holidays = result["school_holidays"]
            names = [h["name"] for h in holidays]
            assert "Thanksgiving" in names
            assert "Family Day" in names
            assert "Good Friday" in names
            assert "Easter Monday" in names
            assert "Victoria Day" in names
        finally:
            os.unlink(path)

    def test_tcdsb_holiday_dates_correct(self):
        path = _write_temp_calendar(TCDSB_CALENDAR)
        try:
            result = parse_calendar(path)
            holiday_map = {h["name"]: h["date_str"] for h in result["school_holidays"]}
            assert holiday_map["Thanksgiving"] == "October 13, 2025"
            assert holiday_map["Family Day"] == "February 16, 2026"
            assert holiday_map["Good Friday"] == "April 3, 2026"
            assert holiday_map["Easter Monday"] == "April 6, 2026"
            assert holiday_map["Victoria Day"] == "May 18, 2026"
        finally:
            os.unlink(path)

    def test_gist_holidays_parsed(self):
        path = _write_temp_calendar(GIST_CALENDAR)
        try:
            result = parse_calendar(path)
            names = [h["name"] for h in result["school_holidays"]]
            assert "Thanksgiving" in names
            assert "Good Friday" in names
            assert "Easter Monday" in names
            assert "Victoria Day" in names
            assert "Remembrance Day" in names
        finally:
            os.unlink(path)

    def test_holidays_exclude_multi_day_breaks(self):
        """Multi-day breaks (Christmas, March) should NOT appear in school_holidays."""
        path = _write_temp_calendar(TCDSB_CALENDAR)
        try:
            result = parse_calendar(path)
            names = [h["name"] for h in result["school_holidays"]]
            assert "Christmas Break" not in names
            assert "Mid-Winter Break (March Break)" not in names
        finally:
            os.unlink(path)


class TestParseCalendarFallBreak:
    """Tests for fall_break parsing."""

    def test_gist_fall_break_parsed(self):
        path = _write_temp_calendar(GIST_CALENDAR)
        try:
            result = parse_calendar(path)
            assert "fall_break" in result
            assert result["fall_break"] is not None
            assert result["fall_break"]["start_str"] == "November 3, 2025"
            assert result["fall_break"]["end_str"] == "November 7, 2025"
        finally:
            os.unlink(path)

    def test_tdsb_no_fall_break(self):
        path = _write_temp_calendar(TDSB_CALENDAR)
        try:
            result = parse_calendar(path)
            assert result["fall_break"] is None
        finally:
            os.unlink(path)

    def test_tcdsb_no_fall_break(self):
        path = _write_temp_calendar(TCDSB_CALENDAR)
        try:
            result = parse_calendar(path)
            assert result["fall_break"] is None
        finally:
            os.unlink(path)


class TestBuildAnnualDaysSchoolHolidays:
    """Tests for school holidays in build_annual_days."""

    def _make_summer_days(self):
        """Create minimal summer days fixture."""
        return [
            {"date": date(2025, 6, 30), "week": 1, "assignments": {"Emma": "YMCA", "Liam": "YMCA"}},
            {"date": date(2025, 7, 1), "week": 1, "assignments": {"Emma": "YMCA", "Liam": "YMCA"}},
        ]

    def test_school_holidays_included(self):
        cal = parse_calendar(_write_temp_calendar(TCDSB_CALENDAR))
        summer = self._make_summer_days()
        days = build_annual_days(summer, cal, "City of Toronto", "YMCA", ["Emma", "Liam"])
        periods = {d["period"] for d in days}
        assert "school_holiday" in periods

    def test_school_holiday_uses_pa_provider(self):
        cal = parse_calendar(_write_temp_calendar(TCDSB_CALENDAR))
        summer = self._make_summer_days()
        days = build_annual_days(summer, cal, "City of Toronto", "YMCA", ["Emma", "Liam"])
        holiday_days = [d for d in days if d["period"] == "school_holiday"]
        for d in holiday_days:
            for child in ["Emma", "Liam"]:
                assert d["assignments"][child] == "City of Toronto"

    def test_school_holidays_not_during_summer(self):
        """Canada Day (Jul 1) should NOT appear as a school_holiday."""
        cal = parse_calendar(_write_temp_calendar(TCDSB_CALENDAR))
        summer = self._make_summer_days()
        days = build_annual_days(summer, cal, "City of Toronto", "YMCA", ["Emma", "Liam"])
        holiday_days = [d for d in days if d["period"] == "school_holiday"]
        holiday_dates = {d["date"] for d in holiday_days}
        assert date(2025, 7, 1) not in holiday_dates  # Canada Day is summer

    def test_school_holidays_not_during_breaks(self):
        """Holidays during winter/March break should not be double-counted."""
        cal = parse_calendar(_write_temp_calendar(TCDSB_CALENDAR))
        summer = self._make_summer_days()
        days = build_annual_days(summer, cal, "City of Toronto", "YMCA", ["Emma", "Liam"])
        # Count total days - should not have duplicates
        all_dates = [d["date"] for d in days]
        assert len(all_dates) == len(set(all_dates)), "Duplicate dates found!"

    def test_tcdsb_school_holiday_count(self):
        """TCDSB should have 5 school holidays: Thanksgiving, Family Day, Good Friday, Easter Monday, Victoria Day."""
        cal = parse_calendar(_write_temp_calendar(TCDSB_CALENDAR))
        summer = self._make_summer_days()
        days = build_annual_days(summer, cal, "City of Toronto", "YMCA", ["Emma", "Liam"])
        school_holidays = [d for d in days if d["period"] == "school_holiday"]
        assert len(school_holidays) == 5

    def test_labour_day_excluded(self):
        """Labour Day (Sep 1) is before school starts - excluded from coverage."""
        cal = parse_calendar(_write_temp_calendar(TCDSB_CALENDAR))
        summer = self._make_summer_days()
        days = build_annual_days(summer, cal, "City of Toronto", "YMCA", ["Emma", "Liam"])
        holiday_days = [d for d in days if d["period"] == "school_holiday"]
        holiday_dates = {d["date"] for d in holiday_days}
        assert date(2025, 9, 1) not in holiday_dates


class TestBuildAnnualDaysFallBreak:
    """Tests for fall break in build_annual_days."""

    def _make_summer_days(self):
        return [
            {"date": date(2025, 6, 30), "week": 1, "assignments": {"Emma": "YMCA"}},
        ]

    def test_gist_fall_break_included(self):
        cal = parse_calendar(_write_temp_calendar(GIST_CALENDAR))
        summer = self._make_summer_days()
        days = build_annual_days(summer, cal, "City of Toronto", "YMCA", ["Emma"])
        periods = {d["period"] for d in days}
        assert "fall_break" in periods

    def test_fall_break_uses_break_provider_default(self):
        cal = parse_calendar(_write_temp_calendar(GIST_CALENDAR))
        summer = self._make_summer_days()
        days = build_annual_days(summer, cal, "City of Toronto", "YMCA", ["Emma"])
        fall_days = [d for d in days if d["period"] == "fall_break"]
        for d in fall_days:
            assert d["assignments"]["Emma"] == "YMCA"

    def test_fall_break_uses_custom_provider(self):
        cal = parse_calendar(_write_temp_calendar(GIST_CALENDAR))
        summer = self._make_summer_days()
        days = build_annual_days(
            summer, cal, "City of Toronto", "YMCA", ["Emma"],
            fall_break_provider="Science Camp"
        )
        fall_days = [d for d in days if d["period"] == "fall_break"]
        for d in fall_days:
            assert d["assignments"]["Emma"] == "Science Camp"

    def test_fall_break_day_count(self):
        """GIST Nov 3-7 = 5 weekdays."""
        cal = parse_calendar(_write_temp_calendar(GIST_CALENDAR))
        summer = self._make_summer_days()
        days = build_annual_days(summer, cal, "City of Toronto", "YMCA", ["Emma"])
        fall_days = [d for d in days if d["period"] == "fall_break"]
        assert len(fall_days) == 5

    def test_tdsb_no_fall_break_days(self):
        cal = parse_calendar(_write_temp_calendar(TDSB_CALENDAR))
        summer = self._make_summer_days()
        days = build_annual_days(summer, cal, "City of Toronto", "YMCA", ["Emma"])
        fall_days = [d for d in days if d["period"] == "fall_break"]
        assert len(fall_days) == 0

    def test_no_double_counting_with_pa_days(self):
        """Fall break days should not overlap with PA days."""
        cal = parse_calendar(_write_temp_calendar(GIST_CALENDAR))
        summer = self._make_summer_days()
        days = build_annual_days(summer, cal, "City of Toronto", "YMCA", ["Emma"])
        all_dates = [d["date"] for d in days]
        assert len(all_dates) == len(set(all_dates))


class TestGroupIntoSectionsNewPeriods:
    """Tests for new period types in _group_into_sections."""

    def test_school_holidays_grouped_individually(self):
        """Each school holiday should be its own section (like PA days)."""
        days = [
            {"date": date(2025, 10, 13), "day_name": "Mon", "period": "school_holiday",
             "period_label": "School Holiday", "assignments": {"Emma": "CoT"}, "notes": "Thanksgiving"},
            {"date": date(2026, 2, 16), "day_name": "Mon", "period": "school_holiday",
             "period_label": "School Holiday", "assignments": {"Emma": "CoT"}, "notes": "Family Day"},
        ]
        sections = _group_into_sections(days)
        assert len(sections) == 2
        assert sections[0]["period"] == "school_holiday"
        assert "Thanksgiving" in sections[0]["title"]

    def test_fall_break_single_section(self):
        """Fall break should be one section (like winter/March break)."""
        days = [
            {"date": date(2025, 11, d), "day_name": "Mon", "period": "fall_break",
             "period_label": "Fall Break", "assignments": {"Emma": "YMCA"}, "notes": ""}
            for d in range(3, 8)
        ]
        sections = _group_into_sections(days)
        assert len(sections) == 1
        assert sections[0]["period"] == "fall_break"
        assert "Fall Break" in sections[0]["title"]

    def test_mixed_periods_sorted_chronologically(self):
        days = [
            {"date": date(2025, 10, 13), "day_name": "Mon", "period": "school_holiday",
             "period_label": "School Holiday", "assignments": {"E": "C"}, "notes": "Thanksgiving"},
            {"date": date(2025, 11, 3), "day_name": "Mon", "period": "fall_break",
             "period_label": "Fall Break", "assignments": {"E": "C"}, "notes": ""},
            {"date": date(2025, 9, 26), "day_name": "Fri", "period": "pa_day",
             "period_label": "PA Day", "assignments": {"E": "C"}, "notes": "PA Day 1"},
        ]
        sections = _group_into_sections(days)
        dates = [s["days"][0]["date"] for s in sections]
        assert dates == sorted(dates)


class TestRenderMarkdownNewPeriods:
    """Tests for new period types in render_markdown and annual summary."""

    def test_summary_includes_school_holidays(self):
        days = [
            {"date": date(2025, 10, 13), "day_name": "Mon", "period": "school_holiday",
             "period_label": "School Holiday", "assignments": {"Emma": "City of Toronto"},
             "notes": "Thanksgiving"},
        ]
        rates = {"City of Toronto": {"daily": 50, "before": 5, "after": 5, "lunch": 2, "total": 62}}
        md = render_markdown(days, rates, ["Emma"])
        assert "School Holidays" in md
        assert "Thanksgiving" in md

    def test_summary_includes_fall_break(self):
        days = [
            {"date": date(2025, 11, d), "day_name": "Mon", "period": "fall_break",
             "period_label": "Fall Break", "assignments": {"Emma": "YMCA"},
             "notes": ""}
            for d in range(3, 8)
        ]
        rates = {"YMCA": {"daily": 70, "before": 8, "after": 8, "lunch": 1, "total": 87}}
        md = render_markdown(days, rates, ["Emma"])
        assert "Fall Break" in md


class TestUpdateXlsxNewPeriods:
    """Verify xlsx includes new period types."""

    def test_xlsx_contains_school_holiday_rows(self):
        import tempfile, shutil
        # Copy sample budget xlsx to temp
        src = os.path.join(os.path.dirname(__file__), "..", "..", "..", "examples", "sample-budget.xlsx")
        if not os.path.exists(src):
            pytest.skip("sample-budget.xlsx not found")
        tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        tmp.close()
        shutil.copy2(src, tmp.name)
        try:
            from generate_annual_schedule import update_xlsx
            days = [
                {"date": date(2025, 10, 13), "day_name": "Mon", "period": "school_holiday",
                 "period_label": "School Holiday", "assignments": {"Emma": "City of Toronto", "Liam": "City of Toronto"},
                 "notes": "Thanksgiving"},
                {"date": date(2025, 11, 3), "day_name": "Mon", "period": "fall_break",
                 "period_label": "Fall Break", "assignments": {"Emma": "YMCA Cedar Glen", "Liam": "YMCA Cedar Glen"},
                 "notes": ""},
            ]
            update_xlsx(tmp.name, days, ["Emma", "Liam"])
            import openpyxl
            wb = openpyxl.load_workbook(tmp.name)
            ws = wb["Annual Schedule"]
            assert ws["C4"].value == "School Holiday"
            assert ws["C5"].value == "Fall Break"
            wb.close()
        finally:
            os.unlink(tmp.name)
