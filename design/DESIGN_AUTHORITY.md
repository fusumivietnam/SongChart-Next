# SongChart Next — Design Authority

**Status: Foundation baseline approved on 2026-10-02 for VS-01a.** The approved threshold is sufficiently consistent, responsive, accessible and stable; this is not a final-brand-polish claim. Do not import prior SongChart visual styling as default.

## Decision priority
Approved brand/design decisions -> semantic tokens -> approved component contracts -> page/pattern contracts -> linked reference screenshots/stories -> feature implementation. A design-tool prototype or AI-generated image is a candidate until approved and linked to code/baseline.

## Current approved Foundation assets
- `design/IDENTITY.md`
- `design/tokens/foundation.json`
- `design/patterns/SHELL.md`
- `design/patterns/ARTIST.md`
- `design/patterns/SEARCH.md`
- `design/patterns/RELEASE.md`
- `design/baselines/FOUNDATION.md`

These assets, together with the reviewed narrow/wide evidence and decision record in `design/decisions/FOUNDATION_BASELINE_APPROVAL.md`, define the approved Foundation baseline.

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

## Approval state
The Foundation gate is approved for VS-01a. Material changes to global layout, font, palette, page anatomy or accessibility behavior still require the normal Design Authority review loop and a new/updated decision record. Later Release/provider/admin/mobile surfaces remain separately scoped.
