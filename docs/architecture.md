# Architecture and data-integrity decisions

## Version 0.1.0

The initial executable slice is intentionally narrow: invoice arithmetic, VAT arithmetic primitives, a multi-line double-entry ledger, reversals, and trial-balance aggregation.

### Money

- Use Decimal at the domain boundary.
- Quantize to EUR cents with commercial half-up rounding.
- Persist integer cents in SQLite. Never aggregate binary floating-point values.

### VAT rules

A VatRate has a code, percentage, effective start/end, source URL, reviewer and approval flag. This is metadata for controlled rule management; it is not an assertion that the percentage is correct for a particular good, service, customer, transaction type or date. The caller must select the rule and establish legal eligibility separately.

### Ledger

- Journal entries are posted as one SQLite transaction.
- Every entry has at least two lines, a positive debit total, a positive credit total and exact equality in cents.
- An account is always scoped to an organization. Composite foreign keys prevent a journal line from referencing an account belonging to another organization.
- A source reference is unique inside an organization when supplied.
- Posted line values and posted entry identity/date/description are immutable.
- Corrections are represented by a new reversal entry that swaps debit and credit on every original line. The original remains stored and is marked reversed.
- Trial balance includes both original and reversal entries. Their sum is zero after a complete reversal.

### Important gaps before production

Authentication, authorization, tenant-aware application sessions, encryption/key management, legally sufficient audit retention, period locks, account mapping, closing logic, accounting reports, reconciliation, DATEV-specific import/export, electronic invoice standards, payroll and tax rule content, official interfaces, monitoring, operational backups, and restore drills are not in this release.

## Validation approach

The automated suite uses synthetic data only. Reference cases cover cent rounding, 100.00 EUR net at 19 percent, 119.00 EUR gross at 19 percent, multi-line balance, rejection of unbalanced entries, rollback on invalid accounts, duplicate references, cross-organization isolation, immutability, reversal and zeroed trial-balance totals.

CI is configured to run the standard-library unittest suite on pushes to main and feat/** and on pull requests.
