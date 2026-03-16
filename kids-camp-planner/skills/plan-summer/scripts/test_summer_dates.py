"""Tests for summer_dates.py."""

import json
import os
import sys
from datetime import date
from io import StringIO
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from summer_dates import (
    find_labour_day,
    get_individual_days,
    get_weekdays,
    get_weeks,
)


class TestFindLabourDay:
    """Tests for find_labour_day() — first Monday in September."""

    def test_2025(self):
        assert find_labour_day(2025) == date(2025, 9, 1)

    def test_2026(self):
        assert find_labour_day(2026) == date(2026, 9, 7)

    def test_2027(self):
        assert find_labour_day(2027) == date(2027, 9, 6)

    def test_2028(self):
        assert find_labour_day(2028) == date(2028, 9, 4)

    def test_2029(self):
        assert find_labour_day(2029) == date(2029, 9, 3)

    def test_2030(self):
        assert find_labour_day(2030) == date(2030, 9, 2)


class TestGetWeekdays:
    """Tests for get_weekdays()."""

    def test_full_week_mon_to_fri(self):
        # Week of 2025-06-30 (Mon) to 2025-07-04 (Fri)
        days = get_weekdays(date(2025, 6, 30), date(2025, 7, 4))
        assert len(days) == 5
        assert days[0] == date(2025, 6, 30)
        assert days[-1] == date(2025, 7, 4)

    def test_boundaries_inclusive(self):
        # Single Monday
        days = get_weekdays(date(2025, 6, 30), date(2025, 6, 30))
        assert days == [date(2025, 6, 30)]

    def test_skips_weekends(self):
        # Mon–Sun range: should return Mon–Fri only
        days = get_weekdays(date(2025, 6, 30), date(2025, 7, 6))
        assert len(days) == 5
        for d in days:
            assert d.weekday() < 5

    def test_weekend_only_range_returns_empty(self):
        # Saturday–Sunday
        days = get_weekdays(date(2025, 7, 5), date(2025, 7, 6))
        assert days == []

    def test_two_full_weeks(self):
        days = get_weekdays(date(2025, 6, 30), date(2025, 7, 11))
        assert len(days) == 10


class TestGetWeeks:
    """Tests for get_weeks()."""

    def test_two_full_weeks(self):
        # Mon Jun 30 to Fri Jul 11 = 2 full weeks
        weeks = get_weeks(date(2025, 6, 30), date(2025, 7, 11))
        assert len(weeks) == 2
        assert all(w["partial"] is False for w in weeks)
        assert all(w["weekdays"] == 5 for w in weeks)

    def test_partial_first_week_wednesday_start(self):
        # Start on Wednesday Jul 2 to Fri Jul 11
        weeks = get_weeks(date(2025, 7, 2), date(2025, 7, 11))
        assert weeks[0]["partial"] is True
        assert weeks[0]["weekdays"] == 3  # Wed, Thu, Fri
        assert weeks[1]["partial"] is False

    def test_partial_last_week(self):
        # Mon Jun 30 to Wed Jul 2
        weeks = get_weeks(date(2025, 6, 30), date(2025, 7, 2))
        assert len(weeks) == 1
        assert weeks[0]["partial"] is True
        assert weeks[0]["weekdays"] == 3

    def test_week_fields_present(self):
        weeks = get_weeks(date(2025, 6, 30), date(2025, 7, 4))
        assert len(weeks) == 1
        w = weeks[0]
        assert "monday" in w
        assert "friday" in w
        assert "start" in w
        assert "end" in w
        assert "weekdays" in w
        assert "partial" in w

    def test_single_monday(self):
        weeks = get_weeks(date(2025, 6, 30), date(2025, 6, 30))
        assert len(weeks) == 1
        assert weeks[0]["weekdays"] == 1
        assert weeks[0]["partial"] is True


