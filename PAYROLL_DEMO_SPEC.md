# Payroll statement demo

The `/payroll` page adds a Persian-first input form and a German-language statement preview.

## Included

- Company name and address.
- A local company-logo selector. PNG, JPEG, and WebP files up to 2 MB are previewed in the browser.
- Employee display name, internal employee number, employment start date, pay period, and payment date.
- Separate gross-pay inputs for base salary, overtime/surcharges, one-off payments, and allowances.
- Manually entered employee deductions, including wage tax and employee-side social insurance.
- Employer-side contribution fields displayed separately from employee deductions.
- Live arithmetic totals and a net payout preview.
- A4 print layout. The PDF action opens the browser print dialog; choose **Save as PDF**.

## Arithmetic

- Gross pay = base salary + overtime/surcharges + one-off payments + allowances.
- Total deductions = the manually entered employee deductions + any previously paid advance.
- Net payout = gross pay - total deductions.
- Employer-side contributions are displayed separately and are not subtracted from the employee's net payout.

All monetary values are entered by the user. The page does not calculate or validate German wage tax or statutory social-insurance contributions.

## Data handling

The form does not submit data to the WSGI server and does not write data to a database. The logo is read by the browser for local preview and printing. Refreshing or closing the page clears the inputs.

Use synthetic information only. Do not enter real payroll records, tax identifiers, social-security numbers, dates of birth, addresses, or bank-account information.

## Legal scope

This page is a layout and arithmetic demo, not a complete German payroll system or an assurance of compliance with a statutory payslip. Section 108 GewO requires the pay period and composition of remuneration, including relevant additions, deductions, advances, and prepayments. The Entgeltbescheinigungsverordnung sets additional information requirements for a full remuneration statement, which this template intentionally does not collect or calculate.

Primary legal texts:
- https://www.gesetze-im-internet.de/gewo/__108.html
- https://www.gesetze-im-internet.de/entgbv/__1.html

Before any real payroll use, the product needs a qualified German payroll provider or specialist, a legally reviewed field model, current tax/social-insurance calculation rules, secure identity and access controls, retention/audit controls, and an independent privacy/security review.

## Validation

The existing GitHub Actions test matrix imports the new route, checks the form/logo/PDF print path, and runs the repository regression suite on Python 3.11 and 3.12.
