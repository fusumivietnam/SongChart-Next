# Source-backed Developer Reference

**Status: contract proposal; no PHP class, hook, endpoint or component is claimed to exist yet.**

Reference entries index actual repository source and explicitly authored semantics; they do not create runtime APIs or override OpenAPI, design rules or code signatures. Do not emulate a global WordPress-style mutable hook bus for canonical decisions.

When a source implementation exists, an entry should have stable ID, kind, status, owner capability, source path/symbol, inputs/outputs, side effects, authorization, execution phase, consumers, example and test paths. Proposed entries must not assert source exists. Generated symbols and link graphs are derived snapshots; never hand-maintain them as another source of truth.

Categories: domain terms, use cases, ports/adapters, events, approved extension points, API operations, UI components/page patterns, workflow, provider/data policies and operations runbooks.

Lifecycle: proposed -> approved -> implemented -> verified -> deprecated -> retired. No write extension point bypasses application services, authorization, canonical rules or human review.

The first implementation scope is the Artist slice only. Index real symbols after the official starter and Artist code actually land.
