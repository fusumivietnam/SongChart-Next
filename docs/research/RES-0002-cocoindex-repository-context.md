# RES-0002 — CocoIndex repository-context and documentation-impact spike

- Status: registered for bounded local evaluation
- Owning issue: #124
- Capability: `project-os`
- Upstream: `https://github.com/cocoindex-io/cocoindex`
- Evaluated release: `v1.0.25`
- Upstream tag commit: `17c84f1a0f9bc5b0b4e1d8ebabb28bde79c4afa3`
- License: Apache-2.0

## Question

Can CocoIndex materially improve always-fresh repository context, documentation-impact discovery and contradiction retrieval for SongChart engineering without becoming project authority or a production dependency?

## Boundaries

Git and the existing governance registries remain authority. `governance/DOCUMENTATION_REGISTRY.json`, `scripts/docs_generate.py` and `scripts/docs_verify.py` remain deterministic merge-blocking documentation freshness controls. CocoIndex state, SQLite output, model cache and benchmark artifacts are disposable derived data.

The spike must not write lifecycle decisions, mutate canonical product data, run as a public service, receive production secrets or become a dependency of the Laravel application. Semantic quality is evidence for human review only and cannot block merges by itself.

## Experiment

The repository-owned spike under `research/cocoindex/` stages a bounded corpus from `docs/`, `governance/`, `design/`, `reference/`, repository scripts, governance/feature tests and selected application source. CocoIndex incrementally embeds chunks with `sentence-transformers/all-MiniLM-L6-v2` and stores derived rows in a disposable SQLite target.

The benchmark records:

1. initial index duration and derived storage footprint;
2. incremental update duration after one staged Markdown edit;
3. incremental update duration after one staged application-source edit;
4. hit@5 over ten known authority questions;
5. impact precision/recall proxies over three documentation-change probes;
6. retrieval coverage over three historical contradiction classes;
7. exact upstream version/revision/license and safety boundaries.

`Research CocoIndex spike` CI preserves the JSON evidence artifact for review. It verifies that the spike runs and respects its boundary, but deliberately does not impose a semantic-quality merge threshold.

## Adoption gate

Do not add CocoIndex to `governance/TECHNOLOGY_REGISTRY.json` as implemented and do not activate a new runtime from this note alone. After exact-head benchmark evidence exists, compare retrieval value, incremental behavior, false-positive proxy, operational complexity and rebuild/removal cost. Human review then chooses one outcome: adopt as a derived local developer tool, defer for a larger repository, or reject.

## Removal/rebuild

Removal is intentionally trivial: delete the disposable `.cocoindex-spike` state/artifacts and the local research image/cache. A clean Git checkout contains every authority needed to rebuild the spike. No SongChart runtime, database migration or authored decision depends on the index.
