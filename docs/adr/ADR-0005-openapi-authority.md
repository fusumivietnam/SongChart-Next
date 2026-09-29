# ADR-0005 — Authored OpenAPI is the public HTTP contract authority

Status: accepted, 2026-09-29.

Decision authority: explicit project-owner approval of D3=A and D4=A during the Foundation decision review. This ADR and its reviewed repository change are the durable authority.

## Context
Issue #11 requires one declaration authority before any public API implementation relies on OpenAPI. Dual maintenance between Laravel source annotations/routes and a separately edited OpenAPI document would create contradictory contract truth.

VS-01a does not require public API exposure. It may use internal typed application/read contracts while this decision establishes the rule for later public HTTP activation.

## Decision
When the public HTTP API capability is activated, the single authored declaration authority is:

`openapi/songchart-public.yaml`

The file does not need to exist until a public API surface is actually approved for implementation. Creating this ADR does not activate that surface.

Laravel routes/controllers/resources, generated SDK/reference material, examples and tests are consumers/implementations of the authored spec. They must not be treated as a separately editable declaration authority.

## Version authority
- Contract source: `openapi/songchart-public.yaml` at the repository Git revision.
- Released API compatibility is tied to an immutable release/revision plus the served API versioning policy.
- Generated files must identify or be reproducible from the source revision; generated artifacts are never hand-edited contract truth.

## Validation and stale-reference rule
Once the first public operation is introduced, CI must:
1. parse/validate the authored OpenAPI document;
2. validate implemented public operations/responses against the declared contract at the same revision;
3. regenerate or validate any generated reference/SDK artifacts;
4. fail when generated/reference material is stale or when an implemented public operation is absent/incompatible with the authored declaration.

Before public API activation, CI must not fabricate an empty API merely to satisfy this ADR.

## Compatibility policy
- Additive compatible changes require contract tests and review.
- Breaking changes require explicit compatibility analysis and an ADR/versioning decision before merge.
- Removing/renaming fields or operations, narrowing accepted values, or changing response semantics is breaking unless a documented compatibility strategy says otherwise.
- Internal PHP/application signatures are not public API compatibility promises unless explicitly surfaced by the authored OpenAPI contract.

## Rejected alternative
Code-first OpenAPI generation from Laravel source is rejected as the declaration authority for this project because it would make framework implementation details define the public contract and would make independent contract review harder. Code generation may still be used as a conformance/derived-output tool if it cannot become a second editable authority.

## Consequences
This resolves the Foundation declaration-authority gate only. It does not promote `api-contracts` to implemented/verified, expose a public endpoint, or require VS-01a to ship REST.
