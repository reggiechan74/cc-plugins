# Kids Camp Planner Roadmap Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement all 8 outstanding roadmap items across 4 phases: calendar parser generalization, multi-board families, spreadsheet structural changes, and calendar data expansion.

**Architecture:** The central `generate_annual_schedule.py` script is touched by 5 of 8 items (Phases 1-3). Phase 1 (parser generalization) is foundational and unblocks Phases 2 and 3. Phase 4 (calendar data) is independent and runs in parallel. All changes maintain backward compatibility with existing 2-child, single-calendar workflows.

**Tech Stack:** Python 3 + openpyxl, pytest for testing, markdown for docs/calendars, YAML frontmatter for skill/config files.

---

## Phase 1: Calendar Parser Generalization

**Goal:** Refactor `parse_calendar()` to parse ALL entries from the Holidays & Breaks table (not just Christmas Break and March Break), enabling school holiday coverage and fall break support.

**Dependency:** None (foundational)

### Task 1: Set Up Test Infrastructure

**Files:**
- Create: `skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py`

**Step 1: Create test file with test fixtures**

```python
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
```

**Step 2: Run tests to verify they pass (regression tests for existing behavior)**

Run: `cd /workspaces/claude-plugins/kids-camp-planner && python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py -v`
Expected: All tests PASS (except `test_tdsb_winter_break_label` may FAIL because current code only matches "Christmas Break", not "Winter Break" — this is a known gap we'll fix in Task 2)

**Step 3: Commit**

```bash
git add skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py
git commit -m "test: add regression test suite for generate_annual_schedule.py"
```

---

### Task 2: Parse School Holidays from Holidays & Breaks Table

**Files:**
- Modify: `skills/generate-annual-schedule/scripts/generate_annual_schedule.py:120-183` (parse_calendar)
- Test: `skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py`

**Context:** Currently `parse_calendar()` only looks for "Christmas Break" and "Mid-Winter Break (March Break)" in the Holidays & Breaks table. Single-day holidays (Thanksgiving, Family Day, Good Friday, Easter Monday, Victoria Day) are present in calendar files but never parsed. These are school-off days that need coverage.

**Step 1: Write failing tests for school holiday parsing**

Append to the test file:

```python
class TestParseCalendarSchoolHolidays:
    """Tests for new school_holidays parsing."""

    def test_tcdsb_school_holidays_parsed(self):
        path = _write_temp_calendar(TCDSB_CALENDAR)
        try:
            result = parse_calendar(path)
            assert "school_holidays" in result
            holidays = result["school_holidays"]
            # Should find: Thanksgiving, Family Day, Good Friday, Easter Monday, Victoria Day
            # Labour Day is BEFORE school starts (Sep 1 < Sep 2) -- include anyway, filtered later
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
            # GIST also has Remembrance Day and Truth & Reconciliation
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
```

**Step 2: Run tests to verify they fail**

Run: `cd /workspaces/claude-plugins/kids-camp-planner && python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py::TestParseCalendarSchoolHolidays -v`
Expected: FAIL with `KeyError: 'school_holidays'`

**Step 3: Implement school holiday parsing in parse_calendar()**

In `generate_annual_schedule.py`, add the following after the March break parsing block (after line 177, before line 179's `return`):

```python
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

            # Skip if this is a break we already parse (Christmas, March)
            if any(skip in name.lower() for skip in ["christmas", "march break", "mid-winter"]):
                continue

            school_holidays.append({
                "name": name,
                "date_str": date_str,
            })
```

Update the return statement to include `school_holidays`:

```python
    return {
        "pa_days": pa_days,
        "winter_break": winter_break,
        "march_break": march_break,
        "school_holidays": school_holidays,
    }
```

Also fix the winter break regex to match both "Christmas Break" and "Winter Break":

```python
    winter_match = re.search(
        r"\|\s*(?:Christmas|Winter) Break\s*\|\s*(.+?)\s*\|\s*\d+\s*\|",
        content,
    )
```

**Step 4: Run tests to verify they pass**

Run: `cd /workspaces/claude-plugins/kids-camp-planner && python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py -v`
Expected: ALL PASS (including the regression tests and new school holiday tests)

**Step 5: Commit**

```bash
git add skills/generate-annual-schedule/scripts/generate_annual_schedule.py \
      skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py
git commit -m "feat: parse single-day school holidays from Holidays & Breaks table

parse_calendar() now returns school_holidays list with single-day entries
(Thanksgiving, Family Day, Good Friday, Easter Monday, Victoria Day, etc.)
Also fixes winter break regex to match both 'Christmas Break' and 'Winter Break' labels."
```

---

### Task 3: Parse Fall Break from Holidays & Breaks Table

**Files:**
- Modify: `skills/generate-annual-schedule/scripts/generate_annual_schedule.py:120-183`
- Test: `skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py`

**Context:** GIST has Fall Break (Nov 3-7, 2025). KCS has Midterm breaks. The parser needs to recognize these.

**Step 1: Write failing tests for fall break parsing**

```python
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
```

**Step 2: Run tests to verify they fail**

Run: `python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py::TestParseCalendarFallBreak -v`
Expected: FAIL with `KeyError: 'fall_break'`

**Step 3: Implement fall break parsing**

Add after the school_holidays parsing block, before the return statement:

```python
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
```

Update the return statement:

```python
    return {
        "pa_days": pa_days,
        "winter_break": winter_break,
        "march_break": march_break,
        "school_holidays": school_holidays,
        "fall_break": fall_break,
    }
```

**Step 4: Run tests to verify they pass**

Run: `python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add skills/generate-annual-schedule/scripts/generate_annual_schedule.py \
      skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py
git commit -m "feat: parse fall break from Holidays & Breaks table

Matches 'Fall Break' and 'Midterm break' patterns with Weekdays Off > 1.
Returns null for public boards (TDSB, TCDSB) that have no fall break."
```

---

### Task 4: Add School Holidays to build_annual_days()

**Files:**
- Modify: `skills/generate-annual-schedule/scripts/generate_annual_schedule.py:244-354` (build_annual_days)
- Test: `skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py`

**Context:** `build_annual_days()` currently handles summer, PA days, winter break, and March break. We need to add school holidays (single-day entries using `pa_provider`) and fall break (multi-day using `break_provider` or new `fall_break_provider`).

**Step 1: Write failing tests**

```python
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

    def test_tcdsb_total_days_increased(self):
        """TCDSB should go from 59 to ~64 with school holidays added."""
        cal = parse_calendar(_write_temp_calendar(TCDSB_CALENDAR))
        summer = self._make_summer_days()
        days = build_annual_days(summer, cal, "City of Toronto", "YMCA", ["Emma", "Liam"])
        # 2 summer + 7 PA + 7 winter + 5 march + school holidays
        # School holidays: Thanksgiving, Family Day, Good Friday, Easter Monday, Victoria Day = 5
        # (Labour Day excluded: falls before first school day Sep 2)
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
```

**Step 2: Run tests to verify they fail**

Run: `python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py::TestBuildAnnualDaysSchoolHolidays -v`
Expected: FAIL

**Step 3: Implement school holidays in build_annual_days()**

Add `fall_break_provider=None` parameter. After the March break block (line 351), add:

```python
    # School holidays (single-day, use pa_provider for coverage)
    # Exclude: holidays during summer, during winter break, during March break
    # These are filtered by seen_dates set
    summer_start = summer_days[0]["date"] if summer_days else None
    summer_end = summer_days[-1]["date"] if summer_days else None
    for holiday in calendar_data.get("school_holidays", []):
        d = parse_date_flexible(holiday["date_str"])
        if d in seen_dates:
            continue
        # Skip holidays during summer period
        if summer_start and summer_end and summer_start <= d <= summer_end:
            continue
        # Skip Labour Day and other pre-school-year holidays
        # Labour Day is always before school starts (first PA day or first school day)
        # Use a simple heuristic: skip holidays in the summer window
        if d.month in (6, 7, 8) or (d.month == 9 and d.day == 1):
            continue
        all_days.append({
            "date": d,
            "day_name": d.strftime("%a"),
            "period": "school_holiday",
            "period_label": "School Holiday",
            "assignments": _resolve_assignments(d, children, pa_provider, overrides),
            "notes": holiday["name"],
        })
        seen_dates.add(d)
```

**Step 4: Run tests to verify they pass**

Run: `python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add skills/generate-annual-schedule/scripts/generate_annual_schedule.py \
      skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py
git commit -m "feat: add school holiday coverage to annual schedule

Single-day holidays (Thanksgiving, Family Day, Good Friday, Easter Monday,
Victoria Day) now included as 'school_holiday' period using pa_provider.
Excludes summer holidays (handled separately) and Labour Day (pre-school)."
```

---

### Task 5: Add Fall Break to build_annual_days()

**Files:**
- Modify: `skills/generate-annual-schedule/scripts/generate_annual_schedule.py` (build_annual_days + argparse)
- Test: `skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py`

**Step 1: Write failing tests**

```python
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
```

**Step 2: Run tests to verify they fail**

Run: `python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py::TestBuildAnnualDaysFallBreak -v`
Expected: FAIL

**Step 3: Implement fall break in build_annual_days()**

Update function signature to add `fall_break_provider=None`:

```python
def build_annual_days(summer_days, calendar_data, pa_provider, break_provider,
                      children, overrides=None, fall_break_provider=None):
```

After school holidays block, add:

```python
    # Fall break (multi-day, use fall_break_provider or break_provider)
    fb_provider = fall_break_provider or break_provider
    if calendar_data.get("fall_break"):
        fb_start = parse_date_flexible(calendar_data["fall_break"]["start_str"])
        fb_end = parse_date_flexible(calendar_data["fall_break"]["end_str"])
        fall_days = get_weekdays_between(fb_start, fb_end)
        for d in fall_days:
            if d in seen_dates:
                continue
            all_days.append({
                "date": d,
                "day_name": d.strftime("%a"),
                "period": "fall_break",
                "period_label": "Fall Break",
                "assignments": _resolve_assignments(d, children, fb_provider, overrides),
                "notes": "",
            })
            seen_dates.add(d)
```

Add `--fall-break-provider` to argparse (after `--break-provider`):

```python
    parser.add_argument("--fall-break-provider",
                        help="Provider for fall break coverage (default: same as --break-provider)")
```

Update `build_annual_days` call in `main()` to pass `fall_break_provider`:

```python
    annual_days = build_annual_days(
        summer_days, calendar_data,
        args.pa_day_provider, args.break_provider, children,
        overrides=overrides,
        fall_break_provider=args.fall_break_provider,
    )
```

**Step 4: Run tests to verify they pass**

Run: `python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add skills/generate-annual-schedule/scripts/generate_annual_schedule.py \
      skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py
git commit -m "feat: add fall break support to annual schedule

Fall break (GIST Nov 3-7, KCS midterm) now included with configurable
--fall-break-provider (defaults to --break-provider).
Public boards with no fall break produce no fall break section."
```

---

### Task 6: Update _group_into_sections() and render_markdown()

**Files:**
- Modify: `skills/generate-annual-schedule/scripts/generate_annual_schedule.py:476-616` (_group_into_sections, render_markdown)
- Test: `skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py`

**Step 1: Write failing tests**

```python
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
```

**Step 2: Run tests to verify they fail**

Run: `python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py::TestGroupIntoSectionsNewPeriods -v`
Expected: FAIL

**Step 3: Implement _group_into_sections updates**

Add to `_group_into_sections()`, after the march_days collection:

```python
    school_holiday_days = [d for d in annual_days if d["period"] == "school_holiday"]
    fall_break_days = [d for d in annual_days if d["period"] == "fall_break"]
```

After the March break section block, add:

```python
    # School holidays - each as its own section (like PA days)
    for sh in school_holiday_days:
        d = sh["date"]
        sections.append({
            "period": "school_holiday",
            "period_key": "school_holidays",
            "title": f"School Holiday: {sh['notes']} ({d.strftime('%b %d, %Y')})",
            "summary_title": "School Holidays",
            "subtotal_label": "School Holiday",
            "days": [sh],
        })

    # Fall break
    if fall_break_days:
        first = fall_break_days[0]["date"]
        last = fall_break_days[-1]["date"]
        sections.append({
            "period": "fall_break",
            "period_key": "fall_break",
            "title": f"Fall Break {first.year} ({first.strftime('%b %d')}-{last.strftime('%b %d')})",
            "summary_title": "Fall Break",
            "subtotal_label": "Fall Break",
            "days": fall_break_days,
        })
```

Update `render_markdown()` summary_order and summary_labels:

```python
    summary_order = ["summer", "pa_day", "school_holiday", "fall_break", "winter_break", "march_break"]
    summary_labels = {
        "summer": "Summer {year}",
        "pa_day": "PA Days ({count})",
        "school_holiday": "School Holidays ({count})",
        "fall_break": "Fall Break",
        "winter_break": "Winter Break",
        "march_break": "March Break",
    }
```

Also update the period description block in `render_markdown()` (around line 394) to add fall break description:

```python
        elif period == "fall_break":
            lines.append(f"{count} weekdays")
            lines.append("")
```

**Step 4: Run tests to verify they pass**

Run: `python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add skills/generate-annual-schedule/scripts/generate_annual_schedule.py \
      skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py
git commit -m "feat: render school holidays and fall break in markdown output

_group_into_sections now handles school_holiday (individual sections)
and fall_break (single section). render_markdown includes both in
the Annual Summary table."
```

---

### Task 7: Update update_xlsx() for New Period Types

**Files:**
- Modify: `skills/generate-annual-schedule/scripts/generate_annual_schedule.py:623-732` (update_xlsx)
- Test: `skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py`

**Context:** `update_xlsx()` doesn't need structural changes — it already writes whatever periods are in `annual_days`. The period_label values ("School Holiday", "Fall Break") are written to column C automatically. But we should add a test to verify this works.

**Step 1: Write test**

```python
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
            days = [
                {"date": date(2025, 10, 13), "day_name": "Mon", "period": "school_holiday",
                 "period_label": "School Holiday", "assignments": {"Emma": "City of Toronto", "Liam": "City of Toronto"},
                 "notes": "Thanksgiving"},
                {"date": date(2025, 11, 3), "day_name": "Mon", "period": "fall_break",
                 "period_label": "Fall Break", "assignments": {"Emma": "YMCA Cedar Glen", "Liam": "YMCA Cedar Glen"},
                 "notes": ""},
            ]
            update_xlsx(tmp.name, days, ["Emma", "Liam"])
            wb = openpyxl.load_workbook(tmp.name)
            ws = wb["Annual Schedule"]
            assert ws["C4"].value == "School Holiday"
            assert ws["C5"].value == "Fall Break"
            wb.close()
        finally:
            os.unlink(tmp.name)
```

Add `import openpyxl` to test file imports.

**Step 2: Run test**

Run: `python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py::TestUpdateXlsxNewPeriods -v`
Expected: PASS (update_xlsx already handles arbitrary periods)

**Step 3: Commit**

```bash
git add skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py
git commit -m "test: verify xlsx output includes school holidays and fall break"
```

---

### Task 8: Update SKILL.md and Sample Files for Phase 1

**Files:**
- Modify: `skills/generate-annual-schedule/SKILL.md`
- Modify: `examples/sample-annual-schedule.md`

**Step 1: Update generate-annual-schedule SKILL.md**

Add `--fall-break-provider` to the Arguments section. Update "What the Script Reads" to mention school holidays. Update output description.

Key changes to SKILL.md:
- Add `--fall-break-provider` argument documentation (default: same as `--break-provider`)
- Update Step 2 defaults table to add Fall Break row
- Update "From school calendar markdown" section to list school holidays
- Update "Markdown file" output description to include school holidays and fall break
- Update Step 5 summary example to include new period types

**Step 2: Update sample-annual-schedule.md**

Add school holiday sections at chronological positions:
- Thanksgiving (Oct 13, 2025) — after PA Day Oct 10
- Family Day (Feb 16, 2026) — after PA Day Feb 13
- Good Friday (Apr 3, 2026) — after March Break
- Easter Monday (Apr 6, 2026) — after Good Friday
- Victoria Day (May 18, 2026) — after Easter Monday

Update Annual Summary table to include "School Holidays (5)" row.
Update total from 59 to 64 days.

**Step 3: Update Cost Notes**

Add line: "School holiday costs use City of Toronto rates ($62/day all-in), same as PA days"

**Step 4: Commit**

```bash
git add skills/generate-annual-schedule/SKILL.md examples/sample-annual-schedule.md
git commit -m "docs: update SKILL.md and sample for school holidays + fall break

Added --fall-break-provider arg docs, school holiday sections in sample,
updated Annual Summary from 59 to 64 days."
```

---

## Phase 4: Calendar Data Expansion (Independent — can run in parallel with Phase 1)

**Goal:** Create calendar scraping/validation tooling, populate 12+ Ontario school board calendars, and add contributing guidelines.

**Dependency:** None

### Task 9: Create validate_calendar.py

**Files:**
- Create: `skills/add-school-calendar/scripts/validate_calendar.py`
- Test: inline (script self-validates existing calendar files)

**Step 1: Write the validation script**

```python
#!/usr/bin/env python3
"""
Validate school calendar markdown files.

Checks:
- Required sections exist (Key Dates, PA Days, Holidays & Breaks, Summer Window)
- Dates are parseable
- School year matches expected format
- Table columns are correct
- No date conflicts (same date in PA days and holidays)

Usage:
    python3 validate_calendar.py path/to/calendar.md
    python3 validate_calendar.py --all path/to/school-calendars/
"""

import argparse
import glob
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

    filename = os.path.basename(path)

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
        pa_dates = []
        for line in pa_section.group(1).strip().split("\n"):
            cols = [c.strip() for c in line.split("|")]
            if len(cols) >= 5 and cols[1].strip().replace(".", "").isdigit():
                date_str = cols[2].strip()
                try:
                    d = _parse_date(date_str)
                    pa_dates.append(d)
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
```

**Step 2: Run validation on existing calendars**

Run: `python3 skills/add-school-calendar/scripts/validate_calendar.py --all skills/camp-planning/references/school-calendars/`
Expected: All existing files (tdsb.md, tcdsb.md, gist.md, kcs.md) should PASS

**Step 3: Commit**

```bash
git add skills/add-school-calendar/scripts/validate_calendar.py
git commit -m "feat: add calendar validation script

Validates required sections, parseable dates, school year format,
table structure, and source/update metadata."
```

---

### Task 10: Create scrape_board_calendar.py

**Files:**
- Create: `skills/add-school-calendar/scripts/scrape_board_calendar.py`
- Modify: `skills/add-school-calendar/SKILL.md`

**Step 1: Write the scraping helper script**

```python
#!/usr/bin/env python3
"""
School Board Calendar Scraper (Draft Quality)

Fetches a school board calendar HTML page and produces a draft markdown file
in the standard calendar-template format. Output requires human/agent review.

Targets common Ontario public board HTML table layouts. PDF-only boards
still need manual extraction via Claude Read tool.

Usage:
    python3 scrape_board_calendar.py \
      --board-name "York Region District School Board" \
      --abbreviation YRDSB \
      --year 2025-2026 \
      --url "https://www2.yrdsb.ca/about-us/school-year-calendar" \
      --output skills/camp-planning/references/school-calendars/public-boards/yrdsb.md
"""

import argparse
import re
import sys
import urllib.request
from datetime import datetime
from html.parser import HTMLParser


class TableExtractor(HTMLParser):
    """Extract table data from HTML."""

    def __init__(self):
        super().__init__()
        self.tables = []
        self._in_table = False
        self._in_row = False
        self._in_cell = False
        self._current_table = []
        self._current_row = []
        self._current_cell = ""

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._in_table = True
            self._current_table = []
        elif tag == "tr" and self._in_table:
            self._in_row = True
            self._current_row = []
        elif tag in ("td", "th") and self._in_row:
            self._in_cell = True
            self._current_cell = ""

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._in_cell:
            self._in_cell = False
            self._current_row.append(self._current_cell.strip())
        elif tag == "tr" and self._in_row:
            self._in_row = False
            if self._current_row:
                self._current_table.append(self._current_row)
        elif tag == "table" and self._in_table:
            self._in_table = False
            if self._current_table:
                self.tables.append(self._current_table)

    def handle_data(self, data):
        if self._in_cell:
            self._current_cell += data


def fetch_and_extract(url):
    """Fetch URL and extract tables."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    parser = TableExtractor()
    parser.feed(html)
    return parser.tables, html


def generate_draft(board_name, abbreviation, year, tables, html):
    """Generate draft markdown from extracted tables."""
    lines = []
    lines.append(f"# {board_name} ({abbreviation})\n")
    lines.append(f"- **Type**: Public")
    lines.append(f"- **Region**: [TODO: fill in region], Ontario")
    lines.append(f"- **Website**: [TODO: fill in website]")
    lines.append(f"- **Calendar URL pattern**: [TODO: fill in URL pattern]")
    lines.append("")
    lines.append("---\n")
    lines.append(f"## {year} School Year\n")
    lines.append(f"**Source**: {board_name} School Year Calendar ({year})\n")

    # Output all extracted tables for review
    lines.append("### Extracted Tables (REVIEW AND REORGANIZE)\n")
    for i, table in enumerate(tables, 1):
        lines.append(f"#### Table {i}\n")
        if table:
            # Build markdown table
            header = table[0]
            lines.append("| " + " | ".join(header) + " |")
            lines.append("|" + "|".join(["---" for _ in header]) + "|")
            for row in table[1:]:
                # Pad rows to match header length
                padded = row + [""] * (len(header) - len(row))
                lines.append("| " + " | ".join(padded[:len(header)]) + " |")
        lines.append("")

    lines.append("### Key Dates\n| Item | Date(s) |\n|------|---------|")
    lines.append("| [TODO] | [TODO] |\n")
    lines.append("### PA Days - Elementary\n| # | Date | Day | Purpose |\n|---|------|-----|---------|")
    lines.append("| [TODO] | [TODO] | [TODO] | [TODO] |\n")
    lines.append("### Holidays & Breaks\n| Holiday/Break | Date(s) | Weekdays Off |\n|---------------|---------|-------------|")
    lines.append("| [TODO] | [TODO] | [TODO] |\n")
    lines.append("### Summer Window (for camp planning)")
    lines.append("- **Last school day**: [TODO]")
    lines.append("- **First fall day**: [TODO]")
    lines.append("- **Summer coverage needed**: ~[TODO] weekdays (~[TODO] weeks)\n")
    lines.append("---\n")
    lines.append(f"*Last updated: {datetime.now().strftime('%Y-%m-%d')}*")
    lines.append(f"*Source: {board_name} {year} School Year Calendar*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scrape school board calendar from HTML page")
    parser.add_argument("--board-name", required=True, help="Full board name")
    parser.add_argument("--abbreviation", required=True, help="Short abbreviation (e.g., YRDSB)")
    parser.add_argument("--year", required=True, help="School year (e.g., 2025-2026)")
    parser.add_argument("--url", required=True, help="Calendar page URL")
    parser.add_argument("--output", help="Output markdown file path")
    args = parser.parse_args()

    print(f"Fetching {args.url}...")
    try:
        tables, html = fetch_and_extract(args.url)
    except Exception as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(tables)} tables")
    draft = generate_draft(args.board_name, args.abbreviation, args.year, tables, html)

    if args.output:
        with open(args.output, "w") as f:
            f.write(draft)
        print(f"Draft written to {args.output}")
        print("NOTE: This is a DRAFT. Review and reorganize into standard calendar format.")
    else:
        print(draft)


if __name__ == "__main__":
    main()
```

**Step 2: Test with `--help`**

Run: `python3 skills/add-school-calendar/scripts/scrape_board_calendar.py --help`
Expected: Shows usage with --board-name, --abbreviation, --year, --url, --output arguments

**Step 3: Update add-school-calendar SKILL.md**

Add a note in the "Additional Resources" section:

```markdown
### Scripts

- **`scripts/scrape_board_calendar.py`** - HTML calendar page scraper. Produces draft-quality markdown from school board websites. Requires human/agent review. Use for boards with HTML calendar pages; PDF-only boards still need manual extraction.
- **`scripts/validate_calendar.py`** - Calendar file validator. Checks required sections, parseable dates, school year format. Use `--all` to validate an entire directory.
```

**Step 4: Commit**

```bash
git add skills/add-school-calendar/scripts/scrape_board_calendar.py \
      skills/add-school-calendar/scripts/validate_calendar.py \
      skills/add-school-calendar/SKILL.md
git commit -m "feat: add calendar scraping and validation scripts

scrape_board_calendar.py: fetch HTML calendar pages, extract tables,
produce draft markdown for review.
validate_calendar.py: validate calendar files for required sections
and parseable dates."
```

---

### Task 11: Populate Tier 1+2 Calendars (12 boards)

**Files:**
- Create 12 files in `skills/camp-planning/references/school-calendars/public-boards/`:
  - `yrdsb.md`, `pdsb.md`, `ddsb.md`, `hdsb.md`, `ocdsb.md`, `dpcdsb.md`, `ycdsb.md` (Tier 1)
  - `hwdsb.md`, `wrdsb.md`, `scdsb.md`, `tvdsb.md`, `ucdsb.md` (Tier 2)
- Modify: `skills/camp-planning/references/school-calendars/RESEARCH-PLAN.md`

**Execution strategy:** For each board:
1. Web search for "[board name] school year calendar 2025-2026"
2. Find the official board website result
3. If a PDF is available, download to `pdfs/[abbreviation]/`
4. Extract key data: PA days, holidays, breaks, first/last days
5. Create markdown file following the established format (tdsb.md/tcdsb.md as reference)
6. Run `validate_calendar.py` on the new file
7. Update RESEARCH-PLAN.md status from TODO to DONE

**This task should be dispatched as 4 parallel subagent groups (3 boards each) to maximize throughput. Each subagent creates 3 calendar files.**

**Subagent group 1:** YRDSB, PDSB, DDSB
**Subagent group 2:** HDSB, OCDSB, DPCDSB
**Subagent group 3:** YCDSB, HWDSB, WRDSB
**Subagent group 4:** SCDSB, TVDSB, UCDSB

**After all 12 are done:**

Run: `python3 skills/add-school-calendar/scripts/validate_calendar.py --all skills/camp-planning/references/school-calendars/`
Expected: All 16 files PASS (4 existing + 12 new)

**Commit after each group:**

```bash
git add skills/camp-planning/references/school-calendars/public-boards/*.md
git commit -m "data: add Tier 1+2 Ontario school board calendars (12 boards)"
```

**Update RESEARCH-PLAN.md:** Change all Tier 1 and Tier 2 entries from TODO to DONE.

```bash
git add skills/camp-planning/references/school-calendars/RESEARCH-PLAN.md
git commit -m "docs: update RESEARCH-PLAN.md - Tiers 1+2 complete"
```

---

### Task 12: Create CONTRIBUTING.md and Update README

**Files:**
- Create: `CONTRIBUTING.md`
- Modify: `README.md`

**Step 1: Create CONTRIBUTING.md**

```markdown
# Contributing to Kids Camp Planner

## Adding School Calendar Data

The most impactful contribution is adding school calendar data for Ontario schools.

### Submission Format

Calendar files must follow the template at `skills/add-school-calendar/references/calendar-template.md`.

#### Required sections:
- School metadata header (name, type, region, website)
- `## YYYY-YYYY School Year` with source citation
- `### Key Dates` table
- `### PA Days - Elementary` table (or note if school uses midterm breaks)
- `### Holidays & Breaks` table
- `### Summer Window` with last school day, first fall day, coverage needed

#### For private schools, also include:
- PA day alignment table comparing against nearest public board
- Coverage challenges ranked by difficulty
- Planning notes section

### Quality Checklist

Before submitting:
- [ ] All dates verified against official school/board publication
- [ ] School year matches (2025-2026 not previous year)
- [ ] PA day count matches board's stated total
- [ ] Holidays & Breaks includes all Ontario statutory holidays
- [ ] Summer window calculation is correct (weekday count)
- [ ] Source citation includes document name and date
- [ ] `*Last updated:` footer with current date
- [ ] Passes validation: `python3 skills/add-school-calendar/scripts/validate_calendar.py path/to/file.md`

### Validation

Run the validator before submitting:

```bash
python3 skills/add-school-calendar/scripts/validate_calendar.py path/to/new-calendar.md
```

### File Locations

- Public boards: `skills/camp-planning/references/school-calendars/public-boards/[abbreviation].md`
- Private schools: `skills/camp-planning/references/school-calendars/private-schools/[abbreviation].md`
- PDFs (if downloaded): `skills/camp-planning/references/school-calendars/pdfs/[abbreviation]/`

### Priority Schools

See `skills/camp-planning/references/school-calendars/RESEARCH-PLAN.md` for the full priority list. Tier 3 (private schools) and Tier 4 (French/international) still need contributors.
```

**Step 2: Update README.md**

Add a "Contributing" section after "Prerequisites":

```markdown
## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add school calendar data for Ontario schools. The most impactful contribution is adding calendar files for Tier 3 (private) and Tier 4 (international) schools.
```

Update the "Pre-Saved Calendar Data" section to mention the new boards.

**Step 3: Commit**

```bash
git add CONTRIBUTING.md README.md
git commit -m "docs: add contributing guidelines and update README

Includes school calendar submission format, quality checklist,
validation instructions, and priority school list."
```

---

## Phase 2: Multi-Board Family Support

**Goal:** Support families with children at different schools by allowing per-child school assignments and multi-calendar input.

**Dependency:** Phase 1 (clean generalized parser)

### Task 13: Update Family Profile Schema

**Files:**
- Modify: `examples/family-profile.md`

**Step 1: Update family-profile.md**

Move `school:` under each child entry. Keep top-level `school:` as deprecated fallback for backward compatibility.

In the YAML frontmatter, change the `kids:` section to:

```yaml
kids:
  - name: "Child 1"
    dob: "2017-05-15"
    school:
      type: "public"
      board: "TDSB"
      name: "Example Public School"
    interests: ["swimming", "art", "robotics"]
    allergies: ["peanuts"]
    dietary: [""]
    medical_notes: ""
    special_accommodations: ""
  - name: "Child 2"
    dob: "2019-09-20"
    school:
      type: "public"
      board: "TDSB"
      name: "Example Public School"
    interests: ["soccer", "nature", "drama"]
    allergies: []
    dietary: [""]
    medical_notes: ""
    special_accommodations: ""
```

Add a comment above the existing top-level `school:` block:

```yaml
# DEPRECATED - Top-level school block (backward compat: used when no per-child school)
# New profiles should put school under each child in the kids array above.
school:
  type: "public"
  board: "TDSB"
  ...
```

**Step 2: Commit**

```bash
git add examples/family-profile.md
git commit -m "feat: add per-child school field to family profile schema

Each child now has their own school block. Top-level school block
kept as deprecated fallback for backward compatibility."
```

---

### Task 14: Multi-Calendar CLI and Parsing

**Files:**
- Modify: `skills/generate-annual-schedule/scripts/generate_annual_schedule.py:739-758` (argparse) + new logic
- Test: `skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py`

**Step 1: Write failing tests**

```python
class TestMultiCalendarCLI:
    """Tests for multi-calendar CLI arg parsing."""

    def test_single_calendar_backward_compat(self):
        """Single --calendar path applies to all children."""
        # This tests the internal calendar resolution logic
        path = _write_temp_calendar(TCDSB_CALENDAR)
        try:
            calendars = resolve_calendars(path, ["Emma", "Liam"])
            assert calendars["Emma"] == path
            assert calendars["Liam"] == path
        finally:
            os.unlink(path)

    def test_multi_calendar_per_child(self):
        path1 = _write_temp_calendar(TDSB_CALENDAR)
        path2 = _write_temp_calendar(GIST_CALENDAR)
        try:
            calendars = resolve_calendars(
                [f"Emma:{path1}", f"Liam:{path2}"],
                ["Emma", "Liam"]
            )
            assert calendars["Emma"] == path1
            assert calendars["Liam"] == path2
        finally:
            os.unlink(path1)
            os.unlink(path2)


class TestMultiCalendarMerge:
    """Tests for merging calendars from different schools."""

    def test_merged_includes_both_pa_days(self):
        """TDSB and GIST PA days are different — merged calendar has both sets."""
        tdsb_path = _write_temp_calendar(TDSB_CALENDAR)
        gist_path = _write_temp_calendar(GIST_CALENDAR)
        try:
            cal_emma = parse_calendar(tdsb_path)
            cal_liam = parse_calendar(gist_path)
            summer = [{"date": date(2025, 6, 30), "week": 1,
                       "assignments": {"Emma": "YMCA", "Liam": "YMCA"}}]
            days = build_annual_days_multi(
                summer,
                {"Emma": cal_emma, "Liam": cal_liam},
                "City of Toronto", "YMCA",
                ["Emma", "Liam"],
            )
            pa_days = [d for d in days if d["period"] == "pa_day"]
            pa_dates = {d["date"] for d in pa_days}
            # TDSB PA: Sep 26, Oct 10, Nov 14, Jan 16, Feb 13, Jun 5, Jun 26
            # GIST PA: Oct 24, Nov 21, Jan 30, May 29
            # Merged unique: 11 PA days
            assert date(2025, 9, 26) in pa_dates  # TDSB only
            assert date(2025, 10, 24) in pa_dates  # GIST only
        finally:
            os.unlink(tdsb_path)
            os.unlink(gist_path)

    def test_in_school_child_marked(self):
        """When only one child is off, the other shows 'In school' with $0."""
        tdsb_path = _write_temp_calendar(TDSB_CALENDAR)
        gist_path = _write_temp_calendar(GIST_CALENDAR)
        try:
            cal_emma = parse_calendar(tdsb_path)
            cal_liam = parse_calendar(gist_path)
            summer = [{"date": date(2025, 6, 30), "week": 1,
                       "assignments": {"Emma": "YMCA", "Liam": "YMCA"}}]
            days = build_annual_days_multi(
                summer,
                {"Emma": cal_emma, "Liam": cal_liam},
                "City of Toronto", "YMCA",
                ["Emma", "Liam"],
            )
            # Oct 24 is GIST PA day only — Emma is in school
            oct24 = [d for d in days if d["date"] == date(2025, 10, 24)]
            assert len(oct24) == 1
            assert oct24[0]["assignments"]["Liam"] == "City of Toronto"
            assert oct24[0]["assignments"]["Emma"] == "In school"
        finally:
            os.unlink(tdsb_path)
            os.unlink(gist_path)
```

**Step 2: Run tests to verify they fail**

Expected: FAIL with `NameError: name 'resolve_calendars' is not defined`

**Step 3: Implement resolve_calendars() and build_annual_days_multi()**

Add `resolve_calendars()` function:

```python
def resolve_calendars(calendar_arg, children):
    """Resolve calendar argument(s) to per-child calendar paths.

    Accepts either:
      - A single path string (applies to all children)
      - A list of "ChildName:path" strings (per-child)

    Returns: {child_name: calendar_path}
    """
    if isinstance(calendar_arg, str):
        # Single calendar for all children
        return {child: calendar_arg for child in children}

    # Multi-calendar: list of "Child:path"
    calendars = {}
    for entry in calendar_arg:
        if ":" not in entry:
            raise ValueError(f"Multi-calendar entry must be 'ChildName:path', got: {entry}")
        child, path = entry.split(":", 1)
        calendars[child.strip()] = path.strip()

    # Validate all children have a calendar
    for child in children:
        if child not in calendars:
            raise ValueError(f"No calendar specified for child: {child}")
    return calendars
```

Add `build_annual_days_multi()` function:

```python
def build_annual_days_multi(summer_days, per_child_calendars, pa_provider,
                            break_provider, children, overrides=None,
                            fall_break_provider=None):
    """Multi-calendar variant of build_annual_days.

    per_child_calendars: {child_name: calendar_data_dict}

    Merges all children's off-school dates. On days when only some children
    are off, others show "In school" with $0 cost.
    """
    overrides = overrides or {}
    all_days = []
    seen_dates = set()

    # Summer days (same for all children — from spreadsheet)
    summer_holidays = get_summer_holidays(summer_days[0]["date"].year) if summer_days else {}
    for sd in summer_days:
        d = sd["date"]
        d_iso = d.isoformat()
        week = sd["week"]
        notes = f"Week {week}" if d.weekday() == 0 else ""
        if d in summer_holidays:
            holiday_name = summer_holidays[d]
            notes = f"{holiday_name} -- VERIFY camp open" + (f" ({notes})" if notes else "")
        assignments = dict(sd["assignments"])
        if d_iso in overrides:
            for child in children:
                if child in overrides[d_iso]:
                    assignments[child] = overrides[d_iso][child]
        all_days.append({
            "date": d, "day_name": d.strftime("%a"), "period": "summer",
            "period_label": f"Summer Wk {week}", "assignments": assignments, "notes": notes,
        })
        seen_dates.add(d)

    # Collect all non-summer dates across all children's calendars
    # For each period type, determine which children are off
    # PA days
    all_pa_dates = {}  # date -> {child: purpose}
    for child, cal in per_child_calendars.items():
        for pa in cal.get("pa_days", []):
            d = parse_date_flexible(pa["date_str"])
            if d not in all_pa_dates:
                all_pa_dates[d] = {}
            all_pa_dates[d][child] = pa.get("purpose", "")

    pa_counter = 0
    for d in sorted(all_pa_dates.keys()):
        if d in seen_dates:
            continue
        pa_counter += 1
        children_off = all_pa_dates[d]
        assignments = {}
        notes_parts = []
        for child in children:
            if child in children_off:
                d_iso = d.isoformat()
                day_overrides = overrides.get(d_iso, {})
                assignments[child] = day_overrides.get(child, pa_provider)
            else:
                assignments[child] = "In school"
        # Note which children are off if not all
        if len(children_off) < len(children):
            off_names = [c for c in children if c in children_off]
            notes_parts.append(f"PA Day {pa_counter} ({', '.join(off_names)} off)")
        else:
            purpose = next(iter(children_off.values()), "")
            notes_parts.append(f"PA Day {pa_counter}" + (f" - {purpose}" if purpose else ""))
        all_days.append({
            "date": d, "day_name": d.strftime("%a"), "period": "pa_day",
            "period_label": "PA Day", "assignments": assignments,
            "notes": " | ".join(notes_parts),
        })
        seen_dates.add(d)

    # School holidays — merge across all calendars
    all_holiday_dates = {}  # date -> {child: name}
    for child, cal in per_child_calendars.items():
        for h in cal.get("school_holidays", []):
            d = parse_date_flexible(h["date_str"])
            if d not in all_holiday_dates:
                all_holiday_dates[d] = {}
            all_holiday_dates[d][child] = h["name"]

    summer_start = summer_days[0]["date"] if summer_days else None
    summer_end = summer_days[-1]["date"] if summer_days else None
    for d in sorted(all_holiday_dates.keys()):
        if d in seen_dates:
            continue
        if summer_start and summer_end and summer_start <= d <= summer_end:
            continue
        if d.month in (6, 7, 8) or (d.month == 9 and d.day == 1):
            continue
        children_off = all_holiday_dates[d]
        assignments = {}
        for child in children:
            if child in children_off:
                d_iso = d.isoformat()
                day_overrides = overrides.get(d_iso, {})
                assignments[child] = day_overrides.get(child, pa_provider)
            else:
                assignments[child] = "In school"
        name = next(iter(children_off.values()))
        all_days.append({
            "date": d, "day_name": d.strftime("%a"), "period": "school_holiday",
            "period_label": "School Holiday", "assignments": assignments, "notes": name,
        })
        seen_dates.add(d)

    # Fall break — merge across calendars
    fb_provider = fall_break_provider or break_provider
    all_fall_dates = set()
    per_child_fall = {}
    for child, cal in per_child_calendars.items():
        if cal.get("fall_break"):
            fb_start = parse_date_flexible(cal["fall_break"]["start_str"])
            fb_end = parse_date_flexible(cal["fall_break"]["end_str"])
            child_dates = set(get_weekdays_between(fb_start, fb_end))
            per_child_fall[child] = child_dates
            all_fall_dates |= child_dates

    for d in sorted(all_fall_dates):
        if d in seen_dates:
            continue
        assignments = {}
        for child in children:
            if child in per_child_fall and d in per_child_fall[child]:
                d_iso = d.isoformat()
                day_overrides = overrides.get(d_iso, {})
                assignments[child] = day_overrides.get(child, fb_provider)
            else:
                assignments[child] = "In school"
        all_days.append({
            "date": d, "day_name": d.strftime("%a"), "period": "fall_break",
            "period_label": "Fall Break", "assignments": assignments, "notes": "",
        })
        seen_dates.add(d)

    # Winter break — use union of all calendars' winter breaks
    # (same logic pattern as fall break)
    all_winter_dates = set()
    per_child_winter = {}
    stat_holidays = set()
    for child, cal in per_child_calendars.items():
        if cal.get("winter_break"):
            wb_start = parse_date_flexible(cal["winter_break"]["start_str"])
            wb_end = parse_date_flexible(cal["winter_break"]["end_str"])
            for year in [wb_start.year, wb_end.year]:
                stat_holidays.add(date(year, 12, 25))
                stat_holidays.add(date(year, 12, 26))
                stat_holidays.add(date(year, 1, 1))
            child_dates = set(get_weekdays_between(wb_start, wb_end, exclude_dates=stat_holidays))
            per_child_winter[child] = child_dates
            all_winter_dates |= child_dates

    for d in sorted(all_winter_dates):
        if d in seen_dates:
            continue
        assignments = {}
        for child in children:
            if child in per_child_winter and d in per_child_winter[child]:
                d_iso = d.isoformat()
                day_overrides = overrides.get(d_iso, {})
                assignments[child] = day_overrides.get(child, break_provider)
            else:
                assignments[child] = "In school"
        notes = ""
        if d.month == 12 and d.day == 24:
            notes = "Christmas Eve -- VERIFY camp open"
        elif d.month == 12 and d.day == 31:
            notes = "New Year's Eve -- VERIFY camp open"
        all_days.append({
            "date": d, "day_name": d.strftime("%a"), "period": "winter_break",
            "period_label": "Winter Break", "assignments": assignments, "notes": notes,
        })
        seen_dates.add(d)

    # March break — same union pattern
    all_march_dates = set()
    per_child_march = {}
    for child, cal in per_child_calendars.items():
        if cal.get("march_break"):
            mb_start = parse_date_flexible(cal["march_break"]["start_str"])
            mb_end = parse_date_flexible(cal["march_break"]["end_str"])
            child_dates = set(get_weekdays_between(mb_start, mb_end))
            per_child_march[child] = child_dates
            all_march_dates |= child_dates

    for d in sorted(all_march_dates):
        if d in seen_dates:
            continue
        assignments = {}
        for child in children:
            if child in per_child_march and d in per_child_march[child]:
                d_iso = d.isoformat()
                day_overrides = overrides.get(d_iso, {})
                assignments[child] = day_overrides.get(child, break_provider)
            else:
                assignments[child] = "In school"
        all_days.append({
            "date": d, "day_name": d.strftime("%a"), "period": "march_break",
            "period_label": "March Break", "assignments": assignments, "notes": "",
        })
        seen_dates.add(d)

    all_days.sort(key=lambda x: x["date"])
    return all_days
```

Update `main()` to support multi-calendar:

```python
    parser.add_argument("--calendar", required=True, action="append",
                        help="School calendar markdown. Single: path. Multi: 'Child:path' per entry")
```

In `main()`, resolve calendars and choose single vs multi path:

```python
    # Resolve calendars
    if len(args.calendar) == 1 and ":" not in args.calendar[0]:
        # Single calendar mode (backward compatible)
        calendar_data = parse_calendar(args.calendar[0])
        annual_days = build_annual_days(...)
    else:
        # Multi-calendar mode
        cal_map = resolve_calendars(args.calendar, children)
        per_child_cals = {child: parse_calendar(path) for child, path in cal_map.items()}
        annual_days = build_annual_days_multi(...)
```

**Step 4: Run tests to verify they pass**

Run: `python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add skills/generate-annual-schedule/scripts/generate_annual_schedule.py \
      skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py
git commit -m "feat: multi-calendar support for families at different schools

--calendar now accepts 'Child:path' for per-child calendars.
build_annual_days_multi() merges coverage dates, marks children
'In school' when their school is in session."
```

---

### Task 15: Update Planning Skills for Multi-Board

**Files:**
- Modify: `skills/generate-annual-schedule/SKILL.md`
- Modify: `skills/setup/SKILL.md`
- Modify: `skills/plan-pa-days/SKILL.md`
- Modify: `skills/plan-summer/SKILL.md`
- Modify: `skills/plan-march-break/SKILL.md`

**Step 1: Update generate-annual-schedule SKILL.md**

Document multi-calendar usage in Step 3:

```markdown
**Multi-school families:** If children attend different schools, pass per-child calendars:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/generate-annual-schedule/scripts/generate_annual_schedule.py \
  --xlsx examples/sample-budget.xlsx \
  --calendar "Emma:${CLAUDE_PLUGIN_ROOT}/.../tdsb.md" \
  --calendar "Liam:${CLAUDE_PLUGIN_ROOT}/.../gist.md" \
  --children "Emma,Liam" \
  ...
```

On days where only some children are off school, the others show "In school" with $0 cost.
```

**Step 2: Update setup SKILL.md**

In Group 2 (School Information), change from collecting one school to collecting school info per child:

```markdown
**Group 2 - School Information (per child):**
For each child listed in Group 1, collect:
- Public or private school
- School board name
- School name
- Run the **3-Tier School Calendar Lookup** per unique school
```

**Step 3: Update plan-pa-days SKILL.md**

Add multi-board handling:

```markdown
**Multi-board families:** If children attend different schools, look up PA days per school. Cross-reference to identify:
- **Both off**: All children need coverage (standard PA day)
- **Partial**: Only some children off (mark others "In school")
Present the merged PA day table showing which children are off each day.
```

**Step 4: Update plan-summer and plan-march-break SKILL.md**

Add per-child summer window notes for private school differences. For March break, note different break dates.

**Step 5: Commit**

```bash
git add skills/generate-annual-schedule/SKILL.md \
      skills/setup/SKILL.md \
      skills/plan-pa-days/SKILL.md \
      skills/plan-summer/SKILL.md \
      skills/plan-march-break/SKILL.md
git commit -m "docs: update planning skills for multi-board family support

Setup collects school per child. PA days, summer, March break skills
now reference multi-calendar merging and per-child school handling."
```

---

## Phase 3: Spreadsheet Structural Changes

**Goal:** Support up to 4 children with dynamic column layout and per-period rate differentiation.

**Dependency:** Phase 1 (for period types in rate lookup)

### Task 16: Dynamic Child Column Layout (Up to 4 Children)

**Files:**
- Modify: `skills/generate-annual-schedule/scripts/generate_annual_schedule.py:83-117` (read_summer_assignments), `623-732` (update_xlsx), `739-767` (main)
- Test: `skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py`

**Step 1: Write failing tests**

```python
class TestDynamicChildColumns:
    """Tests for dynamic child column layout."""

    def test_column_formula_2_children(self):
        """2 children: 3 + 12 + 1 = 16 cols (backward compat)."""
        assert calculate_total_cols(2) == 16

    def test_column_formula_3_children(self):
        """3 children: 3 + 18 + 1 = 22 cols."""
        assert calculate_total_cols(3) == 22

    def test_column_formula_4_children(self):
        """4 children: 3 + 24 + 1 = 28 cols."""
        assert calculate_total_cols(4) == 28

    def test_child_col_offsets_2(self):
        offsets = get_child_col_offsets(2)
        assert offsets == [3, 9]  # 0-indexed: D=3, J=9

    def test_child_col_offsets_3(self):
        offsets = get_child_col_offsets(3)
        assert offsets == [3, 9, 15]

    def test_child_col_offsets_4(self):
        offsets = get_child_col_offsets(4)
        assert offsets == [3, 9, 15, 21]

    def test_max_4_children_enforced(self):
        with pytest.raises(SystemExit):
            # Simulate argparse validation
            validate_child_count(5)

    def test_1_child_supported(self):
        assert calculate_total_cols(1) == 10  # 3 + 6 + 1
```

**Step 2: Run tests to verify they fail**

Expected: FAIL with `NameError`

**Step 3: Implement dynamic column functions**

Replace the hardcoded constants:

```python
SHARED_PREFIX_COLS = 3  # Date, Day, Period/Week#
COLS_PER_CHILD = 6      # Camp Name, Before Care, Camp Fee, After Care, Lunch, Day Total


def calculate_total_cols(n_children):
    """Total columns = prefix + (N * child_block) + daily_total."""
    return SHARED_PREFIX_COLS + (n_children * COLS_PER_CHILD) + 1


def get_child_col_offsets(n_children):
    """Return 0-indexed column offsets for each child's camp name column."""
    return [SHARED_PREFIX_COLS + i * COLS_PER_CHILD for i in range(n_children)]


def validate_child_count(n):
    if n > 4:
        print(f"Error: Maximum 4 children supported. Got {n}.", file=sys.stderr)
        sys.exit(1)
    if n < 1:
        print("Error: At least 1 child required.", file=sys.stderr)
        sys.exit(1)
```

Update `read_summer_assignments()` to use dynamic offsets:

```python
    child_cols = get_child_col_offsets(len(children))
    max_col = calculate_total_cols(len(children))
    for row in ws.iter_rows(min_row=4, max_col=max_col, values_only=False):
        ...
```

Update `update_xlsx()` to generate headers and formulas dynamically for N children.

Update `main()` to replace the max-2 check with `validate_child_count(len(children))`.

**Step 4: Run tests to verify they pass**

Run: `python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add skills/generate-annual-schedule/scripts/generate_annual_schedule.py \
      skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py
git commit -m "feat: support up to 4 children with dynamic column layout

Replaces hardcoded child_cols=[3,9] with formula-based layout.
Column count: 3 + (N*6) + 1. Max 4 children, min 1."
```

---

### Task 17: Per-Period Rate Differentiation

**Files:**
- Modify: `skills/generate-annual-schedule/scripts/generate_annual_schedule.py:55-80` (read_provider_rates), VLOOKUPs in update_xlsx
- Test: `skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py`

**Step 1: Write failing tests**

```python
class TestPerPeriodRates:
    """Tests for per-period rate differentiation."""

    def test_read_provider_rates_with_periods(self):
        """When PA Day/Break columns exist, rates are per-period."""
        # This test uses a mock xlsx with expanded columns
        # For now, test the fallback behavior
        pass  # Will be implemented with xlsx fixture

    def test_fallback_to_summer_rates(self):
        """When PA Day/Break columns are empty, fall back to summer rates."""
        rates = {"Provider": {"summer": {"daily": 60, "before": 10, "after": 10, "lunch": 7, "total": 87},
                              "pa_day": None, "break": None}}
        resolved = resolve_period_rate(rates["Provider"], "pa_day")
        assert resolved == rates["Provider"]["summer"]

    def test_period_specific_rate(self):
        rates = {"summer": {"daily": 60, "before": 10, "after": 10, "lunch": 7, "total": 87},
                 "pa_day": {"daily": 45, "before": 8, "after": 8, "lunch": 5, "total": 66},
                 "break": None}
        resolved = resolve_period_rate(rates, "pa_day")
        assert resolved["total"] == 66
```

**Step 2: Implement per-period rate reading**

Expand `read_provider_rates()` to read 3 rate sections:
- Summer (cols C-F): existing
- PA Day (cols G-J): new
- Break (cols K-N): new

```python
def read_provider_rates(xlsx_path):
    """Read provider rates from Provider Comparison tab.

    Returns {provider: {summer: {daily, before, after, lunch, total},
                        pa_day: {...} or None, break: {...} or None}}
    """
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb["Provider Comparison"]
    rates = {}
    for row in ws.iter_rows(min_row=4, max_col=14, values_only=False):
        name = row[0].value
        if not name or name.startswith("8-Week"):
            break

        # Summer rates (cols C-F)
        summer = _read_rate_block(row, 2)  # 0-indexed col C=2

        # PA Day rates (cols G-J) — optional
        pa_day = _read_rate_block(row, 6)  # col G=6

        # Break rates (cols K-N) — optional
        brk = _read_rate_block(row, 10)  # col K=10

        rates[name] = {
            "summer": summer,
            "pa_day": pa_day,
            "break": brk,
            # Backward compat: flat rate (summer)
            **summer,
        }
    wb.close()
    return rates


def _read_rate_block(row, start_col):
    """Read a 4-column rate block (daily, before, after, lunch). Returns dict or None if all empty."""
    daily = row[start_col].value if len(row) > start_col else None
    before = row[start_col + 1].value if len(row) > start_col + 1 else None
    after = row[start_col + 2].value if len(row) > start_col + 2 else None
    lunch = row[start_col + 3].value if len(row) > start_col + 3 else None

    if all(v is None or v == 0 for v in [daily, before, after, lunch]):
        return None

    daily = daily or 0
    before = before or 0
    after = after or 0
    lunch = lunch or 0
    return {"daily": daily, "before": before, "after": after, "lunch": lunch,
            "total": daily + before + after + lunch}


def resolve_period_rate(provider_rates, period_type):
    """Get rate for a specific period, falling back to summer if not available."""
    period_map = {
        "summer": "summer",
        "pa_day": "pa_day",
        "school_holiday": "pa_day",
        "winter_break": "break",
        "march_break": "break",
        "fall_break": "break",
    }
    rate_key = period_map.get(period_type, "summer")
    rate = provider_rates.get(rate_key)
    if rate is None:
        rate = provider_rates.get("summer", provider_rates)
    return rate
```

Update `render_markdown()` to use period-aware rate lookup when calculating costs.

Update VLOOKUP formulas in `update_xlsx()` to use IF-based column indexing based on the Period column (C).

**Step 3: Run tests**

Expected: ALL PASS

**Step 4: Commit**

```bash
git add skills/generate-annual-schedule/scripts/generate_annual_schedule.py \
      skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py
git commit -m "feat: per-period rate differentiation (Summer/PA Day/Break)

Provider Comparison tab now supports 3 rate sections.
Falls back to summer rates when PA Day/Break columns are empty."
```

---

### Task 18: Update Provider Template and SKILL.md Files for Phase 3

**Files:**
- Modify: `skills/research-camps/references/provider-template.md`
- Modify: `skills/generate-annual-schedule/SKILL.md`
- Modify: `skills/budget-optimization/SKILL.md`
- Modify: `README.md`

**Step 1: Update provider-template.md**

Add Summer/PA Day/Break rate sections to the Costs table:

```markdown
## Costs

### Summer Rates
| Item | Cost | Notes |
|------|------|-------|
| Base fee (daily) | $[X] | Per day rate |
| Before care | $[X]/day | [Hours] |
| After care | $[X]/day | [Hours] |
| Lunch program | $[X]/day | [Optional/Required] |

### PA Day Rates (if different from summer)
| Item | Cost | Notes |
|------|------|-------|
| Base fee (daily) | $[X] | Per day rate |
| Before care | $[X]/day | [Hours] |
| After care | $[X]/day | [Hours] |
| Lunch program | $[X]/day | [Optional/Required] |

### Break Rates (Winter/March/Fall — if different from summer)
| Item | Cost | Notes |
|------|------|-------|
| Base fee (daily) | $[X] | Per day rate |
| Before care | $[X]/day | [Hours] |
| After care | $[X]/day | [Hours] |
| Lunch program | $[X]/day | [Optional/Required] |
```

**Step 2: Update generate-annual-schedule SKILL.md**

Update the Provider Comparison column layout documentation:

```markdown
### From Provider Comparison tab:
- A: Provider name, B: Age Range
- C-F: Summer rates (Daily, Before Care, After Care, Lunch)
- G-J: PA Day rates (Daily, Before Care, After Care, Lunch) — optional, falls back to Summer
- K-N: Break rates (Daily, Before Care, After Care, Lunch) — optional, falls back to Summer
```

Remove the disclaimer about non-summer rates.

**Step 3: Update budget-optimization SKILL.md**

Add note about per-period rate columns:

```markdown
**Per-period rates:** The Provider Comparison tab supports separate rate columns for Summer (C-F), PA Days (G-J), and Breaks (K-N). If PA Day or Break columns are empty, summer rates are used as fallback.
```

**Step 4: Update README.md**

Update the spreadsheet structure table and remove "16 columns" references. Note up to 4 children supported. Update period count from 59 to 64.

**Step 5: Commit**

```bash
git add skills/research-camps/references/provider-template.md \
      skills/generate-annual-schedule/SKILL.md \
      skills/budget-optimization/SKILL.md \
      README.md
git commit -m "docs: update templates and skills for per-period rates + 4 children

Provider template has Summer/PA Day/Break rate sections.
SKILL docs updated with expanded Provider Comparison layout.
README reflects dynamic column layout and 64-day schedule."
```

---

## Execution Order Summary

```
Task 1:  Set up test infrastructure                [Phase 1]
Task 2:  Parse school holidays                     [Phase 1]
Task 3:  Parse fall break                          [Phase 1]
Task 4:  School holidays in build_annual_days      [Phase 1]
Task 5:  Fall break in build_annual_days           [Phase 1]
Task 6:  _group_into_sections + render_markdown    [Phase 1]
Task 7:  update_xlsx for new periods               [Phase 1]
Task 8:  SKILL.md + sample-annual-schedule.md      [Phase 1]
  ↓ Phase 1 complete ↓
Task 9:  validate_calendar.py                      [Phase 4, parallel with 1-8]
Task 10: scrape_board_calendar.py                  [Phase 4, parallel with 1-8]
Task 11: Populate 12 board calendars               [Phase 4, parallel with 1-8]
Task 12: CONTRIBUTING.md + README                  [Phase 4, parallel with 1-8]
  ↓ Phase 4 complete ↓
Task 13: Family profile schema                     [Phase 2, after Phase 1]
Task 14: Multi-calendar CLI + merge logic          [Phase 2]
Task 15: Update planning skills                    [Phase 2]
  ↓ Phase 2 complete ↓
Task 16: Dynamic child columns (up to 4)           [Phase 3, after Phase 1]
Task 17: Per-period rate differentiation           [Phase 3]
Task 18: Update templates + docs                   [Phase 3]
  ↓ Phase 3 complete ↓
```

**Parallelization opportunities:**
- Tasks 9-12 can run in parallel with Tasks 1-8
- Tasks 13-15 and Tasks 16-18 can run in parallel with each other (both only depend on Phase 1)
- Task 11 (12 board calendars) can be split across 4 parallel subagents

**Total commits:** ~18 focused commits
**Total new files:** ~16 (1 test file, 2 scripts, 12 calendars, 1 CONTRIBUTING.md)
**Total modified files:** ~14 unique files
