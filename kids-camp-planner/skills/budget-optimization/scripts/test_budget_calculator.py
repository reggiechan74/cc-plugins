"""Comprehensive tests for budget_calculator.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from argparse import Namespace

import pytest

from budget_calculator import (
    calculate_json_budget,
    calculate_simple_budget,
    format_currency,
    render_csv_detailed,
    render_csv_simple,
    render_markdown_detailed,
    render_markdown_simple,
)


# ---------------------------------------------------------------------------
# format_currency
# ---------------------------------------------------------------------------

class TestFormatCurrency:
    def test_whole_number(self):
        assert format_currency(1000) == "$1,000"

    def test_float_whole(self):
        assert format_currency(1000.0) == "$1,000"

    def test_fractional_cents(self):
        assert format_currency(1234.56) == "$1,234.56"

    def test_zero(self):
        assert format_currency(0) == "$0"

    def test_small_amount(self):
        assert format_currency(50) == "$50"

    def test_large_amount(self):
        assert format_currency(10000) == "$10,000"


# ---------------------------------------------------------------------------
# calculate_simple_budget — weekly mode
# ---------------------------------------------------------------------------

def _weekly_args(**kwargs):
    defaults = dict(
        kids=1,
        weeks=8,
        base_cost=300,
        before_care=0,
        after_care=0,
        lunch=0,
        daily_rate=None,
        days=None,
        before_care_daily=0,
        after_care_daily=0,
        lunch_daily=0,
        sibling_discount=0,
        early_bird=0,
        registration_fee=0,
        budget_limit=0,
    )
    defaults.update(kwargs)
    return Namespace(**defaults)


class TestCalculateSimpleBudgetWeekly:
    def test_one_child_basic(self):
        args = _weekly_args(kids=1, weeks=8, base_cost=300)
        results, grand_total = calculate_simple_budget(args)
        assert len(results) == 1
        assert results[0]["camp_fees"] == 2400  # 300 * 8
        assert results[0]["total"] == 2400
        assert grand_total == 2400

    def test_two_children_no_discount(self):
        args = _weekly_args(kids=2, weeks=8, base_cost=300)
        results, grand_total = calculate_simple_budget(args)
        assert len(results) == 2
        assert grand_total == 4800

    def test_with_before_after_care(self):
        args = _weekly_args(kids=1, weeks=4, base_cost=300, before_care=50, after_care=50)
        results, grand_total = calculate_simple_budget(args)
        assert results[0]["before_after"] == 400  # (50+50) * 4
        assert results[0]["camp_fees"] == 1200    # 300 * 4
        assert results[0]["subtotal"] == 1600

    def test_with_lunch(self):
        args = _weekly_args(kids=1, weeks=4, base_cost=300, lunch=35)
        results, grand_total = calculate_simple_budget(args)
        assert results[0]["lunch_cost"] == 140   # 35 * 4

    def test_with_registration_fee(self):
        args = _weekly_args(kids=1, weeks=4, base_cost=300, registration_fee=50)
        results, grand_total = calculate_simple_budget(args)
        assert results[0]["registration"] == 50
        assert results[0]["subtotal"] == 300 * 4 + 50

    def test_sibling_discount_first_child_zero(self):
        """First child never gets a sibling discount."""
        args = _weekly_args(kids=2, weeks=8, base_cost=300, sibling_discount=10)
        results, _ = calculate_simple_budget(args)
        assert results[0]["sibling_discount"] == 0

    def test_sibling_discount_second_child(self):
        """10% sibling discount on base cost for 2nd child."""
        args = _weekly_args(kids=2, weeks=8, base_cost=300, sibling_discount=10)
        results, _ = calculate_simple_budget(args)
        # 10% of (300 * 8) = 240
        assert results[1]["sibling_discount"] == 240.0

    def test_sibling_discount_100_percent(self):
        """100% sibling discount = full base cost for 2nd child."""
        args = _weekly_args(kids=2, weeks=4, base_cost=200, sibling_discount=100)
        results, _ = calculate_simple_budget(args)
        assert results[1]["sibling_discount"] == 800.0

    def test_sibling_discount_zero_percent(self):
        args = _weekly_args(kids=2, weeks=4, base_cost=200, sibling_discount=0)
        results, _ = calculate_simple_budget(args)
        assert results[1]["sibling_discount"] == 0

    def test_early_bird_discount(self):
        """Early bird is per-week for every child."""
        args = _weekly_args(kids=2, weeks=8, base_cost=300, early_bird=25)
        results, _ = calculate_simple_budget(args)
        for r in results:
            assert r["early_bird_discount"] == 200  # 25 * 8

    def test_early_bird_and_sibling_stacking(self):
        args = _weekly_args(
            kids=2, weeks=8, base_cost=300,
            early_bird=25, sibling_discount=10,
        )
        results, grand_total = calculate_simple_budget(args)
        # Child 1: 2400 - 0 - 200 = 2200
        assert results[0]["total"] == 2200.0
        # Child 2: 2400 - 240 - 200 = 1960
        assert results[1]["total"] == 1960.0
        assert grand_total == 4160.0

    def test_four_children(self):
        args = _weekly_args(kids=4, weeks=4, base_cost=200, sibling_discount=10)
        results, grand_total = calculate_simple_budget(args)
        assert len(results) == 4
        # Only child 1 has no sibling discount
        assert results[0]["sibling_discount"] == 0
        for r in results[1:]:
            assert r["sibling_discount"] > 0

    def test_subtotal_includes_registration(self):
        args = _weekly_args(kids=1, weeks=4, base_cost=300, registration_fee=75)
        results, _ = calculate_simple_budget(args)
        assert results[0]["subtotal"] == 300 * 4 + 75

    def test_grand_total_is_sum_of_totals(self):
        args = _weekly_args(kids=3, weeks=6, base_cost=250, sibling_discount=10, early_bird=20)
        results, grand_total = calculate_simple_budget(args)
        assert grand_total == sum(r["total"] for r in results)


# ---------------------------------------------------------------------------
# calculate_simple_budget — daily mode
# ---------------------------------------------------------------------------

def _daily_args(**kwargs):
    defaults = dict(
        kids=1,
        weeks=None,
        base_cost=None,
        before_care=0,
        after_care=0,
        lunch=0,
        daily_rate=60,
        days=10,
        before_care_daily=0,
        after_care_daily=0,
        lunch_daily=0,
        sibling_discount=0,
        early_bird=0,
        registration_fee=0,
        budget_limit=0,
    )
    defaults.update(kwargs)
    return Namespace(**defaults)


class TestCalculateSimpleBudgetDaily:
    def test_one_child_daily(self):
        args = _daily_args(kids=1, daily_rate=60, days=10)
        results, grand_total = calculate_simple_budget(args)
        assert results[0]["camp_fees"] == 600  # 60 * 10
        assert results[0]["total"] == 600
        assert grand_total == 600

    def test_with_before_after_daily(self):
        args = _daily_args(kids=1, daily_rate=60, days=10,
                           before_care_daily=10, after_care_daily=10)
        results, _ = calculate_simple_budget(args)
        assert results[0]["before_after"] == 200  # (10+10) * 10

    def test_with_lunch_daily(self):
        args = _daily_args(kids=1, daily_rate=60, days=10, lunch_daily=7)
        results, _ = calculate_simple_budget(args)
        assert results[0]["lunch_cost"] == 70  # 7 * 10

    def test_sibling_discount_daily(self):
        args = _daily_args(kids=2, daily_rate=60, days=10, sibling_discount=10)
        results, _ = calculate_simple_budget(args)
        assert results[0]["sibling_discount"] == 0
        assert results[1]["sibling_discount"] == 60.0  # 10% of (60 * 10)

    def test_early_bird_daily_uses_week_count(self):
        # 10 days → ceil(10/5) = 2 weeks → early_bird * 2
        args = _daily_args(kids=1, daily_rate=60, days=10, early_bird=25)
        results, _ = calculate_simple_budget(args)
        assert results[0]["early_bird_discount"] == 50  # 25 * 2

    def test_registration_fee_daily(self):
        args = _daily_args(kids=1, daily_rate=60, days=10, registration_fee=50)
        results, _ = calculate_simple_budget(args)
        assert results[0]["registration"] == 50
        assert results[0]["subtotal"] == 60 * 10 + 50

    def test_daily_mode_activated_by_days_flag(self):
        """Setting days (not daily_rate) should still trigger daily mode."""
        args = _daily_args(daily_rate=None, days=10)
        results, grand_total = calculate_simple_budget(args)
        # daily_rate defaults to 60 inside function when use_daily is True
        assert grand_total == 600


# ---------------------------------------------------------------------------
# calculate_json_budget — weekly format
# ---------------------------------------------------------------------------

WEEKLY_INPUT = {
    "children": [
        {"name": "Alice", "age": 7},
        {"name": "Bob", "age": 5},
    ],
    "budget_limit": 5000,
    "weeks": [
        {
            "week_number": 1,
            "start_date": "2025-06-30",
            "assignments": {
                "Alice": {"provider": "YMCA", "base_cost": 300, "before_care": 50, "after_care": 50, "lunch": 0},
                "Bob":   {"provider": "YMCA", "base_cost": 270, "before_care": 50, "after_care": 50, "lunch": 0},
            },
        },
        {
            "week_number": 2,
            "start_date": "2025-07-07",
            "assignments": {
                "Alice": {"provider": "YMCA", "base_cost": 300, "before_care": 50, "after_care": 50, "lunch": 0},
                "Bob":   {"provider": "YMCA", "base_cost": 270, "before_care": 50, "after_care": 50, "lunch": 0},
            },
        },
    ],
    "discounts": {
        "sibling_percent": 10,
        "early_bird_per_week": 25,
        "multi_week_threshold": 2,
        "multi_week_percent": 5,
    },
    "registration_fees": {"YMCA": 50},
}


class TestCalculateJsonBudgetWeekly:
    def test_returns_expected_keys(self):
        data = calculate_json_budget(WEEKLY_INPUT)
        assert "children" in data
        assert "grand_total" in data
        assert "budget_limit" in data
        assert "weekly_details" in data
        assert "child_names" in data

    def test_budget_limit_preserved(self):
        data = calculate_json_budget(WEEKLY_INPUT)
        assert data["budget_limit"] == 5000

    def test_child_count(self):
        data = calculate_json_budget(WEEKLY_INPUT)
        assert len(data["children"]) == 2

    def test_child_names(self):
        data = calculate_json_budget(WEEKLY_INPUT)
        names = [c["child"] for c in data["children"]]
        assert "Alice" in names
        assert "Bob" in names

    def test_registration_fee_applied(self):
        data = calculate_json_budget(WEEKLY_INPUT)
        for c in data["children"]:
            assert c["registration"] == 50

    def test_sibling_discount_first_child_zero(self):
        data = calculate_json_budget(WEEKLY_INPUT)
        alice = next(c for c in data["children"] if c["child"] == "Alice")
        assert alice["sibling_discount"] == 0

    def test_sibling_discount_second_child_nonzero(self):
        data = calculate_json_budget(WEEKLY_INPUT)
        bob = next(c for c in data["children"] if c["child"] == "Bob")
        # 10% of (270 * 2) = 54
        assert bob["sibling_discount"] == pytest.approx(54.0)

    def test_early_bird_applied_to_all(self):
        data = calculate_json_budget(WEEKLY_INPUT)
        for c in data["children"]:
            assert c["early_bird_discount"] == 50  # 25 * 2 weeks

    def test_multi_week_discount_applied(self):
        data = calculate_json_budget(WEEKLY_INPUT)
        # Alice: 2 weeks >= threshold 2, 5% of (300 * 2) = 30
        alice = next(c for c in data["children"] if c["child"] == "Alice")
        assert alice["multi_week_discount"] == pytest.approx(30.0)

    def test_grand_total_is_sum_of_totals(self):
        data = calculate_json_budget(WEEKLY_INPUT)
        assert data["grand_total"] == pytest.approx(
            sum(c["total"] for c in data["children"])
        )

    def test_weekly_details_count(self):
        data = calculate_json_budget(WEEKLY_INPUT)
        assert len(data["weekly_details"]) == 2

    def test_no_assignment_shows_no_camp(self):
        input_copy = dict(WEEKLY_INPUT)
        # Only Alice assigned in week 1
        input_copy["weeks"] = [
            {
                "week_number": 1,
                "start_date": "2025-06-30",
                "assignments": {
                    "Alice": {"provider": "YMCA", "base_cost": 300, "before_care": 0, "after_care": 0, "lunch": 0},
                },
            }
        ]
        data = calculate_json_budget(input_copy)
        week_row = data["weekly_details"][0]
        assert week_row["Bob"]["provider"] == "No camp"


# ---------------------------------------------------------------------------
# calculate_json_budget — daily format
# ---------------------------------------------------------------------------

DAILY_INPUT = {
    "children": [
        {"name": "Child 1", "age": 7},
        {"name": "Child 2", "age": 5},
    ],
    "budget_limit": 3000,
    "days": [
        {
            "date": f"2025-07-0{d}",
            "assignments": {
                "Child 1": {"provider": "Camp A", "daily_rate": 60, "before_care": 10, "after_care": 10, "lunch": 7},
                "Child 2": {"provider": "Camp A", "daily_rate": 50, "before_care": 10, "after_care": 10, "lunch": 7},
            },
        }
        for d in range(1, 6)  # 5 days = 1 week
    ],
    "discounts": {
        "sibling_percent": 10,
        "early_bird_per_week": 20,
        "multi_week_threshold": 1,
        "multi_week_percent": 5,
    },
    "registration_fees": {"Camp A": 40},
}


class TestCalculateJsonBudgetDaily:
    def test_returns_expected_keys(self):
        data = calculate_json_budget(DAILY_INPUT)
        assert "children" in data
        assert "grand_total" in data

    def test_child_count(self):
        data = calculate_json_budget(DAILY_INPUT)
        assert len(data["children"]) == 2

    def test_camp_fees_calculated_correctly(self):
        data = calculate_json_budget(DAILY_INPUT)
        c1 = next(c for c in data["children"] if c["child"] == "Child 1")
        # (60 + 10 + 10 + 7) * 5 = 87 * 5 = 435
        assert c1["camp_fees"] == 435

    def test_registration_fee_applied(self):
        data = calculate_json_budget(DAILY_INPUT)
        for c in data["children"]:
            assert c["registration"] == 40

    def test_sibling_discount_daily(self):
        data = calculate_json_budget(DAILY_INPUT)
        c1 = next(c for c in data["children"] if c["child"] == "Child 1")
        c2 = next(c for c in data["children"] if c["child"] == "Child 2")
        assert c1["sibling_discount"] == 0
        # 10% of (50 * 5) = 25
        assert c2["sibling_discount"] == pytest.approx(25.0)

    def test_grand_total_is_sum_of_totals(self):
        data = calculate_json_budget(DAILY_INPUT)
        assert data["grand_total"] == pytest.approx(
            sum(c["total"] for c in data["children"])
        )

    def test_weekly_details_generated_from_days(self):
        # 5 days should produce 1 weekly row
        data = calculate_json_budget(DAILY_INPUT)
        assert len(data["weekly_details"]) == 1

    def test_partial_week_creates_extra_row(self):
        # 7 days = 1 full week + 2 leftover days → 2 weekly rows
        extra_days_input = dict(DAILY_INPUT)
        extra_days_input["days"] = DAILY_INPUT["days"] + [
            {
                "date": "2025-07-08",
                "assignments": {
                    "Child 1": {"provider": "Camp A", "daily_rate": 60, "before_care": 0, "after_care": 0, "lunch": 0},
                },
            },
            {
                "date": "2025-07-09",
                "assignments": {
                    "Child 1": {"provider": "Camp A", "daily_rate": 60, "before_care": 0, "after_care": 0, "lunch": 0},
                },
            },
        ]
        data = calculate_json_budget(extra_days_input)
        assert len(data["weekly_details"]) == 2


# ---------------------------------------------------------------------------
# render_markdown_simple
# ---------------------------------------------------------------------------

def _simple_results_one_child(total=2400):
    return [{
        "child": "Child 1",
        "camp_fees": total,
        "before_after": 0,
        "lunch_cost": 0,
        "registration": 0,
        "subtotal": total,
        "sibling_discount": 0,
        "early_bird_discount": 0,
        "total": total,
    }]


def _simple_results_two_children():
    return [
        {
            "child": "Child 1",
            "camp_fees": 2400,
            "before_after": 400,
            "lunch_cost": 140,
            "registration": 50,
            "subtotal": 2990,
            "sibling_discount": 0,
            "early_bird_discount": 200,
            "total": 2790,
        },
        {
            "child": "Child 2",
            "camp_fees": 2400,
            "before_after": 400,
            "lunch_cost": 140,
            "registration": 50,
            "subtotal": 2990,
            "sibling_discount": 240,
            "early_bird_discount": 200,
            "total": 2550,
        },
    ]


class TestRenderMarkdownSimple:
    def test_contains_heading(self):
        results = _simple_results_one_child()
        args = Namespace(budget_limit=0)
        output = render_markdown_simple(results, 2400, args)
        assert "# Camp Budget Summary" in output

    def test_contains_child_name(self):
        results = _simple_results_one_child()
        args = Namespace(budget_limit=0)
        output = render_markdown_simple(results, 2400, args)
        assert "Child 1" in output

    def test_contains_camp_fees_formatted(self):
        results = _simple_results_one_child(total=2400)
        args = Namespace(budget_limit=0)
        output = render_markdown_simple(results, 2400, args)
        assert "$2,400" in output

    def test_before_after_row_hidden_when_zero(self):
        results = _simple_results_one_child()
        args = Namespace(budget_limit=0)
        output = render_markdown_simple(results, 2400, args)
        assert "Before/after care" not in output

    def test_before_after_row_shown_when_nonzero(self):
        results = _simple_results_two_children()
        args = Namespace(budget_limit=0)
        output = render_markdown_simple(results, 5340, args)
        assert "Before/after care" in output

    def test_lunch_row_hidden_when_zero(self):
        results = _simple_results_one_child()
        args = Namespace(budget_limit=0)
        output = render_markdown_simple(results, 2400, args)
        assert "Lunch" not in output

    def test_lunch_row_shown_when_nonzero(self):
        results = _simple_results_two_children()
        args = Namespace(budget_limit=0)
        output = render_markdown_simple(results, 5340, args)
        assert "Lunch" in output

    def test_sibling_discount_row_hidden_when_zero(self):
        results = _simple_results_one_child()
        args = Namespace(budget_limit=0)
        output = render_markdown_simple(results, 2400, args)
        assert "Sibling discount" not in output

    def test_sibling_discount_row_shown(self):
        results = _simple_results_two_children()
        args = Namespace(budget_limit=0)
        output = render_markdown_simple(results, 5340, args)
        assert "Sibling discount" in output

    def test_tax_section_present(self):
        results = _simple_results_one_child()
        args = Namespace(budget_limit=0)
        output = render_markdown_simple(results, 2400, args)
        assert "Tax Recovery Estimate" in output

    def test_budget_check_not_shown_when_zero(self):
        results = _simple_results_one_child()
        args = Namespace(budget_limit=0)
        output = render_markdown_simple(results, 2400, args)
        assert "Budget Check" not in output

    def test_budget_check_over(self):
        results = _simple_results_one_child(total=6000)
        args = Namespace(budget_limit=5000)
        output = render_markdown_simple(results, 6000, args)
        assert "OVER" in output
        assert "$1,000 OVER" in output

    def test_budget_check_under(self):
        results = _simple_results_one_child(total=4000)
        args = Namespace(budget_limit=5000)
        output = render_markdown_simple(results, 4000, args)
        assert "UNDER" in output

    def test_registration_row_shown(self):
        results = _simple_results_two_children()
        args = Namespace(budget_limit=0)
        output = render_markdown_simple(results, 5340, args)
        assert "Registration" in output


# ---------------------------------------------------------------------------
# render_markdown_detailed
# ---------------------------------------------------------------------------

def _detailed_data():
    return {
        "children": [
            {
                "child": "Alice",
                "camp_fees": 800,
                "registration": 50,
                "subtotal": 850,
                "sibling_discount": 0,
                "early_bird_discount": 50,
                "multi_week_discount": 30,
                "total_discount": 80,
                "total": 770,
            },
            {
                "child": "Bob",
                "camp_fees": 700,
                "registration": 50,
                "subtotal": 750,
                "sibling_discount": 54,
                "early_bird_discount": 50,
                "multi_week_discount": 27,
                "total_discount": 131,
                "total": 619,
            },
        ],
        "grand_total": 1389,
        "budget_limit": 2000,
        "weekly_details": [
            {
                "week": 1,
                "start_date": "2025-06-30",
                "Alice": {"provider": "YMCA", "cost": 400, "base": 300},
                "Bob":   {"provider": "YMCA", "cost": 350, "base": 270},
            },
            {
                "week": 2,
                "start_date": "2025-07-07",
                "Alice": {"provider": "YMCA", "cost": 400, "base": 300},
                "Bob":   {"provider": "YMCA", "cost": 350, "base": 270},
            },
        ],
        "child_names": ["Alice", "Bob"],
    }


class TestRenderMarkdownDetailed:
    def test_contains_heading(self):
        output = render_markdown_detailed(_detailed_data())
        assert "# Camp Budget Summary" in output

    def test_contains_child_names(self):
        output = render_markdown_detailed(_detailed_data())
        assert "Alice" in output
        assert "Bob" in output

    def test_weekly_breakdown_section(self):
        output = render_markdown_detailed(_detailed_data())
        assert "Weekly Breakdown" in output

    def test_week_dates_present(self):
        output = render_markdown_detailed(_detailed_data())
        assert "2025-06-30" in output
        assert "2025-07-07" in output

    def test_sibling_discount_row_shown(self):
        output = render_markdown_detailed(_detailed_data())
        assert "Sibling discount" in output

    def test_multi_week_discount_row_shown(self):
        output = render_markdown_detailed(_detailed_data())
        assert "Multi-week discount" in output

    def test_tax_section_present(self):
        output = render_markdown_detailed(_detailed_data())
        assert "Tax Recovery Estimate" in output

    def test_budget_check_under(self):
        output = render_markdown_detailed(_detailed_data())
        assert "UNDER" in output

    def test_budget_check_over(self):
        data = _detailed_data()
        data["grand_total"] = 2500
        data["budget_limit"] = 2000
        output = render_markdown_detailed(data)
        assert "OVER" in output

    def test_budget_check_not_shown_when_zero(self):
        data = _detailed_data()
        data["budget_limit"] = 0
        output = render_markdown_detailed(data)
        assert "Budget Check" not in output


# ---------------------------------------------------------------------------
# render_csv_simple
# ---------------------------------------------------------------------------

class TestRenderCsvSimple:
    def test_header_row(self):
        results = _simple_results_one_child()
        csv = render_csv_simple(results, 2400)
        first_line = csv.splitlines()[0]
        assert "Child" in first_line
        assert "Camp Fees" in first_line
        assert "Total" in first_line

    def test_data_row_count(self):
        results = _simple_results_two_children()
        csv = render_csv_simple(results, 5340)
        lines = csv.splitlines()
        # header + 2 children + TOTAL = 4 lines
        assert len(lines) == 4

    def test_total_row_present(self):
        results = _simple_results_one_child()
        csv = render_csv_simple(results, 2400)
        assert "TOTAL" in csv

    def test_grand_total_in_output(self):
        results = _simple_results_one_child()
        csv = render_csv_simple(results, 2400)
        assert "2400" in csv

    def test_child_name_in_output(self):
        results = _simple_results_one_child()
        csv = render_csv_simple(results, 2400)
        assert "Child 1" in csv


# ---------------------------------------------------------------------------
# render_csv_detailed
# ---------------------------------------------------------------------------

class TestRenderCsvDetailed:
    def test_header_row(self):
        data = _detailed_data()
        csv = render_csv_detailed(data)
        first_line = csv.splitlines()[0]
        assert "Week" in first_line
        assert "Start Date" in first_line

    def test_week_rows_present(self):
        data = _detailed_data()
        csv = render_csv_detailed(data)
        assert "2025-06-30" in csv
        assert "2025-07-07" in csv

    def test_summary_section(self):
        data = _detailed_data()
        csv = render_csv_detailed(data)
        assert "Summary" in csv

    def test_grand_total_in_output(self):
        data = _detailed_data()
        csv = render_csv_detailed(data)
        assert "1389" in csv

    def test_child_names_in_header(self):
        data = _detailed_data()
        csv = render_csv_detailed(data)
        first_line = csv.splitlines()[0]
        assert "Alice" in first_line
        assert "Bob" in first_line


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_one_child_no_discounts(self):
        args = _weekly_args(kids=1, weeks=1, base_cost=100)
        results, grand_total = calculate_simple_budget(args)
        assert len(results) == 1
        assert grand_total == 100

    def test_four_children_grand_total(self):
        args = _weekly_args(kids=4, weeks=4, base_cost=200, sibling_discount=10)
        results, grand_total = calculate_simple_budget(args)
        assert grand_total == sum(r["total"] for r in results)

    def test_json_single_child(self):
        data = {
            "children": [{"name": "Only Child", "age": 8}],
            "budget_limit": 0,
            "weeks": [
                {
                    "week_number": 1,
                    "start_date": "2025-07-01",
                    "assignments": {
                        "Only Child": {"provider": "Camp X", "base_cost": 300, "before_care": 0, "after_care": 0, "lunch": 0},
                    },
                }
            ],
            "discounts": {"sibling_percent": 10, "early_bird_per_week": 0},
            "registration_fees": {},
        }
        result = calculate_json_budget(data)
        assert len(result["children"]) == 1
        assert result["children"][0]["sibling_discount"] == 0
        assert result["grand_total"] == 300

    def test_zero_weeks_json(self):
        data = {
            "children": [{"name": "Child", "age": 7}],
            "budget_limit": 0,
            "weeks": [],
            "discounts": {},
            "registration_fees": {},
        }
        result = calculate_json_budget(data)
        assert result["grand_total"] == 0

    def test_format_currency_cents(self):
        assert format_currency(99.50) == "$99.50"
