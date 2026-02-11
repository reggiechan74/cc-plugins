#!/usr/bin/env python3
"""
Camp Budget Calculator

Calculate and compare camp costs across multiple children, providers, and weeks.
Generates markdown tables or CSV output with discount application and tax estimates.
Supports both weekly and daily rate calculations.

Usage:
    # Simple single-provider calculation (weekly rates)
    python3 budget_calculator.py --kids 2 --weeks 8 --base-cost 300 --format markdown

    # With all cost components (weekly rates)
    python3 budget_calculator.py --kids 2 --weeks 8 --base-cost 300 \
        --before-care 50 --after-care 50 --lunch 35 \
        --sibling-discount 10 --early-bird 25 --registration-fee 50 \
        --format markdown

    # Daily rate calculation
    python3 budget_calculator.py --kids 2 --days 40 --daily-rate 60 \
        --before-care-daily 10 --after-care-daily 10 --lunch-daily 7 \
        --format markdown

    # Multi-provider from JSON input (supports both "weeks" and "days" arrays)
    python3 budget_calculator.py --input budget-input.json --format markdown

    # CSV output
    python3 budget_calculator.py --input budget-input.json --format csv

JSON Input Schema (weekly):
{
    "children": [
        {"name": "Child 1", "age": 7},
        {"name": "Child 2", "age": 5}
    ],
    "budget_limit": 5000,
    "weeks": [
        {
            "week_number": 1,
            "start_date": "2025-06-30",
            "assignments": {
                "Child 1": {
                    "provider": "YMCA Day Camp",
                    "base_cost": 300,
                    "before_care": 50,
                    "after_care": 50,
                    "lunch": 0
                },
                "Child 2": {
                    "provider": "YMCA Day Camp",
                    "base_cost": 270,
                    "before_care": 50,
                    "after_care": 50,
                    "lunch": 0
                }
            }
        }
    ],
    "discounts": {
        "sibling_percent": 10,
        "early_bird_per_week": 25,
        "multi_week_threshold": 4,
        "multi_week_percent": 5
    },
    "registration_fees": {
        "YMCA Day Camp": 50
    }
}

JSON Input Schema (daily - alternative to "weeks"):
{
    "children": [
        {"name": "Child 1", "age": 7},
        {"name": "Child 2", "age": 5}
    ],
    "budget_limit": 5000,
    "days": [
        {
            "date": "2025-06-30",
            "assignments": {
                "Child 1": {
                    "provider": "YMCA Day Camp",
                    "daily_rate": 60,
                    "before_care": 10,
                    "after_care": 10,
                    "lunch": 7
                }
            }
        }
    ],
    "discounts": { ... },
    "registration_fees": { ... }
}
"""

import argparse
import json
import sys
from datetime import datetime, timedelta


