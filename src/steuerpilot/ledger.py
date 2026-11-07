"""Small, auditable double-entry ledger backed by SQLite.

This is an accounting-core prototype. It intentionally has no authentication,
period-close, German chart-of-accounts mapping, or GoBD certification.
"""
from __future__ import annotations

import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Iterator

from .money import from_cents, money, to_cents


class LedgerError(ValueError):
    """Raised when a ledger command violates a business or integrity rule."""


class AccountKind(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"


@dataclass(frozen=True, slots=True)
class JournalLine:
    account_code: str
    debit: Decimal = Decimal("0.00")
    credit: Decimal = Decimal("0.00")
    description: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "debit", money(self.debit))
        object.__setattr__(self, "credit", money(self.credit))
        if not self.account_code.strip():
            raise LedgerError("Account code is required")
        if self.debit < 0 or self.credit < 0:
            raise LedgerError("Debit and credit amounts cannot be negative")
        if (self.debit > 0) == (self.credit > 0):
            raise LedgerError("Each journal line must have exactly one positive side")


@dataclass(frozen=True, slots=True)
class JournalEntry:
    organization_id: str
    booking_date: date
    description: str
    lines: tuple[JournalLine, ...]
    source_reference: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def validate(self) -> None:
        if not self.organization_id.strip():
            raise LedgerError("Organization ID is required")
        if not self.description.strip():
            raise LedgerError("Journal description is required")
        if len(self.lines) < 2:
            raise LedgerError("A journal entry requires at least two lines")
        debit = sum((to_cents(line.debit) for line in self.lines), 0)
        credit = sum((to_cents(line.credit) for line in self.lines), 0)
        if debit == 0 or credit == 0:
            raise LedgerError("A journal entry must contain debit and credit values")
        if debit != credit:
            raise LedgerError(f"Journal entry is not balanced: debit={debit}, credit={credit}")


@dataclass(frozen=True, slots=True)
class AccountBalance:
    account_code: str
    account_name: str
    kind: AccountKind
    debit: Decimal
    credit: Decimal
    net_debit: Decimal


