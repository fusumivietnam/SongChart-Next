# ADR-0016 — Zero-cost preview environment

Status: accepted for preview implementation
Date: 2026-10-13
Issue: #140
Capabilities: `public-web`, `canonical-database`, `project-os`

## Context

SongChart Next has a Docker-first local/CI baseline and an accepted single-VPS production baseline in ADR-0015, but the first real VPS is intentionally deferred until production deployment evidence is worth the recurring cost. The project still benefits from an Internet-accessible environment for browser review, health checks, migrations and representative public journeys.

A preview environment must not become a second product authority, must not alter the production topology merely to fit a hosted platform, and must remain disposable. Canonical product data semantics stay in PostgreSQL and SongChart application/domain code; hosting providers are replaceable infrastructure.

## Decision

The zero-cost preview baseline is:

- Vercel Hobby hosts a preview-only custom container built from root `Dockerfile.vercel`;
- the preview container is a single stateless Laravel HTTP process and listens on Vercel-provided `$PORT`;
- Neon Free hosts an isolated PostgreSQL 18 preview database;
- preview secrets are configured in the hosting control plane and never committed to Git or copied into repository evidence;
- `MUSICBRAINZ_LIVE_ENABLED=false` remains the preview default;
- file-backed session/cache state is explicitly ephemeral and carries no canonical authority;
- schema migrations may run against the isolated preview database as part of preview startup while this remains a single disposable test environment;
- the existing Docker Compose development/CI topology and ADR-0015 PHP-FPM + Nginx + PostgreSQL production topology are unchanged.

The preview environment maps to `staging` when recorded in the infrastructure registry. A Vercel preview URL is not production deployment evidence.

## Cost boundary

This decision authorizes only zero-cost/free-tier resources. If Vercel, Neon or another dependency requires a paid upgrade, the preview must stop or be re-evaluated before cost is incurred. No automatic paid upgrade or metered production service is authorized by this ADR.

## Security and data boundary

- Preview uses a database isolated from any future production database.
- Preview data must be synthetic, deterministic fixtures or otherwise non-sensitive test data.
- `APP_KEY` and database credentials are secret control-plane values.
- Provider live traffic, correction intake, admin review, public API and other separately gated capabilities stay disabled unless independently approved.
- Public error responses use `APP_DEBUG=false`.

## Verification

Implementation is not considered verified until an exact branch/commit preview deployment records:

1. successful Vercel container build;
2. successful PostgreSQL migration against the isolated preview database;
3. `/health` returns HTTP 200;
4. Home/Search and at least one representative canonical public journey render successfully;
5. no deployment from this preview work is promoted or aliased as SongChart production.

Only after that evidence may the actual Vercel and Neon preview instances be recorded as `verified` staging infrastructure.

## Explicit non-decisions

This ADR does not:

- supersede ADR-0015;
- close or satisfy G5 issues #69 or #121;
- select Vercel or Neon for production;
- approve a paid hosting plan;
- authorize production data, production credentials or production provider traffic;
- activate any later roadmap capability.

## Exit and portability

The preview can be deleted without changing SongChart domain/application architecture. A replacement preview provider must need only container/runtime configuration and PostgreSQL connection configuration. Production remains the separately governed single-VPS Docker baseline until another production ADR supersedes ADR-0015.
