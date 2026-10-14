# Vercel preview runbook

Authority: ADR-0016 and issue #140. This runbook is preview/test only. Production remains ADR-0015 and issues #69/#121.

## Resources

- Vercel project: `songchart-next-preview` on the Hobby plan.
- Git source: `fusumivietnam/SongChart-Next`.
- Preview source branch: `infra/vercel-free-preview` while issue #140 is being implemented.
- Database: isolated Neon Free PostgreSQL 18 project `SongChart-Next-Preview`, database `songchart_next_preview`.
- Application container: root `Dockerfile.vercel`.

Provider-generated IDs and credentials are operational details, not application identity and must not be embedded in application code.

## Zero-cost Git deployment guard

While issue #140 is open, the Vercel project uses an Ignored Build Step as a temporary quota guard:

- branches other than `infra/vercel-free-preview` are ignored;
- commits on `infra/vercel-free-preview` are also ignored when the latest commit changes only non-runtime material such as documentation;
- a build proceeds only when the intended preview branch changes application/build inputs such as `Dockerfile.vercel`, `deploy/vercel`, application/config/database/public/resources/routes files, or locked Composer/pnpm inputs.

Vercel's Ignored Build Step contract is inverted from a normal CI success condition: exit code `0` skips the deployment and exit code `1` continues the build. The project setting is therefore operational configuration, not product/application authority.

This guard exists to protect Hobby/free-tier build quota and, critically, to stop normal `main` merges from being treated as Vercel production deployments. It must be reviewed before enabling normal per-PR preview deployments after the baseline is verified. A Vercel deployment whose target is `production` is rejected as SongChart production evidence even if Vercel created it automatically; cancel it rather than allowing it to redefine ADR-0015 or G5.

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

1. Deploy the exact approved `infra/vercel-free-preview` commit as a Vercel Preview deployment.
2. Vercel detects `Dockerfile.vercel` and builds the OCI image.
3. At runtime `deploy/vercel/start.sh` refuses to start without `APP_KEY` or `DB_URL`.
4. Startup applies `php artisan migrate --force --no-interaction` to the isolated preview database.
5. Unless `PREVIEW_SEED_FIXTURES=false`, startup idempotently imports the repository-owned deterministic Artist and Release fixtures through `songchart:fixture:import-artist` and `songchart:fixture:import-release`. No live provider traffic is involved.
6. Laravel listens on `${PORT}` supplied by Vercel.
7. `APP_URL` is derived from `VERCEL_URL` when available.

Never promote a preview deployment to production as evidence for SongChart G5. If Vercel classifies a Git deployment as production because of project Git defaults, cancel it and keep SongChart production lifecycle unchanged.

## Preview versus production parity

Preview is deliberately application-level evidence, not a production-equivalent topology.

| Concern | Preview can verify | Production/G5 still owns |
| --- | --- | --- |
| Laravel routing and public UI | yes | public smoke on the deployed release revision |
| PostgreSQL migrations | yes, against isolated Neon test PostgreSQL | controlled production migration and persistence evidence |
| deterministic canonical Artist/Release/Recording journey | yes | representative journey on the real production environment |
| application `/health` behavior | yes | health after real environment cutover |
| Nginx behavior/configuration | no | ADR-0015 / G5 |
| PHP-FPM topology | no; preview runs the Laravel HTTP server | ADR-0015 / G5 |
| Docker Compose service isolation | no | ADR-0015 / G5 |
| VPS firewall/network hardening | no | #121 / G5 |
| off-host PostgreSQL backup | no | #69/#121 / G5 |
| DNS/TLS/public hostname | no | #69/#121 / G5 |
| immutable production app/web image digests | no | #69/#121 / G5 |
| release-owner production approval | no | G5 |

A green preview must never promote `production-deploy`, replace production-package evidence, or be described as a production deployment.

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
