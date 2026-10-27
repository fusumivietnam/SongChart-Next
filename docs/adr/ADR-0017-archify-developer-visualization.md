# ADR-0017 — Archify as opt-in developer architecture visualization

- Status: proposed; merge/review must accept this decision before technology activation
- Date: 2026-10-24
- Owning issue: #210
- Capability: `developer-analysis` (existing owner; no new product capability)
- Scope: developer shell only; no SongChart runtime or delivery authority

## Context

Codex and human reviewers need a readable, reproducible visual explanation of bounded SongChart source paths. The existing Understand Anything developer-analysis tooling focuses on repository comprehension, while Archify creates interactive, independently verifiable HTML diagrams from agent-authored structured JSON. It does **not** independently discover or verify live runtime behavior.

The evaluated source is `tt-a1i/archify` v3.2.0 at commit `208acba8d412335185b2056fedf54b3405df43fb`. The repository and bundled skill identify MIT licensing. Use Node.js 22+ already declared in the Codespaces developer shell; no additional application package manager or hosting service is needed.

## Proposed decision

Permit opt-in installation through `.devcontainer/install-archify.sh`, pinned to that exact upstream commit, with skill discovery in the Codex-compatible user directory. Do **not** alter `post-create.sh`, application manifests, Dockerfile, Compose, preview, production, or required CI. The script must refuse unknown existing destinations instead of overwriting other skills or checkouts.

Create a small historical source-backed diagram example with a fixed Git revision and a manual command to regenerate its HTML. Derived HTML, browser captures and intermediate artifacts live under ignored `.archify/` and must not be published as maintained architectural truth. Any later automation or generated documentation workflow needs a separate scoped issue/review and CI ownership assessment.

Issue #212 supplies the separate review scope for an optional, read-only browser verification workflow. Its exact-PR-revision run may establish browser evidence independently of Codespaces quota, but it must remain non-required, have no main-push trigger, publish no generated diagram and grant no technology activation.

## Authority and evidence

- Git source/AGENTS, Product Charter, Architecture, ADRs, contracts and governance registries remain authoritative.
- Issues/PRs and exact-SHA CI own execution/verification; capability status is not inferred from diagrams.
- Every real-code diagram records the source repository, full Git SHA and relevant file/line evidence. Unknown links must remain explicitly unknown; a renderer pass proves structure, not behavior.
- Source evidence must be refreshed after relevant code changes. A historical example stays pinned and must never imply current `main` architecture.

## Privacy, security, operational cost

Diagramming uses locally checked-out source. The selected coding agent may send inspected source context to its configured AI provider; never include credentials, production dumps, personal data or unapproved provider data. The Archify update checker may perform a bounded network GET for a stable manifest; set `ARCHIFY_UPDATE_CHECK_DISABLED=1` for reproducible/offline rendering. Generated HTML may embed code-location references and should not be published outside the intended review audience without source/privacy review.

Installation is a manual developer action, not a production service. If network installation fails, existing Codespaces and application behavior remain unchanged. No second orchestration, database, domain contract or license-burdened commercial tier is introduced.

## Alternative and retirement

Mermaid can provide lightweight static documentation but not the same validated interactive source-linked viewer. Understand Anything remains available for separate code exploration; Archify must not supersede it or duplicate its authority. Retirement consists of removing the optional installer/docs/registry entry in a reviewed PR and manually unlinking the skill only after verifying the exact destination; no application migration is required.

## Acceptance before implementation/verified promotion

1. Confirm exact upstream commit, MIT license, copied skill layout and no unapproved data path.
2. Validate installer shell syntax, existing-path protection and pinned SHA behavior.
3. Render the source-backed example with its historical commit, validate HTML/provenance, and complete a real browser check in an approved Codespaces or CI-like development environment.
4. Keep required workflows and production manifests unchanged.

An artifact passing validation alone does not establish Codespaces/browser verification. Reviewer approval of this ADR precedes registry promotion from `candidate`.
