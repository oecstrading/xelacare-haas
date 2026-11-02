# XelaCare HaaS — International architecture and release gates

**Version:** 0.2 engineering foundation. **Status:** synthetic-data demonstration only.

## Product and market model
- Platform operator provisions independent tenants for hospitals, clinics, home-care agencies, and care networks.
- Each tenant owns its organization configuration, members, patients, consent records, observations, alerts, audit records, and billing relationship.
- Regional offerings must have distinct operational agreements, data-processing schedules, localization, clinical protocols, and deployment controls.
- Proposed modules: remote monitoring, chronic-condition management, telehealth, caregiver access, care coordination, clinical workflow, subscriptions, device integrations, white-label portals.
- **Do not** describe current code as clinical-grade, HIPAA-compliant, GDPR-compliant, or production-ready.

## Regional launch matrix (validation checklist, not legal advice)
| Market | Privacy and regulatory workstream | Infrastructure decision | Commercial workstream |
|---|---|---|---|
| St. Lucia / OECS | Country-specific privacy, healthcare, clinical practice, and cross-border transfer review | Caribbean-compatible deployment and processor assessment | XCD/USD contracts, local provider partnerships |
| United States | HIPAA applicability, covered-entity/BAA analysis, state privacy and telehealth rules, FDA device/software assessment where applicable | US regional infrastructure, signed BAAs and verified subcontractors | USD pricing, provider contracts, payer/reimbursement review |
| Canada | PIPEDA/provincial health privacy applicability (including PHIPA in Ontario where applicable), provincial licensing | Province/customer-specific residency and processor terms | CAD invoicing, provincial market strategy |
| UK | UK GDPR and Data Protection Act, clinical safety and medical-device assessment where applicable | UK region and transfer assessment | GBP contracts, UK healthcare procurement |
| EU | GDPR, DPIA where required, EU medical device rules where applicable | EU region, transfers and DPA | EUR subscriptions, country-by-country localization |

## Reference architecture (target, not all implemented)
1. Edge: managed WAF, TLS, DDoS controls, rate limits, request IDs.
2. Identity: external OIDC/SAML provider, MFA, tenant membership, least-privilege RBAC, short sessions, break-glass workflow.
3. API: validated FastAPI routes, tenant context from verified identity, quotas, service authorization.
4. Data: PostgreSQL per region; database RLS, tenant-scoped foreign keys, encryption at rest, field protection for sensitive data; independently tested migrations.
5. Workflows: queue for device ingestion, alert escalation, consent revocation, notifications, and billing events.
6. Integrations: FHIR R4 interfaces, HL7 where required, device vendor APIs, video provider, payment processor; all gated by signed contracts and sandbox validation.
7. Observability: redacted structured logs, audit integrity, security alerts, SLO dashboards, incident response, retention and deletion rules.
8. Operations: encrypted backups and restore drills, regional disaster recovery, vulnerability scanning, penetration tests, release gates, DPA/BAA register.

## Current v0.2 safeguards
- Server-side organization-scoped patient, observation, alert, consent and audit queries.
- Explicit consent grant and withdrawal events with tenant checks.
- Region cannot be set to a real hosted region by changing metadata; provisioning must verify actual hosting.
- Production configuration refuses SQLite and weak/missing JWT secrets.
- No fictitious live payment processing; checkout fails closed.
- No autonomous clinical triage or patient-facing medication recommendations.

## Known blockers to live patient data
- No verified deployment-region infrastructure or contractual data residency.
- No formal threat model, independent penetration test, MFA, SSO, invitation lifecycle, or credential recovery.
- No database-level row security; tenant isolation currently relies on application queries.
- No Alembic migration history; tables currently use create_all.
- No complete consent enforcement policy across all clinical read/write operations; clinical_mode is disabled.
- No secure object storage, PHI redaction program, retention policies, data export/deletion workflow, or audit immutability.
- No medical-device vendor credentials, ingestion validation, clinician-approved alert algorithms, clinical safety case, or emergency escalation SLA.
- No verified payment integration, tax/VAT handling, dunning, or invoicing.
- No signed BAAs/DPAs, jurisdiction-specific legal review, or clinical/regulatory clearance.

## Release gates
- **Gate A: Demo-ready** — synthetic data only, reproducible build, tenant-isolation tests, functional UX, customer demonstrations.
- **Gate B: Commercial pre-sales** — contracts clearly state pilot scope and launch dependencies; billing only after a verified merchant integration.
- **Gate C: Controlled clinical pilot** — independent security assessment, contractual approvals, clinical protocols, support/incident operations, verified region, consent and privacy controls.
- **Gate D: General availability** — independent audit, scale/load tests, disaster recovery, accessibility, complete operational documentation, market-specific compliance approval.

## Engineering priority
1. Identity provider + MFA + invitations + account recovery.
2. PostgreSQL RLS + composite tenant foreign keys + Alembic migrations.
3. Regional deployment automation + verified region routing and tenancy provisioning.
4. Consent policy engine + patient portal + delegated caregiver access.
5. Payment provider webhooks, metering, subscription lifecycle, taxes and receipts.
6. Device gateway, vendor sandbox, FHIR mappings, clinical safety validation.
7. Telehealth, notifications, care pathways, patient communications.
8. Observability, backup restoration, independent pen test and staged release.
