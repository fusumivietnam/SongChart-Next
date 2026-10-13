# Vercel preview setup checklist

This checklist contains no secret values. Complete secret configuration directly between the Neon and Vercel control planes.

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
