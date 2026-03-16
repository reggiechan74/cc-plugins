"""Markdown rendering functions for annual schedule generation."""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from rate_resolver import resolve_period_rate


def _group_into_sections(annual_days):
    """Group annual days into sections for markdown rendering.

    Summer is one big section. PA days and school holidays are individual sections.
    Winter break, March break, and fall break are each one section.
    """
    sections = []

    # Collect by period
    summer_days = [d for d in annual_days if d["period"] == "summer"]
    pa_days = [d for d in annual_days if d["period"] == "pa_day"]
    winter_days = [d for d in annual_days if d["period"] == "winter_break"]
    march_days = [d for d in annual_days if d["period"] == "march_break"]
    school_holiday_days = [d for d in annual_days if d["period"] == "school_holiday"]
    fall_break_days = [d for d in annual_days if d["period"] == "fall_break"]

    # Summer section
    if summer_days:
        first = summer_days[0]["date"]
        last = summer_days[-1]["date"]
        sections.append({
            "period": "summer",
            "period_key": "summer",
            "title": f"Summer {first.year} ({first.strftime('%b %d')} - {last.strftime('%b %d')})",
            "summary_title": f"Summer {first.year}",
            "subtotal_label": "Summer",
            "days": summer_days,
        })

    # PA days - each as its own section
    for pa in pa_days:
        d = pa["date"]
        sections.append({
            "period": "pa_day",
            "period_key": "pa_days",
            "title": f"PA Day: {d.strftime('%b %d, %Y')}",
            "summary_title": "PA Days",
            "subtotal_label": "PA Day",
            "days": [pa],
        })

    # Winter break
    if winter_days:
        first = winter_days[0]["date"]
        last = winter_days[-1]["date"]
        year_label = f"{first.year}-{last.year}" if first.year != last.year else str(first.year)
        sections.append({
            "period": "winter_break",
            "period_key": "winter_break",
            "title": f"Winter Break {year_label} ({first.strftime('%b %d')} - {last.strftime('%b %d')})",
            "summary_title": "Winter Break",
            "subtotal_label": "Winter Break",
            "days": winter_days,
        })

    # March break
    if march_days:
        first = march_days[0]["date"]
        last = march_days[-1]["date"]
        sections.append({
            "period": "march_break",
            "period_key": "march_break",
            "title": f"March Break {first.year} ({first.strftime('%b %d')}-{last.strftime('%b %d')})",
            "summary_title": "March Break",
            "subtotal_label": "March Break",
            "days": march_days,
        })

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

    # Sort sections chronologically by first day
    sections.sort(key=lambda s: s["days"][0]["date"])
    return sections


