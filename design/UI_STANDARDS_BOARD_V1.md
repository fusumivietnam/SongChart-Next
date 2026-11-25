# SongChart Next — UI Standards Board v1.0 (Concept A)

**Status:** PROPOSED / ALL DEC-01–09 DIRECTIONS ENDORSED BY OWNER / MATERIAL CHANGES NOT APPROVED. **Decision:** the owner selected Concept A (Calm Editorial), and on 2026-11-25 agreed with the *direction* of all nine DEC items. This is **not** approval to merge, change global tokens, alter production UI/navigation/typography/shared behavior, or activate deferred capabilities. Created 2026-11-25 against the repository's current `main` source. **Scope:** public-web MVP; internal reviewer/admin remains a separate candidate. **Issues:** [#175](https://github.com/fusumivietnam/SongChart-Next/issues/175), [#253](https://github.com/fusumivietnam/SongChart-Next/issues/253).

> This is a comparison board and source audit, not an additional authoritative design system. Until an explicit owner-approved decision is recorded under `design/decisions/`, existing `design/DESIGN_AUTHORITY.md`, concept, tokens, patterns, components, archetypes and QA contracts remain authoritative. The board must not be used to silently rewrite those contracts.

## 1. Status vocabulary and decision rules

- **APPROVED:** explicitly approved Foundation or subsequent Design Authority decision within its stated surface scope. Approval of a concept/token does **not** automatically approve all pages.
- **IMPLEMENTED (source):** observed in the indicated source file. Source existence is not browser/visual acceptance.
- **CANDIDATE:** proposed future component, page change or visual variation; no permission to implement a global change.
- **GAP / REVIEW:** code-level divergence, duplicated anatomy, unresolved correspondence or a behavior requiring browser measurements. Not automatically a demonstrated UX defect.
- **DEFERRED / BLOCKED:** outside MVP or separate authorization and legal/provider activation.
- **VERIFIED:** requires exact SHA, deterministic fixture, both 390×844 and 1440×1024 evidence, keyboard/focus/states and owner review. This board itself verifies **no new browser behavior**.

Approval hierarchy: Design Authority decisions → concept contract → semantic tokens → shared component contracts → page archetype/pattern → exact-SHA screenshot and test evidence → implementation. Source audit is diagnostic evidence, not authorization.

## 2. Concept A — Calm Editorial comparison

| Aspect | APPROVED Foundation source of truth | PROPOSED v1.0 review direction | Boundary |
| --- | --- | --- | --- |
| Identity | Trustworthy calm knowledge interface / editorial database; metadata and relationships first: `design/IDENTITY.md`, `design/CONCEPT_CONTRACT.md` | **Retain** calm editorial; emphasize music context via information hierarchy and factual media, not flashy playback or pseudo-rankings | Retention of existing concept is not approval for revised layouts |
| Canvas | White `#FFFFFF`, quiet `#F8FAFC` surface, `#F1F5F9` subtle | Keep approved palette for comparison; no alternative color proposal in this version | Global palette LOCKED until material-change review |
| Text | `#0F172A` primary, `#475569` muted, `#CBD5E1` borders | Align headings/secondary labels and distinguish metadata vs explanatory copy | Contrast must be measured |
| Actions | Blue `#1D4ED8`, hover `#1E40AF`, focus `#2563EB` | One primary action per local task, explicit external provider destination | Never encode Artist vs Release by different accent colors |
| Typography | System sans stack; 12/14/16/18/24/32/36px; 1.2/1.5/1.65 line heights | Rationalize page title/section/meta assignments; no custom font or global type scale change yet | Typeface/size changes are material |
| Spacing / shape | 4px base; 4/8/12/16/24/32/48/64px; 6/10/14px radii | Common anatomy for search/header, metadata rows, sections and forms | Avoid arbitrary pill or card-per-section |
| Layout | Content max 72rem; reading max 48rem; compact reading 40rem; mobile 16px and wide 24px gutters | One responsive public shell and reading-width variant; mobile identity-first | Shell width/nav changes are material |
| Interaction | 44px pointer target, 2px focus ring + 2px offset; 120/180ms motion; reduced-motion safe | Standardize keyboard focus/search form/empty/error/provenance semantics | Require separate interaction evidence |
| Data claims | Provider claims ≠ canonical IDs; do not invent artwork, rankings, verification, playback | Promote informative disambiguation/provenance; explicit external navigation | Preserve rights and correction-review boundaries |

