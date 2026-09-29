# Design identity — Foundation baseline candidate

Status: candidate for human visual review. The direction is new SongChart Next identity; no prior SongChart visual styling is inherited.

## Product posture
SongChart Next is a search-first music knowledge catalogue with restrained editorial qualities. The UI should prioritize entity identity, relationships, provenance and provider navigation over decorative chrome.

## Identity principles
- Content and music metadata are primary; UI chrome remains quiet.
- Clear hierarchy must distinguish Artist, Release, Recording and provider destination.
- Provenance/unknown/contested states are explicit but not visually alarmist.
- Artwork is supportive rather than mandatory; layouts remain complete with deterministic placeholders.
- Accessibility, narrow-screen reading and long/international names are baseline constraints.
- No visual language should imply streaming playback where SongChart only links to external providers.

## Candidate visual language
This is a reviewable baseline, not yet approved:
- typography: modern system sans stack first; no externally hosted font dependency in Foundation;
- shape: restrained medium radius; avoid pill-heavy/generic dashboard styling;
- color: neutral surfaces/text with one accessible accent family used for actions/links, not entity semantics;
- spacing: 4px base rhythm with semantic spacing steps;
- motion: minimal, reduced-motion safe; no motion required to understand state;
- artwork: square/near-square entity artwork slots with placeholder fallback; Artist page must remain usable without artwork.

Concrete semantic token names live in `design/tokens/foundation.json`. Approval of this identity requires rendered narrow/wide references, not this prose alone.

## Content tone
Concise, factual, provenance-aware. Avoid promotional superlatives and fabricated verification language. Provider actions should say where they lead rather than imply SongChart hosts the media.

## Deferred
Logo/wordmark exploration, custom typeface, expressive motion, dark theme, multi-brand themes and native-client-specific rendering remain outside the first baseline unless separately approved.
