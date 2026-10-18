# MVP page sample map — implementation-aware design references

**State: candidate reference package, not a newly approved visual baseline.** Reuse [Design Authority](DESIGN_AUTHORITY.md), [concept](CONCEPT_CONTRACT.md), [tokens](tokens/foundation.json), [components](components/COMPONENT_CONTRACTS.md), [quality](QUALITY_CONTRACT.md) and [page archetypes](PAGE_ARCHETYPES.md). No new palette, spacing scale, shell or UI framework. Actual implementations and approvals remain with owning sources/decisions. This file is a **navigation and review aid**, not another roadmap or runtime-status authority.

## How to review a sample
Read each row as **surface → owner → implementation reference → required UX cases → approval boundary**. The example anatomy below is informational wireframe text, not evidence that a UI is deployed. On every UX PR attach exact Git SHA and deployment/fixture, narrow 390×844 + wide 1440×1024 renders, accessible keyboard/focus evidence and empty/error states. Evidence lives in PR/Actions and issue #175, not in this file. Use the existing page's own source and pattern before creating anything new.

| Sample | Archetype / source of anatomy | Capability / slice / issue | Implementation vs design boundary | Required review |
| --- | --- | --- | --- | --- |
| A — Home/discovery | Discovery/list, SiteHeader, SearchField, EntityResultRow | `public-web`, VS-03, #175 | public route implemented; generalized browse/category design still candidate | search entry, representative items, no false ranking, narrow/wide, zero fixture |
| B — Search/results | Search/results; `patterns/SEARCH.md` | `public-web`, VS-03, #175 | bounded mixed-entity results implemented; extension patterns require evidence | same names, no-results, invalid/error, keyboard |
| C — Artist → Release → Recording/Credits | Entity detail; `patterns/ARTIST.md`, `patterns/RELEASE.md` | `public-web`, VS-01/02/03, #175 | bounded entity journey implemented; candidate artwork/dense anatomy unapproved | canonical identity/redirect, missing artwork, Unicode, relationships |
| D — Provider destination | Provider destination chooser, TextLink | `public-web`, VS-03c, #175; rights #174 | permitted destination chooser implemented with fixtures; live/public provider activation NOT approved | present/absent URL, explicit outbound naming, no fake playback, opener safety |
| E — Correction intake | Form/action, FormField, CorrectionEntry, SubmissionStatus | `public-web`, VS-05c/d, #175 | anonymous evidence POST implemented; accepting evidence != canonical mutation | valid, invalid, 429/503, duplicate, 180-day pending policy |
| F — Reviewer sign-in / queue / decision | Auth/editorial, Review/status | `admin-review` candidate, VS-05e, #173 | **design candidate only**, no reviewer route or decision runtime; one provisioned reviewer, mandatory confirmed 2FA | unauthorized / no-2FA / revoked, queue empty, conflict, evidence approve/reject, audit, no canonical edit |
| G — Supporting documents | Document/legal, DocumentHeader, DocumentSection | `public-web`, VS-04a, #175 | About/Privacy/Terms/Disclaimer/Support implemented; content/legal approval separate | reading width, footer paths, keyboard, mobile |
| H — Service and error | Utility/error, EmptyState, ErrorState, LoadingState | `public-web`, VS-04, #175 | generic readiness implemented; visual error family remains candidate | 404/503, DB outage/recovery, retry, no fabricated content |

## Sample E — Public correction intake (existing public surface)

```text
SiteHeader | Search
Home / Corrections
Corrections                         [page heading]
Report a metadata correction
Subject type  [Artist / Release / Recording]
Subject ID    [stable SongChart identifier]
Claim         [multi-line text 1–4000 characters]
Evidence URL  [optional HTTPS/HTTP URL]
[Submit evidence]
Help: We review evidence; submitting does not change music records.
[Field errors | Throttled | Unavailable | Accepted for possible review]
SiteFooter | About | Privacy | Terms | Disclaimer | Support
```

This is an **anatomy reference**, not an instruction to replicate controls if existing `/corrections` source differs. Validate real existing labels/flow against [correction policy](../docs/product/CORRECTION_INTAKE_POLICY.md). Do not introduce contact fields, automatic URL fetching, persistent submitter IP or inferred verification badges.

## Sample F — Internal reviewer flow (candidate only)

```text
INTERNAL ONLY — design candidate, not an activated URL
Sign in → verified provisioned account → confirmed 2FA → reviewer permission
Pending evidence queue [identity | age | subject | safe claim summary]
  Empty: No submissions pending
  Unauthorized: No reviewer permission (deny)
Correction detail [canonical subject link | claim | untrusted evidence URL]
  Decision: [Accept evidence] [Reject evidence] [Cancel]
  Confirmation: evidence decision only, no automatic canonical edit
  Outcome: [decision recorded | already resolved/conflict | unavailable]
  Audit: [who | what | when] → resolved retention contract (365 days)
```

**Security boundary:** no public registration, no self-service reviewer privilege, no implicit rights from Laravel starter dashboard. The reviewer decision must fail closed for anonymous/non-reviewer/unverified/no-confirmed-2FA/revoked accounts. Proposed review workflow remains behind [activation trigger](../governance/ACTIVATION_TRIGGERS.json); neither these samples nor owner-approved policy activate `admin-review`.

## Sample C/D — Canonical knowledge and destination flow

```text
Home → Search (query)
 → disambiguated Artist result [type | canonical ID | relevant context]
 → Artist [name | relationships | source/provenance]
 → Release [title | artist credits | tracks]
 → Recording [canonical recording | duration/credits | provenance]
 → Available external destination [provider name] → leave SongChart safely
 → No destination? State absence plainly, no fabricated player link
```

## Sample G/H — Supporting and failure flows

```text
Document: SiteHeader → page type/title → constrained reading content → footer
Empty:    explain what is absent → useful search/back action
Error:    explain unavailable/failed service → bounded retry/back action
Loading:  structural placeholder only, without fabricated identity/metrics
```

## Review handoff, one place
- **Current implemented UI**: read `resources/js/pages` and owning route, then compare it to Design Authority; do not infer it from this document.
- **UX evidence / visual acceptance**: issue [#175](https://github.com/fusumivietnam/SongChart-Next/issues/175), exact preview SHA + deployment + screenshots.
- **Reviewer authorization/activation**: issue [#173](https://github.com/fusumivietnam/SongChart-Next/issues/173). Manual review: role/2FA provisioning/revocation and actual moderation trigger.
- **Public provider data/rights**: issue [#174](https://github.com/fusumivietnam/SongChart-Next/issues/174). Manual review: service rights, licensing/attribution, data coverage.
- **Production**: issues [#121](https://github.com/fusumivietnam/SongChart-Next/issues/121) / [#69](https://github.com/fusumivietnam/SongChart-Next/issues/69), intentionally after code/product freeze.

A candidate sample cannot be promoted to approved until reviewed narrow/wide visual evidence, interaction/accessibility states and an authored design decision exist.