def calculate_simple_budget(args):
    """Calculate budget for a simple single-provider scenario.

    Supports both weekly rates (--base-cost/--weeks) and daily rates
    (--daily-rate/--days). Daily rates take precedence if both are provided.
    """
    kids = args.kids
    sibling_pct = args.sibling_discount or 0
    early_bird = args.early_bird or 0
    reg_fee = args.registration_fee or 0

    # Determine if using daily or weekly rates
    use_daily = args.daily_rate is not None or args.days is not None

    if use_daily:
        num_days = args.days or 40
        daily_rate = args.daily_rate or 60
        before_daily = args.before_care_daily or 0
        after_daily = args.after_care_daily or 0
        lunch_daily = args.lunch_daily or 0
        daily_total = daily_rate + before_daily + after_daily + lunch_daily
        # Convert to equivalent weekly values for discount calculations
        num_weeks = (num_days + 4) // 5  # ceiling division for week count
    else:
        num_weeks = args.weeks
        base = args.base_cost
        before = args.before_care or 0
        after = args.after_care or 0
        lunch = args.lunch or 0

    results = []
    grand_total = 0

    for i in range(kids):
        child_num = i + 1

        if use_daily:
            camp_fees = daily_rate * num_days
            before_after = (before_daily + after_daily) * num_days
            lunch_cost = lunch_daily * num_days
            subtotal = (daily_total * num_days) + reg_fee

            sibling_disc = 0
            if i > 0 and sibling_pct > 0:
                sibling_disc = camp_fees * (sibling_pct / 100)

            early_disc = early_bird * num_weeks
            total = subtotal - sibling_disc - early_disc

            results.append({
                "child": f"Child {child_num}",
                "daily_cost": daily_total,
                "days": num_days,
                "camp_fees": camp_fees,
                "before_after": before_after,
                "lunch_cost": lunch_cost,
                "registration": reg_fee,
                "subtotal": subtotal,
                "sibling_discount": sibling_disc,
                "early_bird_discount": early_disc,
                "total": total,
            })
        else:
            weekly_cost = base + before + after + lunch

            sibling_disc = 0
            if i > 0 and sibling_pct > 0:
                sibling_disc = base * (sibling_pct / 100) * num_weeks

            subtotal = (weekly_cost * num_weeks) + reg_fee
            early_disc = early_bird * num_weeks
            total = subtotal - sibling_disc - early_disc

            results.append({
                "child": f"Child {child_num}",
                "weekly_cost": weekly_cost,
                "weeks": num_weeks,
                "camp_fees": base * num_weeks,
                "before_after": (before + after) * num_weeks,
                "lunch_cost": lunch * num_weeks,
                "registration": reg_fee,
                "subtotal": subtotal,
                "sibling_discount": sibling_disc,
                "early_bird_discount": early_disc,
                "total": total,
            })
        grand_total += total

    return results, grand_total


def calculate_json_budget(input_data):
    """Calculate budget from a detailed JSON input.

    Supports both "weeks" and "days" arrays. If "days" is present, it takes
    precedence. Each day entry has a date and per-child assignments with
    daily_rate, before_care, after_care, and lunch fields.
    """
    children = input_data["children"]
    budget_limit = input_data.get("budget_limit", 0)
    days_data = input_data.get("days", [])
    weeks_data = input_data.get("weeks", [])
    discounts = input_data.get("discounts", {})
    reg_fees = input_data.get("registration_fees", {})

    # If days data is present, convert to weekly format for processing
    if days_data:
        return _calculate_daily_json_budget(input_data)


    sibling_pct = discounts.get("sibling_percent", 0)
    early_bird = discounts.get("early_bird_per_week", 0)
    multi_week_threshold = discounts.get("multi_week_threshold", 0)
    multi_week_pct = discounts.get("multi_week_percent", 0)

    child_names = [c["name"] for c in children]
    child_totals = {name: 0 for name in child_names}
    child_base_totals = {name: 0 for name in child_names}
    providers_used = {name: set() for name in child_names}
    weekly_details = []

    for week in weeks_data:
        week_num = week["week_number"]
        start_date = week.get("start_date", "")
        week_row = {"week": week_num, "start_date": start_date}

        for child_name in child_names:
            assignment = week.get("assignments", {}).get(child_name)
            if assignment:
                provider = assignment.get("provider", "TBD")
                base = assignment.get("base_cost", 0)
                before = assignment.get("before_care", 0)
                after = assignment.get("after_care", 0)
                lunch = assignment.get("lunch", 0)
                weekly = base + before + after + lunch

                child_totals[child_name] += weekly
                child_base_totals[child_name] += base
                providers_used[child_name].add(provider)
                week_row[child_name] = {
                    "provider": provider,
                    "cost": weekly,
                    "base": base,
                }
            else:
                week_row[child_name] = {
                    "provider": "No camp",
                    "cost": 0,
                    "base": 0,
                }

        weekly_details.append(week_row)

    # Apply discounts
    child_discounts = {name: {"sibling": 0, "early_bird": 0, "multi_week": 0} for name in child_names}

    for i, name in enumerate(child_names):
        num_weeks = sum(
            1 for w in weekly_details if w.get(name, {}).get("cost", 0) > 0
        )

        # Sibling discount on 2nd+ child
        if i > 0 and sibling_pct > 0:
            child_discounts[name]["sibling"] = child_base_totals[name] * (sibling_pct / 100)

        # Early bird
        if early_bird > 0:
            child_discounts[name]["early_bird"] = early_bird * num_weeks

        # Multi-week discount
        if multi_week_threshold > 0 and num_weeks >= multi_week_threshold and multi_week_pct > 0:
            child_discounts[name]["multi_week"] = child_base_totals[name] * (multi_week_pct / 100)

    # Registration fees
    child_reg = {}
    for name in child_names:
        total_reg = sum(reg_fees.get(p, 0) for p in providers_used[name])
        child_reg[name] = total_reg

    # Final totals
    results = []
    grand_total = 0
    for name in child_names:
        disc = child_discounts[name]
        total_disc = disc["sibling"] + disc["early_bird"] + disc["multi_week"]
        final = child_totals[name] + child_reg[name] - total_disc
        results.append({
            "child": name,
            "camp_fees": child_totals[name],  # Includes base + before/after care + lunch
            "registration": child_reg[name],
            "subtotal": child_totals[name] + child_reg[name],
            "sibling_discount": disc["sibling"],
            "early_bird_discount": disc["early_bird"],
            "multi_week_discount": disc["multi_week"],
            "total_discount": total_disc,
            "total": final,
        })
        grand_total += final

    return {
        "children": results,
        "grand_total": grand_total,
        "budget_limit": budget_limit,
        "weekly_details": weekly_details,
        "child_names": child_names,
    }


