# Payroll statement demo

The `/payroll` page provides a Persian-first form and German-language A4 statement preview. The browser renders the selected company logo and opens the print dialog for PDF output.

## Inputs and automatic calculations

- Company name, address, local logo preview, employee display name and internal number, pay period and payment date.
- Monthly gross base salary, contracted monthly hours, one-off payments and other gross allowances.
- Shift records with date, start/end time and break interval. Shifts crossing midnight are split minute-by-minute.
- Night work (20:00-06:00), Sunday work, and public holidays are detected from the shift date. Easter Sunday and Pentecost Sunday are included in the §3b tax classification. Sunday and public-holiday classifications are not double-counted for the holiday component of the tax-free estimate; night work can still be combined with either category. Christmas Eve and New Year’s Eve special supplement rules are not included in this demo.
- Public holidays include nationwide holidays and state-specific 2026 dates for the selected Bundesland. Additional local dates can be entered manually. Bavaria's Assumption Day is municipality-dependent and is not inferred automatically.
- Contract-entered night, Sunday and public-holiday supplement rates are calculated separately and added to gross pay. These are contract rates, not mandatory statutory supplement rates.
- The estimated tax-free portion and social-insurance-free portion of each supplement category are displayed separately, using the relevant Grundlohn caps and the entered work-time categories.
- Automatic 2026 employee/employer shares for statutory health insurance (14.6% default base rate plus the entered Krankenkasse Zusatzbeitrag, split equally), long-term care insurance (employee rate varies by child count and Saxony), pension insurance (18.6%, split equally), and unemployment insurance (2.6%, split equally).
- Monthly contribution assessment caps used in the 2026 standard scenario: EUR 5,812.50 for health/care and EUR 8,450 for pension/unemployment.
- Net pay = gross pay - employee social insurance - manually entered wage tax/solidarity surcharge/church tax - other deductions/advance.
- Employer shares are shown separately and do not reduce employee net pay.
- Browser print layout is A4. Choose **Save as PDF** in the browser print dialog.

## Assumptions and exclusions

This is a learning/test calculation, not a certified payroll engine. It assumes a full monthly payroll period, one ordinary employee subject to statutory insurance, statutory GKV membership, one employer, and premiums paid in addition to regular base pay. It does not cover Minijob, private health insurance, multiple employers, mid-month employment, short-time work, special occupational pension arrangements, contribution splitting, special sector rates, or all payroll edge cases.

Wage tax (Lohnsteuer), solidarity surcharge, and church tax are not calculated. Those values are separate manual inputs because a correct calculation requires further personal and payroll data and a maintained official tax calculation engine. The Krankenkasse Zusatzbeitrag must be entered for the selected fund; 2.9% is only the 2026 average default.

The tax/SV-free premium estimates assume actual qualifying work and are not a determination that the employer must pay any particular supplement. If night, Sunday and holiday periods overlap, the demo adds contract-entered payment rates for the separate time categories; the statutory tax-free classification follows the non-duplicative Sunday/holiday treatment, with night work separately combined. If night, Sunday and holiday periods overlap, the demo adds the contract-entered rates; the applicable agreement may use different combination rules. Contract or collective-agreement rules determine payment entitlement and rates. The user must select the workplace Bundesland before the net estimate is shown. Regional/local holiday variations may require additional dates.

## Data handling

The form does not submit payroll data to the WSGI server or write it to a database. The logo is read locally by the browser. Refreshing or closing the page clears the inputs. Use synthetic information only. Do not enter real employee records, tax IDs, social-security numbers, dates of birth, addresses, or bank-account details.

## Legal scope and sources

This page is not a complete statutory Entgeltbescheinigung and does not claim legal or payroll compliance. Before any real payroll use, the feature needs specialist review and a certified payroll calculation workflow.

- German trade regulation, payslip composition: https://www.gesetze-im-internet.de/gewo/__108.html
- Entgeltbescheinigungsverordnung: https://www.gesetze-im-internet.de/entgbv/__1.html
- 2026 statutory health insurance rates and cap: https://www.bundesgesundheitsministerium.de/beitraege/seite
- 2026 social-insurance calculation values: https://www.bmas.de/DE/Service/Gesetze-und-Gesetzesvorhaben/sozialversicherungs-rechengroessenverordnung-2026.html
- Care-insurance employee/employer shares and child adjustments: https://www.bundesgesundheitsministerium.de/themen/pflege/online-ratgeber-pflege/die-pflegeversicherung/finanzierung
- Tax-free supplements for night/Sunday/holiday work: https://www.gesetze-im-internet.de/estg/__3b.html
- Social-insurance exemption rules for supplements: https://www.gesetze-im-internet.de/svev/__1.html

## Validation

The Python test suite checks that the route exposes the shift, state, insurance, contribution cap, and print/PDF features. It does not replace interactive browser tests or specialist payroll validation.
