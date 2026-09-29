# Foundation rendered baseline checklist

Status: candidate contract; rendered evidence still required before Issue #10 can close.

## Deterministic fixtures
Review at minimum:
- Artist: normal Latin name with artwork placeholder.
- Artist: very long international/mixed-script name, no artwork.
- Search: mixed Artist/Release/Recording result set with duplicate/similar names.
- Search: empty/no-results/error state.

## Required viewport references
- narrow: 390 x 844 CSS px (or equivalent documented narrow viewport)
- wide: 1440 x 1024 CSS px (or equivalent documented wide viewport)

## Approval evidence
For each required page/state, store or link:
- exact fixture/revision;
- viewport;
- rendered screenshot/reference provenance;
- accessibility/keyboard notes;
- review decision and date.

Text contracts and token files alone do not satisfy approval. The first approved baselines must cover Shell + Artist + Search on narrow and wide layouts. Release may remain contract-level until VS-02 provided the Artist/Search decisions do not conflict with it.
