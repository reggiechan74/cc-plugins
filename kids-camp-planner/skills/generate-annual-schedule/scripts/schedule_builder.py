"""Schedule building functions for annual schedule generation."""

import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from calendar_parser import get_weekdays_between, get_summer_holidays, find_civic_holiday, parse_date_flexible
from rate_resolver import _resolve_assignments


def build_annual_days(summer_days, calendar_data, pa_provider, break_provider,
                      children, overrides=None, fall_break_provider=None):
    """Combine summer + non-summer into a unified list of annual days.

    Args:
        overrides: dict of {"YYYY-MM-DD": {"ChildName": "Provider"}}
            Per-child, per-date provider overrides. For summer days, overrides
            replace the spreadsheet assignment. For non-summer days, overrides
            replace the period default. Any child not listed for a date falls
            back to the period default (or spreadsheet value for summer).

    Returns list of dicts sorted by date:
    [{date, day_name, period, period_label, assignments: {child: camp}, notes}]
    """
    overrides = overrides or {}
    all_days = []
    seen_dates = set()  # Track dates to prevent double-counting

    # Summer days (from spreadsheet, with optional overrides)
    summer_holidays = get_summer_holidays(summer_days[0]["date"].year) if summer_days else {}
    for sd in summer_days:
        d = sd["date"]
        d_iso = d.isoformat()
        week = sd["week"]
        notes = f"Week {week}" if d.weekday() == 0 else ""
        # Flag summer statutory/civic holidays
        if d in summer_holidays:
            holiday_name = summer_holidays[d]
            notes = f"{holiday_name} -- VERIFY camp open" + (f" ({notes})" if notes else "")
        # Apply overrides on top of spreadsheet assignments
        assignments = dict(sd["assignments"])
        if d_iso in overrides:
            for child in children:
                if child in overrides[d_iso]:
                    assignments[child] = overrides[d_iso][child]
        all_days.append({
            "date": d,
            "day_name": d.strftime("%a"),
            "period": "summer",
            "period_label": f"Summer Wk {week}",
            "assignments": assignments,
            "notes": notes,
        })
        seen_dates.add(d)

    # PA days (skip if date already covered by another period)
    for i, pa in enumerate(calendar_data["pa_days"], 1):
        d = parse_date_flexible(pa["date_str"])
        if d in seen_dates:
            print(f"  Warning: PA Day {d.isoformat()} overlaps with another period, skipping", file=sys.stderr)
            continue
        purpose = pa.get("purpose", "")
        all_days.append({
            "date": d,
            "day_name": d.strftime("%a"),
            "period": "pa_day",
            "period_label": "PA Day",
            "assignments": _resolve_assignments(d, children, pa_provider, overrides),
            "notes": f"PA Day {i}" + (f" - {purpose}" if purpose else ""),
        })
        seen_dates.add(d)

    # Winter break (skip dates already covered)
    if calendar_data["winter_break"]:
        wb_start = parse_date_flexible(calendar_data["winter_break"]["start_str"])
        wb_end = parse_date_flexible(calendar_data["winter_break"]["end_str"])
        # Exclude stat holidays: Dec 25 (Christmas), Dec 26 (Boxing Day), Jan 1 (New Year's)
        stat_holidays = set()
        for year in [wb_start.year, wb_end.year]:
            stat_holidays.add(date(year, 12, 25))
            stat_holidays.add(date(year, 12, 26))
            stat_holidays.add(date(year, 1, 1))
        winter_days = get_weekdays_between(wb_start, wb_end, exclude_dates=stat_holidays)
        for d in winter_days:
            if d in seen_dates:
                continue
            notes = ""
            if d.month == 12 and d.day == 24:
                notes = "Christmas Eve -- VERIFY camp open"
            elif d.month == 12 and d.day == 31:
                notes = "New Year's Eve -- VERIFY camp open"
            all_days.append({
                "date": d,
                "day_name": d.strftime("%a"),
                "period": "winter_break",
                "period_label": "Winter Break",
                "assignments": _resolve_assignments(d, children, break_provider, overrides),
                "notes": notes,
            })
            seen_dates.add(d)

    # March break (skip dates already covered)
    if calendar_data["march_break"]:
        mb_start = parse_date_flexible(calendar_data["march_break"]["start_str"])
        mb_end = parse_date_flexible(calendar_data["march_break"]["end_str"])
        march_days = get_weekdays_between(mb_start, mb_end)
        for d in march_days:
            if d in seen_dates:
                continue
            all_days.append({
                "date": d,
                "day_name": d.strftime("%a"),
                "period": "march_break",
                "period_label": "March Break",
                "assignments": _resolve_assignments(d, children, break_provider, overrides),
                "notes": "",
            })
            seen_dates.add(d)

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

    all_days.sort(key=lambda x: x["date"])
    return all_days


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

    # Summer days (same for all children)
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

    # PA days — merge across all calendars
    all_pa_dates = {}
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
        for child in children:
            if child in children_off:
                d_iso = d.isoformat()
                day_overrides = overrides.get(d_iso, {})
                assignments[child] = day_overrides.get(child, pa_provider)
            else:
                assignments[child] = "In school"
        if len(children_off) < len(children):
            off_names = [c for c in children if c in children_off]
            notes = f"PA Day {pa_counter} ({', '.join(off_names)} off)"
        else:
            purpose = next(iter(children_off.values()), "")
            notes = f"PA Day {pa_counter}" + (f" - {purpose}" if purpose else "")
        all_days.append({
            "date": d, "day_name": d.strftime("%a"), "period": "pa_day",
            "period_label": "PA Day", "assignments": assignments, "notes": notes,
        })
        seen_dates.add(d)

    # School holidays — merge across all calendars
    all_holiday_dates = {}
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

    # Winter break — union of all calendars
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

    # March break — union pattern
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