class TestGetIndividualDays:
    """Tests for get_individual_days()."""

    def test_count_matches_weekdays(self):
        start = date(2025, 6, 30)
        end = date(2025, 7, 11)
        days = get_individual_days(start, end)
        weekdays = get_weekdays(start, end)
        assert len(days) == len(weekdays)

    def test_week_numbering_monday_start(self):
        # Starts Monday: week 1 = Mon–Fri, week 2 = next Mon+
        days = get_individual_days(date(2025, 6, 30), date(2025, 7, 11))
        week1 = [d for d in days if d["week_number"] == 1]
        week2 = [d for d in days if d["week_number"] == 2]
        assert len(week1) == 5
        assert len(week2) == 5

    def test_day_format(self):
        days = get_individual_days(date(2025, 6, 30), date(2025, 7, 4))
        assert days[0]["date"] == "2025-06-30"
        assert days[0]["day_of_week"] == "Mon"
        assert isinstance(days[0]["week_number"], int)

    def test_partial_week_pre_monday_is_week_1(self):
        # Start on Wednesday
        days = get_individual_days(date(2025, 7, 2), date(2025, 7, 11))
        # Days before first Monday (Jul 7) should be week 1
        assert days[0]["week_number"] == 1
        assert days[0]["day_of_week"] == "Wed"

    def test_empty_range(self):
        # Weekend-only range
        days = get_individual_days(date(2025, 7, 5), date(2025, 7, 6))
        assert days == []


class TestMainCLI:
    """Integration tests for main() via patched sys.argv and sys.stdout."""

    def _run(self, argv):
        """Run main() with given argv list, return stdout string."""
        with patch("sys.argv", argv):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                import summer_dates
                summer_dates.main()
                return mock_out.getvalue()

    def test_json_output_format(self):
        argv = [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-26",
            "--first-fall-day", "2025-09-02",
            "--format", "json",
        ]
        out = self._run(argv)
        data = json.loads(out)
        assert data["year"] == 2025
        assert data["last_school_day"] == "2025-06-26"
        assert "coverage_start" in data
        assert "coverage_end" in data
        assert "weeks" in data
        assert isinstance(data["coverage_weekdays"], int)

    def test_markdown_output_format(self):
        argv = [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-26",
            "--first-fall-day", "2025-09-02",
            "--format", "markdown",
        ]
        out = self._run(argv)
        assert "# Summer 2025 Coverage Window" in out
        assert "**Last school day:**" in out
        assert "## Week-by-Week Breakdown" in out

    def test_text_output_format(self):
        argv = [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-26",
            "--first-fall-day", "2025-09-02",
            "--format", "text",
        ]
        out = self._run(argv)
        assert "Summer 2025 Coverage Window" in out
        assert "Last school day:" in out
        assert "Week-by-Week:" in out

    def test_exclusion_dates_subtract_days(self):
        # One full week excluded (Mon–Fri = 5 days)
        argv_no_excl = [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-26",
            "--first-fall-day", "2025-09-02",
            "--format", "json",
        ]
        argv_with_excl = [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-26",
            "--first-fall-day", "2025-09-02",
            "--format", "json",
            "--exclude", "2025-07-14:2025-07-18",
        ]
        out_no = self._run(argv_no_excl)
        out_with = self._run(argv_with_excl)
        data_no = json.loads(out_no)
        data_with = json.loads(out_with)
        assert data_with["coverage_weekdays"] == data_no["coverage_weekdays"] - 5
        assert data_with["excluded_weekdays"] == 5

    def test_output_days_flag(self):
        argv = [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-26",
            "--first-fall-day", "2025-09-02",
            "--format", "json",
            "--output-days",
        ]
        out = self._run(argv)
        data = json.loads(out)
        assert "days" in data
        assert len(data["days"]) > 0
        first_day = data["days"][0]
        assert "date" in first_day
        assert "day_of_week" in first_day
        assert "week_number" in first_day
        assert "excluded" in first_day

    def test_private_school_early_start_before_labour_day(self):
        # first_fall_day before Labour Day 2025 (Sep 1): e.g., Aug 28 (Thu)
        argv = [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-26",
            "--first-fall-day", "2025-08-28",
            "--format", "json",
        ]
        out = self._run(argv)
        data = json.loads(out)
        assert data["first_fall_day"] == "2025-08-28"
        # Coverage should end before Aug 28
        from datetime import date
        cov_end = date.fromisoformat(data["coverage_end"])
        first_fall = date.fromisoformat(data["first_fall_day"])
        assert cov_end < first_fall

    def test_last_school_day_on_friday_coverage_starts_monday(self):
        # Jun 27 2025 is a Friday; coverage should start Mon Jun 30
        argv = [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-27",
            "--first-fall-day", "2025-09-02",
            "--format", "json",
        ]
        out = self._run(argv)
        data = json.loads(out)
        assert data["coverage_start"] == "2025-06-30"
