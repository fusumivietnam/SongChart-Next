# Docker-first application development (Issue #5)

Status: development app runtime is merged into `main` from [PR #6](https://github.com/fusumivietnam/SongChart-Next/pull/6). Foundation CI passed on exact PR head `05e60db52d424ceee71b079b8ff93d321c2d400a` before merge, covering app/db build, PostgreSQL connectivity, starter tests, frontend checks, dependency audits, provenance, SBOM generation and runtime smoke checks. Framework/runtime verification does **not** verify SongChart product features or production deployment. ADR-0001 governs local Docker; ADR-0003 records the accepted Foundation runtime baseline. Source and real dependency lockfiles are on `main`. These instructions assume a new, disposable database, not a PostgreSQL 17 data migration.

## Environment and startup

Install Docker Engine/Desktop with Compose v2. Copy `.env.example` to untracked `.env` and replace the password placeholder (both occurrences) with the same unique local secret. Do not use sample values for real access. Do not commit `.env`. PostgreSQL binds no host port; application and Vite are bound to host loopback.

Once `composer.lock` and `pnpm-lock.yaml` are available:

1. Run `docker compose config --quiet`, then `docker compose build app`.
2. Run `docker compose up -d --wait db app`. First boot installs locked Composer and pnpm dependencies into named development volumes.
3. Run `docker compose exec app php artisan key:generate --force` once; this writes an APP_KEY to your untracked `.env`. Check it exists before using auth/session pages.
4. Run `docker compose exec app php artisan migrate --force` for the **new local** database only. The starter migrations are not SongChart canonical music schemas.
5. Run `docker compose exec app pnpm run build`, or `docker compose exec app pnpm dev --host 0.0.0.0` separately for hot reload.
6. Run `docker compose exec -e APP_ENV=testing -e DB_CONNECTION=sqlite -e DB_DATABASE=:memory: app php artisan test`; the upstream scaffold suite uses in-memory SQLite (pdo_sqlite extension). Never run the fixture test suite against a populated PostgreSQL development database. The app's *runtime* database is PostgreSQL and must be checked separately via `docker compose exec app php artisan db:show --database=pgsql`.
7. Browse http://localhost:8000 only for framework smoke testing. Upstream welcome/auth/dashboard pages are **not** SongChart's approved design or released product.

## Codespaces Design Authority live review

The Foundation Design Authority preview is intentionally available only in `local` and `testing` environments. Codespaces forwards the existing app service on port 8000 through an HTTPS reverse proxy; local/testing runtime trusts the standard `X-Forwarded-For`, `X-Forwarded-Host`, `X-Forwarded-Port` and `X-Forwarded-Proto` headers. Production proxy trust remains a separate release decision.

Human review deliberately reuses the approved local Compose app instead of creating a second preview runtime. Run:

```bash
bash scripts/design_review.sh
```

The script bootstraps an untracked `.env` only when required, generating a local-only PostgreSQL password and Laravel `APP_KEY` without printing either secret. It then starts the normal `db` + `app` Compose services only when the app is not already running, installs locked frontend dependencies in the existing app dependency volume, removes any stale Vite `public/hot` marker, builds static assets, runs TypeScript checks, verifies all five local preview routes, verifies Codespaces HTTPS asset generation when applicable, and prints the exact review URLs. It removes only the superseded `songchart-foundation-preview` container if one remains from the retired workflow; it creates no preview container, extra port binding, preview-specific Docker image or preview-specific dependency volume. Existing PostgreSQL data and dependency volumes are preserved.

This separation is intentional: local human review uses the long-lived Compose development runtime, while deterministic screenshot evidence uses a clean, isolated CI-only server in `scripts/foundation_visual_ci.sh`. The two paths validate different concerns and no longer share mutable local Docker state.

Review these deterministic routes:
- `/_design/foundation/artist`
- `/_design/foundation/artist-long`
- `/_design/foundation/search`
- `/_design/foundation/search-empty`
- `/_design/foundation/search-error`

Use the required 390 × 844 and 1440 × 1024 viewport references, then verify keyboard focus, skip-link behavior, long/mixed-script wrapping, no-artwork behavior and search empty/error semantics. Record the exact Git revision with the owner decision. Visual CI runs on relevant pull requests and `main` pushes so automated evidence is tied to the exact evaluated revision.

## PostgreSQL 18 volume and safety

The postgres:18.6 image stores PGDATA at /var/lib/postgresql/18/docker; mount its parent at /var/lib/postgresql. Compose uses the **new** `postgres18_data` named volume. Never mount existing `postgres_data` from the PostgreSQL 17 scaffold into the 18 container. A PostgreSQL major upgrade requires a reviewed backup, restore/pg_upgrade plan and test; do not imply an automatic volume migration. Named volumes survive `docker compose down` but do **not** constitute backups. `docker compose down -v` destroys local database and dependency volumes; never run it on data you need.

## Provenance evidence
`python3 scripts/foundation_provenance.py` derives the pinned starter revision, lockfile hashes/resolved key versions and container image references without a second dependency database. Foundation CI additionally resolves each external image to its registry manifest SHA-256 digest and retains the report as a short-lived artifact. Local floating tags remain acceptable for this non-production Foundation workflow; controlled release manifests require reviewed immutable pins. The provenance report remains distinct from the SPDX JSON SBOMs generated by Foundation CI for source dependencies and the built production image. Neither artifact replaces human license review or a future production OS/container vulnerability policy.

## Image footprint
The production target intentionally excludes Composer, Node/npm/pnpm, tests, docs and governance source; build dependencies remain in intermediate stages. Foundation CI reports development and production image sizes and requires production to be smaller. Do not switch to Alpine or another libc/base family solely for a smaller number: evaluate extension compatibility, debugging/operations cost and measured transfer/storage benefit first.

## Image/build policy

The multi-stage Dockerfile separates extension compilation, lean PHP runtime, PHP/Node toolchain, source-only development, dependency build, frontend build, production dependency resolution and final PHP-FPM runtime stages; the production target is **PHP-FPM only**, not a complete public web serving or deployment configuration. Use the development target for local work. It intentionally does not bake `vendor` or `node_modules` into the image because Compose owns them as named development volumes and installs strictly from committed lockfiles on first startup. Composer and pnpm lockfiles are mandatory build inputs; no dependency resolution during production image build. PHP 8.4, Node 22 and pnpm 10.17.1 are the verified Foundation development baseline. Base image SHA pinning, complete license/edition review, production secrets, ingress, backups and serving controller remain separate release gates.