**Illustrative visual sample A (not an approved screenshot):** white header with wordmark and compact search; 72rem shell; page type label → large identity title → contextual disambiguation → data/relationships → provenance/correction; borders and editorial whitespace rather than stacked dashboard cards. See existing local-only `/_design/foundation/*` rendered baseline before proposing changes.

## 3. Source inspection — concrete file evidence

| ID | Surface / inspected source | OBSERVED (source) | Assessment and impact | Disposition proposal |
| --- | --- | --- | --- | --- |
| AUD-01 | `resources/css/app.css` vs `design/tokens/foundation.json` | Laravel starter sets `--font-sans: 'Instrument Sans'`, neutral OKLCH theme, light/dark variables. Approved Foundation specifies system sans and explicit blue/slate semantic tokens. | **REVIEW / Major mapping ambiguity:** CSS has a different global token authority; actual public pages often override via Tailwind and inline font. Do **not** assert that public screenshots currently render the wrong font without computed-style evidence. | Trace computed styles and usage per public/starter layout; design one mapping/segregation strategy; never edit global tokens before approval. |
| AUD-02 | `resources/js/app.tsx`, `resources/js/pages/dashboard.tsx`, `routes/web.php` | Inertia default layout is `AppLayout`, with auth/settings separate; `/dashboard` is authenticated starter placeholder UI. Public pages each supply their own shell markup. | **REVIEW / Major architecture:** risk of starter/public design crossover; current public components must be judged by actual resolved layout. Dashboard is **not** activated SongChart admin design. | Preserve public/auth boundary. Candidate unified public shell only after checking Inertia resolution and avoiding double layout. |
| AUD-03 | `resources/js/pages/home/index.tsx` vs `search/index.tsx`, `artists/show.tsx`, `releases/show.tsx`, `recordings/show.tsx`, `site/document.tsx` | Header/search/skip-link/main/max-width blocks are repeated page-locally. Home header omits global search and instead has a dominant hero search. Document header uses a `max-w-md` search form; entity/search header uses flex search. | **GAP / Major consistency risk:** several independently maintained global shell anatomies, with differences that may be intentional on Home but lack shared contracts in code. | Candidate reusable `PublicShell`, `SiteHeader`, `GlobalSearch`, `SkipLink`; preserve Home search-first hero variant via explicit prop/pattern. |
| AUD-04 | `resources/js/components/public-footer.tsx` | PublicFooter already centralized with real About/Privacy/Terms/Disclaimer/Support/Corrections/Sitemap links. | **IMPLEMENTED reuse; retain.** | Keep Footer shared; test responsive wrapping and keyboard focus. |
| AUD-05 | `resources/js/pages/home/index.tsx`, `search/index.tsx` | Both use mixed-entity rows and slate dividers; markup for label/title/detail is repeated; Home has 3 discovery columns on desktop while Search has one list. | **GAP / Medium maintainability, UX not yet failed:** risk of diverging entity-result states. | Candidate `EntityResultRow` with variant: discovery vs result; no invented recommendation/ranking. |
| AUD-06 | `resources/js/pages/artists/show.tsx`, `releases/show.tsx`, `recordings/show.tsx` | Shared metadata `dl` anatomy and near-square artwork/placeholder present; same `MetadataRow`/`Meta` patterns repeated. Artist/Release/Recording share identity hierarchy and corrections action. | **GAP / Medium** duplicated entity-detail primitives; recording placeholder currently text “Recording metadata”, while other entities say artwork unavailable. | Candidate `EntityIdentity`, `ArtworkPlaceholder`, `MetadataList`, `ProvenanceBlock`, `CorrectionLink`; preserve domain-specific Work/Track details. |
| AUD-07 | `resources/js/pages/site/document.tsx` | One document component renders About/Privacy/Terms/Disclaimer/Support and public correction form; uses `max-w-3xl` inside 72rem shell, form field styles repeated, explicit accepted/validation/throttled/unavailable states. | **IMPLEMENTED with REVIEW:** good long-form anatomy; reusable fields/states candidate. Need full accessibility/interaction evidence before marking visual regression. | Keep shared document anatomy and correction policy; extract only reuse justified across screens. |
| AUD-08 | `resources/js/pages/design/foundation-preview.tsx` | Five local/testing-only fixtures render approved Foundation identity, Artist normal/long, Search results/empty/error, separate `FoundationShell`. | **APPROVED baseline (bounded) / IMPLEMENTED fixture.** Do not replace with an unrelated new look. | Compare runtime screenshots against approved exact-SHA Foundation artifacts; later update decision only if a material delta is accepted. |
| AUD-09 | `resources/js/pages/dashboard.tsx` | Starter `PlaceholderPattern` cards and default AppLayout, not domain UI. | **DEFERRED:** never treat it as the approved public home or reviewer/admin. | No scope expansion until #173 reviewer activation decision. |
| AUD-10 | Actual rendered DOM, responsive screenshots, computed CSS, focus order on current local SHA | **NOT INSPECTED** in this source-only pass. | **UNKNOWN**, not PASS or FAIL. | Capture deterministic 390×844 and 1440×1024 UI matrix and compare before any visual rebaseline. |

