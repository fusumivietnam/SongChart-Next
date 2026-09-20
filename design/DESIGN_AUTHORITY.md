# SongChart Next — Design Authority

**Status: framework accepted; visual identity and page baselines NOT YET APPROVED.** Do not import prior SongChart visual styling as default; do not treat proposed editorial/search-first concepts as approved brand.

## Decision priority
Approved brand/design decisions -> semantic tokens -> approved component contracts -> page/pattern contracts -> linked reference screenshots/stories -> feature implementation. A design-tool prototype or AI-generated image is a candidate until approved and linked to code/baseline.

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
Before first public UI: approve identity, responsive navigation/global shell, Artist/Search/Release page patterns and at least mobile+desktop baselines. Until then visually novel UI is a proposal, not the SongChart style.
