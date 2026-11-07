# Security and data handling

This repository currently contains an unauthenticated local accounting-core prototype.

- Do not deploy it as a network service.
- Do not use real personal, payroll, bank, customer, invoice or tax records.
- The SQLite file may contain financial data; protect it as confidential and exclude it from version control.
- Organization-scoped foreign keys are an integrity control, not user authorization.
- No encryption-at-rest, identity provider, role model, access-log service, backup automation, restore verification, penetration test, or privacy impact assessment is claimed in this version.
- Before production, complete threat modeling, authentication and least-privilege authorization, secrets and key management, encryption, logging/retention review, backup/restore drills, dependency governance and independent security testing.

Report suspected vulnerabilities privately to the repository maintainer. Do not include real personal or financial data in issue reports.
