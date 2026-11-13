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

**Git-triggered deployments are disabled by default** in repository-root `vercel.json` using `git.deploymentEnabled: false`. Unlike an Ignored Build Step, this prevents Vercel from creating automatic deployments on every pushed commit; it applies to `main` and all feature/test/governance branches. Source authority: [Vercel Git configuration](https://vercel.com/docs/project-configuration/git-configuration). The project remains connected to Git; no Git disconnect, production deployment or public Preview is authorized by this configuration.

**Incident boundary (issue #215):** Vercel Container Registry returned `denied: repository has reached the maximum allowed number of images` while pushing the Preview image for SHA `39263bc`. Until the image-count limit is resolved, the provider-side Ignored Build Step is temporarily set to `exit 0` to fail closed. It is an emergency provider setting, not the normal repository policy and not evidence of a successful Preview. Vercel may still record canceled deployments when this older mechanism is used. Do not restore permissive auto-build behavior merely to test the registry.

**Deliberate Preview acceptance:** After examining registry capacity and existing image references, an authorized operator may use Vercel Dashboard → project → Deployments → Create Deployment with an exact Git SHA / Preview context (see [Vercel Git deployment docs](https://vercel.com/docs/git)), or a reviewed Vercel CLI workflow, only after checking that it respects the repository opt-out and current Ignored Build Step. Verify environment target is Preview, SSO/protection remains enabled, isolated Neon configuration is correct and the SHA is the intended tested revision. If the deployment is blocked by either gate, stop; do not silently override it, expand branch eligibility, disconnect Git or create production deployment. Any documented temporary gate change must be reviewed and reverted once acceptance finishes. Record the resulting deployment URL/ID and runtime evidence in #215/#175 without exposing credentials. Passing GitHub Actions alone is not runtime acceptance.

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
4. repository-root `vercel.json` on the verified source revision has `git.deploymentEnabled: false`; check the provider-side Ignored Build Step separately: during incident #215 it is temporarily `exit 0`, and any supervised one-off Preview change must be explicitly reviewed, scoped and reverted afterward; do **not** restore the obsolete `main|governance/*|docs/*` branch-skip policy;
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

## Protected Preview browser verification boundary (#215 / #175)

The workflow `protected-preview-browser-preflight.yml` is **manual only**, restricted to trusted `main`, the protected `preview-test` GitHub environment and an exact deployment URL, ID and source SHA. It independently verifies READY Preview provenance through authenticated Vercel REST and performs one same-origin, redirect-blocked bypass-cookie bootstrap. The cookie is immediately discarded in memory: no browser session, DOM assertion, screenshot, correction POST, token or cookie artifact is produced. This proves the authentication boundary **only**, not #175 UX acceptance. This narrow step reuses the existing PR #216 Python modules without installing a browser dependency.

Operator-owned setup, **before any manual dispatch**:

1. Confirm `preview-test` environment protection requires an authorized human reviewer and is restricted to the trusted default branch. Preserve the existing Vercel SSO and `VERCEL_AUTOMATION_BYPASS_SECRET` secret; do not reproduce or rotate its value here.
2. Review Vercel access-token permissions. Provision a **separate**, shortest practical lifetime token with the narrowest team/project scope enabling authenticated deployment GET; label it `VERCEL_API_READ_TOKEN` as a `preview-test` environment secret. The workflow executes no Vercel mutation API. If the provider/account cannot scope the token adequately, **do not add a broad management token**; stop and use authorized manual review instead. Configure non-secret `VERCEL_TEAM_ID` in the same environment variables.
3. Before explicit-input preflight, an operator checks that the deployment is READY, is Preview (not production), belongs to the expected project, and matches the intended source SHA. Never enter share URLs, cookies or token values as workflow inputs. The read-only browser probe instead supports **zero-input discovery** of a matching READY deployment (bounded to 30 days) through the scoped Vercel API credential; all three explicit inputs may override discovery only when supplied together.
4. Dispatch either `Protected Preview browser credential preflight (manual)` for cookie/provenance verification only, or the separately reviewed `Protected Preview browser read probe (manual candidate)` on trusted `main` for two read-only viewports. Approve the `preview-test` environment gate and inspect only sanitized phase codes and fixed verdicts. A failed/blocked run does not authorize relaxing protection.

The separate browser handoff is now implemented as `protected-preview-browser-read-probe.yml` with hash-locked Python Playwright, the runner's existing Chromium, a host-only cookie and an origin-only request guard. The workflow is **manual-only**, `main`-only, protected by `preview-test`, has a six-minute job ceiling and a 150-second bounded provenance/browser command, and publishes no screenshots, traces, artifacts, cookies or page data. `scripts/verify_protected_preview_browser.py` checks Home at 390×844 and 1440×1024 for successful read response, a body element and no horizontal overflow. Known safe read failures are `HTTP_RESPONSE_REJECTED`, `DOCUMENT_MISSING` and `HORIZONTAL_OVERFLOW`; unclassified exceptions remain `SAFE_FAILURE`. A previously authorized run reached mobile navigation but failed before viewport verification; PR #244 improved fixed-code classification without establishing a passing protected browser run. **No successful live protected-browser UX acceptance has been established by this repository change.** The #175 interactive UX matrix remains incomplete/UNKNOWN for hydration, keyboard/focus, correction submission, empty/error states and legal/support journeys. `protected-preview-smoke.yml` remains the separate HTTP-only smoke owner. No production/deployment authority or automatic trigger is introduced.

An unsuccessful manual credential preflight prints only a fixed classification, never the underlying exception, HTTP response, token or cookie: `CONFIG_MISSING` (required environment values absent), `INPUT_INVALID` (origin/ID/SHA shape), `API_LOOKUP_FAILED` (authenticated Vercel control-plane request unavailable or rejected), `PROVENANCE_REJECTED` (deployment metadata or response validation), `BYPASS_REJECTED` (deployment refused the bypass request), `BYPASS_UNAVAILABLE` (network failure), `COOKIE_INVALID` (unexpected or unsafe cookie) or `UNCLASSIFIED` (other caught local failure). These categories narrow operator investigation but do not authorize loosening checks, posting secrets, rotating credentials automatically or blind retries. Inspect deployment metadata and environment configuration using the normal authorized provider UI; only retry after correcting a demonstrated cause.

For `x-vercel-set-bypass-cookie: true`, Vercel documents a possible redirect carrying `Set-Cookie`. The bootstrap may inspect the cookie on a 302/303/307/308 response **without following that redirect** only when its `Location` resolves to the exact deployment HTTPS root. External, path-changing, query-bearing or missing destinations fail closed. A valid response still needs the existing strict host-only cookie validation; no request replays the bypass secret after the initial GET. `BYPASS_REJECTED` therefore remains possible for an actual refusal or an unsafe redirect, and a successful preflight is not UX acceptance.

### Browser-context handoff (implemented for manual read-only probe)

`scripts/preview_browser_context.py` validates the exact Preview origin and host-only cookie contract, registers an origin-only route before injecting the cookie with Playwright's URL-scoped API, and aborts requests to other origins. `scripts/verify_protected_preview_browser.py` now boots a separate disposable Chromium context for each viewport with `service_workers='block'`, invokes provenance/cookie bootstrap first and closes contexts on all outcomes. The standalone loopback containment checks and deterministic fake-context tests are supporting security evidence only: neither proves public Preview UX completeness or authorizes broader credential-bearing navigation.

The isolated Python browser dependency lives in `requirements-browser.in` and its hash-pinned `requirements-browser.lock`, separate from Composer, application pnpm and production images. Regenerate only with `uv pip compile --python-version 3.12 --generate-hashes --output-file requirements-browser.lock requirements-browser.in`; validate with `uv pip install --dry-run --python <python-3.12> --require-hashes -r requirements-browser.lock`. The locked dependency is installed only by explicit, protected, trusted-main verification; it is **not** permission to install a browser in production, dispatch the protected workflow without owner approval or broaden the scoped read-only proof.

The optional `preview-browser-loopback-containment.yml` provides an independent narrow security gate, **manual-only** on trusted `main` with no credentials: it creates two temporary TLS loopback fixtures and uses the runner's existing Chrome plus the hash-locked Python package to ensure cross-origin assets, redirects and popup requests never reach the second server. No screenshot, browser report, secret, Preview URL or artifact is retained. A green loopback run proves only that particular Chromium/request interception boundary; it does not authorize a protected Preview session or complete the #175 matrix.
