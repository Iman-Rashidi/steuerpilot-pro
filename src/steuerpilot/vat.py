"""Versionable VAT arithmetic primitives, not a legal tax-rate catalogue."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .money import as_decimal, money


class VatRuleError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class VatRate:
    """A rate with an explicit effective period and review provenance.

    Rates are supplied by the caller. The package deliberately does not infer
    legal eligibility from the percentage alone.
    """

    code: str
    percent: Decimal
    valid_from: date
    valid_to: date | None = None
    source_url: str | None = None
    reviewed_by: str | None = None
    approved: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "percent", as_decimal(self.percent))
        if not self.code.strip():
            raise VatRuleError("VAT rate code is required")
        if not self.percent.is_finite() or self.percent < 0 or self.percent > 100:
            raise VatRuleError("VAT percent must be between 0 and 100")
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise VatRuleError("VAT rate validity period is inverted")
        if self.approved and (not self.source_url or not self.reviewed_by):
            raise VatRuleError("Approved VAT rates require a source URL and reviewer")

    def applies_on(self, on_date: date) -> bool:
        return self.valid_from <= on_date and (self.valid_to is None or on_date <= self.valid_to)


@dataclass(frozen=True, slots=True)
class VatBreakdown:
    net: Decimal
    tax: Decimal
    gross: Decimal
    rate_percent: Decimal
    rate_code: str


def vat_from_net(net: Decimal | str | int, rate: VatRate) -> VatBreakdown:
    net_amount = money(net)
    tax_amount = money(net_amount * rate.percent / Decimal(100))
    return VatBreakdown(
        net=net_amount,
        tax=tax_amount,
        gross=money(net_amount + tax_amount),
        rate_percent=rate.percent,
        rate_code=rate.code,
    )


def vat_from_gross(gross: Decimal | str | int, rate: VatRate) -> VatBreakdown:
    gross_amount = money(gross)
    denominator = Decimal(100) + rate.percent
    if denominator == 0:
        raise VatRuleError("VAT denominator cannot be zero")
    tax_amount = money(gross_amount * rate.percent / denominator)
    return VatBreakdown(
        net=money(gross_amount - tax_amount),
        tax=tax_amount,
        gross=gross_amount,
        rate_percent=rate.percent,
        rate_code=rate.code,
    )
