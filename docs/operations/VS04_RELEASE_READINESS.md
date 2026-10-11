# VS-04 release-readiness record

Status: **G2/G3/G4 launch-proof readiness record — launch is not declared.** Production deployment remains candidate/unactivated until issue #69 selects a platform and a separate G5 release proves the deployed immutable artifact, production migrations, health/smoke behavior and rollback/recovery path.

## Evidence gates

### G2 — public product/read journey
Verified public scope includes deterministic Home discovery, typed PostgreSQL search, canonical Artist → Release → Recording/credits journeys, verified external destination navigation, and repository-owned About/Privacy/Terms/Disclaimer/Support/Corrections plus fixed-route robots/sitemap. Evidence is owned by the VS-01/VS-02/VS-03/VS-04 workflows and the corresponding merged source PRs recorded in roadmap/capability authority.

### G3 — security and release candidate
The Foundation workflow owns locked Composer/pnpm vulnerability audits, dependency license inventories, source/image SPDX SBOMs, image provenance and non-deployable production-target validation. VS-04 owns fail-closed tracked-secret scanning and the runtime `.env` tracking guard. These gates must be green on the same exact candidate SHA.

### G4 — operational and recovery readiness
Repository-owned evidence includes responsive/browser launch-support checks, application+PostgreSQL `/health`, actual disposable database outage behavior, PostgreSQL logical backup/drop-create/restore with canonical snapshot equality, bounded migration rollback/forward re-apply, incident response, recovery runbook and threat model.

## Required release-owner review before any G5 attempt

1. Confirm all required exact-head CI checks are success with no unresolved review/thread blocker.
2. Confirm release scope does not activate an unapproved capability/provider/technology.
3. Confirm no runtime secret file is tracked and no secret-scanner finding exists.
4. Confirm migration impact and release-specific rollback/forward-fix plan.
5. Confirm recovery evidence is applicable to the release's schema changes; disposable CI evidence is not a substitute for production backup/PITR.
6. Confirm legal/provider policy for any newly exposed provider destination/evidence.
7. Confirm issue #69 has an explicit approved deployment-target decision before performing production work.
8. For G5, record immutable artifact identity/digest, platform/environment identity, production migration result, `/health` and user-journey smoke evidence, rollback/recovery evidence and release approval.

## Current stop decision

**STOP before production deployment.** The repository currently proves tested G2/G3/G4 scope only. There is no selected/verified production target, immutable deployed artifact, production DNS/TLS/network, production database migration/backup, production secret-delivery, production smoke, production alerting or production rollback evidence.

Passing VS-04 must not close #69, must not promote `production-deploy` out of candidate solely from CI, and must not be described as a launch. The next production-facing action is a separate explicit deployment-target decision and G5 execution package.

## Evidence ownership and maintenance

Roadmap scope/dependency/acceptance belongs to `docs/roadmap/VERTICAL_SLICES.md`; capability lifecycle belongs to `governance/CAPABILITY_MAP.json`; Issues/PRs and exact-head Actions runs own execution evidence. This record is a synthesis, not a second source of lifecycle truth. Post-merge roadmap reconciliation must keep the authority files current.
