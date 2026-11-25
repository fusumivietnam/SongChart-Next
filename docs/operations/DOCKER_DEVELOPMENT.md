# Docker-first application development (Issue #5)

Status: development app runtime is merged into `main` from [PR #6](https://github.com/fusumivietnam/SongChart-Next/pull/6). Foundation CI passed on exact PR head `05e60db52d424ceee71b079b8ff93d321c2d400a` before merge, covering app/db build, PostgreSQL connectivity, starter tests, frontend checks, dependency audits, provenance, SBOM generation and runtime smoke checks. Framework/runtime verification does **not** verify SongChart product features or production deployment. ADR-0001 governs local Docker; ADR-0003 records the accepted Foundation runtime baseline. Source and real dependency lockfiles are on `main`. These instructions assume a new, disposable database, not a PostgreSQL 17 data migration.

## One-command local WSL startup and port preflight

On Windows 11 / VS Code **WSL: Ubuntu**, use `bash scripts/dev_up.sh` as the preferred entry point after reviewing `git status`. It validates the configured host port, checks Docker Desktop availability, detects an existing Windows listener (including stale VS Code forwards) and local Linux listeners when possible, then starts the existing Compose app/db and runs the read-only nine-route smoke. On a conflict it **fails with a diagnosis** instead of killing processes, switching ports automatically, creating secrets, resetting data, or deleting volumes.

Default URL: `http://127.0.0.1:8000`. For a **deliberate**, temporary override, set `SONGCHART_HTTP_PORT=18080 bash scripts/dev_up.sh` after ensuring the new port is free. This changes only the host-side loopback mapping, not Laravel's internal 8000 or the production Nginx/PHP-FPM topology. The smoke uses the same configured port. For the normal case use the default; do not change ports merely to mask a Docker Desktop forwarding-service error. The optional Vite host port is *not* required for a static-build-based browser review.

This script assumes a working untracked local `.env` and an available development app image; it does not create passwords, run migrations, build images, or inject fixtures. If the image is missing, use the established Docker development setup as a separate deliberate action. Docker named volumes remain intact.

## VS Code auto-start on folder open (Windows WSL)

Open this repository using **VS Code Remote - WSL** with Docker Desktop already running. The repository's `.vscode/tasks.json` declares a `folderOpen` task that runs `bash scripts/dev_up.sh` from the workspace root. On the first trusted workspace open, VS Code may ask to **Allow Automatic Tasks**; approve only after inspecting the tracked task. If automatic tasks were previously disallowed, open the Command Palette and run **Tasks: Manage Automatic Tasks in Folder**, then select **Allow Automatic Tasks**. This setting is controlled locally by VS Code; repository commits cannot bypass it.

When the SongChart Compose app is already running and loopback HTTP health responds, `dev_up.sh` leaves containers untouched and runs the existing read-only 9-route smoke. This check happens **before** inspecting Windows VS Code port listeners: a legitimate forward of a healthy app is no longer treated as a startup conflict. If the container is running but health is unreachable, startup **fails closed** with diagnostics instead of restarting it. If no app is running, the script performs the original Windows/WSL port preflight and starts the existing Compose services only if the port is available. It never kills VS Code, chooses a new port, runs migrations, resets the database, builds images or changes production settings.

Auto-start runs when opening the trusted folder, **not** when Windows boots. It does not start Docker Desktop for you. If you open several VS Code windows on the same workspace, check the task output and `docker compose ps` if a forwarding race occurs. Vite HMR remains opt-in and is not required for app bootstrap. Disable automatic startup by choosing **Disallow Automatic Tasks** via the same VS Code command; you can always run `bash scripts/dev_up.sh` manually.

## Environment and startup

Install Docker Engine/Desktop with Compose v2. Copy `.env.example` to untracked `.env` and replace the password placeholder (both occurrences) with the same unique local secret. Do not use sample values for real access. Do not commit `.env`. PostgreSQL binds no host port; the application publishes host-loopback port 8000 by default, configurable via `SONGCHART_HTTP_PORT`. Vite hot reload is optional and must opt in to a separately reviewed host-port mapping; the default boot path does not depend on port 5173.

Once `composer.lock` and `pnpm-lock.yaml` are available:

1. Run `docker compose config --quiet`, then `docker compose build app`.
2. Run `docker compose up -d --wait db app`. First boot installs locked Composer and pnpm dependencies into named development volumes.
3. Run `docker compose exec app php artisan key:generate --force` once; this writes an APP_KEY to your untracked `.env`. Check it exists before using auth/session pages.
4. Run `docker compose exec app php artisan migrate --force` for the **new local** database only. The starter migrations are not SongChart canonical music schemas.
5. Run `docker compose exec app pnpm run build`. For optional hot reload, `docker compose exec app pnpm dev --host 0.0.0.0` starts Vite inside the container, but accessing Vite from the host also requires a separately configured local-only port mapping; it is intentionally not active during default bootstrap.
6. Run `docker compose exec -e APP_ENV=testing -e DB_CONNECTION=sqlite -e DB_DATABASE=:memory: app php artisan test`; the upstream scaffold suite uses in-memory SQLite (pdo_sqlite extension). Never run the fixture test suite against a populated PostgreSQL development database. The app's *runtime* database is PostgreSQL and must be checked separately via `docker compose exec app php artisan db:show --database=pgsql`.
7. Browse http://localhost:8000 only for framework smoke testing. Upstream welcome/auth/dashboard pages are **not** SongChart's approved design or released product.

## Codespaces Design Authority live review

The Foundation Design Authority preview is intentionally available only in `local` and `testing` environments. Codespaces forwards the existing app service on port 8000 through an HTTPS reverse proxy; local/testing runtime trusts the standard `X-Forwarded-For`, `X-Forwarded-Host`, `X-Forwarded-Port` and `X-Forwarded-Proto` headers. Production proxy trust remains a separate release decision.

Human review deliberately reuses the approved local Compose app instead of creating a second preview runtime. Run:

```bash
bash scripts/design_review.sh
```

The script bootstraps an untracked `.env` only when required, generating a local-only PostgreSQL password and Laravel `APP_KEY` without printing either secret. It then starts the normal `db` + `app` Compose services only when the app is not already running, installs locked frontend dependencies in the existing app dependency volume, removes any stale Vite `public/hot` marker, builds static assets, runs TypeScript checks, verifies all five local preview routes, verifies Codespaces HTTPS asset generation when applicable, and prints the exact review URLs. It removes only the superseded `songchart-foundation-preview` container if one remains from the retired workflow; it creates no preview container, extra port binding, preview-specific Docker image or preview-specific dependency volume. Existing PostgreSQL data and dependency volumes are preserved. If Docker reports a known stale container-layer failure such as `RWLayer ... unexpectedly nil`, the review command automatically removes and recreates only the Compose `app` and `db` containers once, preserving all named volumes; it does not prune the Docker daemon or delete database/dependency volumes.

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
