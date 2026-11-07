"""Database-enforced period locks and append-only technical events.

Instantiate LedgerControls(store) immediately after LedgerStore. The extension
shares the same SQLite connection and transaction boundary as the ledger.

This is a technical integrity control, not a certified GoBD audit trail.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import date, datetime, timezone
from typing import Any

from .ledger import LedgerError, LedgerStore


class LedgerControls:
    """Install and query database-enforced period and history controls."""

    def __init__(self, store: LedgerStore) -> None:
        self.store = store
        self._native_controls = callable(getattr(store, "close_period", None)) and callable(
            getattr(store, "audit_events", None)
        )
        with self.store._lock:
            self.store._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS accounting_periods (
                    id TEXT PRIMARY KEY,
                    organization_id TEXT NOT NULL REFERENCES organizations(id),
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    close_reason TEXT NOT NULL CHECK(length(trim(close_reason)) > 0),
                    closed_at TEXT NOT NULL,
                    CHECK (end_date >= start_date),
                    UNIQUE (organization_id, start_date, end_date)
                );
                CREATE INDEX IF NOT EXISTS idx_periods_org_dates
                    ON accounting_periods(organization_id, start_date, end_date);

                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    organization_id TEXT NOT NULL REFERENCES organizations(id),
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    detail_json TEXT NOT NULL,
                    occurred_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_audit_entity
                    ON audit_events(organization_id, entity_type, entity_id, occurred_at);

                CREATE TRIGGER IF NOT EXISTS reject_posting_to_closed_period
                BEFORE INSERT ON journal_entries
                WHEN EXISTS (
                    SELECT 1 FROM accounting_periods p
                    WHERE p.organization_id = NEW.organization_id
                      AND p.start_date <= NEW.booking_date
                      AND p.end_date >= NEW.booking_date
                )
                BEGIN
                    SELECT RAISE(ABORT, 'booking date belongs to a closed accounting period');
                END;

                CREATE TRIGGER IF NOT EXISTS immutable_audit_events_update
                BEFORE UPDATE ON audit_events
                BEGIN
                    SELECT RAISE(ABORT, 'audit events are append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS immutable_audit_events_delete
                BEFORE DELETE ON audit_events
                BEGIN
                    SELECT RAISE(ABORT, 'audit events are append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS immutable_accounting_periods_update
                BEFORE UPDATE ON accounting_periods
                BEGIN
                    SELECT RAISE(ABORT, 'closed accounting periods cannot be modified');
                END;
                CREATE TRIGGER IF NOT EXISTS immutable_accounting_periods_delete
                BEFORE DELETE ON accounting_periods
                BEGIN
                    SELECT RAISE(ABORT, 'closed accounting periods cannot be deleted');
                END;
                """
            )

            if not self._native_controls:
                self.store._connection.executescript(
                    """
                    CREATE TRIGGER IF NOT EXISTS audit_journal_entry_insert
                    AFTER INSERT ON journal_entries
                    BEGIN
                        INSERT INTO audit_events
                        (id, organization_id, entity_type, entity_id, event_type, detail_json, occurred_at)
                        VALUES (
                            lower(hex(randomblob(16))),
                            NEW.organization_id,
                            'journal_entry',
                            NEW.id,
                            'journal_entry_posted',
                            '{}',
                            strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                        );
                    END;

                    CREATE TRIGGER IF NOT EXISTS audit_journal_entry_reversal
                    AFTER UPDATE OF status ON journal_entries
                    WHEN OLD.status = 'posted' AND NEW.status = 'reversed'
                    BEGIN
                        INSERT INTO audit_events
                        (id, organization_id, entity_type, entity_id, event_type, detail_json, occurred_at)
                        VALUES (
                            lower(hex(randomblob(16))),
                            NEW.organization_id,
                            'journal_entry',
                            NEW.id,
                            'journal_entry_reversed',
                            '{}',
                            strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                        );
                    END;

                    CREATE TRIGGER IF NOT EXISTS audit_period_close
                    AFTER INSERT ON accounting_periods
                    BEGIN
                        INSERT INTO audit_events
                        (id, organization_id, entity_type, entity_id, event_type, detail_json, occurred_at)
                        VALUES (
                            lower(hex(randomblob(16))),
                            NEW.organization_id,
                            'accounting_period',
                            NEW.id,
                            'period_closed',
                            json_object(
                                'start_date', NEW.start_date,
                                'end_date', NEW.end_date,
                                'reason', NEW.close_reason
                            ),
                            strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                        );
                    END;
                    """
                )

    def close_period(
        self,
        organization_id: str,
        start_date: date,
        end_date: date,
        reason: str,
    ) -> str:
        """Close a non-overlapping range. No reopen operation is provided."""
        if end_date < start_date:
            raise LedgerError("Period end date cannot be before its start date")
        if not organization_id.strip():
            raise LedgerError("Organization ID is required")
        if not reason.strip():
            raise LedgerError("A period-close reason is required")

        if self._native_controls:
            return self.store.close_period(organization_id, start_date, end_date, reason)

        period_id = str(uuid.uuid4())
        try:
            with self.store._transaction() as conn:
                overlap = conn.execute(
                    """SELECT id FROM accounting_periods
                       WHERE organization_id = ?
                         AND NOT (end_date < ? OR start_date > ?) LIMIT 1""",
                    (organization_id, start_date.isoformat(), end_date.isoformat()),
                ).fetchone()
                if overlap is not None:
                    raise LedgerError(
                        f"Period overlaps an already closed period ({overlap['id']})"
                    )
                conn.execute(
                    """INSERT INTO accounting_periods
                       (id, organization_id, start_date, end_date, close_reason, closed_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        period_id,
                        organization_id,
                        start_date.isoformat(),
                        end_date.isoformat(),
                        reason.strip(),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
            return period_id
        except sqlite3.IntegrityError as exc:
            raise LedgerError(f"Could not close accounting period: {exc}") from exc

    def audit_events(
        self,
        organization_id: str,
        entity_id: str | None = None,
    ) -> tuple[dict[str, Any], ...]:
        with self.store._lock:
            if entity_id is None:
                rows = self.store._connection.execute(
                    """SELECT * FROM audit_events
                       WHERE organization_id = ?
                       ORDER BY rowid""",
                    (organization_id,),
                ).fetchall()
            else:
                rows = self.store._connection.execute(
                    """SELECT * FROM audit_events
                       WHERE organization_id = ? AND entity_id = ?
                       ORDER BY rowid""",
                    (organization_id, entity_id),
                ).fetchall()

        return tuple(
            {
                "id": row["id"],
                "organization_id": row["organization_id"],
                "entity_type": row["entity_type"],
                "entity_id": row["entity_id"],
                "event_type": row["event_type"],
                "details": json.loads(row["detail_json"]),
                "occurred_at": row["occurred_at"],
            }
            for row in rows
        )
