# Environments, responsibility and recovery

Infrastructure Registry owns the **inventory of actual environment-scoped instances**, not product capability definitions or version numbers. Only add an instance when a configuration and approval exists. Technology Registry owns technology selection; manifests and container digests own versions; secrets stay outside Git. `main` has no registered runtime instance until approved source is merged; PR-only Docker scaffold is not a deployed application.

For each development/CI/staging/production instance, identify an accountable runtime owner, capability and technology refs, source configuration, network/data classification, secret locator (never secret value), failure mode, backup/recovery links where applicable and acceptance evidence. Distinguish named local Docker volume persistence from verified backup/restore. PostgreSQL is the intended canonical data authority once instantiated; derived cache/index must be rebuildable. Only one production deployment controller owns releases; Compose for development does not imply a production controller.

Before enabling production require access boundaries, secrets handling, monitoring and on-call/incident ownership, RPO/RTO targets appropriate to the service, tested restore, rollback and immutable release provenance. No production deployment or destructive changes without explicit review.
