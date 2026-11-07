# BMF Lohnsteuer PAP 2026

Official reference for the tax-calculation adapter:

- BMF publication (12 November 2025): https://www.bundesfinanzministerium.de/Content/DE/Downloads/Steuern/Steuerarten/Lohnsteuer/Programmablaufplan/2025-11-12-PAP-2026.html
- BMF developer service, which publishes XML pseudocode for the PAP: https://www.bmf-steuerrechner.de/interface/pseudocodes.xhtml
- BMF XML pseudocode is intended for software development. The external BMF interface is described as a test interface; its terms do not authorize using it as the production calculation service.

## Source and provenance

`Lohnsteuer2026.xml` is retained unmodified as the machine-readable PAP source published by the BMF. The BMF data portal entry was updated/published on 12 November 2025 and explicitly includes an `APPLICATION/XHTML+XML` download. The BMF developer service also publishes the XML pseudocode used by software implementations.

- Final BMF data portal entry: https://www.bundesfinanzministerium.de/Datenportal/Daten/frei-nutzbare-produkte/Anwendungen/Programmablaufplan-2026/Programmablaufplan-2026.html
- XML resource listed by the BMF data portal: https://www.bundesfinanzministerium.de/Datenportal/Daten/frei-nutzbare-produkte/Anwendungen/Programmablaufplan-2026/Programmablaufplan-2026-XML.xhtml?__blob=publicationFile&v=3
- BMF developer service: https://www.bmf-steuerrechner.de/interface/pseudocodes.xhtml
- Developer-service XML endpoint: https://www.bmf-steuerrechner.de/javax.faces.resource/daten/xmls/Lohnsteuer2026.xml.xhtml

The XML retains its embedded technical stand date `2025-10-23 12:40`. The final data portal entry explains that the published PAPs differ from the drafts only by minor editorial changes. The source file is preserved unchanged and that technical timestamp is recorded here rather than silently altered. The BMF data portal lists the dataset under CC BY-ND 4.0; see `THIRD_PARTY_NOTICES.md`.

The browser adapter uses the MIT-licensed `paprun` interpreter pinned to a specific commit. Its upstream test documentation says the 2026 tariff is tested over all six tax classes; special cases are not equally well covered. This project therefore enables automatic withholding only for the standard monthly statutory-insurance case that it explicitly validates. Unsupported employee or wage scenarios must be blocked rather than estimated.

The PAP covers wage-tax withholding, solidarity surcharge, and the church-tax assessment base. It does not calculate social-insurance contributions or a complete net-pay statement.

A production adapter must use the exact final BMF 2026 pseudocode, preserve its rounding semantics, expose input/output provenance, and be regression-tested against official reference cases before it can be used to issue payslips.