def render_markdown(annual_days, provider_rates, children, render_context=None):
    """Render the annual schedule as markdown matching the sample format."""
    render_context = render_context or {}
    lines = []

    # Determine school year span
    dates = [d["date"] for d in annual_days]
    first_year = min(dates).year
    last_year = max(dates).year
    year_label = f"{first_year}-{last_year}" if first_year != last_year else str(first_year)

    lines.append(f"# {year_label} Annual Camp Schedule\n")
    lines.append(f"**Children**: {' & '.join(children)}")
    lines.append(f"**Generated**: {date.today().isoformat()}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Group days by period sections
    sections = _group_into_sections(annual_days)

    period_totals = {}  # {period_key: {child: cost, days: count}}

    for section in sections:
        period = section["period"]
        section_days = section["days"]
        title = section["title"]
        count = len(section_days)

        lines.append(f"## {title}")
        lines.append("")

        # Period description
        if period == "summer":
            week_nums = set()
            for d in section_days:
                week_nums.add(d["period_label"].replace("Summer Wk ", ""))
            total_weeks = len(week_nums) if week_nums else count // 5
            lines.append(f"{total_weeks} full weeks, {count} weekdays")
            lines.append("")
        elif period == "winter_break":
            lines.append(f"{count} camp-eligible weekdays (Dec 25-26 Christmas/Boxing Day and Jan 1 New Year's are stat holidays)")
            lines.append("")
        elif period == "march_break":
            lines.append(f"{count} weekdays")
            lines.append("")
        elif period == "fall_break":
            lines.append(f"{count} weekdays")
            lines.append("")

        # Table header
        child_headers = []
        for child in children:
            child_headers.extend([f"{child}'s Camp", f"{child} Cost"])
        header = "| Date | Day | " + " | ".join(child_headers) + " | Daily Total | Notes |"
        sep = "|------|-----|" + "|".join(["-------------|----------" for _ in children]) + "|-------------|-------|"
        lines.append(header)
        lines.append(sep)

        section_child_totals = {child: 0 for child in children}
        section_total = 0

        for day in section_days:
            d = day["date"]
            cells = [d.isoformat(), day["day_name"]]
            daily_total = 0
            for child in children:
                camp = day["assignments"].get(child, "")
                camp_rates = provider_rates.get(camp, {})
                resolved = resolve_period_rate(camp_rates, day["period"]) if camp_rates.get("summer") else camp_rates
                rate = resolved.get("total", 0) if isinstance(resolved, dict) else 0
                cells.extend([camp, f"${rate:.2f}"])
                section_child_totals[child] += rate
                daily_total += rate
            cells.extend([f"${round(daily_total, 2):.2f}", day["notes"]])
            lines.append("| " + " | ".join(str(c) for c in cells) + " |")
            section_total += daily_total

        lines.append("")

        # Subtotals for multi-day periods
        period_key = section["period_key"]
        if period_key not in period_totals:
            period_totals[period_key] = {
                "period": period,
                "title": section["summary_title"],
                "days": 0,
                **{child: 0 for child in children},
                "combined": 0,
            }
        period_totals[period_key]["days"] += count
        for child in children:
            period_totals[period_key][child] += section_child_totals[child]
        period_totals[period_key]["combined"] += section_total

        if count > 1:
            parts = []
            for child in children:
                parts.append(f"{child} ${round(section_child_totals[child], 2):,.2f}")
            parts.append(f"Combined ${round(section_total, 2):,.2f}")
            lines.append(f"**{section['subtotal_label']} subtotal**: " + " | ".join(parts))
            lines.append("")

        lines.append("---")
        lines.append("")

    # Annual summary table
    lines.append("## Annual Summary")
    lines.append("")
    child_headers = [f"{child} Total" for child in children]
    header = "| Period | Days | " + " | ".join(child_headers) + " | Combined |"
    sep = "|--------|------|" + "|".join(["----------" for _ in children]) + "|----------|"
    lines.append(header)
    lines.append(sep)

    grand_days = 0
    grand_child_totals = {child: 0 for child in children}
    grand_total = 0

    # Summarize by period type
    summary_order = ["summer", "pa_day", "school_holiday", "fall_break", "winter_break", "march_break"]
    summary_labels = {
        "summer": "Summer {year}",
        "pa_day": "PA Days ({count})",
        "school_holiday": "School Holidays ({count})",
        "fall_break": "Fall Break",
        "winter_break": "Winter Break",
        "march_break": "March Break",
    }

    for period_type in summary_order:
        # Aggregate all sections of this type
        days_count = 0
        child_sums = {child: 0 for child in children}
        combined = 0
        for pk, pt in period_totals.items():
            if pt["period"] == period_type:
                days_count += pt["days"]
                for child in children:
                    child_sums[child] += pt[child]
                combined += pt["combined"]
        if days_count == 0:
            continue

        label = summary_labels[period_type]
        if "{year}" in label:
            label = label.format(year=first_year)
        if "{count}" in label:
            label = label.format(count=days_count)

        child_cells = [f"${round(child_sums[child], 2):,.2f}" for child in children]
        lines.append(f"| {label} | {days_count} | " + " | ".join(child_cells) + f" | ${round(combined, 2):,.2f} |")

        grand_days += days_count
        for child in children:
            grand_child_totals[child] += child_sums[child]
        grand_total += combined

    # Total row
    child_cells = [f"**${round(grand_child_totals[child], 2):,.2f}**" for child in children]
    lines.append(f"| **Annual Total** | **{grand_days}** | " + " | ".join(child_cells) + f" | **${round(grand_total, 2):,.2f}** |")
    lines.append("")

    # Cost notes -- dynamically reference actual providers and rates
    lines.append("### Cost Notes")
    lines.append("")
    lines.append("- Summer costs include daily camp fee + before care + after care + lunch (from Provider Comparison rates)")

    # Use actual provider args and rates (passed in via render context)
    pa_prov = render_context.get("pa_provider", "")
    break_prov = render_context.get("break_provider", "")
    pa_resolved = resolve_period_rate(provider_rates.get(pa_prov, {}), "pa_day")
    pa_rate = pa_resolved.get("total", 0) if isinstance(pa_resolved, dict) else 0
    break_resolved = resolve_period_rate(provider_rates.get(break_prov, {}), "winter_break")
    break_rate = break_resolved.get("total", 0) if isinstance(break_resolved, dict) else 0
    has_overrides = render_context.get("has_overrides", False)
    if has_overrides:
        lines.append(f"- PA day default: {pa_prov} (${pa_rate}/day); per-child overrides applied where specified")
        lines.append(f"- Break default: {break_prov} (${break_rate}/day); per-child overrides applied where specified")
    else:
        lines.append(f"- PA day costs use {pa_prov} rates (${pa_rate}/day all-in)")
        lines.append(f"- Winter and March Break use {break_prov} rates (${break_rate}/day all-in)")
    lines.append("- Costs shown are pre-discount; apply sibling/early-bird discounts to reduce totals")

    # List provider rates
    rate_parts = []
    for name, prates in sorted(provider_rates.items()):
        summer_total = prates.get("summer", prates).get("total", prates.get("total", 0)) if isinstance(prates.get("summer", prates), dict) else prates.get("total", 0)
        rate_parts.append(f"{name} ${summer_total}/day")
    lines.append(f"- Daily rates (summer): {', '.join(rate_parts)}")
    # Note about per-period rates
    has_period_rates = any(
        r.get("pa_day") is not None or r.get("break") is not None
        for r in provider_rates.values()
        if isinstance(r, dict)
    )
    if has_period_rates:
        lines.append("- Per-period rates applied where available (PA Day, Break); falls back to summer rates when not set")
    else:
        lines.append("- Non-summer rates are assumed equal to summer rates from Provider Comparison; confirm actual PA day and break program pricing with providers")
    lines.append("- Dates flagged VERIFY may be statutory/civic holidays when camps are closed")
    lines.append("")

    return "\n".join(lines)
