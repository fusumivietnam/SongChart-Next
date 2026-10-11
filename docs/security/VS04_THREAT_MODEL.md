# VS-04 public launch threat model

Status: bounded pre-deployment threat model for the currently activated public SongChart surfaces. Deployment-specific controls remain unknown until #69 is resolved.

## Assets and trust boundaries

Primary assets are canonical PostgreSQL identities/relationships, provenance/evidence records, destination-link policy state, repository/release evidence, credentials supplied at runtime, and the integrity/availability of public read/search pages.

Trust boundaries:

1. public browser → SongChart public routes;
2. SongChart application → canonical PostgreSQL;
3. reviewed provider evidence → SongChart canonical import/adaptation boundary;
4. SongChart public destination links → third-party websites after the user navigates away;
5. public GitHub support/correction issues → human review → any later canonical mutation;
6. CI/repository credentials → GitHub workflows and approved repository mutations;
7. future deployment platform/network/database services — currently unselected and therefore not asserted as controlled.

## Current threats and controls

### Public read/search inputs
Search is bounded and PostgreSQL-first. Blank queries do not scan, deterministic ranking is used, and no public mutation API is activated. Laravel/query-builder parameterization is preferred over string-built SQL. Resource exhaustion and abusive traffic controls remain deployment-specific; a launch cannot claim production rate limiting until G5 proves it.

### External destination links
Destination URLs are stored as structured SongChart records with provider/type/provenance/verification state. Public projection exposes verified destinations only. The initial server path performs **no server-side fetch** of destination URLs, so arbitrary destination submission is not an SSRF fetch primitive. Browser navigation uses external-link isolation/referrer restrictions. Future live provider ingestion or URL fetching requires a separately reviewed provider/network policy.

### Corrections and support
Support/correction actions currently use the public repository issue tracker. Copy warns users not to post secrets/sensitive data. A correction submission is evidence for review and never writes canonical tables directly. Human/admin review implementation remains a separate capability; canonical mutation must continue through approved validation/import/review paths.

### Provider data and canonical identity
Provider IDs, names and URLs are evidence, not canonical SongChart identity. Name-only joins and provider overwrite of canonical semantics are prohibited. Live/commercial provider access remains governed by provider-policy/rights gates.

### Secrets
Runtime `.env` files must not be tracked. The repository-owned high-confidence scanner fails closed for common credential formats without printing matched values. Dependency/provenance/SBOM evidence is exact-SHA. Rotation/revocation remains the credential owner's action through the relevant provider/platform; no production secret store is assumed before deployment selection.

### Canonical database and destructive operations
PostgreSQL is canonical. VS-04 recovery exercises dump/restore and one-step migration rollback only on disposable CI infrastructure. Production destructive migration, restore/PITR, retention and RPO/RTO remain release/platform-specific and cannot be inferred from CI rehearsal.

### Health information disclosure
`/health` exposes only generic `ok`/`unavailable` state and status code. Database host, credentials, SQL errors, entity data, dependency/framework versions and stack traces are not part of the contract.

## Deferred/deployment-specific risks

Until #69 selects a target and G5 verifies it, the repository cannot claim controls for TLS/DNS, edge/proxy headers, production rate limits/WAF, runtime secret injection/rotation, managed PostgreSQL backup/PITR, network segmentation, immutable artifact promotion, platform IAM, production logging retention/redaction, alert delivery, deployment rollback, or production smoke behavior.

Authenticated accounts/admin review, public API/SDK, search index, recommendation/ranking, provider production traffic and external workflow engines are also outside the current activated launch-proof surface.

## Review triggers

Re-review this threat model before: selecting a deployment platform; enabling live provider network traffic; adding server-side destination fetching; enabling public writes/accounts/API; introducing a search index/recommendation system; changing canonical identity semantics; adding new secret-bearing services; or performing the first production deployment.
