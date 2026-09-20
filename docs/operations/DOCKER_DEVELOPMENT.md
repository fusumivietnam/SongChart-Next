# Docker development — infrastructure scaffold

Status: implemented as a PostgreSQL-only Compose scaffold; not an initialized Laravel application, verified runtime, production stack or backup system. Authority: [ADR-0001](../adr/ADR-0001-docker-first-development.md).

## Prerequisites
Install a supported Docker Engine/Desktop with Docker Compose v2. No host PostgreSQL, PHP or Node.js is required for the database scaffold.

## Local steps
1. Copy `.env.example` to `.env`; replace `POSTGRES_PASSWORD` with a unique local secret. The example value must never be used in a shared or production environment.
2. Run `docker compose config --quiet` to check interpolation and syntax.
3. Run `docker compose up -d db`, then `docker compose ps`.
4. Run `docker compose exec db pg_isready -U songchart -d songchart` (adjust names if overridden).
5. Run `docker compose down` to stop services. Do **not** run `docker compose down -v` unless you explicitly intend to delete the local database volume.

The DB has no published host port by default. Application containers on the `songchart` network will use hostname `db`, port 5432. After the Laravel starter and lockfiles exist, a separate PR will add the application image, its DB environment mapping, initialization, app health checks and test commands. Never infer an app exists from a healthy PostgreSQL container.

## Security and lifecycle
- `.env` is untracked; never commit secrets, data dumps or credentials.
- A named volume persists across normal restarts; **this is not a backup**. Verify backup *and* restore before production approval.
- PostgreSQL major version is an initial development choice; image digest pinning, version review, migration and restore compatibility are needed before production.
- `docker compose config --quiet` checks configuration only, not application or provider contracts.
