from datetime import date
from decimal import Decimal
import sqlite3
import tempfile
import unittest
from pathlib import Path

from steuerpilot.invoice import Invoice, InvoiceLine
from steuerpilot.ledger import (
    AccountKind,
    JournalEntry,
    JournalLine,
    LedgerError,
    LedgerStore,
)
from steuerpilot.money import from_cents, money, to_cents
from steuerpilot.vat import VatRate, VatRuleError, vat_from_gross, vat_from_net


AS_OF = date(2026, 1, 1)
RATE_19 = VatRate("TEST-19", Decimal("19"), AS_OF, approved=False)
RATE_7 = VatRate("TEST-7", Decimal("7"), AS_OF, approved=False)


class MoneyTests(unittest.TestCase):
    def test_half_up_rounding(self):
        self.assertEqual(money("1.005"), Decimal("1.01"))
        self.assertEqual(money("1.004"), Decimal("1.00"))

    def test_cents_round_trip(self):
        self.assertEqual(to_cents("123.45"), 12345)
        self.assertEqual(from_cents(12345), Decimal("123.45"))

    def test_rejects_boolean_and_non_finite(self):
        with self.assertRaises(ValueError):
            money(True)
        with self.assertRaises(ValueError):
            money("NaN")


class VatTests(unittest.TestCase):
    def test_standard_rate_net_to_gross_reference_case(self):
        result = vat_from_net("100.00", RATE_19)
        self.assertEqual((result.net, result.tax, result.gross),
                         (Decimal("100.00"), Decimal("19.00"), Decimal("119.00")))

    def test_gross_to_net_reference_case(self):
        result = vat_from_gross("119.00", RATE_19)
        self.assertEqual((result.net, result.tax, result.gross),
                         (Decimal("100.00"), Decimal("19.00"), Decimal("119.00")))

    def test_reduced_rate_arithmetic(self):
        result = vat_from_net("100.00", RATE_7)
        self.assertEqual(result.tax, Decimal("7.00"))
        self.assertEqual(result.gross, Decimal("107.00"))

    def test_zero_rate(self):
        zero = VatRate("ZERO", Decimal("0"), AS_OF)
        result = vat_from_net("100.00", zero)
        self.assertEqual(result.tax, Decimal("0.00"))
        self.assertEqual(result.gross, Decimal("100.00"))

    def test_rate_validity_and_approval_provenance(self):
        with self.assertRaises(VatRuleError):
            VatRate("BAD", Decimal("19"), date(2026, 2, 1), date(2026, 1, 1))
        with self.assertRaises(VatRuleError):
            VatRate("UNSOURCED", Decimal("19"), AS_OF, approved=True)


