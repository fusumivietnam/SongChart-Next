# Concept A — Calm Editorial 2026 visual direction decision

**Status: APPROVED DIRECTION by product owner on 2026-11-26; runtime visual baseline NOT YET APPROVED.**
**Applies to:** SongChart Next public-web MVP — Home, Search, Artist, Release, Recording, external destinations, Corrections, About/Privacy/Terms/Disclaimer/Support and their shared shell.
**Provenance:** Owner explicitly selected the newer illustrated Concept A / Calm Editorial storyboard (Home, Artist, Release; desktop and mobile) as the direction to follow and asked to persist it in repository Markdown. Direction review of DEC-01–09 was previously agreed. Tracked in [PR #271](https://github.com/fusumivietnam/SongChart-Next/pull/271).
**Foundation:** This *refines* the approved calm knowledge interface/editorial database; it does not revoke or overwrite the 2026-10-02 Foundation approval in [FOUNDATION_BASELINE_APPROVAL.md](FOUNDATION_BASELINE_APPROVAL.md).

## Decision: use this visual direction for every future public design proposal

SongChart Next should resemble a modern, trustworthy **editorial music knowledge atlas**, not a developer dashboard or a streaming player. The newer **Concept A** storyboard is the selected **directional reference**: search-first Home; identity-first Artist; credits/tracklist-first Release; matching narrow/wide views. It is an inspiration for page anatomy and density, **not** a pixel-perfect or runnable specification, nor a license to implement features depicted by generated art.

### Locked visual DNA (keep approved token values until separately changed)

1. White/light surface as the main canvas, slate text hierarchy and one restrained blue identity/interaction accent. Semantic values remain defined solely by `design/tokens/foundation.json`; the generated storyboard is not a color sampler.
2. Modern **system sans** type, readable headings and labels, generous but disciplined editorial whitespace, light dividers/borders before shadows, modest 6/10/14px radius family. Do not switch to a custom font, automatic dark theme or unapproved alternative palette.
3. A **single coherent public header/search/footer language**, distinct from Laravel starter dashboard/auth shells. Home search can be more prominent than header search but must use the same underlying input/action accessibility semantics.
4. Desktop `1440×1024` review: max `72rem` shell, reading `48rem`, identity content may use two columns. Mobile `390×844` review: one column, prioritize essential identity/search, stack supporting data below, prevent unintended horizontal scrolling.
5. The three signature page patterns:
   - **Home:** high-priority search entry and non-personalized *factual* canonical Artist/Release/Recording discovery, including honest zero-data state. Avoid unlicensed visual media, fake “recent/popular” rankings and clutter.
   - **Artist:** page/entity type, full name and disambiguation before secondary artwork; concise structured metadata, relationships/releases, provenance and correction affordance. Missing artwork never compromises identity layout.
   - **Release:** title, artist credits and release data; structured medium/tracklist with links to canonical Recording; provenance/correction. Long names and multi-medium data must work on mobile.
6. Search/results, Recording and support/legal/correction pages **extend the same component vocabulary**, not separate visual themes. Recording external actions are named, permitted provider links; SongChart does not embed a player by default.
7. Components to consolidate **after material implementation approval**: PublicShell/SiteHeader/GlobalSearch/SkipLink, EntityResultRow, EntityTitleBlock, ArtworkPlaceholder, MetadataList, RelationshipSection, ProvenanceBlock, CorrectionLink, StateView; reuse the existing PublicFooter and approved document patterns. No replacement UI library/design system.
8. Keep semantics honest: clear entity type, canonical-vs-provider identities, factual unknown/contested state, proper keyboard focus/labels, accessible contrast, no invented counts or trust badges, and no mandatory login to public discovery.

## Mockup features intentionally NOT approved

- **Inline play buttons, in-app streaming, autoplay** and any behavior implying SongChart hosts provider audio/video. A track links to Recording; a Recording may link out to a permitted named provider.
- Generated portraits, album art, names, artist activity ranges, release dates, track counts and metadata as if canonical data; these are **fictional layout placeholders only**.
- Generic Artists/Releases/Recordings/Documents top-nav routes, working tabs/filters, “recently added”, popularity or personalized recommendations unless backed by separately approved product contracts and actual routes/data.
- Personalized “my corrections” or public reviewer queues/accounts, generic admin dashboard, or relaxing internal reviewer/confirmed-2FA gates.
- Blue bar-chart brand logo as a final identity, decorative wave illustration, hero gradients, dark mode or a revised global font/palette; these are **optional candidates** until separately reviewed and approved.

## Implementation and evidence boundary

- **Approved now:** Concept A as the target design *direction* and the constraints above; document/wireframe comparisons and read-only visual audits.
- **NOT approved yet:** pixel-perfect screenshots, new global styles/tokens, new shell/navigation anatomy in running React, material component hierarchy changes, replacing deterministic baselines, new routes/operations, deployment or merging a UI implementation PR.
- For every future design task, read **this decision** together with `design/DESIGN_AUTHORITY.md`, `design/CONCEPT_CONTRACT.md`, `design/tokens/foundation.json`, owning archetype/pattern and `design/UI_STANDARDS_BOARD_V1.md`. If a proposed feature in a mockup conflicts with approved product/rights policies, the contracts and this explicit exclusions list win.
- Capture **actual** Home, Artist, Release plus Search/Recording/Document/Correction states at both `390×844` and `1440×1024`, exact SHA and deterministic fixture; measure computed CSS/contrast, keyboard/focus, empty/error and long Unicode cases. Then review before/after and obtain a separate authored **material-change approval** before modifying global runtime CSS, shell or token authority.
- Source implementation, CI validation, full browser acceptance and deployment remain distinct from design direction approval; neither the generated concept image nor a green render workflow alone proves them.

**Supersession rule:** Future changes to this selected direction require explicit owner approval recorded under `design/decisions/`. Earlier standalone mockups, chat-only suggestions, unrelated starter UI and previous SongChart repo styling are not allowed to silently replace it.
