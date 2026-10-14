# Vercel preview evidence

Issue: #140
Decision: ADR-0016

This record intentionally separates implementation, runtime verification, infrastructure registration, and production deployment.

## Implemented

- Vercel Hobby project `songchart-next-preview` is linked to the SongChart Next repository.
- Neon Free project `SongChart-Next-Preview` provides an isolated PostgreSQL 18 preview database.
- `Dockerfile.vercel` defines the preview-only OCI runtime.
- `deploy/vercel/start.sh` requires preview secrets, migrates the database, imports deterministic repository fixtures, and starts Laravel on `$PORT`.
- Preview secrets are stored only in the Vercel Preview control plane; their values are not recorded in GitHub or this evidence file.
- `DB_URL` uses the direct Neon read-write endpoint for startup DDL/migrations rather than a transaction-pooler endpoint.
- Vercel forwarded HTTPS is trusted only in the preview environment so generated asset/navigation URLs and session cookies remain HTTPS-correct.
- The first automatically-classified Vercel deployment that targeted production was canceled and is not accepted as SongChart deployment evidence.

## Verified runtime — 2026-10-15 (Asia/Bangkok)

Exact source revision:

- Git branch: `infra/vercel-free-preview`
- Git SHA: `53153e9e205e179e20e3bef5d312b75534959186`
- Vercel deployment: `dpl_Bkv5EabKWnJdK2Tnf5ejZansMVre`
- Deployment URL: `https://songchart-next-preview-cd417bnj7-fusumivietnam.vercel.app`
- Vercel target: preview/non-production (`target=null`)
- Deployment state: `READY`
- Container image evidence: `sha256:bb7152403ba8f7490ab6c73cfee481b10b4f59a3df4f0ad810bca2d40ebcfca5`

Runtime evidence:

- startup reported `Nothing to migrate` against the isolated Neon preview database;
- deterministic Artist fixture import succeeded for `Aster Echo`;
- deterministic Release/Recording fixture import succeeded for `Signals at Dawn`;
- Laravel started on the Vercel-provided port;
- `/health` returned HTTP 200 with `{"status":"ok"}`;
- Home returned HTTP 200 and exposed deterministic Artist/Release/Recording discovery data;
- `/search?q=Signals` returned HTTP 200 with the deterministic Release and Recording results;
- representative Artist, Release, and Recording canonical routes each returned HTTP 200;
- generated asset/navigation URLs were HTTPS and the Laravel session cookie was `Secure`;
- preview responses retained `X-Robots-Tag: noindex`;
- runtime-log review for the verification window showed no application error/fatal record for the smoke journey.

Representative canonical routes:

- `/artists/01m4xhg00fj3qgdbn34j43731a/aster-echo`
- `/releases/01m4xhg22zj51ctppzfqxe07y1/signals-at-dawn`
- `/recordings/01m4xhg3et77xdjfkhwxedg1qm/signals-at-dawn`

Exact-head GitHub verification also completed successfully for:

- Project governance;
- Project OS contracts;
- Roadmap health;
- Foundation visual render verification;
- VS-04 launch proof verification;
- G5 VPS baseline verification;
- Foundation application checks.

## Known preview-only operational constraint

A completely empty preview database can spend enough time on startup migrations and fixture imports to exceed the first request's container startup budget. After the isolated preview database is initialized, the idempotent startup path serves normally. This is a preview operational optimization item, not G5/production evidence; production remains governed by ADR-0015 and its explicit release/migration procedure.

## Infrastructure registration boundary

The verified Neon PostgreSQL staging instance can be registered against the existing `postgresql` technology entry. Vercel itself requires its own technology-registry entry before its runtime instance can be added to `INFRASTRUCTURE_REGISTRY.json`; it must not be mislabeled as Laravel/Inertia merely to satisfy schema linkage.

Runtime verification is therefore **verified preview evidence**, but issue #140 should remain open until the Vercel technology/runtime registration is committed and exact-head governance re-verifies that final evidence revision.

This evidence does **not** imply `production-deploy=deployed`, does not satisfy G5 issues #69/#121, and does not authorize live provider traffic or production data.