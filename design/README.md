# Design package

The Design Authority is `design/DESIGN_AUTHORITY.md`. This folder is an authored control package, not a gallery and not a second roadmap.

## Read order for UI work

1. `DESIGN_AUTHORITY.md` — lifecycle/authority and change boundary.
2. `IDENTITY.md` — approved Foundation identity direction.
3. `CONCEPT_CONTRACT.md` — cross-page concept DNA.
4. `tokens/foundation.json` — semantic values.
5. `components/COMPONENT_CONTRACTS.md` — reusable anatomy/states.
6. `PAGE_ARCHETYPES.md` — map the target URL/surface to an approved or candidate page family.
7. `QUALITY_CONTRACT.md` — responsive, accessibility, content/internationalization and state requirements.
8. `patterns/` — page-specific contracts.
9. `baselines/` and `decisions/` — deterministic evidence and approval decisions.

## Authority boundary

- Authored contracts/tokens/decisions are authority according to `DESIGN_AUTHORITY.md`.
- Source implementation is evidence of implementation, not permission to redefine design contracts.
- Screenshots, Figma frames and AI-generated mockups are references/candidates until linked to an authored approval decision and deterministic source evidence.
- Chat memory and generated summaries are never design authority.
- Candidate page archetypes do not imply implemented/verified public product pages.

## Package completeness

The package intentionally covers concept, semantic tokens, shared components, page families, interaction/state behavior, responsive/accessibility/content quality, baseline evidence and change governance. New pages should map to this package before any new design primitive is introduced.

## Selected concept direction (approved by owner; visual implementation pending)

For **every public UI task**, read [Concept A direction decision](decisions/CONCEPT_A_2026_DIRECTION_APPROVAL.md) alongside this Design Authority package. It selects the newer responsive Calm Editorial visual concept, but does **not** make the AI-generated illustration an exact design baseline or approve global CSS/token and shared anatomy changes. [UI Standards Board v1.0](UI_STANDARDS_BOARD_V1.md) is the candidate comparison/evidence board, not a second set of authoritative design tokens.

## Current proposals (not approved authority)

- [UI Standards Board v1.0 — Concept A proposal and source audit](UI_STANDARDS_BOARD_V1.md) compares approved Foundation rules, observed public UI source and candidate consolidation decisions. **Concept A visual direction selected by owner on 2026-11-26; exact runtime visual implementation and material changes still pending review**: the board does not modify or supersede the Design Authority, foundation tokens, page archetypes or runtime styles.
