# Design decision — cross-page authority package consolidation

Status: accepted
Date: 2026-10-04
Owning capability: `design-authority`
Issue: #66

## Context

The Foundation Design Authority was approved on 2026-10-02, but authored assets had lifecycle drift: the authority/decision records said approved while `IDENTITY.md` and `tokens/foundation.json` still said candidate. The authority also required reusable component contracts, while `design/components/` did not exist. Future editorial/legal/error/correction/discovery pages therefore risked deriving style from chat or isolated mockups instead of one authored concept.

## Decision

Package the approved Foundation concept as one cross-page authority stack:

`Design Authority -> Identity -> Concept Contract -> Semantic Tokens -> Component Contracts -> Page Archetypes/Patterns -> Quality Contract -> Baselines/Evidence -> Decisions`.

The shared concept is named **calm knowledge interface / editorial database**.

This decision aligns lifecycle metadata for already-approved Foundation identity/tokens and adds reusable cross-page constraints. It does **not** approve later page anatomy by documentation alone. Release/Recording/Credits, discovery, editorial, legal, correction/form and utility/error archetypes remain candidate until their owning work provides deterministic narrow/wide evidence and review.

## Reference-image policy

AI-generated images, design-tool frames and screenshots may inform candidate exploration, but are not source authority. They must not silently redefine semantic tokens, component anatomy or approved page hierarchy. Promotion requires an authored decision linked to deterministic source/evidence.

## Consequences

- Future pages map to a bounded archetype instead of starting from a blank design.
- Design drift is reviewable against one concept contract.
- Foundation status labels are internally consistent.
- No new design framework, runtime dependency or second design-system authority is introduced.
- `public-web` remains candidate; this consolidation is not implementation/verification/deployment evidence.
