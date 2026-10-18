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

Issue #140 was closed on 2026-10-15 after the preview infrastructure baseline was recorded. The original `infra/vercel-free-preview` branch is historical implementation provenance, **not** an active work branch or evidence of current preview health. The current preview operating contract is [`VERCEL_PREVIEW.md`](../operations/VERCEL_PREVIEW.md), with historical exact-revision evidence in [`VERCEL_PREVIEW_EVIDENCE.md`](../operations/VERCEL_PREVIEW_EVIDENCE.md); validate live deployment state before claiming a later SHA is verified. UX acceptance for the current MVP is tracked separately by issue #175. Vercel/Neon remain replaceable hosting infrastructure only; PostgreSQL remains canonical data authority and SongChart source remains product/domain authority.

## Exit criteria

Close #140 only when the PR is merged and preview verification is either complete with recorded evidence or explicitly blocked solely by operator-owned secret configuration. Any unresolved secret handoff must be documented as manual setup; secret values themselves must never enter repository evidence.
