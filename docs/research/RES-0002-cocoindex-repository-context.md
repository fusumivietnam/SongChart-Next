# RES-0002 — CocoIndex repository-context and documentation-impact spike

- Status: evaluated; adoption deferred
- Owning issue: #124
- Capability: `project-os`
- Upstream: `https://github.com/cocoindex-io/cocoindex`
- Evaluated release: `v1.0.25`
- Upstream tag commit: `17c84f1a0f9bc5b0b4e1d8ebabb28bde79c4afa3`
- License: Apache-2.0
- Exact-head benchmark: `e4541368d3833bc2f1fc77cfefd67b2008f3f39e`, workflow run `38158529429`

## Question

Can CocoIndex materially improve always-fresh repository context, documentation-impact discovery and contradiction retrieval for SongChart engineering without becoming project authority or a production dependency?

## Boundaries

Git and the existing governance registries remain authority. `governance/DOCUMENTATION_REGISTRY.json`, `scripts/docs_generate.py` and `scripts/docs_verify.py` remain deterministic merge-blocking documentation freshness controls. CocoIndex state, SQLite output, model cache and benchmark artifacts are disposable derived data.

The spike must not write lifecycle decisions, mutate canonical product data, run as a public service, receive production secrets or become a dependency of the Laravel application. Semantic quality is evidence for human review only and cannot block merges by itself.

## Experiment

The repository-owned spike under `research/cocoindex/` stages a bounded corpus from `docs/`, `governance/`, `design/`, `reference/`, repository scripts, governance/feature tests and selected application source. CocoIndex incrementally embeds chunks with `sentence-transformers/all-MiniLM-L6-v2` and stores derived rows in a disposable SQLite target. CocoIndex's own incremental state is separately placed under the same disposable spike work directory via `COCOINDEX_DB`.

The benchmark records initial and incremental update timing, derived storage, authority retrieval, documentation-impact suggestions and historical contradiction retrieval. Semantic results are intentionally observational rather than merge-blocking.

## Exact-head evidence

The corrected repo-relative benchmark on exact head `e4541368d3833bc2f1fc77cfefd67b2008f3f39e` completed successfully in `Research CocoIndex spike` run `38158529429` over 95 staged files / 163 indexed chunks.

Measured CI evidence:

- initial index/update: 11.624 seconds;
- one Markdown delta: 6.474 seconds;
- one application-source delta: 6.306 seconds;
- target SQLite: 696,320 bytes;
- total disposable spike workdir: 1,770,080 bytes;
- authority retrieval hit@5: 0.10;
- document-impact mean precision@5: 0.0667;
- document-impact mean recall@5: 0.1111;
- false-positive proxy: 0.9333;
- historical contradiction retrieval hit@10: 0.6667.

The pipeline itself therefore works and remains cheaply rebuildable at the derived-data layer. However, this baseline embedding/chunking/ranking configuration does **not** provide sufficient authority or documentation-impact retrieval quality to justify adopting CocoIndex as an active SongChart developer dependency today. Contradiction-oriented recall is promising enough to retain the reproducible spike for future comparison, but it is not sufficient to replace deterministic registries/search or become an automatic reviewer.

A separate operational concern is dependency footprint: the default Linux `sentence-transformers` stack used in the spike pulled a large Torch/CUDA dependency set even though the benchmark ran CPU inference. Any future re-evaluation should first use a CPU-only dependency/image strategy and should test metadata-aware or hybrid lexical/semantic retrieval against the same benchmark corpus rather than promoting this baseline.

## Evaluation outcome

**Defer adoption.** Do not add CocoIndex to `governance/TECHNOLOGY_REGISTRY.json`, do not activate a new capability/runtime, and do not make semantic judgement merge-blocking. The deterministic documentation registry/generator/verifier remains the production Project OS solution for freshness.

Re-evaluate only if one of these conditions becomes true:

1. the repository grows enough that deterministic path/text search becomes materially costly;
2. a CPU-light embedding/reranking configuration is available;
3. a metadata-aware or hybrid retrieval spike materially improves the frozen authority/document-impact benchmark;
4. long-horizon agent workflows require incremental derived context beyond what repository-native retrieval provides.

## Removal/rebuild

Removal is intentionally trivial: delete the disposable `.cocoindex-spike` state/artifacts and the local research image/cache. A clean Git checkout contains every authority needed to rebuild the spike. No SongChart runtime, database migration or authored decision depends on the index.
