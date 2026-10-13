# Vercel preview evidence

Issue: #140
Decision: ADR-0016

This record intentionally separates implementation from verification.

## Implemented

- Vercel Hobby project `songchart-next-preview` is linked to the SongChart Next repository.
- Neon Free project `SongChart-Next-Preview` provides an isolated PostgreSQL 18 preview database.
- `Dockerfile.vercel` defines the preview-only OCI runtime.
- `deploy/vercel/start.sh` requires preview secrets, migrates the database, imports deterministic repository fixtures, and starts Laravel on `$PORT`.
- The first automatically-classified Vercel deployment that targeted production was canceled and is not accepted as SongChart deployment evidence.

## Verification pending

Verification remains pending until the Vercel Preview environment has `APP_KEY` and `DB_URL` configured directly in its control plane and an exact current branch SHA passes runtime smoke. Secret values must not be added to this record.

Required evidence after secret configuration:

- exact Git SHA and Vercel deployment ID/URL;
- target is preview/non-production;
- build `READY`;
- migrations and deterministic fixture imports successful;
- `/health` HTTP 200;
- Home/Search plus representative canonical fixture routes successful;
- GitHub PR required checks successful.

Until those checks pass, status is **implemented, not verified, not production-deployed**.
