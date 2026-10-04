# SongChart Next — Design Authority

**Status: Foundation baseline approved on 2026-10-02 for VS-01a.** The approved threshold is sufficiently consistent, responsive, accessible and stable; this is not a final-brand-polish claim. Do not import prior SongChart visual styling as default.

## Decision priority

Approved brand/design decisions -> concept contract -> semantic tokens -> approved component contracts -> page/pattern contracts -> linked reference screenshots/stories -> feature implementation.

A design-tool prototype, AI-generated image or standalone screenshot is a **candidate/reference** until approved and linked to deterministic source/evidence. It never overrides authored tokens/contracts by visual similarity alone.

## Approved Foundation authority

- `design/IDENTITY.md` — concept and identity posture.
- `design/CONCEPT_CONTRACT.md` — cross-page visual/layout/interaction DNA.
- `design/tokens/foundation.json` — semantic values.
- `design/components/COMPONENT_CONTRACTS.md` — shared component anatomy/state rules; only already-rendered Foundation behavior inherits Foundation approval.
- `design/QUALITY_CONTRACT.md` — responsive, accessibility, content/internationalization and state quality rules.
- `design/PAGE_ARCHETYPES.md` — complete page-family inventory with explicit approved/candidate/deferred states.
- `design/patterns/SHELL.md`.
- `design/patterns/ARTIST.md`.
- `design/patterns/SEARCH.md`.
- `design/patterns/RELEASE.md` — contract-level/candidate for its later rendered surface.
- `design/baselines/FOUNDATION.md`.
- `design/decisions/FOUNDATION_BASELINE_APPROVAL.md`.

The approved Foundation visual evidence covers Shell + Artist + Search. Later page families in `PAGE_ARCHETYPES.md` are deliberately **candidate** until their owning slice supplies deterministic render/accessibility evidence and a review decision.

## Concept lock

All future public pages start from the same concept: **calm knowledge interface / editorial database**. Implementations may vary their content anatomy, but they must reuse the approved visual DNA, semantic tokens, shared interaction/state language and quality constraints before proposing a new primitive.

The following are material global changes and require Design Authority review/decision: global font, palette, shell width/navigation, common component anatomy, shared focus/accessibility behavior, entity-detail hierarchy, or global state semantics.

## Required authored package

The minimum maintainable package is:
- identity/concept;
- semantic tokens;
- shared components and state anatomy;
- page archetype inventory;
- responsive/accessibility/content quality contract;
- concrete page patterns;
- deterministic baselines/evidence;
- decisions recording approvals/material changes.

A new page does **not** require a new design system. It maps to an existing archetype, reuses shared components/tokens, then adds only the smallest page-specific contract needed.

## Mandatory AI/developer design loop

1. Identify target surface and its page archetype/status.
2. Retrieve owning product requirements, concept contract, tokens, component contracts, page pattern and approved baselines.
3. Reuse existing anatomy and propose the minimum delta.
4. Implement with deterministic fixture content.
5. Check narrow/wide responsive behavior, keyboard/focus, semantic accessibility and relevant loading/empty/error states.
6. Review impact against material-change boundary.
7. Promote a new/changed baseline only with an authored decision and exact-source evidence.

AI may fill implementation gaps under existing constraints; it cannot silently redefine global layout, font, palette, component anatomy or page hierarchy. Chat history is never Design Authority.

## Cross-platform

React web, Filament and future Flutter share identity, tokens, semantics and information hierarchy, not necessarily the same rendering/component implementation. Never equate screenshot similarity with accessibility or correct domain disclosure.

## Lifecycle boundaries

- `design-authority`: approved Foundation concept/baseline.
- `public-web`: remains candidate until actual product surfaces are implemented and verified.
- Candidate Release/Recording/Credits/discovery/editorial/legal/form/error archetypes are planning/design contracts, not implementation evidence.
- Production deployment and launch remain separate gates.
