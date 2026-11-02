> **Version 0.2 — internationalization and consent foundation.** Synthetic data only; not approved for live patient data. See [Global Architecture](docs/GLOBAL_ARCHITECTURE.md) and [Codex Implementation Brief](docs/CODEX_IMPLEMENTATION_BRIEF.md).

# XelaCare HaaS — Foundational Prototype (v0.1.0)

**Status: engineering prototype, not production-ready and NOT authorized for live patient data.**

XelaCare is a new, from-scratch multi-tenant Healthcare-as-a-Service foundation. Includes a polished responsive care-operations UI, self-service tenant creation, session authentication, tenant-scoped patient enrollment, observations, care-team alerts, audit events, and illustrative subscription tiers.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000. Register a **fictional** organization and use **synthetic** patients only. By default development uses local SQLite and a process-generated session secret. The development login session is stored in browser sessionStorage; this must be replaced with a hardened identity provider and secure session cookies before clinical production.

## Docker with PostgreSQL

Copy `.env.example` to `.env`, replace both secrets with cryptographically random values, then `docker compose up --build`. The web port binds to localhost. Add a managed HTTPS reverse proxy for any remote access.

## Test

```bash
pytest -q
```

## Included

- Tenant model with unique organization ID on all patient-facing resources.
- Explicit org-scoped queries and checks on patient-linked writes.
- Owner and clinician authorization checks; authenticated audit log reads limited to owner/admin.
- Password hashing using scrypt and signed expiring JWTs.
- No automatic clinical decision-making; alerts are manually created.
- No payment collection until a verified provider is connected.
- Health endpoint, local container packaging and a responsive prototype UI.

## Production blockers — mandatory before patient use

1. **Identity**: managed auth/SSO, MFA, password reset, email verification, rate limiting, session revocation, secure HttpOnly cookies, CSRF strategy, invitation-based staff enrollment, consent and access review.
2. **Tenant isolation**: enforce PostgreSQL row-level security with `SET LOCAL` verified tenant context, independent integration and penetration tests, and isolation of files, exports, caches, jobs and telemetry.
3. **Data**: reviewed schema migrations, field encryption as needed, backups and tested restores, retention/deletion policies, data residency, incident response, immutable audit trail and tamper-evident access logging.
4. **Clinical safety**: licensed clinical governance, validated alert thresholds and escalation protocols, adverse event procedures, device data validation, consent, accessibility and human oversight. No automated dosing advice.
5. **Interoperability**: device vendor agreements and OAuth; validated Dexcom, Bluetooth/cellular gateways, FHIR R4 resources, healthcare provider workflows, notification reliability and offline conflict resolution.
6. **Commercial**: real subscription gateway, signed webhook verification, pricing/usage enforcement, invoicing, tax treatment, trials and cancellation, SLAs, tenant provisioning and support.
7. **Compliance**: HIPAA security/privacy assessment and BAAs where applicable, relevant Caribbean data protection laws, medical-device/software regulatory classification, documented security risk assessment, vendor reviews and privacy notices.
8. **Operations**: HTTPS, WAF, secrets manager, monitoring, alerts, disaster recovery, CI/CD, SAST/DAST, dependency audits, load tests, multi-region strategy, and independent security review.
9. **Code hygiene**: remove `create_all` in favor of Alembic migrations; validate numeric measurement units and clinically sensible ranges; implement concurrency-safe quota and tenant limits.

**Not implemented:** live Dexcom/device connectivity, telehealth video, AI-generated summaries, real payments, SMS, patient-facing accounts, mobile apps, clinician invitations, consent, regulatory controls, or production RLS. Do not advertise these as shipped features.

## Proposed roadmap

- Phase A: secure identity, Postgres RLS, migrations, role policies, audit and tenant isolation tests.
- Phase B: enrollment, patient and caregiver apps, consent, device gateway and clinical escalation.
- Phase C: telehealth, FHIR, AI-assisted summaries with clinician signoff, billing, white-label portals.
- Phase D: regional clinical pilots, independent audits, regulatory approvals and controlled launch.

## v0.3 — Release engineering update
- Added GitHub Actions compile, test, and dependency vulnerability-audit checks.
- Added Docker build exclusions for secrets, local databases, and test artifacts.
- Added an explicit production release checklist in `docs/PRODUCTION_RELEASE_GATES.md`.
- These are packaging and process improvements, not proof of production readiness.
