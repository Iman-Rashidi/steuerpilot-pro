from datetime import date
from decimal import Decimal
import sqlite3
import tempfile
import unittest
from pathlib import Path

from steuerpilot.controls import LedgerControls
from steuerpilot.ledger import AccountKind, JournalEntry, JournalLine, LedgerError, LedgerStore


class LedgerControlsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = LedgerStore(Path(self.temp_dir.name) / "ledger.sqlite3")
        self.store.add_organization("org-1", "Synthetic test organisation")
        self.store.add_account("org-1", "1000", "Bank", AccountKind.ASSET)
        self.store.add_account("org-1", "8400", "Revenue", AccountKind.INCOME)
        self.controls = LedgerControls(self.store)

    def tearDown(self):
        self.store.close()
        self.temp_dir.cleanup()

    def entry(self, booking_date=date(2026, 1, 10), ref="TEST-001"):
        return JournalEntry(
            "org-1", booking_date, "Synthetic test posting", (
                JournalLine("1000", debit=Decimal("10.00")),
                JournalLine("8400", credit=Decimal("10.00")),
            ), source_reference=ref,
        )

    def test_closed_period_blocks_postings_at_database_level(self):
        self.controls.close_period("org-1", date(2026, 1, 1), date(2026, 1, 31), "Month end")
        with self.assertRaises(LedgerError):
            self.store.post(self.entry())
        self.assertEqual(self.store.count_entries("org-1"), 0)
        self.store.post(self.entry(date(2026, 2, 1), "FEB-001"))
        self.assertEqual(self.store.count_entries("org-1"), 1)

    def test_overlapping_periods_are_rejected(self):
        self.controls.close_period("org-1", date(2026, 1, 1), date(2026, 1, 31), "January")
        with self.assertRaises(LedgerError):
            self.controls.close_period("org-1", date(2026, 1, 15), date(2026, 2, 15), "Overlap")

    def test_posting_and_reversal_events_are_transactional(self):
        entry = self.entry()
        self.store.post(entry)
        self.assertEqual(
            [event["event_type"] for event in self.controls.audit_events("org-1", entry.id)],
            ["journal_entry_posted"],
        )
        reversal_id = self.store.reverse(entry.id, date(2026, 1, 11), "Correction")
        self.assertEqual(
            [event["event_type"] for event in self.controls.audit_events("org-1", entry.id)],
            ["journal_entry_posted", "journal_entry_reversed"],
        )
        self.assertEqual(
            [event["event_type"] for event in self.controls.audit_events("org-1", reversal_id)],
            ["journal_entry_posted"],
        )

    def test_audit_events_are_append_only(self):
        entry = self.entry()
        self.store.post(entry)
        event = self.controls.audit_events("org-1", entry.id)[0]
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._transaction() as conn:
                conn.execute("UPDATE audit_events SET event_type = 'edited' WHERE id = ?", (event["id"],))
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._transaction() as conn:
                conn.execute("DELETE FROM audit_events WHERE id = ?", (event["id"],))

    def test_reversal_into_closed_period_rolls_back_original_status(self):
        entry = self.entry()
        self.store.post(entry)
        self.controls.close_period("org-1", date(2026, 1, 11), date(2026, 1, 31), "Close reversal dates")
        with self.assertRaises(LedgerError):
            self.store.reverse(entry.id, date(2026, 1, 12), "Blocked reversal")
        self.assertEqual(self.store.get_entry_status(entry.id), "posted")
        self.assertEqual(self.store.count_entries("org-1"), 1)
        events = self.controls.audit_events("org-1", entry.id)
        self.assertEqual([event["event_type"] for event in events], ["journal_entry_posted"])

    def test_period_close_is_audited_and_period_is_immutable(self):
        period_id = self.controls.close_period(
            "org-1", date(2026, 1, 1), date(2026, 1, 31), "Month-end close"
        )
        self.assertEqual(
            [event["event_type"] for event in self.controls.audit_events("org-1", period_id)],
            ["period_closed"],
        )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._transaction() as conn:
                conn.execute("DELETE FROM accounting_periods WHERE id = ?", (period_id,))

    def test_failed_posting_does_not_leave_an_audit_event(self):
        broken = JournalEntry(
            "org-1", date(2026, 1, 10), "Unbalanced", (
                JournalLine("1000", debit=Decimal("10")),
                JournalLine("8400", credit=Decimal("9")),
            ), source_reference="BAD-001",
        )
        with self.assertRaises(LedgerError):
            self.store.post(broken)
        self.assertEqual(self.controls.audit_events("org-1", broken.id), ())


if __name__ == "__main__":
    unittest.main(verbosity=2)
