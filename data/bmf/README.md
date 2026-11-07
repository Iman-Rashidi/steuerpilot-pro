# BMF Lohnsteuer PAP 2026

Official reference for the tax-calculation adapter:

- BMF publication (12 November 2025): https://www.bundesfinanzministerium.de/Content/DE/Downloads/Steuern/Steuerarten/Lohnsteuer/Programmablaufplan/2025-11-12-PAP-2026.html
- BMF developer service, which publishes XML pseudocode for the PAP: https://www.bmf-steuerrechner.de/interface/pseudocodes.xhtml
- BMF XML pseudocode is intended for software development. The external BMF interface is described as a test interface; its terms do not authorize using it as the production calculation service.

## Import policy

Do not vendor or execute a third-party mirror of the PAP without verifying its exact contents against the final BMF publication. An XML mirror encountered during development contained an internal stand date of 23 October 2025, while the final BMF publication is dated 12 November 2025. It was therefore removed from this branch rather than treated as the authoritative 2026 source.

The PAP covers wage-tax withholding, solidarity surcharge, and the church-tax assessment base. It does not calculate social-insurance contributions or a complete net-pay statement.

A production adapter must use the exact final BMF 2026 pseudocode, preserve its rounding semantics, expose input/output provenance, and be regression-tested against official reference cases before it can be used to issue payslips.
