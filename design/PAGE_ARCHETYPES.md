# SongChart Next — page archetype inventory

This inventory prevents every URL from becoming a bespoke design. Status applies to **page anatomy**, not product implementation.

| Archetype | Representative pages | Design state | Notes |
|---|---|---|---|
| Global shell | header, global search, footer, skip link, mobile nav | approved Foundation | `patterns/SHELL.md`; mobile-nav detail remains candidate until rendered evidence exists |
| Entity detail | Artist | approved Foundation | Artist normal + long-name baselines approved |
| Entity detail extension | Release, Recording, Credits | candidate | must reuse Artist hierarchy; Release contract exists but rendered approval belongs to VS-02 |
| Search/results | result list, same-name disambiguation, empty, error | approved Foundation | loading/filter/pagination remain candidate extensions |
| Discovery/list | Home, category, tag, browse/discovery lists | candidate | VS-03 Home implementation is verified; generalized category/tag anatomy remains candidate |
| Editorial index | News/Updates, posts list | candidate | collection/list anatomy; not MVP-critical unless activated |
| Editorial article | post/article detail | candidate | long-form reading width + metadata + related navigation |
| Document/legal | About, Terms, Privacy, Disclaimer | approved VS-04a | one readable document anatomy under the approved shell; evidence/decision in Issue #105 and `design/decisions/VS04_SUPPORTING_SURFACES_APPROVAL.md` |
| Form/action | Support and correction guidance | approved VS-04a bounded subset | current action is safe external issue-tracker navigation only; submission forms and authenticated review remain candidate/separately scoped |
| Review/status | correction submitted/pending/rejected/accepted messaging | candidate | public submission never implies direct canonical write |
| Utility/navigation | fixed-route sitemap/help | approved VS-04a bounded subset | deterministic fixed public routes only; generalized browse sitemap remains candidate |
| Utility/error | 404, 403, 500/service unavailable | candidate | reuse common error-state component; no playful treatment that obscures recovery |
| Loading/skeleton | entity/search/list loading | candidate | no fabricated values; preserve final layout hierarchy |
| Provider destination chooser | external permitted destinations | candidate | VS-03 implementation is verified; generalized provider-choice extensions remain candidate |
| Auth/editorial | internal login/review/admin | separately scoped | upstream auth scaffold is not public product design authority |

## Minimum public page set before launch proof

The product charter and roadmap imply the following representative journeys must eventually be covered by approved/verified design and implementation evidence:

- Home/discovery -> Search -> Artist -> Release -> Recording/Credits -> external permitted destination.
- Search results, empty and recoverable error.
- Entity missing artwork/metadata.
- Basic correction/report path and review acknowledgement.
- Privacy/support/legal minimum needed for launch.
- 404 and service failure/recovery.

## Supporting content routes

Activated VS-04a supporting routes reuse shared anatomy rather than bespoke visual systems:

- `/about` -> Document/legal.
- `/terms` -> Document/legal.
- `/privacy` -> Document/legal.
- `/disclaimer` -> Document/legal.
- `/support` -> bounded Form/action guidance + external issue tracker.
- `/corrections` -> bounded Form/action guidance + external issue tracker; never direct canonical write.
- `/sitemap.xml` -> bounded Utility/navigation machine-readable fixed-route projection.

Editorial/category/tag pages and transactional support/review flows remain candidate until separately activated.

## Approval rule

A candidate archetype becomes approved only when its owning slice/issue has deterministic fixture content, narrow+wide evidence, accessibility/interaction review and an authored Design Authority decision. A generated mockup alone never advances lifecycle state.
