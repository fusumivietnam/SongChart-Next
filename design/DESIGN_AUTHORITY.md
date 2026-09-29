# SongChart Next — Design Authority

**Status: Foundation baseline candidate prepared; visual identity and rendered page baselines are NOT YET APPROVED.** Do not import prior SongChart visual styling as default. The project owner approved a new SongChart Next identity direction and Foundation scope of Shell + Artist + Search first; concrete rendered references still require visual review before lifecycle promotion.

## Decision priority
Approved brand/design decisions -> semantic tokens -> approved component contracts -> page/pattern contracts -> linked reference screenshots/stories -> feature implementation. A design-tool prototype or AI-generated image is a candidate until approved and linked to code/baseline.

## Current candidate assets
- `design/IDENTITY.md`
- `design/tokens/foundation.json`
- `design/patterns/SHELL.md`
- `design/patterns/ARTIST.md`
- `design/patterns/SEARCH.md`
- `design/patterns/RELEASE.md`
- `design/baselines/FOUNDATION.md`

These define the review surface but do not by themselves satisfy the rendered mobile+desktop approval gate.

## Required authored assets
- design/IDENTITY.md: brand goals, prohibited motifs, typography/artwork principles, content tone.
- design/tokens/: one semantic-token authority with web/mobile/admin mappings; never scatter raw brand values through feature code.
- design/components/: anatomy, variants, allowed states, accessibility, responsive rules and reuse map.
- design/patterns/: global shell, entity detail, search, provider chooser, loading/empty/error/review.
- design/baselines/: approved screen sizes, deterministic fixtures, screenshot provenance and review decision.
- design/decisions/: accepted changes to tokens/anatomy/layout and their affected consumers.

## Mandatory AI design loop
Identify target surface -> retrieve owning requirements, tokens, related components and approved baselines -> propose reuse/minimum delta -> implement -> deterministic visual+interaction+a11y checks -> review impact -> only then promote new baseline. AI may fill implementation gaps under existing constraints; it cannot silently redefine global layout, font, palette or page anatomy.

## Cross-platform
React web, Filament and future Flutter share identity, tokens, semantics and information hierarchy, not necessarily the same rendering/component implementation. Never equate screenshot similarity with accessibility or correct domain disclosure.

## Approval gate
Before first public UI: approve identity, semantic token values, responsive navigation/global shell, Artist/Search patterns and Foundation-level Release pattern, plus at least one narrow and one wide rendered baseline using deterministic fixtures. Until then visually novel UI is a proposal, not the SongChart style.