def _calculate_daily_json_budget(input_data):
    """Calculate budget from daily JSON input format."""
    children = input_data["children"]
    budget_limit = input_data.get("budget_limit", 0)
    days_data = input_data["days"]
    discounts = input_data.get("discounts", {})
    reg_fees = input_data.get("registration_fees", {})

    sibling_pct = discounts.get("sibling_percent", 0)
    early_bird = discounts.get("early_bird_per_week", 0)
    multi_week_threshold = discounts.get("multi_week_threshold", 0)
    multi_week_pct = discounts.get("multi_week_percent", 0)

    child_names = [c["name"] for c in children]
    child_totals = {name: 0 for name in child_names}
    child_base_totals = {name: 0 for name in child_names}
    providers_used = {name: set() for name in child_names}
    daily_details = []

    for day_entry in days_data:
        day_date = day_entry.get("date", "")
        day_row = {"date": day_date}

        for child_name in child_names:
            assignment = day_entry.get("assignments", {}).get(child_name)
            if assignment:
                provider = assignment.get("provider", "TBD")
                daily_rate = assignment.get("daily_rate", 0)
                before = assignment.get("before_care", 0)
                after = assignment.get("after_care", 0)
                lunch = assignment.get("lunch", 0)
                day_cost = daily_rate + before + after + lunch

                child_totals[child_name] += day_cost
                child_base_totals[child_name] += daily_rate
                providers_used[child_name].add(provider)
                day_row[child_name] = {
                    "provider": provider,
                    "cost": day_cost,
                    "base": daily_rate,
                }
            else:
                day_row[child_name] = {
                    "provider": "No camp",
                    "cost": 0,
                    "base": 0,
                }

        daily_details.append(day_row)

    # Count weeks for discount purposes (every 5 days = 1 week)
    child_day_counts = {}
    for name in child_names:
        child_day_counts[name] = sum(
            1 for d in daily_details if d.get(name, {}).get("cost", 0) > 0
        )

    child_discounts = {name: {"sibling": 0, "early_bird": 0, "multi_week": 0} for name in child_names}

    for i, name in enumerate(child_names):
        num_weeks = (child_day_counts[name] + 4) // 5

        if i > 0 and sibling_pct > 0:
            child_discounts[name]["sibling"] = child_base_totals[name] * (sibling_pct / 100)

        if early_bird > 0:
            child_discounts[name]["early_bird"] = early_bird * num_weeks

        if multi_week_threshold > 0 and num_weeks >= multi_week_threshold and multi_week_pct > 0:
            child_discounts[name]["multi_week"] = child_base_totals[name] * (multi_week_pct / 100)

    child_reg = {}
    for name in child_names:
        total_reg = sum(reg_fees.get(p, 0) for p in providers_used[name])
        child_reg[name] = total_reg

    results = []
    grand_total = 0
    for name in child_names:
        disc = child_discounts[name]
        total_disc = disc["sibling"] + disc["early_bird"] + disc["multi_week"]
        final = child_totals[name] + child_reg[name] - total_disc
        results.append({
            "child": name,
            "camp_fees": child_totals[name],
            "registration": child_reg[name],
            "subtotal": child_totals[name] + child_reg[name],
            "sibling_discount": disc["sibling"],
            "early_bird_discount": disc["early_bird"],
            "multi_week_discount": disc["multi_week"],
            "total_discount": total_disc,
            "total": final,
        })
        grand_total += final

    # Convert daily details to weekly format for rendering compatibility
    weekly_details = []
    current_week = []
    week_num = 1
    for d in daily_details:
        current_week.append(d)
        if len(current_week) == 5:
            week_row = {"week": week_num, "start_date": current_week[0].get("date", "")}
            for name in child_names:
                week_cost = sum(day.get(name, {}).get("cost", 0) for day in current_week)
                providers_in_week = set(
                    day.get(name, {}).get("provider", "")
                    for day in current_week
                    if day.get(name, {}).get("cost", 0) > 0
                )
                week_row[name] = {
                    "provider": ", ".join(sorted(providers_in_week)) or "No camp",
                    "cost": week_cost,
                    "base": sum(day.get(name, {}).get("base", 0) for day in current_week),
                }
            weekly_details.append(week_row)
            current_week = []
            week_num += 1

    # Handle remaining days
    if current_week:
        week_row = {"week": week_num, "start_date": current_week[0].get("date", "")}
        for name in child_names:
            week_cost = sum(day.get(name, {}).get("cost", 0) for day in current_week)
            providers_in_week = set(
                day.get(name, {}).get("provider", "")
                for day in current_week
                if day.get(name, {}).get("cost", 0) > 0
            )
            week_row[name] = {
                "provider": ", ".join(sorted(providers_in_week)) or "No camp",
                "cost": week_cost,
                "base": sum(day.get(name, {}).get("base", 0) for day in current_week),
            }
        weekly_details.append(week_row)

    return {
        "children": results,
        "grand_total": grand_total,
        "budget_limit": budget_limit,
        "weekly_details": weekly_details,
        "child_names": child_names,
    }


