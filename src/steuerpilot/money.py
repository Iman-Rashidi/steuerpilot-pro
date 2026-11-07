"""Decimal-safe EUR money helpers.

The accounting core stores amounts as integer euro cents in SQLite. Decimal is
used at the application boundary; binary floating-point is never used for math.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import SupportsInt

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


class MoneyError(ValueError):
    """Raised when a value cannot be represented as money."""


def as_decimal(value: Decimal | str | int | float) -> Decimal:
    if isinstance(value, bool):
        raise MoneyError("Boolean values are not valid monetary amounts")
    try:
        # str(float) avoids importing the float's full binary expansion.
        return value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise MoneyError(f"Invalid decimal amount: {value!r}") from exc


def money(value: Decimal | str | int | float) -> Decimal:
    """Quantize to cents using commercial half-up rounding."""
    amount = as_decimal(value)
    if not amount.is_finite():
        raise MoneyError("Monetary amounts must be finite")
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def to_cents(value: Decimal | str | int | float) -> int:
    return int(money(value) * 100)


def from_cents(value: int | SupportsInt) -> Decimal:
    if isinstance(value, bool):
        raise MoneyError("Boolean values are not valid cents")
    return (Decimal(int(value)) / Decimal(100)).quantize(CENT)
