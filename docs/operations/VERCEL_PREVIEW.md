# Vercel preview runbook

Authority: ADR-0016 and issues #140/#150/#161/#165/#167. This runbook is the **current operating contract** for preview/test. Historical runtime proof lives in `VERCEL_PREVIEW_EVIDENCE.md`; current provider/control-plane state must be queried live. Production remains ADR-0015 and issues #69/#121.

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

As Vercel's Ignored Build Step, exit `0` skips `main`, `governance/*` and `docs/*`; other non-main branches remain eligible for Preview builds. `Project governance` enforces the matching branch-safety contract: a `docs/*` or `governance/*` PR may not carry runtime-impacting paths. If runtime work is needed, use a runtime-eligible branch rather than weakening the skip guard.

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
5. Unless `PREVIEW_SEED_FIXTURES=false`, bootstrap idempotently imports repository-owned deterministic Artist/Release/Recording fixtures. No live provider traffic is involved.
6. If bootstrap fails, startup fails closed: the readiness gate is terminated and the container exits non-zero.
7. If bootstrap succeeds, startup terminates the readiness gate and hands the same `${PORT}` to `php artisan serve`.
8. Normal Laravel `/health`, Home, Search and canonical routes are served only after the hand-off.

## Standard preview verification gate

Use the same route set for every runtime smoke:

- `/health` — HTTP 200 and exactly `{"status":"ok"}`;
- `/` — Home;
- `/search?q=Signals`;
- `/artists/01m4xhg00fj3qgdbn34j43731a/aster-echo`;
- `/releases/01m4xhg22zj51ctppzfqxe07y1/signals-at-dawn`;
- `/recordings/01m4xhg3et77xdjfkhwxedg1qm/signals-at-dawn`;
- `/corrections` — public correction intake surface;
- `/about`, `/privacy`, `/terms`, `/disclaimer`, `/support` — public legal and support surfaces.

HTML routes must return 200 and keep `X-Robots-Tag: noindex`; HTTPS must be preserved.

For an SSO-protected deployment, obtain a temporary share URL through the authenticated Vercel control plane and run:

```sh
python3 scripts/preview_smoke.py --share-url 'TEMPORARY_SHARE_URL'
```

For a repository-owned alternative to external metered browser services, run the GitHub Actions workflow **Protected Preview smoke (manual)** (`.github/workflows/protected-preview-smoke.yml`) with the exact source SHA from the chosen Vercel Preview deployment. Set up the protected GitHub Actions environment `preview-test` with `VERCEL_AUTOMATION_BYPASS_SECRET`, provisioned through Vercel Deployment Protection → Protection Bypass for Automation. Select **Actions → Protected Preview smoke (manual) → Run workflow**, supply the deployment-specific HTTPS Vercel origin (not a secret or a share URL) and its exact source SHA, and inspect the step summary. Restrict environment authorization to trusted maintainers; the project-level bypass is sensitive and must be revoked/rotated in Vercel if exposed. Keep Vercel SSO enabled; do not put bypass values in workflow inputs, issues, artifacts or screenshots. The smoke sends a bypass header only to the selected deployment and forbids redirects while the credential is present. The input SHA is an **operator-declared provenance label**, not cryptographic proof that the share URL points to that deployment; verify the Vercel deployment ID and source SHA separately before citing the run. This workflow verifies HTTP routes only and does not perform interactive accessibility/responsive/Corrections POST acceptance. The existing local Docker and visual/browser CI remain useful without any Vercel credentials.

The verifier retries only HTTP 503 bootstrap responses, honors a bounded `Retry-After` (maximum five seconds per retry), and fails on every other non-200 response.

### Fast failure classification

```text
Vercel build not READY
  -> build/container/dependency problem

READY but /health never reaches 200
  -> bootstrap, migration, DB_URL/Neon connectivity or application startup problem

/health = 200 but one MVP route fails
  -> application route/query/render regression

all routes = 200 but runtime error/fatal logs exist
  -> runtime defect

smoke passes + runtime logs clean
  -> application runtime verified for that exact deployment SHA
```

## Live control-plane acceptance

Before recording **new** preview runtime evidence, query Vercel live rather than copying provider state from a Markdown evidence file. Confirm all of:

1. deployment source SHA equals the intended exact Git revision;
2. deployment target is preview/non-production;
3. Vercel Authentication/SSO protection is enabled for preview access;
4. the Ignored Build Step matches the approved `main|governance/*|docs/*` skip policy;
5. Preview environment retains the approved non-production provider/data boundary, including `MUSICBRAINZ_LIVE_ENABLED=false`;
6. runtime startup has no application error/fatal record for the verification window;
7. `scripts/preview_smoke.py` passes the current standard route set;
8. no production alias or G5 lifecycle state is changed.

If a provider fact cannot be queried, record it as **unknown** and do not infer it from historical evidence. A historical deployment ID proves only its own recorded revision and time window.

## Preview versus production parity

Preview is application-level evidence, not a production-equivalent topology.

| Concern | Preview can verify | Production/G5 still owns |
| --- | --- | --- |
| Laravel routing and public UI | yes | public smoke on the deployed release revision |
| PostgreSQL migrations | yes, against isolated Neon test PostgreSQL | controlled production migration and persistence evidence |
| deterministic canonical journey | yes | representative journey on the real production environment |
| application `/health` behavior | yes | health plus external production monitoring/alert routing |
| correction intake route/render | yes | production privacy/runtime evidence on real environment |
| Nginx/PHP-FPM/Compose topology | no | ADR-0015 / G5 |
| VPS firewall/network hardening | no | #121 / G5 |
| off-host PostgreSQL backup | no | #69/#121 / G5 |
| DNS/TLS/public hostname | no | #69/#121 / G5 |
| immutable production image digests | no | #69/#121 / G5 |
| release-owner production approval | no | G5 |

A green preview must never promote `production-deploy`, replace production-package evidence, or be described as a production deployment.

## Failure and recovery

The preview environment is disposable:

- failed application build: fix the bounded branch and redeploy exact SHA;
- missing/invalid secret: correct only in Vercel Preview environment settings and redeploy;
- bootstrap in progress: callers receive bounded `503` readiness responses and retry according to `Retry-After`;
- bootstrap failure: container exits non-zero and must not expose Laravel;
- preview DB corruption/schema experiment: recreate the isolated preview database only with explicit approval, then rerun migrations/fixtures;
- free-tier suspension or quota exhaustion: allow the environment to sleep or recreate it; do not enable paid service without approval;
- platform incompatibility: retire the preview infrastructure entry and select another preview provider without modifying SongChart domain/application architecture.

No backup of synthetic preview data is required. Repository migrations and deterministic fixtures are the recovery authority for this disposable environment.
