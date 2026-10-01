# ADR-0007 — Understand Anything as Codespaces developer-analysis tooling

- Status: accepted for repository developer tooling
- Date: 2026-10-02
- Scope: developer analysis only; no product/runtime authority
- Owning issue: #35

## Context

SongChart Next needs a reproducible way for coding agents and developers to inspect a growing codebase without using chat memory as implementation truth. Understand Anything can derive a structural/semantic knowledge graph and exposes Codex-compatible skills, but its Node/pnpm runtime would conflict with ADR-0006 if silently treated as an application toolchain.

The upstream reviewed for this decision is `Egonex-AI/Understand-Anything` at commit `b05cc3b20990afca537b4fc0a49b4d7fbdc65bb0`. Its repository license is MIT. At that revision the project requires Node.js >=22 for development and pins pnpm 10.6.2.

## Decision

Adopt Understand Anything as optional developer-analysis tooling in the repository-owned Codespaces shell.

The integration:
- pins the upstream Git commit in `.devcontainer/install-understand-anything.sh`;
- installs Node 22 in the dev-container shell only to support this developer tool;
- activates the upstream-pinned pnpm version for this tool and builds its core package;
- links upstream skills into the Codex-compatible `~/.agents/skills` location;
- never adds Understand Anything to SongChart `package.json`, `composer.json`, runtime images or production manifests;
- keeps SongChart application build/run authority in Dockerfile + Docker Compose under ADR-0001/ADR-0003;
- treats `.ua` graphs, summaries, inferred layers and tours as derived analysis only;
- does not enable upstream post-commit auto-update in this first adoption slice.

This ADR narrows one clause of ADR-0006: a host Node/pnpm toolchain is allowed only for approved developer-analysis tooling. It remains prohibited as a competing SongChart application toolchain.

## Authority boundary

Understand Anything may help locate files, relationships and likely architecture. It cannot approve or overwrite Product Charter, roadmap scope, governance registries, ADRs/contracts, Design Authority, canonical music semantics/data, live GitHub execution state, CI evidence or deployment evidence.

When generated analysis conflicts with repository authority, repository authority wins.

## Data, privacy and cost

Static analysis runs against the checked-out repository. Semantic analysis is performed by the coding-agent/LLM provider selected by the user, so repository content may follow that provider's data path and terms. Do not analyze secrets, production dumps or other material not approved for the active provider.

Initial full analysis can consume significant model tokens; incremental runs are expected to be smaller. This is developer cost, not SongChart runtime operating cost.

## Failure and recovery

Failure to install/build Understand Anything must not make the Codespace unusable. The post-create lifecycle logs a warning and continues. Retry `bash .devcontainer/install-understand-anything.sh` or recreate the disposable Codespace. Update the pinned upstream SHA only through reviewed dependency provenance.

Do not use a floating upstream `main` installer as the repository bootstrap path.

## Generated artifacts

Only ephemeral `.ua` scratch data and diff overlays are ignored. A future PR may commit a reviewed graph/config, but such files remain derived evidence and never become project authority. Large graphs require a separate Git LFS/repository-size decision.

## Verification

G1 is the merged pinned configuration. G2 requires an exact-revision Codespaces run proving pinned checkout, skill discovery, a bounded `$understand` analysis and private dashboard access. Until then, do not claim the graph itself is verified.
