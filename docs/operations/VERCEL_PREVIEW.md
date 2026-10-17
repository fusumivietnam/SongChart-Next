# Vercel preview runbook

Authority: ADR-0016 and issues #140/#150/#161/#165. This runbook is preview/test only. Production remains ADR-0015 and issues #69/#121.

## Resources

- Vercel project: `songchart-next-preview` on the Hobby plan.
- Git source: `fusumivietnam/SongChart-Next`.
- Database: isolated Neon Free PostgreSQL 18 project `SongChart-Next-Preview`, database `songchart_next_preview`.
- Application container: root `Dockerfile.vercel`.
- Repository smoke verifier: `scripts/preview_smoke.py`.

Provider-generated IDs and credentials are operational details, not application identity and must not be embedded in application code.

## Zero-cost deployment boundary

The preview project exists only for preview/test evidence. A Vercel deployment whose target is `production` is rejected as SongChart production evidence even if Vercel creates it automatically; cancel/ignore it rather than allowing it to redefine ADR-0015 or G5.

The Hobby quota guard skips branches that cannot provide useful application runtime evidence:

```sh
case "$VERCEL_GIT_COMMIT_REF" in main|governance/*|docs/*) exit 0;; *) exit 1;; esac
```

As Vercel's Ignored Build Step, exit `0` skips `main`, `governance/*` and `docs/*`; other non-main branches remain eligible for Preview builds. This is a quota/control-plane optimization, not application authority. A governance/docs work unit that unexpectedly queues a deployment should be canceled instead of accepted as runtime evidence.

Vercel Authentication/SSO remains enabled for preview deployments. Do not make the preview project public merely to simplify automation. For command-line smoke checks, create a temporary authenticated Vercel share URL and pass it to the repository verifier; never commit or print that URL.

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

Do not paste `APP_KEY`, `DB_URL`, database passwords, Vercel share URLs, cookies or access tokens into GitHub issues, pull requests, CI logs or chat.

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

This is intentionally a single-container supervised startup contract. It does not add a queue, workflow engine, second application service or production migration mechanism.

## Standard preview verification gate

Use the same route set for every runtime smoke so a failure has one obvious owner:

- `/health` — must return HTTP 200 and exactly `{"status":"ok"}`;
- `/` — Home;
- `/search?q=Signals` — deterministic fixture search;
- `/artists/01m4xhg00fj3qgdbn34j43731a/aster-echo`;
- `/releases/01m4xhg22zj51ctppzfqxe07y1/signals-at-dawn`;
- `/recordings/01m4xhg3et77xdjfkhwxedg1qm/signals-at-dawn`;
- `/corrections` — public correction intake surface.

HTML routes must return 200 and keep `X-Robots-Tag: noindex`; production-like indexing of preview URLs is a failure. HTTPS must be preserved.

For an SSO-protected Vercel deployment, obtain a temporary share URL through the authenticated Vercel control plane and run:

```sh
python3 scripts/preview_smoke.py --share-url 'TEMPORARY_SHARE_URL'
```

Do not save the share URL in shell history when that matters for the operator environment. The verifier authenticates once into an in-memory cookie jar, then checks only the deployment origin. It never prints response bodies, cookies or the supplied URL.

For a locally authenticated/unprotected endpoint:

```sh
python3 scripts/preview_smoke.py --base-url 'https://preview.example'
```

The verifier retries only HTTP 503 bootstrap responses, honors a bounded `Retry-After` (maximum five seconds per retry), and fails on every other non-200 response. A cold instance may therefore report more than one attempt without being classified as a defect.

### Fast failure classification

```text
Vercel build not READY
  -> build/container/dependency problem; inspect build events

READY but /health never reaches 200
  -> bootstrap, migration, DB_URL/Neon connectivity or application startup problem

/health = 200 but one MVP route fails
  -> application route/query/render regression

all routes = 200 but runtime error/fatal logs exist
  -> runtime defect requiring investigation before acceptance

smoke passes + runtime logs clean
  -> preview runtime verified for that exact deployment SHA
```

This gate is deliberately not a production release gate. It is a cheap way to answer "does the current web actually run, and where does it fail?" before VPS work begins.

## Preview versus production parity

Preview is application-level evidence, not a production-equivalent topology.

| Concern | Preview can verify | Production/G5 still owns |
| --- | --- | --- |
| Laravel routing and public UI | yes | public smoke on the deployed release revision |
| PostgreSQL migrations | yes, against isolated Neon test PostgreSQL | controlled production migration and persistence evidence |
| deterministic canonical Artist/Release/Recording journey | yes | representative journey on the real production environment |
| application `/health` behavior | yes | health after real environment cutover |
| correction intake route/render | yes | production privacy/runtime evidence on real environment |
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
- runtime startup completes without application error/fatal records;
- no startup `FUNCTION_INVOCATION_FAILED` is observed;
- `scripts/preview_smoke.py` passes the standard route set;
- generated asset/navigation URLs remain HTTPS behind Vercel's proxy;
- preview responses retain `X-Robots-Tag: noindex`;
- `MUSICBRAINZ_LIVE_ENABLED=false`;
- no production alias or G5 lifecycle state is changed.

The isolated preview database may already be initialized during normal verification. Do not destroy or recreate it merely to force a slow empty-database bootstrap unless a separate destructive test is explicitly approved.

## Failure and recovery

The preview environment is disposable:

- failed application build: fix the bounded branch and redeploy exact SHA;
- missing/invalid secret: correct only in Vercel Preview environment settings and redeploy;
- pooled-connection migration failure: confirm `DB_URL` uses the direct Neon read-write hostname without `-pooler`, then redeploy the exact preview SHA;
- bootstrap in progress: callers receive bounded `503` readiness responses and retry according to `Retry-After`;
- bootstrap failure: container exits non-zero and must not expose Laravel; inspect runtime logs, correct the bounded defect, and redeploy;
- preview DB corruption/schema experiment: recreate the isolated preview database only with explicit approval, then rerun migrations/fixtures;
- free-tier suspension or quota exhaustion: allow the environment to sleep or recreate it; do not enable paid service without a new approval;
- platform incompatibility: retire the preview infrastructure entry and select another preview provider without modifying SongChart domain/application architecture.

No backup of synthetic preview data is required. Repository migrations and deterministic fixture sources are the recovery authority for this disposable environment.
