# Vercel preview runbook

Authority: ADR-0016 and issues #140/#150. This runbook is preview/test only. Production remains ADR-0015 and issues #69/#121.

## Resources

- Vercel project: `songchart-next-preview` on the Hobby plan.
- Git source: `fusumivietnam/SongChart-Next`.
- Database: isolated Neon Free PostgreSQL 18 project `SongChart-Next-Preview`, database `songchart_next_preview`.
- Application container: root `Dockerfile.vercel`.

Provider-generated IDs and credentials are operational details, not application identity and must not be embedded in application code.

## Zero-cost deployment boundary

The preview project exists only for preview/test evidence. A Vercel deployment whose target is `production` is rejected as SongChart production evidence even if Vercel creates it automatically; cancel it rather than allowing it to redefine ADR-0015 or G5.

Any Ignored Build Step used to protect Hobby/free-tier quota is control-plane configuration, not product/application authority. For bounded verification work, an explicit Preview deployment of the exact approved Git SHA may be used without changing SongChart production lifecycle.

## Required Vercel preview environment variables

Configure these for the **Preview** environment only:

| Variable | Secret | Required value/policy |
| --- | --- | --- |
| `APP_KEY` | yes | Dedicated preview Laravel application key generated outside Git/chat. |
| `DB_URL` | yes | Direct Neon read-write PostgreSQL connection URI for the isolated preview database. Do not use the `-pooler` hostname for migrations. |
| `DB_CONNECTION` | no | `pgsql` (also defaulted by `Dockerfile.vercel`). |
| `APP_ENV` | no | `preview` (also defaulted by `Dockerfile.vercel`). |
| `APP_DEBUG` | no | `false`. |
| `SESSION_DRIVER` | no | `file`; ephemeral preview state only. |
| `CACHE_STORE` | no | `file`; ephemeral preview cache only. |
| `QUEUE_CONNECTION` | no | `sync`. |
| `MUSICBRAINZ_LIVE_ENABLED` | no | `false`. |
| `PREVIEW_SEED_FIXTURES` | no | `true` by default; set `false` only when an intentionally empty preview DB is required. |

Do not paste `APP_KEY`, `DB_URL`, database passwords or access tokens into GitHub issues, pull requests, CI logs or chat.

Use Neon's direct read-write endpoint for migrations. Runtime evidence from the baseline preview showed migration failure through the pooled endpoint and successful completion through the direct endpoint.

## Supervised bootstrap and readiness contract

Vercel container startup must bind `$PORT` quickly. SongChart therefore separates **readiness traffic** from **database bootstrap** inside one supervised container lifecycle:

1. `deploy/vercel/start.sh` validates `APP_KEY` and `DB_URL` without printing their values and derives `APP_URL` from `VERCEL_URL` when available.
2. The startup process immediately launches a minimal PHP readiness gate on `${PORT}`.
3. The gate returns HTTP `503`, `Retry-After: 2`, `Cache-Control: no-store`, and `{"status":"bootstrapping"}` for every request. Laravel is not exposed while schema work is incomplete.
4. After the gate is confirmed bound, `deploy/vercel/bootstrap.sh` runs `php artisan migrate --force --no-interaction` against the direct Neon endpoint.
5. Unless `PREVIEW_SEED_FIXTURES=false`, bootstrap idempotently imports the repository-owned Artist and Release fixtures. No live provider traffic is involved.
6. If bootstrap fails, startup fails closed: the readiness gate is terminated and the container exits non-zero.
7. If bootstrap succeeds, startup terminates the readiness gate and hands the same `${PORT}` to `php artisan serve`.
8. Normal Laravel `/health`, Home, Search and canonical routes are served only after the hand-off.

This is intentionally a single-container supervised startup contract. It does not add a queue, workflow engine, second application service or production migration mechanism. Vercel's Docker container contract requires an HTTP server on `$PORT`; it does not provide SongChart with a repository-owned deploy-time migration authority, so database bootstrap remains explicit application startup work while first-request readiness is bounded.

## Preview versus production parity

Preview is application-level evidence, not a production-equivalent topology.

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

- repository contract tests prove the readiness gate is bound before bootstrap and Laravel hand-off occurs only after bootstrap;
- Vercel build state is `READY` and source SHA matches the intended Git commit;
- deployment target is preview/non-production;
- runtime logs show migrations and deterministic fixture imports complete without error;
- no startup `FUNCTION_INVOCATION_FAILED` is observed from waiting for migrations before `$PORT` is bound;
- after bootstrap, `GET /health` returns 200;
- `/` renders the Home surface;
- `/search` returns deterministic fixture entities for an applicable query;
- representative canonical Artist/Release/Recording routes render successfully;
- generated asset/navigation URLs remain HTTPS behind Vercel's proxy;
- `MUSICBRAINZ_LIVE_ENABLED=false`;
- no production alias or G5 lifecycle state is changed.

The isolated preview database may already be initialized during normal verification. Do not destroy or recreate it merely to force a slow empty-database bootstrap unless a separate destructive test is explicitly approved. Static contract tests plus exact-deployment runtime evidence are sufficient for this bounded cold-start fix.

## Failure and recovery

The preview environment is disposable:

- failed application build: fix the bounded branch and redeploy exact SHA;
- missing/invalid secret: correct only in Vercel Preview environment settings and redeploy;
- pooled-connection migration failure: confirm `DB_URL` uses the direct Neon read-write hostname without `-pooler`, then redeploy the exact preview SHA;
- bootstrap in progress: callers receive bounded `503` readiness responses and should retry according to `Retry-After`;
- bootstrap failure: container exits non-zero and must not expose Laravel; inspect runtime logs, correct the bounded defect, and redeploy;
- preview DB corruption/schema experiment: recreate the isolated preview database only with explicit approval, then rerun migrations/fixtures;
- free-tier suspension or quota exhaustion: allow the environment to sleep or recreate it; do not enable paid service without a new approval;
- platform incompatibility: retire the preview infrastructure entry and select another preview provider without modifying SongChart domain/application architecture.

No backup of synthetic preview data is required. Repository migrations and deterministic fixture sources are the recovery authority for this disposable environment.
