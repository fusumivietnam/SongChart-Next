# Source-backed Developer Reference

**Status: reference contract and indexing guidance.** The repository now includes implemented application source, routes, migrations and UI from bounded verified slices. This reference document does not itself prove any specific endpoint, PHP symbol, hook, or component exists: follow linked current source/tests and capability lifecycle evidence.

Reference entries index actual repository source and explicitly authored semantics; they do not create runtime APIs or override OpenAPI, design rules or code signatures. When a public HTTP API is activated, `openapi/songchart-public.yaml` is its single declaration authority under ADR-0005; generated/reference views are derived and must fail stale-reference validation when they diverge. Do not emulate a global WordPress-style mutable hook bus for canonical decisions.

When a source implementation exists, an entry should have stable ID, kind, status, owner capability, source path/symbol, inputs/outputs, side effects, authorization, execution phase, consumers, example and test paths. Proposed entries must not assert source exists. Generated symbols and link graphs are derived snapshots; never hand-maintain them as another source of truth.

Categories: domain terms, use cases, ports/adapters, events, approved extension points, API operations, UI components/page patterns, workflow, provider/data policies and operations runbooks.

Lifecycle: proposed -> approved -> implemented -> verified -> deprecated -> retired. No write extension point bypasses application services, authorization, canonical rules or human review.

The initial Artist slice and subsequent Release/Recording, discovery, launch-support and correction-intake work have landed in bounded PRs. New reference entries must index only currently existing symbols and authored contracts, with tests and lifecycle evidence; do not infer activation of a public API, generalized hooks, provider-production access or deployment from framework or application source.
