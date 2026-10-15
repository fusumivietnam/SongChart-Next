# Preview environment execution track

Issue: #140
Decision: ADR-0016
Runbook: `docs/operations/VERCEL_PREVIEW.md`
Production authority: ADR-0015 and G5 issues #69/#121 remain unchanged.

## Purpose

This is an infrastructure execution track, not a new product vertical slice. It exists to provide zero-cost Internet-accessible test evidence before paying for the first production VPS.

## Lifecycle

- **approved** — zero-cost preview boundary accepted by ADR-0016.
- **implemented** — `Dockerfile.vercel`, preview startup contract, Vercel Hobby project and isolated Neon Free PostgreSQL exist.
- **verified** — exact-SHA Vercel preview is non-production, migrations/fixtures succeed, `/health` is 200, Home/Search and representative canonical routes pass.
- **deployed** — not used for this track; preview/staging evidence must never promote `production-deploy` or satisfy G5.

## Current execution

The active implementation is issue #140 on branch `infra/vercel-free-preview`. Vercel/Neon are replaceable hosting infrastructure only. PostgreSQL remains canonical data authority and SongChart source remains product/domain authority.

## Exit criteria

Close #140 only when the PR is merged and preview verification is either complete with recorded evidence or explicitly blocked solely by operator-owned secret configuration. Any unresolved secret handoff must be documented as manual setup; secret values themselves must never enter repository evidence.
