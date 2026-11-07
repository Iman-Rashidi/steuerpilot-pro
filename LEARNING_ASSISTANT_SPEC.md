# SteuerPilot Pro — Learning & Execution Assistant

**Product identity:** bilingual educational and operational assistant for small-company managers in Germany.

## Operating contract

Every workflow follows: Learn → Prepare → Answer guided questions → Create draft → Validate → Require the right human review → Record the outcome.

The prototype is educational, in-memory, and synthetic-data-only. It does not store real customer or employee data, calculate payroll taxes, determine legal termination validity, issue legal tax advice, or submit filings.

## Implemented in this branch

- Bilingual lesson catalogue for accounting basics, sales invoices, purchase invoices, bank reconciliation, employee onboarding, employee offboarding, tax-return preparation, and monthly management review.
- Required-field tracking for each lesson.
- Training-case state machine with explicit states: draft, information complete, specialist review required, and training completed.
- High-risk topics are routed to specialist review and cannot be marked completed by the prototype.
- Real-data mode is rejected. Only lesson-declared synthetic fields are accepted.

## Not implemented

- Persistent database, authentication, authorization, tenant isolation, encryption, audit-grade history, or production document upload.
- Real bookkeeping posting, VAT eligibility decisions, income/corporate/trade tax computation, payroll, social-insurance calculations, or legally complete HR workflows.
- ELSTER/ERiC, DEÜV, DATEV, XRechnung/ZUGFeRD, bank feeds, or official submissions.
- Professional legal/tax review or product approval for commercial use.

## Test

Run:

```
python -m unittest discover -s tests -v
```

Tests cover the lesson catalogue, missing fields, declared-field restrictions, synthetic-only mode, state transitions, and specialist-review gating.

## German reference sources used for product requirements

- HGB §238: https://www.gesetze-im-internet.de/hgb/__238.html
- AO §145: https://www.gesetze-im-internet.de/ao_1977/__145.html
- AO §146: https://www.gesetze-im-internet.de/ao_1977/__146.html
- StBerG §5: https://www.gesetze-im-internet.de/stberg/__5.html
- StBerG §6: https://www.gesetze-im-internet.de/stberg/__6.html
- BGB §622: https://www.gesetze-im-internet.de/bgb/__622.html
- Bundesportal, social-insurance registration: https://verwaltung.bund.de/leistungsverzeichnis/DE/leistung/99107065104000

The laws and administrative procedures must be rechecked by qualified specialists before any real-world release. A link to a statute is not proof of software compliance.