def format_currency(amount):
    """Format a number as currency."""
    if amount == int(amount):
        return f"${int(amount):,}"
    return f"${amount:,.2f}"


def render_markdown_simple(results, grand_total, args):
    """Render simple budget as markdown."""
    lines = []
    lines.append("# Camp Budget Summary\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n")
    lines.append("## Cost Summary\n")

    # Header
    header = "| | " + " | ".join(r["child"] for r in results) + " | **Total** |"
    sep = "|---|" + "|".join(["--------:" for _ in results]) + "|--------:|"
    lines.append(header)
    lines.append(sep)

    # Rows
    total_camp = sum(r["camp_fees"] for r in results)
    total_ba = sum(r["before_after"] for r in results)
    total_lunch = sum(r["lunch_cost"] for r in results)
    total_reg = sum(r["registration"] for r in results)
    total_sub = sum(r["subtotal"] for r in results)
    total_sib = sum(r["sibling_discount"] for r in results)
    total_eb = sum(r["early_bird_discount"] for r in results)

    def row(label, key, negate=False):
        vals = []
        for r in results:
            v = r[key]
            if negate and v > 0:
                vals.append(f"-{format_currency(v)}")
            else:
                vals.append(format_currency(v))
        total = sum(r[key] for r in results)
        total_str = f"-{format_currency(total)}" if negate and total > 0 else format_currency(total)
        return f"| {label} | " + " | ".join(vals) + f" | **{total_str}** |"

    lines.append(row("Camp fees", "camp_fees"))
    if total_ba > 0:
        lines.append(row("Before/after care", "before_after"))
    if total_lunch > 0:
        lines.append(row("Lunch", "lunch_cost"))
    if total_reg > 0:
        lines.append(row("Registration", "registration"))
    lines.append(row("**Subtotal**", "subtotal"))
    if total_sib > 0:
        lines.append(row("Sibling discount", "sibling_discount", negate=True))
    if total_eb > 0:
        lines.append(row("Early bird discount", "early_bird_discount", negate=True))
    lines.append(row("**Total**", "total"))

    lines.append("")

    # Tax estimate
    lines.append("## Tax Recovery Estimate\n")
    for r in results:
        deductible = min(r["total"], 8000 if "age" not in r else (8000 if r.get("age", 7) < 7 else 5000))
        estimated_savings = deductible * 0.25  # rough marginal rate estimate
        lines.append(f"- **{r['child']}**: {format_currency(r['total'])} eligible, ~{format_currency(estimated_savings)} estimated tax savings (at ~25% marginal rate)")
    lines.append("")

    # Budget check
    if hasattr(args, "budget_limit") and args.budget_limit:
        diff = grand_total - args.budget_limit
        status = "OVER" if diff > 0 else "UNDER"
        lines.append("## Budget Check\n")
        lines.append(f"- Budget limit: {format_currency(args.budget_limit)}")
        lines.append(f"- Projected total: {format_currency(grand_total)}")
        lines.append(f"- Status: **{format_currency(abs(diff))} {status} budget**")
        lines.append("")

    return "\n".join(lines)