class LedgerStore:
    """SQLite ledger. Use a durable file path for data that must survive restarts."""

    def __init__(self, database: str | Path = "steuerpilot.sqlite3") -> None:
        self.database = str(database)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(self.database, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        if self.database != ":memory:":
            self._connection.execute("PRAGMA journal_mode = WAL")
        self._initialize()

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            try:
                self._connection.execute("BEGIN IMMEDIATE")
                yield self._connection
                self._connection.commit()
            except Exception:
                self._connection.rollback()
                raise

    def _initialize(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS organizations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL CHECK(length(trim(name)) > 0)
            );
            CREATE TABLE IF NOT EXISTS accounts (
                organization_id TEXT NOT NULL REFERENCES organizations(id),
                code TEXT NOT NULL,
                name TEXT NOT NULL CHECK(length(trim(name)) > 0),
                kind TEXT NOT NULL CHECK(kind IN ('asset','liability','equity','income','expense')),
                PRIMARY KEY (organization_id, code)
            );
            CREATE TABLE IF NOT EXISTS journal_entries (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL REFERENCES organizations(id),
                booking_date TEXT NOT NULL,
                description TEXT NOT NULL CHECK(length(trim(description)) > 0),
                source_reference TEXT,
                status TEXT NOT NULL CHECK(status IN ('posted','reversed')),
                reversal_of TEXT REFERENCES journal_entries(id),
                created_at TEXT NOT NULL,
                UNIQUE (organization_id, source_reference)
            );
            CREATE TABLE IF NOT EXISTS journal_lines (
                id TEXT PRIMARY KEY,
                entry_id TEXT NOT NULL REFERENCES journal_entries(id),
                organization_id TEXT NOT NULL,
                account_code TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                debit_cents INTEGER NOT NULL DEFAULT 0 CHECK(debit_cents >= 0),
                credit_cents INTEGER NOT NULL DEFAULT 0 CHECK(credit_cents >= 0),
                CHECK ((debit_cents > 0 AND credit_cents = 0) OR
                       (credit_cents > 0 AND debit_cents = 0)),
                FOREIGN KEY (organization_id, account_code)
                    REFERENCES accounts(organization_id, code)
            );
            CREATE INDEX IF NOT EXISTS idx_entries_org_date
                ON journal_entries(organization_id, booking_date);
            CREATE INDEX IF NOT EXISTS idx_lines_entry ON journal_lines(entry_id);
            CREATE TRIGGER IF NOT EXISTS immutable_posted_lines_update
            BEFORE UPDATE ON journal_lines
            WHEN (SELECT status FROM journal_entries WHERE id = OLD.entry_id) IN ('posted','reversed')
            BEGIN SELECT RAISE(ABORT, 'posted journal lines are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS immutable_posted_lines_delete
            BEFORE DELETE ON journal_lines
            WHEN (SELECT status FROM journal_entries WHERE id = OLD.entry_id) IN ('posted','reversed')
            BEGIN SELECT RAISE(ABORT, 'posted journal lines are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS immutable_posted_entry_delete
            BEFORE DELETE ON journal_entries
            WHEN OLD.status IN ('posted','reversed')
            BEGIN SELECT RAISE(ABORT, 'posted journal entries cannot be deleted'); END;
            CREATE TRIGGER IF NOT EXISTS immutable_posted_entry_fields
            BEFORE UPDATE OF organization_id, booking_date, description, source_reference, reversal_of
            ON journal_entries
            WHEN OLD.status IN ('posted','reversed')
            BEGIN SELECT RAISE(ABORT, 'posted journal entry fields are immutable'); END;
            """
        )

    def add_organization(self, organization_id: str, name: str) -> None:
        if not organization_id.strip() or not name.strip():
            raise LedgerError("Organization ID and name are required")
        try:
            with self._transaction() as conn:
                conn.execute(
                    "INSERT INTO organizations(id, name) VALUES (?, ?)",
                    (organization_id, name.strip()),
                )
        except sqlite3.IntegrityError as exc:
            raise LedgerError(f"Could not create organization: {exc}") from exc

    def add_account(self, organization_id: str, code: str, name: str, kind: AccountKind) -> None:
        if not code.strip() or not name.strip():
            raise LedgerError("Account code and name are required")
        try:
            with self._transaction() as conn:
                conn.execute(
                    "INSERT INTO accounts(organization_id, code, name, kind) VALUES (?, ?, ?, ?)",
                    (organization_id, code.strip(), name.strip(), kind.value),
                )
        except sqlite3.IntegrityError as exc:
            raise LedgerError(f"Could not create account: {exc}") from exc

    def post(self, entry: JournalEntry) -> str:
        entry.validate()
        created_at = datetime.now(timezone.utc).isoformat()
        try:
            with self._transaction() as conn:
                conn.execute(
                    """INSERT INTO journal_entries
                    (id, organization_id, booking_date, description, source_reference,
                     status, reversal_of, created_at)
                    VALUES (?, ?, ?, ?, ?, 'posted', NULL, ?)""",
                    (entry.id, entry.organization_id, entry.booking_date.isoformat(),
                     entry.description.strip(), entry.source_reference, created_at),
                )
                for line in entry.lines:
                    conn.execute(
                        """INSERT INTO journal_lines
                        (id, entry_id, organization_id, account_code, description,
                         debit_cents, credit_cents)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (str(uuid.uuid4()), entry.id, entry.organization_id,
                         line.account_code, line.description,
                         to_cents(line.debit), to_cents(line.credit)),
                    )
            return entry.id
        except sqlite3.IntegrityError as exc:
            raise LedgerError(f"Posting failed; no partial entry was saved: {exc}") from exc

    def reverse(self, entry_id: str, reversal_date: date, reason: str) -> str:
        if not reason.strip():
            raise LedgerError("A reversal reason is required")
        reversal_id = str(uuid.uuid4())
        try:
            with self._transaction() as conn:
                original = conn.execute(
                    "SELECT * FROM journal_entries WHERE id = ?", (entry_id,)
                ).fetchone()
                if original is None:
                    raise LedgerError("Journal entry was not found")
                if original["status"] != "posted":
                    raise LedgerError("Only a currently posted entry can be reversed")
                lines = conn.execute(
                    "SELECT * FROM journal_lines WHERE entry_id = ? ORDER BY rowid", (entry_id,)
                ).fetchall()
                conn.execute(
                    "UPDATE journal_entries SET status = 'reversed' WHERE id = ?", (entry_id,)
                )
                conn.execute(
                    """INSERT INTO journal_entries
                    (id, organization_id, booking_date, description, source_reference,
                     status, reversal_of, created_at)
                    VALUES (?, ?, ?, ?, ?, 'posted', ?, ?)""",
                    (reversal_id, original["organization_id"], reversal_date.isoformat(),
                     f"Reversal of {entry_id}: {reason.strip()}", f"REV:{entry_id}",
                     entry_id, datetime.now(timezone.utc).isoformat()),
                )
                for line in lines:
                    conn.execute(
                        """INSERT INTO journal_lines
                        (id, entry_id, organization_id, account_code, description,
                         debit_cents, credit_cents)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (str(uuid.uuid4()), reversal_id, line["organization_id"],
                         line["account_code"], f"Reversal: {line['description']}",
                         line["credit_cents"], line["debit_cents"]),
                    )
            return reversal_id
        except sqlite3.IntegrityError as exc:
            raise LedgerError(f"Reversal failed; transaction rolled back: {exc}") from exc

    def trial_balance(
        self, organization_id: str, start_date: date, end_date: date
    ) -> tuple[AccountBalance, ...]:
        if end_date < start_date:
            raise LedgerError("End date cannot be before start date")
        with self._lock:
            rows = self._connection.execute(
                """SELECT a.code, a.name, a.kind,
                          COALESCE(SUM(l.debit_cents), 0) AS debit_cents,
                          COALESCE(SUM(l.credit_cents), 0) AS credit_cents
                   FROM accounts a
                   LEFT JOIN journal_lines l
                     ON l.organization_id = a.organization_id
                    AND l.account_code = a.code
                   LEFT JOIN journal_entries e
                     ON e.id = l.entry_id
                    AND e.status IN ('posted', 'reversed')
                    AND e.booking_date BETWEEN ? AND ?
                   WHERE a.organization_id = ?
                     AND (l.id IS NULL OR e.id IS NOT NULL)
                   GROUP BY a.code, a.name, a.kind
                   ORDER BY a.code""",
                (start_date.isoformat(), end_date.isoformat(), organization_id),
            ).fetchall()
        return tuple(
            AccountBalance(
                account_code=row["code"],
                account_name=row["name"],
                kind=AccountKind(row["kind"]),
                debit=from_cents(row["debit_cents"]),
                credit=from_cents(row["credit_cents"]),
                net_debit=from_cents(row["debit_cents"] - row["credit_cents"]),
            )
            for row in rows
        )

    def get_entry_status(self, entry_id: str) -> str | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT status FROM journal_entries WHERE id = ?", (entry_id,)
            ).fetchone()
        return None if row is None else str(row["status"])

    def count_entries(self, organization_id: str) -> int:
        with self._lock:
            row = self._connection.execute(
                "SELECT COUNT(*) AS count FROM journal_entries WHERE organization_id = ?",
                (organization_id,),
            ).fetchone()
        return int(row["count"])
