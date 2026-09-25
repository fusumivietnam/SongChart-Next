# Docker-first application development (Issue #5)

Status: development app runtime implemented on [draft PR #6](https://github.com/fusumivietnam/SongChart-Next/pull/6), not merged into `main`. [Run #36090841394](https://github.com/fusumivietnam/SongChart-Next/actions/runs/36090841394) verified app/database startup and scaffold tests at commit `83df1d867248626f4d22fd45d46ecdb4dcd272cd`; later revisions require their own evidence. This does **not** verify product features or production runtime. ADR-0001 governs local Docker; ADR-0003 proposes the runtime baseline. Source and real dependency lockfiles are committed on the PR branch. These instructions assume a new, disposable database, not a PostgreSQL 17 data migration.

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

## PostgreSQL 18 volume and safety

The postgres:18.6 image stores PGDATA at /var/lib/postgresql/18/docker; mount its parent at /var/lib/postgresql. Compose uses the **new** `postgres18_data` named volume. Never mount existing `postgres_data` from the PostgreSQL 17 scaffold into the 18 container. A PostgreSQL major upgrade requires a reviewed backup, restore/pg_upgrade plan and test; do not imply an automatic volume migration. Named volumes survive `docker compose down` but do **not** constitute backups. `docker compose down -v` destroys local database and dependency volumes; never run it on data you need.

## Image/build policy

The multi-stage Dockerfile defines php-base, php-toolchain, development, frontend-build and production targets; the production target is **PHP-FPM only**, not a complete public web serving or deployment configuration. Use the development target for local work. Composer and pnpm lockfiles are mandatory build inputs; no dependency resolution during production image build. PHP 8.4, Node 22 and pnpm 10.17.1 are baseline candidates for verification. Base image SHA pinning, complete license/edition review, production secrets, ingress, backups and serving controller remain separate release gates.
