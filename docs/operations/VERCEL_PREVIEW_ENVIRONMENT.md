# Vercel preview environment inventory

Environment class: staging/preview (non-production)
Issue: #140
Decision: ADR-0016

| Component | Provider | Plan | Identifier | Authority |
| --- | --- | --- | --- | --- |
| HTTP preview | Vercel | Hobby | `songchart-next-preview` | replaceable runtime only |
| Preview PostgreSQL | Neon | Free | `SongChart-Next-Preview` / `songchart_next_preview` | hosting only; PostgreSQL remains canonical DB technology |
| Source | GitHub | repository | `fusumivietnam/SongChart-Next` | repository source of truth |

Secret values and provider connection credentials are intentionally excluded. Production environment identity remains unset until G5 execution under #69/#121.
