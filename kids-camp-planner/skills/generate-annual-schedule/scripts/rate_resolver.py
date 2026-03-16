"""Rate resolution functions for annual schedule generation."""

import os
import sys


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


def _read_rate_block(row, start_col):
    """Read a 4-column rate block (daily, before, after, lunch).

    Returns dict with {daily, before, after, lunch, total} or None if all empty.
    Non-numeric cell values are treated as empty.
    """
    def _num(col_idx):
        if len(row) <= col_idx:
            return None
        v = row[col_idx].value
        return v if isinstance(v, (int, float)) else None

    daily = _num(start_col)
    before = _num(start_col + 1)
    after = _num(start_col + 2)
    lunch = _num(start_col + 3)

    if all(v is None or v == 0 for v in [daily, before, after, lunch]):
        return None

    daily = daily or 0
    before = before or 0
    after = after or 0
    lunch = lunch or 0
    return {"daily": daily, "before": before, "after": after, "lunch": lunch,
            "total": round(daily + before + after + lunch, 2)}


def _resolve_assignments(d, children, default_provider, overrides):
    """Resolve per-child provider for a given date.

    For each child, checks the overrides dict for a date-specific provider.
    Falls back to default_provider if no override exists for that child+date.
    """
    d_iso = d.isoformat()
    day_overrides = overrides.get(d_iso, {})
    return {child: day_overrides.get(child, default_provider) for child in children}
