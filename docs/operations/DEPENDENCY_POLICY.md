# Dependency provenance and adoption

The Technology Registry owns **selection and capability mapping**, not installed versions; `composer.lock`, the selected JS lockfile, pinned Docker image digests and deployment manifests own actual versions. A research item, a name in a registry or a watch trigger does not install or approve technology.

Before adopting a **direct** dependency/service, record: owner capability, upstream URL, required feature, alternative/native option, current version/edition, license and provider terms, known security risks, privacy/data paths, cost/failure mode, approval ADR/issue if material, replacement/retirement plan, and reproducible version authority. Record important choices in TECHNOLOGY_REGISTRY and decision in ADR; transitive packages are traced through lockfiles/SBOM rather than individual ADRs.

Installation PR must commit lockfiles and reviewed manifests, pin image digests for controlled environments, run applicable dependency/license/secret checks and link CI evidence to SHA. A floating Docker tag is not immutable provenance. Never commit credentials or generated secret values. Changes to canonical data/provider rights require separate domain/legal review. Do not enable Meilisearch, Kestra, Filament, Coolify, Flutter, or other watch technologies solely because they are researched.

Review upgrades for compatibility, license/edition changes, migration/restore consequences and rollback. Standards-based SBOM generation and automated vulnerability scanning are required release evidence once application dependencies exist. Foundation CI may establish these controls before release; distinguish package-manager audits from OS/container vulnerability coverage and never treat a generated SBOM as a vulnerability scan.


## Approved admission model (2026-09-29)

Common direct OSS dependencies may proceed through the normal repository review path without a separate project-owner decision when all of the following are true:
- license is a standard, compatible OSS license for the intended use;
- upstream source, owner capability and version authority are explicit;
- no separate paid/enterprise edition is required for the selected capability;
- no hidden telemetry, data egress, hosted-service dependency or material privacy path is introduced;
- the dependency does not redefine SongChart product/domain/design authority;
- manifests/lockfiles and applicable audit/SBOM checks remain reproducible.

Escalate to explicit owner decision when license/edition terms are non-standard or ambiguous, a commercial/community boundary affects required features, a hosted service handles project/user data, redistribution/content rights apply, operating cost or lock-in is material, or the dependency would create a second authority/control plane.

Treat technical installation, license/edition approval, data/privacy approval and production approval as separate claims. Transitive packages remain governed through lockfiles/SBOM and security review rather than individual owner approvals unless a transitive dependency itself creates a material legal/security exception.
