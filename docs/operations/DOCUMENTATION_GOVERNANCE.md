# Documentation governance and freshness

SongChart Next keeps project authority in Git and machine-readable governance registries. Markdown may explain authority or project it for humans, but generated Markdown must never become a second lifecycle source of truth.

## Document modes

`governance/DOCUMENTATION_REGISTRY.json` registers high-value documentation with one of three modes:

- `authored`: human-maintained explanation or decision-support material. Its declared `sources` show what authority should be reviewed when the document changes.
- `generated`: byte-deterministic projection. Never edit these files by hand; run `python3 scripts/docs_generate.py`.
- `mixed`: authored document containing automation-owned sections. `README.md` stays mixed because roadmap reconciliation owns its status block.

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

The required `governance` GitHub Actions context runs these checks on the exact PR/main revision. If a projected capability or technology changes status without regenerating its Markdown projection, the merge gate fails.

## Ownership boundaries

- `governance/CAPABILITY_MAP.json` owns capability lifecycle.
- `governance/TECHNOLOGY_REGISTRY.json` owns technology adoption state.
- `docs/roadmap/VERTICAL_SLICES.md` owns slice scope/dependency/acceptance intent, not live execution status.
- GitHub Issues/PRs and exact-SHA Actions evidence own live execution/evidence.
- roadmap reconciliation remains the sole automation owner of the README status block.
- `docs/generated/*` is disposable derived output and can always be rebuilt from declared authority.

## Semantic indexing and CocoIndex

A later CocoIndex experiment may index code, governance and documentation for semantic retrieval, impact analysis and contradiction discovery. That index must remain a derived cache: it may suggest documents requiring review, but it cannot mutate lifecycle authority, approve decisions or become required application runtime infrastructure without a separately reviewed activation.

Deterministic registry/generator checks come first. Semantic/LLM-based checks should begin as advisory evidence and only become merge-blocking after a stable deterministic invariant is identified.
