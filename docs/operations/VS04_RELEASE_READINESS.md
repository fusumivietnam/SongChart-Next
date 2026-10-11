# VS-04 release-readiness record

Status: **G2/G3/G4 launch-proof readiness record — launch is not declared.** ADR-0015 and PR #119 select and implement the initial single-VPS Docker deployment package, but production deployment is not yet evidenced. A separate G5 execution must prove the real environment, deployed immutable artifacts, production migrations, health/smoke behavior and rollback/recovery path.

## Evidence gates

### G2 — public product/read journey
Verified public scope includes deterministic Home discovery, typed PostgreSQL search, canonical Artist → Release → Recording/credits journeys, verified external destination navigation, and repository-owned About/Privacy/Terms/Disclaimer/Support/Corrections plus fixed-route robots/sitemap. Evidence is owned by the VS-01/VS-02/VS-03/VS-04 workflows and the corresponding merged source PRs recorded in roadmap/capability authority.

### G3 — security and release candidate
The Foundation workflow owns locked Composer/pnpm vulnerability audits, dependency license inventories, source/image SPDX SBOMs, image provenance and production-target validation. VS-04 owns fail-closed tracked-secret scanning and the runtime `.env` tracking guard. These gates must be green on the same exact candidate SHA.

### G4 — operational and recovery readiness
Repository-owned evidence includes responsive/browser launch-support checks, application+PostgreSQL `/health`, actual disposable database outage behavior, PostgreSQL logical backup/drop-create/restore with canonical snapshot equality, bounded migration rollback/forward re-apply, incident response, recovery runbook and threat model.

### G5a — deployable single-VPS package
ADR-0015 selects one Ubuntu 24.04 LTS VPS using Docker Compose, Nginx, PHP-FPM and PostgreSQL 18.6 for the initial low-cost production baseline. PR #119 implements `compose.production.yaml`, separate app/web image targets, fail-closed environment/backup contracts and deploy/smoke/rollback helpers. Exact-head CI builds both production images, runs forward migrations in a disposable production topology, verifies `/health`, `/` and `/search`, and proves app/PostgreSQL have no host-published ports. This is packaging evidence, not production deployment evidence.

## Required release-owner review before real G5 execution

1. Confirm all required exact-head CI checks are success with no unresolved review/thread blocker.
2. Confirm release scope does not activate an unapproved capability/provider/technology.
3. Confirm no runtime secret file is tracked and no secret-scanner finding exists.
4. Confirm migration impact and release-specific rollback/forward-fix plan.
5. Confirm recovery evidence is applicable to the release's schema changes; disposable CI evidence is not a substitute for production backup/PITR.
6. Confirm legal/provider policy for any newly exposed provider destination/evidence.
7. Confirm the actual VPS/environment, access boundary, intended hostname/DNS/TLS path and independent off-host backup destination.
8. Record immutable app/web image identities/digests built from the approved release revision.
9. For G5, record production backup result, migration result, `/health` and user-journey smoke evidence, rollback/recovery evidence and release approval.

## Current stop decision

**STOP before production deployment.** The deployment architecture/package is selected and implemented, but there is no concrete production VPS environment, immutable released app/web digest, production DNS/TLS/network evidence, production database migration/backup, production secret delivery, public production smoke, alerting or production rollback evidence.

Issue #69 remains open until the real G5 environment/deployment evidence is recorded. `production-deploy` may be `implemented` because deployable source/config exists, but it must not be described as `deployed` or as a public launch solely from PR #119 or disposable CI. The next production-facing action is environment provisioning and controlled G5 execution.

## Evidence ownership and maintenance

Roadmap scope/dependency/acceptance belongs to `docs/roadmap/VERTICAL_SLICES.md`; capability lifecycle belongs to `governance/CAPABILITY_MAP.json`; Issues/PRs and exact-head Actions runs own execution evidence. This record is a synthesis, not a second source of lifecycle truth. Post-merge authority reconciliation must keep these sources current.
