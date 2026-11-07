# SteuerPilot Pro

**Status: engineering prototype 0.1.0. Not approved for productive bookkeeping or tax filing.**

SteuerPilot Pro is a German accounting and tax-workflow project. Product requirements and release decisions are maintained in Notion; this repository contains an executable domain core and automated regression tests.

## Implemented in 0.1.0

- Decimal-safe EUR arithmetic with cent rounding (ROUND_HALF_UP).
- VAT calculations from net and gross using caller-supplied, dated rate definitions.
- VAT rate provenance fields. A rate cannot be marked approved without a source URL and reviewer.
- Invoice-line arithmetic and structural review warnings.
- Multi-organization SQLite ledger with organization-scoped accounts and journal lines.
- Balanced, multi-line Soll/Haben postings and duplicate source-reference protection.
- Immutable posted journal lines and corrections by reversal entry.
- Date-bounded trial balance.
- Standard-library unit tests and GitHub Actions CI.

## Quick start

Python 3.11 or newer is required. No runtime third-party dependencies are needed.

Run the test suite:

    PYTHONPATH=src python -m unittest discover -s tests -v

Create a ledger with LedgerStore("accounting.sqlite3"), register an organization and its accounts, then post a JournalEntry containing balanced JournalLine objects. Use a durable database path; :memory: is intended for tests only.

## Deliberate boundaries

This version is an accounting-engine foundation, not a complete German bookkeeping product. It does **not** implement authentication or user roles, a legally classified SKR03/SKR04 chart of accounts, period locks, a certified GoBD audit trail, DATEV import/export, XRechnung/ZUGFeRD generation or validation, ELSTER/ERiC, DEÜV, payroll tax or social-insurance calculations, EÜR/balance-sheet/tax-return filing, bank feeds, document OCR, or production backup/restore.

VAT arithmetic is separate from the legal decision about which rate applies to a supply. Rate definitions must be supplied with an effective period and checked by a qualified reviewer. A passing arithmetic test is not legal tax approval. Invoice structural checks are not a substitute for checking every requirement under German invoice law.

The code has no authentication layer. Do not expose the SQLite database or this package to the public internet, and do not store real employee, customer, payroll, banking, or tax data in this prototype.

## Source of truth and traceability

- Product concept and project plan: https://app.notion.com/p/4116c89302188133b5e6c05e114b2226
- QA and release criteria: https://app.notion.com/p/4116c89302188153adc2e9a1b044bbe4
- Workspace dashboard: https://app.notion.com/p/4116c89302188183aadacab43e7ed0fc
