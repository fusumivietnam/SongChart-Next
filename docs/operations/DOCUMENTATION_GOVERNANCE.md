# Documentation governance and freshness

SongChart Next keeps project authority in Git and machine-readable governance registries. Markdown may explain authority or project it for humans, but generated Markdown must never become a second lifecycle source of truth.

## Document modes

`governance/DOCUMENTATION_REGISTRY.json` registers high-value documentation with one of two supported modes:

- `authored`: human-maintained explanation or decision-support material. Its declared `sources` show what authority should be reviewed when the document changes.
- `generated`: byte-deterministic projection. Never edit these files by hand; run `python3 scripts/docs_generate.py`.
`mixed` is not an accepted registry mode (`scripts/docs_verify.py` rejects it). `README.md` is registered as `authored`. Roadmap reconciliation no longer writes a README status block; it updates only designated roadmap/capability authorities through reviewed PRs. Do not restore an automation-owned README section without a separately approved ownership change.

The registry is intentionally incremental. A document only becomes freshness-governed after it is explicitly registered with an owner and source set; do not pretend an unregistered document has automated freshness guarantees.

## Required commands

Regenerate repository projections:

```bash
python3 scripts/docs_generate.py
```

Verify paths, owners, source references, authority IDs and committed generated output:

```bash
python3 scripts/docs_verify.py
python3 scripts/docs_generate.py --check
```

For a read-only, Git-backed inventory of tracked Markdown files and local relative-link diagnostics, run `python3 scripts/docs_verify.py --audit-json`. The output now includes `ownership_coverage`: explicitly registered owner, path-governed/research-registry coverage, and unresolved paths, plus `unreferenced_candidates` with zero incoming *inline relative Markdown links*. These are triage signals, **not proof** that a file is unused or unowned: runtime/code references, external links, implicit index conventions and human workflows are outside the link scan. This audit is generated to stdout only; it never deletes files, rewrites authored docs, promotes lifecycle or asserts skill/agent activation. ADR, research, design decision and historical evidence require provenance review before any proposed removal. The `Project governance` workflow runs it on PRs and main alongside strict documentation checks, so new commits are inspected without a chat-driven checklist.

The required `governance` GitHub Actions context runs these checks on the exact PR/main revision. If a projected capability or technology changes status without regenerating its Markdown projection, the merge gate fails.

## Ownership boundaries

- `governance/CAPABILITY_MAP.json` owns capability lifecycle.
- `governance/TECHNOLOGY_REGISTRY.json` owns technology adoption state.
- `docs/roadmap/VERTICAL_SLICES.md` owns slice scope/dependency/acceptance intent, not live execution status.
- GitHub Issues/PRs and exact-SHA Actions evidence own live execution/evidence.
- `README.md` is authored navigation and policy context, not a mutable execution/status projection. Roadmap reconciliation does not update README.
- `docs/generated/PROJECT_STATUS.md` is the single committed generated lifecycle/technology status projection; `scripts/project_status.py` is an offline read-only diagnostic and not another committed status authority.
- `docs/generated/*` is disposable derived output and can always be rebuilt from declared authority.

## Semantic indexing and CocoIndex

The bounded CocoIndex research spike was evaluated under [Issue #124](https://github.com/fusumivietnam/SongChart-Next/issues/124) and [PR #125](https://github.com/fusumivietnam/SongChart-Next/pull/125). Its recorded evaluation outcome was **defer adoption**: baseline semantic retrieval and document-impact precision were insufficient to justify technology activation. The experimental index remains a rebuildable, disposable research artifact, not an installed production dependency or a documentation authority.

Deterministic registry/generator checks remain merge-blocking. Future semantic/LLM-based document-impact suggestions are advisory unless a separately reviewed, reproducible invariant and adoption decision justify a stronger gate.
