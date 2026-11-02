# Codex engineering brief — XelaCare HaaS

Repository root contains a FastAPI prototype. Work on a feature branch. Never use real PHI in development, tests, AI prompts, telemetry, or bug reports.

## Mission
Transform v0.2 into a secure, international, multi-tenant, subscription-based Healthcare-as-a-Service product. Use `docs/GLOBAL_ARCHITECTURE.md` as acceptance criteria. Implement in independently reviewable pull requests.

## First pull request — identity, tenant security and migrations
- Add Alembic and a baseline migration, plus migration verification in CI. Remove `Base.metadata.create_all` from production startup.
- Add PostgreSQL RLS policies for each tenant-scoped table; use transaction-scoped tenant context and test negative cross-tenant queries.
- Enforce tenant-scoped composite foreign keys and prohibit cross-tenant references even for direct SQL writes.
- Introduce production identity via a verified OIDC provider, MFA and invitation-only clinical staff onboarding.
- Add auth rate limiting, audit of login failures without logging credentials, secure token revocation and account recovery.
- Add unit, integration and authorization matrix tests. Never claim security complete without an independent assessment.

## Second pull request — region and consent
- Create a deployment region registry that is populated only by verified infrastructure provisioning, not a tenant input.
- Define organization operating jurisdiction separately from actual data location and subprocessor location.
- Implement consent purpose/version/evidence/provenance and enforce withdrawal across all processing pathways.
- Add export, correction, retention and deletion request workflows; define region-specific defaults after legal review.

## Third pull request — SaaS subscriptions
- Integrate verified merchant sandbox (e.g., Stripe where available) with idempotent webhook processing and replay protection.
- Separate billing organizations, service entitlements, trial/grace states, and metered usage. Enforce entitlements server-side.
- Add tax and currency configuration and jurisdiction-specific invoice requirements.

## Fourth pull request — clinical integrations
- Define FHIR resources, device connector contracts and an ingestion queue.
- Add clinician-configured alert rules and acknowledgement escalation with auditable handoff.
- No autonomous diagnosis, emergency dispatch, or dosing advice without separate clinical and regulatory approval.

## Verification
Run `python -m pytest -q`; add PostgreSQL integration tests, dependency scanning, SAST, SBOM, container scanning, API contract tests, accessibility tests, load tests and disaster-recovery exercises. Produce evidence and residual-risk register before any production deployment.
