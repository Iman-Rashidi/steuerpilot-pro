"""Invoice structure and arithmetic checks.

Passing these checks does not establish compliance with German invoice law.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .money import as_decimal, money
from .vat import VatBreakdown, VatRate, vat_from_net


class InvoiceValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class InvoiceLine:
    description: str
    quantity: Decimal
    unit_net: Decimal
    vat_rate: VatRate

    def __post_init__(self) -> None:
        object.__setattr__(self, "quantity", as_decimal(self.quantity))
        object.__setattr__(self, "unit_net", money(self.unit_net))
        if not self.description.strip():
            raise InvoiceValidationError("Invoice line description is required")
        if not self.quantity.is_finite() or self.quantity <= 0:
            raise InvoiceValidationError("Invoice line quantity must be positive")
        if self.unit_net < 0:
            raise InvoiceValidationError("Unit net price cannot be negative")

    @property
    def amounts(self) -> VatBreakdown:
        return vat_from_net(money(self.quantity * self.unit_net), self.vat_rate)


@dataclass(frozen=True, slots=True)
class InvoiceTotals:
    net: Decimal
    vat: Decimal
    gross: Decimal


@dataclass(frozen=True, slots=True)
class Invoice:
    invoice_number: str
    issue_date: date
    seller_name: str
    buyer_name: str
    lines: tuple[InvoiceLine, ...]
    supply_date: date | None = None

    def __post_init__(self) -> None:
        if not self.invoice_number.strip():
            raise InvoiceValidationError("Invoice number is required")
        if not self.seller_name.strip() or not self.buyer_name.strip():
            raise InvoiceValidationError("Seller and buyer names are required")
        if not self.lines:
            raise InvoiceValidationError("At least one invoice line is required")
        for line in self.lines:
            if not line.vat_rate.applies_on(self.issue_date):
                raise InvoiceValidationError(
                    f"VAT rate {line.vat_rate.code} is not valid on issue date"
                )

    @property
    def totals(self) -> InvoiceTotals:
        net = money(sum((line.amounts.net for line in self.lines), Decimal("0.00")))
        vat = money(sum((line.amounts.tax for line in self.lines), Decimal("0.00")))
        return InvoiceTotals(net=net, vat=vat, gross=money(net + vat))

    def structure_warnings(self) -> tuple[str, ...]:
        """Return review prompts; never label these checks as legal clearance."""
        warnings: list[str] = []
        if self.supply_date is None:
            warnings.append("Supply date has not been recorded")
        if any(not line.vat_rate.approved for line in self.lines):
            warnings.append("One or more VAT rates have not been formally approved")
        return tuple(warnings)