def render_markdown_detailed(data):
    """Render detailed JSON-based budget as markdown."""
    lines = []
    results = data["children"]
    child_names = data["child_names"]
    grand_total = data["grand_total"]
    budget_limit = data["budget_limit"]
    weekly = data["weekly_details"]

    lines.append("# Camp Budget Summary\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n")

    # Summary table
    lines.append("## Cost Summary\n")
    header = "| | " + " | ".join(r["child"] for r in results) + " | **Total** |"
    sep = "|---|" + "|".join(["--------:" for _ in results]) + "|--------:|"
    lines.append(header)
    lines.append(sep)

    def row(label, key, negate=False):
        vals = []
        for r in results:
            v = r[key]
            if negate and v > 0:
                vals.append(f"-{format_currency(v)}")
            else:
                vals.append(format_currency(v))
        total = sum(r[key] for r in results)
        total_str = f"-{format_currency(total)}" if negate and total > 0 else format_currency(total)
        return f"| {label} | " + " | ".join(vals) + f" | **{total_str}** |"

    lines.append(row("Weekly costs (camp + care + lunch)", "camp_fees"))
    lines.append(row("Registration", "registration"))
    lines.append(row("**Subtotal**", "subtotal"))

    total_sib = sum(r["sibling_discount"] for r in results)
    total_eb = sum(r["early_bird_discount"] for r in results)
    total_mw = sum(r["multi_week_discount"] for r in results)

    if total_sib > 0:
        lines.append(row("Sibling discount", "sibling_discount", negate=True))
    if total_eb > 0:
        lines.append(row("Early bird discount", "early_bird_discount", negate=True))
    if total_mw > 0:
        lines.append(row("Multi-week discount", "multi_week_discount", negate=True))
    lines.append(row("**Total**", "total"))
    lines.append("")

    # Weekly breakdown
    lines.append("## Weekly Breakdown\n")
    header = "| Week | Date | " + " | ".join(f"{n} | Cost" for n in child_names) + " | Week Total |"
    sep = "|---:|---:|" + "|".join(["---|---:" for _ in child_names]) + "|--------:|"
    lines.append(header)
    lines.append(sep)

    for w in weekly:
        week_total = sum(w.get(n, {}).get("cost", 0) for n in child_names)
        cells = []
        for n in child_names:
            info = w.get(n, {})
            cells.append(f" {info.get('provider', '-')} | {format_currency(info.get('cost', 0))}")
        lines.append(f"| {w['week']} | {w.get('start_date', '')} |{'|'.join(cells)}| **{format_currency(week_total)}** |")
    lines.append("")

    # Tax estimate
    lines.append("## Tax Recovery Estimate\n")
    for r in results:
        deductible = min(r["total"], 5000)  # conservative estimate
        estimated_savings = deductible * 0.25
        lines.append(f"- **{r['child']}**: {format_currency(r['total'])} eligible, ~{format_currency(estimated_savings)} estimated tax savings")
    lines.append("")

    # Budget check
    if budget_limit > 0:
        diff = grand_total - budget_limit
        status = "OVER" if diff > 0 else "UNDER"
        lines.append("## Budget Check\n")
        lines.append(f"- Budget limit: {format_currency(budget_limit)}")
        lines.append(f"- Projected total: {format_currency(grand_total)}")
        lines.append(f"- Status: **{format_currency(abs(diff))} {status} budget**")
        lines.append("")

    return "\n".join(lines)


