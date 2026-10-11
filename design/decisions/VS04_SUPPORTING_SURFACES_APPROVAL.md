# VS-04a supporting public surfaces approval

Status: approved for the bounded VS-04a scope
Decision date: 2026-10-11
Owner decision: Issue #105
Technical evidence: exact-head `VS-04 launch proof verification` is required before this decision can merge

## Decision

Approve one shared SongChart Next supporting-content anatomy for the VS-04a launch-proof surface, reusing the Foundation global-shell hierarchy rather than introducing a second design system.

## Approved scope

- document/legal anatomy for About, Privacy, Terms and Disclaimer;
- bounded support and correction guidance using explicit external issue-tracker actions;
- fixed-route sitemap utility treatment;
- public footer links only to routes that actually exist;
- readable long-form width, restrained section separators and existing semantic typography/focus treatment;
- skip-link and search-landmark accessibility contract;
- narrow 390×844 and wide 1440×1024 deterministic render evidence;
- correction language that clearly separates submission from canonical mutation.

## Evidence contract

The owning implementation must pass at one exact PR head:
- HTTP contracts for all six supporting routes;
- canonical/meta-description source contract;
- deterministic robots/sitemap checks;
- production-style frontend build;
- browser rendering of all six surfaces at the approved narrow and wide viewport sizes;
- source checks for skip link, search landmark, footer links and safe external issue-tracker treatment;
- project governance and protected-main required contexts.

Because this decision is carried by the implementation PR itself, approval becomes effective only if that exact revision passes the required evidence and is merged. A failed or superseded revision does not inherit approval.

## Explicit non-claims

This approval does not:
- approve a public account or registration experience;
- implement or approve authenticated editorial/admin review;
- create a confidential support channel;
- establish a legal entity, postal address, support email, data-retention period or hosting processor that the repository has not approved;
- approve production deployment, DNS, provider production access, public API, search-index, recommendation, or external workflow activation;
- approve generalized editorial/category/tag layouts, transactional forms or correction status pages;
- make the fixed sitemap a scale-ready dynamic entity sitemap.

Material changes to this anatomy or its legal/support interaction semantics return through the Design Authority review loop.