class InvoiceTests(unittest.TestCase):
    def test_invoice_totals_and_warnings(self):
        invoice = Invoice(
            invoice_number="TEST-2026-001",
            issue_date=AS_OF,
            seller_name="Example Seller GmbH",
            buyer_name="Example Buyer GmbH",
            lines=(InvoiceLine("Consulting", Decimal("2"), Decimal("50"), RATE_19),),
        )
        self.assertEqual(invoice.totals.net, Decimal("100.00"))
        self.assertEqual(invoice.totals.vat, Decimal("19.00"))
        self.assertEqual(invoice.totals.gross, Decimal("119.00"))
        self.assertTrue(invoice.structure_warnings())

    def test_rejects_empty_invoice_and_invalid_quantity(self):
        with self.assertRaises(ValueError):
            Invoice("", AS_OF, "Seller", "Buyer", ())
        with self.assertRaises(ValueError):
            InvoiceLine("Service", Decimal("0"), Decimal("10"), RATE_19)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "ledger.sqlite3"
        self.store = LedgerStore(self.db_path)
        self.store.add_organization("org-1", "Example Organisation")
        self.store.add_account("org-1", "1000", "Bank", AccountKind.ASSET)
        self.store.add_account("org-1", "8400", "Revenue", AccountKind.INCOME)
        self.store.add_account("org-1", "1776", "Output VAT", AccountKind.LIABILITY)

    def tearDown(self):
        self.store.close()
        self.temp_dir.cleanup()

    def entry(self, *, org="org-1", reference="INV-001"):
        return JournalEntry(
            organization_id=org,
            booking_date=AS_OF,
            description="Test customer invoice",
            source_reference=reference,
            lines=(
                JournalLine("1000", debit=Decimal("119.00")),
                JournalLine("8400", credit=Decimal("100.00")),
                JournalLine("1776", credit=Decimal("19.00")),
            ),
        )

    def test_posts_balanced_multi_line_entry(self):
        entry = self.entry()
        self.assertEqual(self.store.post(entry), entry.id)
        balances = {row.account_code: row for row in self.store.trial_balance("org-1", AS_OF, AS_OF)}
        self.assertEqual(balances["1000"].debit, Decimal("119.00"))
        self.assertEqual(balances["8400"].credit, Decimal("100.00"))
        self.assertEqual(balances["1776"].credit, Decimal("19.00"))
        self.assertEqual(sum((x.debit for x in balances.values()), Decimal("0.00")), Decimal("119.00"))
        self.assertEqual(sum((x.credit for x in balances.values()), Decimal("0.00")), Decimal("119.00"))

    def test_rejects_unbalanced_entry_before_writing(self):
        broken = JournalEntry(
            "org-1", AS_OF, "Broken", (
                JournalLine("1000", debit=Decimal("10")),
                JournalLine("8400", credit=Decimal("9")),
            ),
        )
        with self.assertRaises(LedgerError):
            self.store.post(broken)
        self.assertEqual(self.store.count_entries("org-1"), 0)

    def test_unknown_account_rolls_back_header_and_lines(self):
        broken = JournalEntry(
            "org-1", AS_OF, "Unknown account", (
                JournalLine("1000", debit=Decimal("10")),
                JournalLine("9999", credit=Decimal("10")),
            ),
        )
        with self.assertRaises(LedgerError):
            self.store.post(broken)
        self.assertEqual(self.store.count_entries("org-1"), 0)

    def test_duplicate_source_reference_is_rejected(self):
        self.store.post(self.entry())
        with self.assertRaises(LedgerError):
            self.store.post(self.entry())
        self.assertEqual(self.store.count_entries("org-1"), 1)

    def test_cross_organization_account_cannot_be_used(self):
        self.store.add_organization("org-2", "Other Organisation")
        foreign = JournalEntry(
            "org-2", AS_OF, "Cross tenant attempt", (
                JournalLine("1000", debit=Decimal("10")),
                JournalLine("8400", credit=Decimal("10")),
            ),
        )
        with self.assertRaises(LedgerError):
            self.store.post(foreign)
        self.assertEqual(self.store.count_entries("org-2"), 0)

    def test_reversal_is_a_new_balanced_entry_and_original_stays_visible(self):
        original = self.entry()
        self.store.post(original)
        reversal_id = self.store.reverse(original.id, date(2026, 1, 2), "Correction of test posting")
        self.assertEqual(self.store.get_entry_status(original.id), "reversed")
        self.assertEqual(self.store.get_entry_status(reversal_id), "posted")
        balances = self.store.trial_balance("org-1", AS_OF, date(2026, 1, 2))
        self.assertTrue(all(row.debit == row.credit for row in balances))
        self.assertTrue(all(row.net_debit == Decimal("0.00") for row in balances))

    def test_cannot_reverse_same_entry_twice(self):
        original = self.entry()
        self.store.post(original)
        self.store.reverse(original.id, date(2026, 1, 2), "First reversal")
        with self.assertRaises(LedgerError):
            self.store.reverse(original.id, date(2026, 1, 3), "Second reversal")
        self.assertEqual(self.store.count_entries("org-1"), 2)

    def test_posted_journal_lines_are_immutable(self):
        entry = self.entry()
        self.store.post(entry)
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._transaction() as conn:
                conn.execute("UPDATE journal_lines SET debit_cents = 1 WHERE entry_id = ?", (entry.id,))

    def test_trial_balance_date_range_is_validated(self):
        with self.assertRaises(LedgerError):
            self.store.trial_balance("org-1", date(2026, 2, 1), date(2026, 1, 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
