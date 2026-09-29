# Pattern — Artist detail (candidate)

## Hierarchy
1. Entity type + Artist name.
2. Artwork/placeholder and concise identity metadata.
3. Disambiguation/provenance where useful.
4. Releases/relationships preview.
5. Permitted external destinations only when available.
6. Correction/provenance affordances at lower hierarchy.

## Narrow
Single column. Name and disambiguation precede secondary metadata. Artwork must not push the primary identity below the first useful viewport.

## Wide
Two-column hero is allowed: bounded artwork column + flexible identity/content column, followed by full-width sections. Long names and missing artwork must not collapse layout.

## Required states
Missing artwork, long/international name, unknown country/type, contested metadata, no releases, no provider destinations, loading and recoverable error.
