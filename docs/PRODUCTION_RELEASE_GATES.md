# XelaCare — Release gates (not yet satisfied)

This repository is a synthetic-data demonstration. Do not accept real patient data, advertise regulatory certification, or activate clinical monitoring based solely on the demonstration.

## Gate 1 — Source control and deployment
- [ ] Create a dedicated private XelaCare repository with protected main branch and mandatory CI.
- [ ] Provision a cloud account and deployment region under the owner's control; configure DNS, TLS, WAF and a verified custom domain.
- [ ] Set up dev/staging/production with distinct credentials and databases; deploy only from approved release tags.
- [ ] Provision managed PostgreSQL, encrypted backups, tested restore, monitoring and incident escalation.

## Gate 2 — Security and identity
- [ ] Replace prototype bearer-token storage with an audited identity provider, MFA, revocable sessions, staff invitation and password recovery.
- [ ] Implement reviewed Alembic migrations and PostgreSQL RLS for every tenant-linked table; verify tenant context is fail-closed.
- [ ] Perform independent penetration testing, secrets review, dependency scanning and vulnerability remediation.
- [ ] Add application rate limits, anti-automation protections, security event monitoring, retention policies and encrypted PHI storage.

## Gate 3 — Clinical and privacy
- [ ] Establish a clinical safety officer, clinical SOPs, escalation ownership and after-hours coverage.
- [ ] Obtain regulatory classification review per market and assess HIPAA, PIPEDA/provincial Canadian rules, GDPR/UK GDPR, and Caribbean privacy laws as applicable.
- [ ] Sign relevant BAAs/data-processing agreements, validate data-residency claims and complete privacy/security risk assessments.
- [ ] Validate devices, units, timestamps, thresholds, alert reliability and clinical handoff; no autonomous dosing.
- [ ] Validate accessibility, patient consent and emergency disclaimers with actual clinical stakeholders.

## Gate 4 — Commercial
- [ ] Configure payment processor with verified webhook signatures, tax handling, invoicing, plan quotas, cancellations and refunds.
- [ ] Publish service terms, privacy notice, support commitments and clearly delimited services.
- [ ] Test subscription lifecycle and tenant provisioning with synthetic customers in staging.

## Gate 5 — Go live
- [ ] Conduct supervised clinical pilot, tabletop incident response, load tests, DR restore and final independent signoff.
- [ ] Confirm every deployment URL and regional claim from the actual provider control plane.

## Deployment blocker
No deployment account, domain, secrets or dedicated repository is currently linked to this build environment. A public, persistent production URL cannot be generated from a ZIP alone. Never fabricate a URL.
