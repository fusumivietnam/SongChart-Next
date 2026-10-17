# Vercel preview historical baseline evidence

Issue: #140
Decision: ADR-0016
Evidence class: **historical runtime baseline — not current preview state**

This record preserves the first accepted Vercel + Neon runtime verification. It must not be read as the current deployment, current branch, current route inventory, current cold-start behavior, or current Vercel control-plane configuration. Current operating behavior belongs to `docs/operations/VERCEL_PREVIEW.md`; current runtime/control-plane state must be queried live from Vercel.

## Baseline verification — 2026-10-15 (Asia/Bangkok)

- Git branch: `infra/vercel-free-preview`
- Git SHA: `53153e9e205e179e20e3bef5d312b75534959186`
- Vercel deployment: `dpl_Bkv5EabKWnJdK2Tnf5ejZansMVre`
- target: preview/non-production (`target=null`)
- state at verification: `READY`
- database: isolated Neon PostgreSQL 18 preview database
- container image evidence: `sha256:bb7152403ba8f7490ab6c73cfee481b10b4f59a3df4f0ad810bca2d40ebcfca5`

The baseline proved migrations against the direct Neon endpoint, deterministic Artist/Release/Recording fixtures, `/health`, Home, Search and canonical Artist/Release/Recording routes, HTTPS-correct generated URLs, Secure session cookies, `X-Robots-Tag: noindex`, and no application error/fatal records during the smoke window.

## Superseded observations

The original baseline observed that a completely empty preview database could spend enough time in startup migrations/imports to exceed an initial request budget. That observation is **historical**. PR #153 / issue #150 subsequently introduced the supervised readiness gate: the container binds `$PORT` immediately, returns bounded `503 bootstrapping` while migrations/fixtures run, then hands the port to Laravel only after bootstrap succeeds. Current behavior is defined by `VERCEL_PREVIEW.md`, not by the old observation.

The original evidence also predated VS-05c public correction intake. Its statement that preview evidence did not authorize correction intake was true for that revision only. `/corrections` is now part of the standard preview smoke contract; this does not make preview production or authorize canonical mutation/reviewer workflows.

## Evidence interpretation rule

Historical evidence is append-only proof that a specific revision/runtime was verified. It is not a cached status document. Before recording new preview runtime evidence, query the live control plane and confirm at minimum:

1. deployment source SHA equals the intended exact Git revision;
2. deployment target is preview/non-production;
3. Vercel Authentication/SSO protection remains enabled for preview access;
4. the Ignored Build Step still matches the repository runbook policy;
5. preview provider/data boundaries remain intact (`MUSICBRAINZ_LIVE_ENABLED=false`, synthetic preview data only);
6. `scripts/preview_smoke.py` passes the current route set;
7. runtime error/fatal logs are clean for the verification window.

If any live provider fact cannot be queried, record it as unknown rather than copying a value from this file.

## Lifecycle boundary

This evidence supports the registered **verified staging preview** baseline only. It never implies `production-deploy=deployed`, never satisfies G5 issues #69/#121, and never substitutes for live preview verification of a later exact SHA.