**Interpretation:** duplication and CSS divergence are source-backed maintainability/authority risks; they are not, without visual evidence, proof of changes in appearance. Product behavior, provider permissions and DB schema remain outside the requested design proposal.

## 4. Page archetypes and review samples — board IDs

| Board ID | Page / reference route | Design lifecycle at start | Required sample/anatomy | Required states / acceptance |
| --- | --- | --- | --- | --- |
| S01 | Public shell, all public routes | **APPROVED Foundation** bounded | Wordmark, search, primary content landmark, skip-link and shared footer | mobile/wide, keyboard/focus, long localization strings; Home hero search variant explicitly reviewed |
| S02 | Home `/` | **CANDIDATE anatomy**; VS-03 implementation source exists | Search-first hero, factual discovery groups for Artist/Release/Recording; no popularity badges | data and zero-data, mobile/wide, no invented content |
| S03 | Search `/search` | **APPROVED Foundation** bounded | SearchField, disambiguated EntityResultRow, query context | initial/no query, mixed similar names, no result, recoverable error, keyboard |
| S04 | Artist `/artists/{id}/{slug}` | **APPROVED Foundation** bounded | Entity type/title, optional disambiguation, artwork placeholder, metadata, releases, provenance/correction | long Unicode, missing artwork, relationships empty, redirects, narrow/wide |
| S05 | Release detail `/releases/...` | **CANDIDATE design anatomy**; source implemented under VS-02 | Entity identity, credits, medium/tracklist → recording, provenance | multi-disc, missing date/credits, narrow tracklist overflow |
| S06 | Recording detail `/recordings/...` | **CANDIDATE design anatomy**; source implemented under VS-02/03 | Recording ID, credit, Works, appearances on Releases, external destination | missing Work, missing provider, present verified URL, safe external link |
| S07 | Corrections `/corrections` | **IMPLEMENTED / VERIFIED bounded intake**, not reviewer | Record type, canonical ID, claim, optional public URL, honest review notice | invalid form without posting valid evidence, 429/503, accepted-for-review wording |
| S08 | Documents `/about`, `/privacy`, `/terms`, `/disclaimer`, `/support` | **APPROVED VS-04a** bounded | Same readable DocumentHeader/Section; real footer/support links | mobile/wide width, heading order, focus, factual copy |
| S09 | Utility 404/503, loading | **CANDIDATE** | ErrorState, EmptyState, LoadingState grounded in real service behavior | outage/recovery, meaningful retry, reduced motion |
| S10 | Internal reviewer, admin | **CANDIDATE / BLOCKED** (#173) | Separate internal shell, provisioned identities and permission states | do not implement/activate until governance authorization; no generic public admin UI |

These references extend `design/PAGE_ARCHETYPES.md` and `design/MVP_PAGE_SAMPLES.md`; they do not supersede them.

## 5. Proposed standardized component matrix (not yet approved)

| Candidate primitive | Reuse scope | Current evidence | What would change after approval | Test gate |
| --- | --- | --- | --- | --- |
| `PublicShell` / `SiteHeader` | Home, Search, entities, Docs | Header repeated across at least six page files | One shared responsive anatomy, Home remains intentional variant | DOM landmarks, 390/1440, focus, duplicate-shell regression |
| `GlobalSearch` / `SearchField` | Header, Home hero, Search | Same form styles repeated, heights 40/44px | Explicit size/role variants under approved 44px interaction intent | label, submit, focus, mobile input/button wrap |
| `EntityResultRow` | Home/Search/relationships | Similar type/name/detail markup | Reusable semantic row with identity/disambiguation | duplicate names, long Unicode, link safety |
| `EntityTitleBlock` | Artist, Release, Recording | H1/type/title structures similar | Shared context/title/provenance order while preserving page-specific fields | title wrapping, one H1, main DOM order |
| `ArtworkPlaceholder` | Entity detail | Artist/Release/Recording placeholders inconsistent in copy | One accessible square placeholder policy | no image, decorative vs informative alt |
| `MetadataList` | Entity detail | `dl` row duplication | Shared label/value spacing and semantics | long IDs, stacked mobile labels, readable contrast |
| `RelationshipSection` | Entity detail | Relationships use list, panel and empty variants | Consistent section spacing, empty state, heading | no relationships, multi-disc, nested links |
| `ProvenanceBlock` / `CorrectionLink` | Entity detail, correction entry | Repeated supporting copy/action | Explicit canonical-vs-provider language, review limitations | factual status, outbound distinction |
| `DocumentSection` / `FormField` | Legal/support/correction | Already one document screen, form fields repeated | Only extract after proving genuine reuse, avoid abstraction for its own sake | errors and help-text relationships |
| `StateView` | Search/entities/forms | Empty/error treatments implemented across files | Shared tone/semantics, not one generic layout for all | error/empty/503 keyboard + announcement |

**No new dependency, UI kit, Figma-to-code import, second design system or brand name is approved by this board.**

## 6. Non-negotiable quality and copy contracts

1. Reference viewport **390×844** and **1440×1024** CSS px, plus responsive behavior in between; no unintended horizontal overflow.
2. 44px primary pointer targets where layout permits; visible skip-link, keyboard focus, semantic labels and main; WCAG AA intent measured with actual rendered colors, not assumed from tokens.
3. Public visitors remain unauthenticated; no public dashboard controls in site shell.
4. Unknown metadata remains unknown. Same-name identities are disambiguated; international Unicode titles wrap, not truncated on detail pages.
5. External listening/watch actions explicitly leave SongChart; no unlicensed player/preview, fake verification status or engagement metrics.
6. Correction submission is evidence-only, does not mutate canonical data; reviewer/auth/admin is separately activation-gated.
7. Motion is nonessential and respects reduced-motion; state uses words/semantics, not only badge/icon/color.
8. Always use page archetypes and existing tokens before introducing a new primitive. No starter CSS token “fix” without confirming whether public pages use it.

## 7. Design governance — proposed approval checkpoints

| Gate | Evidence / reviewer action | Result before owner approval |
| --- | --- | --- |
| G0: authority baseline | Read `DESIGN_AUTHORITY.md`, existing tokens and design decisions, record exact main SHA | Existing approved values unchanged |
| G1: source audit | Record per-page code paths, computed styles and duplicated primitives | Current document = **partial source audit** |
| G2: visual comparison | Foundation vs current public screenshots at 390×844 and 1440×1024, matched fixtures and SHA | **PENDING**, no new visual acceptance claimed |
| G3: design decision | Owner selects retain/refine/change for palette, type, shell, component hierarchy, page anatomy, and records decision under `design/decisions/` | **BLOCKED** until explicit approval |
| G4: implementation PR | One cohesive public-web component/style consolidation with smallest necessary source changes, no unrelated admin/provider/DB work | **NOT STARTED** |
| G5: verification | Existing design/browser workflow owner; exact-head CI, keyboard, responsive, empty/error and regression, with approved baselines | **NOT STARTED** |
| G6: promote standard | Only after G3–G5 update owning tokens/contracts/patterns as approved, with decision and evidence | **NOT AUTHORIZED** |

Suggested order after G3: public shell/search → shared entity/result primitives → Home/Search/Artist → Release/Recording → document/correction → utility errors. Correct visual defects only with reproducible evidence; no speculative redesign of all screens.

## 8. Owner directional review — recorded 2026-11-25

**Review disposition:** all nine DEC proposals are **DIRECTION ENDORSED** (owner input on PR #271 planning). This is a review outcome on the candidate board only. It does not promote any candidate to `approved` or `verified`, authorize a source implementation, merge this Draft PR, or override the existing Foundation approvals.

| Decision ID | Direction endorsed by owner | Remaining material decision |
| --- | --- | --- |
| DEC-01 — Palette | Retain the approved blue/slate Foundation palette | No global token edit authorized; measured contrast and any requested palette delta need separate evidence/decision |
| DEC-02 — Typography | Retain system sans and Foundation scale; audit starter font | Computed public styles / cross-layout mapping still unknown; global font/scale edit not authorized |
| DEC-03 — Header & Search | Pursue one coherent shared public shell/search anatomy | Exact responsive examples, Home exception, focus and single-main behavior must be reviewed before changing common component anatomy |
| DEC-04 — Entity details | Standardize Artist/Release/Recording identity, artwork, metadata and provenance primitives | Compare domain-specific relationships and narrow/wide screenshots; no entity-hierarchy rewrite yet |
| DEC-05 — Home/Discovery | Search-first Calm Editorial layout with truthful canonical modules | Compare actual Home + zero-data rendering; no ranking/feed/popularity assumptions |
| DEC-06 — Search, empty and error | Keep semantics while pursuing consistent result and state visuals | Verify empty, ambiguous, recoverable error, keyboard and screen-reader behavior; no search-ranking change |
| DEC-07 — Documents & Corrections | Preserve approved legal anatomy and correction evidence-only behavior, improve consistency | Confirm rendered form labels/error semantics; no change to 180/365-day policy, schema or reviewer rights |
| DEC-08 — Admin / Reviewer | Defer runtime design/activation to the separately reviewed #173 permission gate | Endorsement explicitly **does not** authorize reviewer routes, privileges, 2FA bypass or generic admin dashboard |
| DEC-09 — Logo, brand, dark mode | Keep these as separately evaluated material design questions | No change to public brand identity, logo, global dark theme or custom font approved |

### Evidence still missing (owner endorsement does not satisfy these)

| Evidence ID | Required proof | Minimum record | Current status |
| --- | --- | --- | --- |
| EV-01 | Current public web vs approved Foundation at **390×844** and **1440×1024** | Exact Git SHA, deterministic same-content fixture, route/state, rendered screenshot and diff/observation | **PENDING** — existing Foundation CI PASS is not a current public-page comparison |
| EV-02 | Computed font, colors, spacing and layout for starter/public boundaries | Current public DOM/computed styles, applicable CSS source, reason for deviations, contrast measurements | **PENDING** — only code-level CSS mismatch observed |
| EV-03 | Shared shell, Home variant and global search behavior | Header/search on Home/Search/Artist/Release/Recording/Documents; one main, skip link, 44px pointer targets, no duplicate nav | **PENDING** |
| EV-04 | Entity detail and result consistency | Long mixed-script names, no-artwork, duplicate artist names, multi-medium tracklist, Works missing, destination present/absent | **PENDING** |
| EV-05 | Corrections/document/accessibility state matrix | Form invalid without persistence; 429/503 from safe disposable tests; readable document measure; focus/labels/error announcements | **PENDING** |
| EV-06 | Owner material-change approval decision | Reviewed before/after proposal, scope, risk, relevant screenshots, owner signoff under `design/decisions/` | **NOT GIVEN** — directional agreement only |
| EV-07 | Implementation regression and owner acceptance | Bounded UI PR, exact-head TypeScript/browser/visual/keyboard tests, 390/1440 artifacts, issue #175/#253 evidence and decision | **NOT STARTED** |
| EV-08 | Reviewer-specific permission activation if later pursued | Real moderation need, authorized roles/2FA review, default-deny tests and separate explicit activation | **BLOCKED** under #173, independent of UI Board |

Existing rendered Foundation evidence (approved on 2026-10-02) is referenced in `design/decisions/FOUNDATION_BASELINE_APPROVAL.md` and `design/baselines/FOUNDATION.md`; reuse it, do not infer public-page acceptance from it. Current public browser/computed-style inspection remains to be performed.

### Changes permitted at this stage

- **Allowed without changing product runtime:** source/contract audit; document candidate component anatomy and responsive wireframes; calculate token-to-CSS mapping and contrast; collect exact-SHA **read-only** screenshots; use existing deterministic local/CI fixture and browser evidence; record discrepancies and owner decisions in this board / #175 / #253.
- **Allowed only after separate G3 material approval:** editing `design/tokens/foundation.json`, global CSS/fonts, common shell/navigation and page identity hierarchy, global state semantics, replacing baseline screenshots; merging an implementation or design-system rebaseline.
- **Not authorized:** auto-merge PR #271; change app routes/data/migrations; fetch third-party music records; create a second design system/UI framework; implement/activate admin/reviewer (#173); release/deploy production or change SSO/security.

**Next review sequence:** evidence EV-01–05 first; present a concrete visual before/after and severity matrix; obtain an authored Design Authority decision (EV-06) for material changes; only then open one cohesive UI implementation work unit with exact-SHA verification (EV-07). Keep current Draft PR unmerged until the owner explicitly approves its documentation lifecycle.

## 9. Evidence links and boundaries

- Authorities: [Design Authority](DESIGN_AUTHORITY.md), [Identity](IDENTITY.md), [Concept Contract](CONCEPT_CONTRACT.md), [Foundation tokens](tokens/foundation.json), [Component Contracts](components/COMPONENT_CONTRACTS.md), [Archetypes](PAGE_ARCHETYPES.md), [Quality](QUALITY_CONTRACT.md), [Foundation approval](decisions/FOUNDATION_BASELINE_APPROVAL.md).
- Existing cross-page sample reference: [MVP Page Samples](MVP_PAGE_SAMPLES.md).
- UX acceptance / screenshots: [Issue #175](https://github.com/fusumivietnam/SongChart-Next/issues/175) and local review ledger [#253](https://github.com/fusumivietnam/SongChart-Next/issues/253).
- Source used for this audit: `resources/css/app.css`, `resources/js/app.tsx`, `routes/web.php`, `resources/js/pages/home/index.tsx`, `search/index.tsx`, `artists/show.tsx`, `releases/show.tsx`, `recordings/show.tsx`, `site/document.tsx`, `design/foundation-preview.tsx`, `dashboard.tsx`, `resources/js/components/public-footer.tsx`.
- Exclusions: no screenshot capture, live browser, computed CSS, external data/rights, migration, UI runtime modification or production release in this document-only proposal.
