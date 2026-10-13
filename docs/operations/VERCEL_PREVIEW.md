# Vercel preview runbook

Authority: ADR-0016 and issue #140. This runbook is preview/test only. Production remains ADR-0015 and issues #69/#121.

## Resources

- Vercel project: `songchart-next-preview` on the Hobby plan.
- Git source: `fusumivietnam/SongChart-Next`.
- Preview source branch: `infra/vercel-free-preview` while issue #140 is being implemented; normal future PR branches may create their own preview deployments after this baseline merges.
- Database: isolated Neon Free PostgreSQL 18 project `SongChart-Next-Preview`, database `songchart_next_preview`.
- Application container: root `Dockerfile.vercel`.

Provider-generated IDs and credentials are operational details, not application identity and must not be embedded in application code.

## Required Vercel preview environment variables

Configure these for the **Preview** environment only:

| Variable | Secret | Required value/policy |
| --- | --- | --- |
| `APP_KEY` | yes | Dedicated preview Laravel application key generated outside Git/chat. |
| `DB_URL` | yes | Neon preview PostgreSQL connection URI copied directly from the Neon control plane. |
| `DB_CONNECTION` | no | `pgsql` (also defaulted by `Dockerfile.vercel`). |
| `APP_ENV` | no | `preview` (also defaulted by `Dockerfile.vercel`). |
| `APP_DEBUG` | no | `false`. |
| `SESSION_DRIVER` | no | `file`; ephemeral preview state only. |
| `CACHE_STORE` | no | `file`; ephemeral preview cache only. |
| `QUEUE_CONNECTION` | no | `sync`. |
| `MUSICBRAINZ_LIVE_ENABLED` | no | `false`. |
| `PREVIEW_SEED_FIXTURES` | no | `true` by default; set `false` only when an intentionally empty preview DB is required. |

Do not paste `APP_KEY`, `DB_URL`, database passwords or access tokens into GitHub issues, pull requests, CI logs or chat.

## Deployment contract

1. Deploy a non-production branch/commit as a Vercel Preview deployment.
2. Vercel detects `Dockerfile.vercel` and builds the OCI image.
3. At runtime `deploy/vercel/start.sh` refuses to start without `APP_KEY` or `DB_URL`.
4. Startup applies `php artisan migrate --force --no-interaction` to the isolated preview database.
5. Unless `PREVIEW_SEED_FIXTURES=false`, startup idempotently imports the repository-owned deterministic Artist and Release fixtures through `songchart:fixture:import-artist` and `songchart:fixture:import-release`. No live provider traffic is involved.
6. Laravel listens on `${PORT}` supplied by Vercel.
7. `APP_URL` is derived from `VERCEL_URL` when available.

Never promote a preview deployment to production as evidence for SongChart G5. If a newly-created Vercel project incorrectly classifies its first branch build as production, cancel that deployment and keep only the branch preview deployment.

## Verification checklist

For the exact preview commit record:

- Vercel build state is `READY` and source SHA matches the intended Git commit;
- deployment target is preview/non-production;
- runtime log shows migrations and deterministic fixture imports complete without error;
- `GET /health` returns 200;
- `/` renders the Home surface;
- `/search` renders Search and returns the deterministic fixture entities for an applicable query;
- representative canonical Artist/Release/Recording routes from the deterministic fixtures render successfully;
- `MUSICBRAINZ_LIVE_ENABLED=false`;
- no production alias or G5 lifecycle state is changed.

After verification, record the provider instances in `governance/INFRASTRUCTURE_REGISTRY.json` as `staging` infrastructure with exact operational evidence. Do not record them as production.

## Failure and recovery

The preview environment is disposable:

- failed application build: fix the bounded branch and redeploy exact SHA;
- missing/invalid secret: correct only in Vercel Preview environment settings and redeploy;
- preview DB corruption/schema experiment: recreate the isolated preview database and rerun migrations/fixtures;
- free-tier suspension or quota exhaustion: allow the environment to sleep or recreate it; do not enable paid service without a new approval;
- platform incompatibility: retire the preview infrastructure entry and select another preview provider without modifying SongChart domain/application architecture.

No backup of synthetic preview data is required. Repository migrations and deterministic fixture sources are the recovery authority for this disposable environment.
