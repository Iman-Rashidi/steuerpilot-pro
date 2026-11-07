# SteuerPilot Pro

**Status: engineering prototype 0.2.1. Not approved for productive bookkeeping or tax filing.**

SteuerPilot Pro is a German accounting and tax-workflow project. Product requirements are maintained in Notion; this repository contains an executable domain core and automated regression tests.

## Implemented in 0.2.1

- Decimal-safe EUR arithmetic with cent rounding (ROUND_HALF_UP).
- VAT calculations from net and gross amounts using caller-supplied, dated rate definitions.
- VAT rate provenance fields. A rate cannot be marked approved without a source URL and reviewer.
- Invoice-line arithmetic and structural review warnings.
- Multi-organization SQLite ledger with organization-scoped accounts and journal lines.
- Balanced, multi-line Soll/Haben postings and duplicate source-reference protection.
- Immutable posted journal lines and correction by reversal entry.
- Date-bounded trial balance.
- Optional LedgerControls extension: database-enforced closed periods and append-only technical events for postings, reversals and period closures. Instantiate LedgerControls(store) after LedgerStore to install these controls; they share the ledger's SQLite transaction.
- GitHub Actions installs the package and runs the regression suite on Python 3.11 and 3.12.

## Installation and tests

Python 3.11 or newer is required. The application has no runtime third-party dependencies; setuptools is used to install the package.

Create and activate a virtual environment, then install the project:

~~~~
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install .
~~~~

Run the suite:

~~~~
python -m unittest discover -s tests -v
~~~~

Example VAT calculation:

~~~~
from datetime import date
from decimal import Decimal
from steuerpilot.vat import VatRate, vat_from_net

rate = VatRate("EXAMPLE-19", Decimal("19"), date(2026, 1, 1))
result = vat_from_net("100.00", rate)
assert (result.net, result.tax, result.gross) == (
    Decimal("100.00"), Decimal("19.00"), Decimal("119.00")
)
~~~~

To enable period guards and technical event history:

~~~~
from steuerpilot.ledger import LedgerStore
from steuerpilot.controls import LedgerControls

store = LedgerStore("accounting.sqlite3")
controls = LedgerControls(store)
~~~~

Use a durable database path; :memory: is intended for tests only.

## Deliberate boundaries

This is an accounting-engine foundation, not a complete German bookkeeping product. It does **not** implement authentication or user roles, a legally classified SKR03/SKR04 chart of accounts, permission-controlled period reopening, a certified GoBD audit trail, DATEV import/export, XRechnung/ZUGFeRD generation or validation, ELSTER/ERiC, DEÜV, payroll tax or social-insurance calculations, EÜR/balance-sheet/tax-return filing, bank feeds, document OCR, or production backup/restore.

The event table is an append-only technical log protected by SQLite triggers. It is not a certified, tamper-proof or legally sufficient GoBD audit trail. A database administrator or anyone with direct file access may still alter the SQLite file outside the application. The optional period-control extension intentionally has no reopen API; an authorized period-reopening workflow is a separate production requirement.

VAT arithmetic is separate from the legal decision about which rate applies to a supply. Rate definitions must be supplied with an effective period and checked by a qualified reviewer. A passing arithmetic test is not legal tax approval. Invoice structural checks are not a substitute for checking every requirement under German invoice law.

The code has no authentication layer. Do not expose the SQLite database or this package to the public internet, and do not store real employee, customer, payroll, banking, or tax data in this prototype.

## Source of truth and traceability

- Product concept and project plan: https://app.notion.com/p/4116c89302188133b5e6c05e114b2226
- QA and release criteria: https://app.notion.com/p/4116c89302188153adc2e9a1b044bbe4
- Workspace dashboard: https://app.notion.com/p/4116c89302188183aadacab43e7ed0fc
