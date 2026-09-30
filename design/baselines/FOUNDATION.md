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


## Local/testing preview routes

The candidate is rendered from source only in `local` and `testing` environments; these routes are intentionally absent from production:

- `/_design/foundation/artist`
- `/_design/foundation/artist-long`
- `/_design/foundation/search`
- `/_design/foundation/search-empty`
- `/_design/foundation/search-error`

The preview uses deterministic fixture copy only. It does not read or mutate canonical data and must not be treated as a public product surface.

### Automated GitHub render evidence

`.github/workflows/foundation-visual.yml` renders the five deterministic preview surfaces on a GitHub-hosted Ubuntu runner using the browser supplied by that runner image. It builds static frontend assets first, serves the Laravel preview only on runner-local port 8000, verifies expected hydrated fixture text, rejects accidental Vite development-server references, captures exact 390 × 844 and 1440 × 1024 PNG references, and uploads the PNG files plus rendered DOM and an evidence manifest as a short-lived workflow artifact.

The workflow records the exact pull-request head SHA (or dispatched SHA) as evidence provenance. Passing automation proves that the candidate renders deterministically in a real headless browser at the required reference sizes. It does **not** approve token values, hierarchy, responsive behavior, accessibility, or the `design-authority` lifecycle state. Human keyboard/focus review and owner visual approval on Issue #10 remain required.

This verification intentionally adds no browser-test package or second design-system runtime to the application dependency graph. If browser automation later becomes a maintained product test suite rather than Foundation evidence capture, adopt and register that tooling through the dependency policy first.

### Manual capture procedure

1. Run the approved Docker development stack, or use the exact-SHA GitHub render artifact produced by `foundation-visual.yml`.
2. Open the required preview route.
3. Capture at exactly 390 × 844 CSS px and 1440 × 1024 CSS px.
4. Record the exact Git commit SHA, route, viewport and review date with each screenshot/reference.
5. Verify visible keyboard focus, skip link behavior, long-name wrapping, no-artwork layout, and search empty/error semantics.
6. Human approval or requested changes are recorded on Issue #10 before any `design-authority` lifecycle promotion.
