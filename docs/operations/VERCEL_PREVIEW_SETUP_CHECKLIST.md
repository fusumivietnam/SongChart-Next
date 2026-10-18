# Vercel preview initial setup checklist (historical handoff)

**Status: retained setup snapshot, not a live environment checklist.** Issue #140 closed on 2026-10-15; the accepted exact-SHA preview proof is in [VERCEL_PREVIEW_EVIDENCE.md](VERCEL_PREVIEW_EVIDENCE.md). Unchecked boxes below reflect the original operator handoff, **not** a current claim that secrets are missing or that verification has not happened. Current operating instructions and required live control-plane verification belong to [VERCEL_PREVIEW.md](VERCEL_PREVIEW.md); the active UX acceptance audit belongs to issue #175.

This snapshot contains no secret values. Configure or rotate secrets only through the Neon and Vercel control planes; do not copy provider-secret state into this file.

- [x] Vercel Hobby project `songchart-next-preview` linked to `fusumivietnam/SongChart-Next`.
- [x] Neon Free project `SongChart-Next-Preview` created with isolated PostgreSQL 18 database `songchart_next_preview`.
- [x] Preview OCI container and startup contract committed.
- [x] Deterministic Artist/Release fixtures configured for preview startup.
- [ ] Set Vercel **Preview** variable `APP_KEY` to a dedicated Laravel preview key.
- [ ] Set Vercel **Preview** variable `DB_URL` from the Neon preview project's connection details.
- [ ] Redeploy the exact implementation SHA after both secrets are set.
- [ ] Confirm target is Preview/non-production.
- [ ] Confirm migration + fixture import in runtime logs.
- [ ] Confirm `/health` HTTP 200.
- [ ] Confirm Home/Search and canonical Artist/Release/Recording fixture journeys.
- [ ] Record verified staging infrastructure evidence without secret values.

Never put the values of `APP_KEY` or `DB_URL` into this file, a GitHub issue/PR, CI output, or chat.
