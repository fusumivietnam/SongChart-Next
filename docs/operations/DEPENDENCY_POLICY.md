# Dependency provenance and adoption

The Technology Registry owns **selection and capability mapping**, not installed versions; `composer.lock`, the selected JS lockfile, pinned Docker image digests and deployment manifests own actual versions. A research item, a name in a registry or a watch trigger does not install or approve technology.

Before adopting a **direct** dependency/service, record: owner capability, upstream URL, required feature, alternative/native option, current version/edition, license and provider terms, known security risks, privacy/data paths, cost/failure mode, approval ADR/issue if material, replacement/retirement plan, and reproducible version authority. Record important choices in TECHNOLOGY_REGISTRY and decision in ADR; transitive packages are traced through lockfiles/SBOM rather than individual ADRs.

Installation PR must commit lockfiles and reviewed manifests, pin image digests for controlled environments, run applicable dependency/license/secret checks and link CI evidence to SHA. A floating Docker tag is not immutable provenance. Never commit credentials or generated secret values. Changes to canonical data/provider rights require separate domain/legal review. Do not enable Meilisearch, Kestra, Filament, Coolify, Flutter, or other watch technologies solely because they are researched.

Review upgrades for compatibility, license/edition changes, migration/restore consequences and rollback. SBOM and automated vulnerability scanning become required release evidence once application dependencies exist; absence today is recorded as not implemented, not passed.
