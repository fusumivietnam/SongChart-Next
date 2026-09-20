# SongChart Next — AI and developer contract

This document governs **this repository only**. Do not load, cite as current authority, clone, import or silently reuse fusumivietnam/SongChart, any old SongChart ZIP, historic Stage 1–28 plan, or earlier chat as implementation truth. External material is research/reference only until a scoped issue and ADR approve adoption.

## Read order
1. README.md and docs/product/PRODUCT_CHARTER.md
2. docs/architecture/ARCHITECTURE.md
3. governance/CAPABILITY_MAP.json, TECHNOLOGY_REGISTRY.json and ACTIVATION_TRIGGERS.json
4. design/DESIGN_AUTHORITY.md and the owning page/component contract for UI work
5. reference/README.md and owning OpenAPI/provider/event contract
6. docs/roadmap/VERTICAL_SLICES.md and the actual GitHub issue/PR for the task
7. Inspect actual source, manifests, migrations and tests; these supersede guesses about installed code.

## Work protocol
- On every new session: read current main HEAD, open issues/PRs and manifests before claiming status. Existing work on an active branch is resumed rather than duplicated.
- Separate **candidate / approved / implemented / verified / deployed**. Do not infer later states from earlier ones.
- Propose a bounded change, identify the owning capability, blast radius, data/security/legal implications, contracts and acceptance tests before coding.
- Use one small branch/PR per semantic change; no unrequested merge, production deploy, migration, data deletion, secret rotation, provider terms override or irreversible action.
- Prefer native framework features, then a maintained approved dependency, then minimum custom SongChart code. Do not build a general-purpose platform.
- Domain truth belongs to SongChart Core + PostgreSQL; provider payloads are evidence, not identity. AI suggestions cannot mutate canonical data without deterministic safeguards and appropriate review.
- A public REST/MCP/CLI/Filament surface routes through the same application use cases. Never bypass authorization or directly write canonical tables.
- For UI reuse approved tokens, components, layouts, responsive/empty/error states; no unapproved redesign, fabricated metrics, fabricated verification badges or generic-looking new card when a reusable pattern exists.
- Tests and golden fixtures must not be weakened to make a change pass. Any contract-breaking change needs compatibility analysis and ADR.
- Update only the owning authored authority; generated indexes and summaries must be reproducible and must not become a second source of truth.
- Report precisely what changed, which checks ran, which did not run, and what remains unapproved.
