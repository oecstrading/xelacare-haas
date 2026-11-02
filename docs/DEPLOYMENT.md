# XelaCare — Deployment and commercial readiness

## What can be deployed now
The `preview/` directory is a **public, synthetic-data demonstration** of XelaCare's multi-tenant product experience. It runs entirely in the browser without API requests, local storage, authentication, personal information or payments. Do not describe it as a live clinical platform or as ready for patients.

The root `render.yaml` provisions only this preview as a Render static site. It does not deploy the FastAPI backend, database, or medical workflows.

### Render
1. Connect the `oecstrading/xelacare-haas` GitHub repository to your Render account.
2. Choose New → Blueprint and select `main`, using `render.yaml`.
3. Confirm that the Blueprint creates **one static site only** and no paid database resources.
4. Wait for the Render deploy to complete; use the actual URL provided by Render, and verify the dashboard, tenant switch, patient drilldowns, tabs, services and subscription demonstrations.

The static preview must not contain a real-patient contact form, analytics collecting protected health information, embedded device SDKs, or third-party chat providers.

### GitHub Pages alternative
A publish workflow exists at `.github/workflows/publish-preview.yml`. GitHub Pages must be enabled on the repository, using Settings → Pages → Source: GitHub Actions. For private repositories, GitHub plan eligibility applies. The workflow cannot enable Pages with its default token.

## What is NOT deployable for clinical use yet
`app/main.py` and the associated Docker composition are an engineering proof of concept. The backend uses application-enforced tenant filtering, process-local development session management, and schema creation at startup. It does not provide production-certified PostgreSQL row-level security, strong identity, secure clinical alert governance, regulated medical integrations, contracts, subscription payments or independent privacy audits.

A healthcare production launch requires all gates in `docs/PRODUCTION_RELEASE_GATES.md`. These include:
- Independent penetration testing and privacy threat modeling.
- Database-enforced and verified tenant isolation.
- Region-specific hosting and retention rules, with independently verifiable residency.
- HIPAA safeguards and vendor BAAs in applicable US workflows; applicable Canadian provincial and federal requirements; EU and UK privacy duties where offered.
- Clinician-led protocol validation, incident response, auditability, and accessibility.
- Financial terms, subscription billing, verified payment webhooks, tax handling, and customer SLAs.
- Explicit user acceptance testing, backup-restore exercises and operational monitoring.

## Engineering checks
`quality.yml` runs Python compilation, four foundation tests, a strict dependency audit, JavaScript syntax checking, and a preview check that rejects network and browser storage APIs.

## Current deployment status
The Render Blueprint is infrastructure-as-code, not evidence that a Render site exists. A public URL is valid only after a hosting provider confirms deployment and an HTTPS request verifies that exact URL.
