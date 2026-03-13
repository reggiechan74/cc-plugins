"""Lightweight unit algebra for dimensional consistency checks.

Supports base units (hours, headcount, dollars, points, dimensionless) and
compound units formed by multiplication and division. Not a full physical
units library — a tag system sufficient to catch common errors.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Unit:
    """A unit represented as a fraction: numer / denom (sorted tuples)."""
    numer: tuple[str, ...]
    denom: tuple[str, ...]

    def __str__(self) -> str:
        if not self.numer and not self.denom:
            return "dimensionless"
        n = "*".join(self.numer) if self.numer else "1"
        if not self.denom:
            return n
        d = "*".join(self.denom)
        return f"{n}/{d}"


def parse_unit(spec: str) -> Unit:
    """Parse a unit string like 'hours', 'hours/headcount', or 'dimensionless'."""
    spec = spec.strip()
    if spec == "dimensionless":
        return Unit(numer=(), denom=())
    if "/" in spec:
        numer_str, denom_str = spec.split("/", 1)
        numer = tuple(sorted(numer_str.strip().split("*")))
        denom = tuple(sorted(denom_str.strip().split("*")))
        return Unit(numer=numer, denom=denom)
    return Unit(numer=(spec,), denom=())


def units_compatible(a: Unit, b: Unit) -> bool:
    """Check if two units are compatible (i.e., identical after normalization)."""
    return a == b


def _cancel(numer: list[str], denom: list[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Cancel matching terms between numerator and denominator."""
    n = list(numer)
    d = list(denom)
    for term in list(n):
        if term in d:
            n.remove(term)
            d.remove(term)
    return tuple(sorted(n)), tuple(sorted(d))


def units_multiply(a: Unit, b: Unit) -> Unit:
    """Multiply two units: (a.numer * b.numer) / (a.denom * b.denom), with cancellation."""
    numer = list(a.numer) + list(b.numer)
    denom = list(a.denom) + list(b.denom)
    n, d = _cancel(numer, denom)
    return Unit(numer=n, denom=d)


def units_divide(a: Unit, b: Unit) -> Unit:
    """Divide units: a / b = a * (1/b)."""
    flipped = Unit(numer=b.denom, denom=b.numer)
    return units_multiply(a, flipped)
