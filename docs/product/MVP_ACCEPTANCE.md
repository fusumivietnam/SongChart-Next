# MVP acceptance contract — SongChart Next

**Status: proposed for Issue #9 review.** This document makes the current Product Charter testable. It does **not** approve product scope, promote `product-scope`, activate a deferred capability, or prove implementation.

## Product boundary

SongChart Next MVP is an international music-knowledge, metadata-discovery and legal provider-navigation product. It does not stream, host or redistribute audio/video and is not a general developer platform.

The MVP must preserve the distinction between:
- SongChart canonical identity and external provider identifiers;
- provider/source claims and SongChart canonical decisions;
- verified/known data, unknown data and contested/correctable data;
- SongChart pages and permitted external listening/viewing destinations.

## Primary user journey

A user can:

1. Enter from Home or Search.
2. Find results that identify entity type and disambiguating information.
3. Open an Artist page.
4. Navigate from Artist to Release and Recording/credits where data exists.
5. Understand provenance/uncertainty where it materially affects interpretation.
6. Follow a permitted official/provider destination without SongChart redistributing media.
7. Recover gracefully from missing artwork, incomplete metadata, unavailable destinations or unknown entities.

The complete journey is accepted only after narrow and wide viewport browser evidence exists under an approved Design Authority baseline.

## MVP capability scope

The proposed MVP requires, at minimum:

| Area | Required MVP behavior | Explicit boundary |
| --- | --- | --- |
| Search | Find supported music entities with enough context to disambiguate results | Dedicated external search engine is not implied; PostgreSQL-first until measured trigger |
| Artist | Canonical read page and stable SongChart identity | No name-only automatic merge |
| Release | Canonical read page with correct release/release-group semantics when implemented | No flattening of distinct music concepts for UI convenience |
| Recording / credits | Read supported recording and credit relationships | Work/recording/release distinctions remain domain-owned |
| Provider ingestion | MusicBrainz-derived claims with provenance and provider-policy compliance | Fixture-first before live provider activation |
| Identity | Stable SongChart IDs plus mapped external identifiers | Provider identifiers are evidence, not canonical identity |
| Provenance | Source attribution/claim history appropriate to displayed metadata | Provenance requirements may vary by field/provider but cannot be silently discarded |
| Correction/review | Minimum path to identify and review meaningful metadata problems | Full moderation platform is not required before an actual unresolved-claim workflow exists |
| Public web | Responsive, accessible entity journey with international-ready URLs and SEO | Laravel starter screens are not SongChart product/design acceptance |
| Destinations | Safe navigation to permitted external provider destinations | No media redistribution |
| Operations | Automated checks plus recovery evidence appropriate to release stage | Local named volume persistence is not backup/restore proof |

Authentication is included only for a workflow that demonstrably requires an identity/session boundary. Presence of inherited starter auth source does not activate an MVP auth feature.

## Explicitly deferred

Unless a later reviewed roadmap decision activates them, the MVP excludes:

- rankings/charts without defined, licensed ranking semantics;
- audio/video redistribution or media hosting;
- Flutter/native applications;
- public plugin marketplace/runtime;
- write-enabled remote MCP;
- advanced autonomous agents;
- partner billing/premium commerce;
- distributed databases;
- Kubernetes;
- redundant deployment/control planes;
- Meilisearch, Kestra or other watched infrastructure without activation evidence;
- recommendation/ranking systems not required by the accepted MVP journey.

Research about these items may be registered without changing this scope.

## Foundation acceptance criteria

Issue #9 can be approved only when reviewers agree that the following are sufficient to start product implementation without inventing scope in later chats.

### G0 — product governance

- Product boundary and non-goals are explicit.
- Primary MVP journey is accepted or revised.
- Supported MVP entity concepts are named.
- Deferred/watch capabilities cannot enter implementation merely because a starter/dependency contains them.
- Product scope remains linked to the Product Charter and Capability Map rather than a separate task/status document.

### Slice activation boundary

Approval of this contract permits review of dependent capabilities; it does not automatically approve them.

In particular:
- Design Authority still requires its own baseline approval.
- OpenAPI declaration authority still requires its own decision.
- Canonical Artist/domain contracts still require VS-01a scope and tests.
- Live provider ingestion waits for fixture-first Artist evidence and provider policy.
- Production deployment waits for release/recovery/security gates.

### Product-level VS-01a acceptance

Before VS-01a can be considered product-verified, evidence must show:

- a deterministic Artist fixture enters through the approved claim/admission boundary;
- identity resolves by stable external identifier without name-only merge;
- duplicate fixture imports are idempotent;
- a SongChart Artist can be persisted/read using the canonical database boundary;
- the Artist read view renders under approved responsive/accessibility design references;
- missing/partial metadata has defined behavior;
- unit, database and browser tests pass at the accepted revision.

This contract does not prescribe the implementation structure beyond existing Architecture/Delivery Contract authority.

## Launch acceptance remains later

MVP scope approval is not launch approval. VS-04 still requires, as applicable:

- representative permitted data;
- complete responsive/accessible browser journey;
- provider/legal/privacy review;
- verified errors/empty states/redirects;
- dependency and secret checks;
- production-equivalent migrations;
- tested backup **and restore**;
- rollback evidence;
- health/incident runbooks;
- explicit release approval and deployment evidence.

## Decision checklist for Issue #9

Reviewers should record one of the following outcomes in GitHub:

- **Accept as proposed** — then a reviewed repository change may move `product-scope` from `candidate` to `approved`.
- **Accept with edits** — edit the Product Charter/this contract in the same bounded decision PR before lifecycle promotion.
- **Defer** — keep `product-scope` candidate and record the unresolved product question.
- **Reject** — explain which product boundary or journey must be replaced; do not silently substitute chat memory.

No lifecycle change is implied by opening or merging a proposal PR unless the reviewed change explicitly contains the authorized status promotion and supporting decision evidence.
