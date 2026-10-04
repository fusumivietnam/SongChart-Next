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
