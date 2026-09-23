# Project control and session bootstrap

**Authoritative data:** Git main owns product/architecture/design/governance/roadmap scope, source and decisions; GitHub Issues/PRs own execution; manifests/lockfiles own installed versions; CI/release/deployment records own measured evidence. Chat, project memory, old SongChart, ZIPs and generated snapshots are never current implementation evidence. Research registered in RESEARCH_REGISTRY is only evaluated reference material.

## Session read protocol
1. Read current main HEAD, README and AGENTS; read Product Charter, Architecture and owning Design/contract docs.
2. Validate CAPABILITY_MAP, TECHNOLOGY_REGISTRY, ACTIVATION_TRIGGERS, RESEARCH_REGISTRY and INFRASTRUCTURE_REGISTRY with `python3 scripts/verify_project_os.py`.
3. Read roadmap scope; run `python3 scripts/project_status.py` for a local **read-only** inventory. This offline report intentionally marks Issues/PRs/CI/deployment unknown.
4. Query **live** GitHub Issues, PRs, branch HEADs, CI, manifests and tests; identify existing active capability/slice/branch. If API unavailable report unknown; never infer from snapshot or chat memory.
5. Resume an owning Issue/PR rather than duplicate it. Distinguish proposed/approved/implemented/verified/deployed; use referenced G0–G5 acceptance evidence. Obtain review for decisions and provider/data-impact changes.
6. Commit bounded changes to a branch, run validation/tests, open/update PR with exact SHA and evidence. Do not merge/deploy/perform destructive changes without explicit review. Update owning authorities, not generated copies.

## Authority and linking
- Research ID RES-0001: research provenance and disposition, not approval; link to existing capability and decision.
- Capability ID in CAPABILITY_MAP: canonical scope/status; technology ID in TECHNOLOGY_REGISTRY: approved/candidate/watch selection.
- Runtime instance ID in INFRASTRUCTURE_REGISTRY: environment-specific configuration and operational owner, not technology version authority.
- VERTICAL_SLICES defines slice scope; Issue/PR tracks work; ADR captures major architectural decisions; source and CI establish implementation/verification.
- Local status report is regenerated per run. Never commit an auto-written CURRENT_STATUS file or manually maintain competing status flags.

## PR review checklist
Record: owning capability and issue, proposed vs approved boundary, affected source/contracts/registries, security/privacy/provider rights, dependency provenance, relevant acceptance gates, test command/results at SHA, outstanding unknown evidence and recovery implications. CI validates only registry consistency and its own regression tests; it cannot approve a business decision or prove production health.

## Change propagation
Scope change -> Product Charter/ADR then relevant Capability Map and roadmap; technology adoption -> decision and Technology Registry then manifest; runtime creation -> Infra Registry and environment policy; research evaluation -> Research Registry with decision reference. Each PR checks inbound references and preserves historical decision links. A merge updates main authority only after review.
