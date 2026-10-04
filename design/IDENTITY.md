# Design identity — approved Foundation concept

Status: **approved Foundation concept baseline since 2026-10-02 for VS-01a**. This approval covers the identity direction shared by Shell, Artist and Search; it does not pre-approve later page anatomy, final logo/brand polish, dark mode or product release readiness. No prior SongChart visual styling is inherited.

## Concept anchor

**Calm knowledge interface / editorial database.** SongChart Next should feel like a trustworthy music knowledge catalogue: quiet chrome, strong information hierarchy, restrained editorial spacing, explicit provenance and disambiguation, and minimal decorative UI.

When a new page is designed, preserving this concept takes priority over matching an isolated screenshot.

## Product posture

SongChart Next is a search-first music knowledge catalogue and legal provider-navigation product. The UI prioritizes entity identity, relationships, provenance, correction and destination context over decorative chrome or engagement mechanics.

## Identity principles

- Content and music metadata are primary; UI chrome remains quiet.
- Clear hierarchy distinguishes Artist, Release, Recording and provider destination.
- Provenance, unknown and contested states are explicit but not visually alarmist.
- Artwork is supportive rather than mandatory; layouts remain complete with deterministic placeholders.
- Accessibility, narrow-screen reading, keyboard use and long/international names are baseline constraints.
- No visual language implies streaming playback where SongChart only links to external providers.
- Borders and spacing establish structure before shadows; shadows are exceptional, not the default card language.
- Blue is the primary interaction/identity accent, not an entity-type encoding system.
- Dense metadata stays readable through grouping and hierarchy rather than excessive cards, pills or decoration.

## Approved visual language

- typography: modern system sans stack; no externally hosted font dependency in Foundation;
- shape: restrained medium radius; avoid pill-heavy/generic dashboard styling;
- color: neutral surfaces/text with one accessible accent family for actions/links;
- spacing: 4px base rhythm with semantic spacing steps;
- motion: minimal and reduced-motion safe; no motion required to understand state;
- artwork: square/near-square entity artwork with deterministic placeholder fallback;
- layout: centered content shell with explicit reading-width variants for long-form pages;
- state communication: text + semantics first; color/icon may reinforce but never carry meaning alone.

Concrete semantic values live in `design/tokens/foundation.json`. Cross-page interpretation is governed by `design/CONCEPT_CONTRACT.md`.

## Content tone

Concise, factual and provenance-aware. Avoid promotional superlatives, fabricated verification language, false certainty, manipulative urgency and social-engagement language. Provider actions state where they lead rather than imply SongChart hosts media.

## Deferred

Logo/wordmark exploration, custom typeface, expressive motion, dark theme, multi-brand themes and native-client-specific rendering remain outside this baseline unless separately approved.