def render_csv_simple(results, grand_total):
    """Render simple budget as CSV."""
    lines = ["Child,Camp Fees,Before/After Care,Lunch,Registration,Subtotal,Sibling Discount,Early Bird Discount,Total"]
    for r in results:
        lines.append(
            f"{r['child']},{r['camp_fees']},{r['before_after']},{r['lunch_cost']},"
            f"{r['registration']},{r['subtotal']},{r['sibling_discount']},"
            f"{r['early_bird_discount']},{r['total']}"
        )
    lines.append(f"TOTAL,,,,,,,, {grand_total}")
    return "\n".join(lines)


def render_csv_detailed(data):
    """Render detailed budget as CSV."""
    lines = ["Week,Start Date," + ",".join(f"{n} Provider,{n} Cost" for n in data["child_names"]) + ",Week Total"]
    for w in data["weekly_details"]:
        week_total = sum(w.get(n, {}).get("cost", 0) for n in data["child_names"])
        cells = []
        for n in data["child_names"]:
            info = w.get(n, {})
            cells.append(f"{info.get('provider', '')},{info.get('cost', 0)}")
        lines.append(f"{w['week']},{w.get('start_date', '')},{','.join(cells)},{week_total}")
    lines.append(f"\nSummary")
    for r in data["children"]:
        lines.append(f"{r['child']},Total:,{r['total']}")
    lines.append(f"Grand Total,,{data['grand_total']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Camp Budget Calculator")
    parser.add_argument("--input", "-i", help="JSON input file for detailed multi-provider budget")
    parser.add_argument("--kids", type=int, default=1, help="Number of children (simple mode)")
    parser.add_argument("--weeks", type=int, default=8, help="Number of camp weeks (weekly mode)")
    parser.add_argument("--base-cost", type=float, default=300, help="Base cost per week (weekly mode)")
    parser.add_argument("--before-care", type=float, default=0, help="Before-care cost per week")
    parser.add_argument("--after-care", type=float, default=0, help="After-care cost per week")
    parser.add_argument("--lunch", type=float, default=0, help="Lunch cost per week")
    parser.add_argument("--days", type=int, default=None, help="Number of camp days (daily mode, overrides --weeks)")
    parser.add_argument("--daily-rate", type=float, default=None, help="Base cost per day (daily mode, overrides --base-cost)")
    parser.add_argument("--before-care-daily", type=float, default=0, help="Before-care cost per day")
    parser.add_argument("--after-care-daily", type=float, default=0, help="After-care cost per day")
    parser.add_argument("--lunch-daily", type=float, default=0, help="Lunch cost per day")
    parser.add_argument("--sibling-discount", type=float, default=0, help="Sibling discount percentage")
    parser.add_argument("--early-bird", type=float, default=0, help="Early bird discount per week")
    parser.add_argument("--registration-fee", type=float, default=0, help="One-time registration fee per child")
    parser.add_argument("--budget-limit", type=float, default=0, help="Total budget limit")
    parser.add_argument("--format", choices=["markdown", "csv"], default="markdown", help="Output format")

    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            input_data = json.load(f)
        data = calculate_json_budget(input_data)
        if args.format == "markdown":
            print(render_markdown_detailed(data))
        else:
            print(render_csv_detailed(data))
    else:
        results, grand_total = calculate_simple_budget(args)
        if args.format == "markdown":
            print(render_markdown_simple(results, grand_total, args))
        else:
            print(render_csv_simple(results, grand_total))


if __name__ == "__main__":
    main()
