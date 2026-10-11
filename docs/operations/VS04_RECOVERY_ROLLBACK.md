# VS-04 PostgreSQL recovery and rollback rehearsal

Status: repository-owned G4 rehearsal for disposable CI infrastructure. This is **not** a production backup, point-in-time recovery claim, or authorization to run destructive commands against production.

## Owner and scope

SongChart owns this runbook. The `VS-04 launch proof verification` workflow is the evidence owner for the tested rehearsal. PostgreSQL is the canonical database authority. The rehearsal uses the repository's deterministic Artist/Release/Recording fixtures plus a deterministic verified destination record.

## Preconditions

1. Run only against a disposable database created by the VS-04 CI job or an explicitly disposable local Compose environment.
2. Confirm the target database is `songchart` inside the repository Compose stack and no production endpoint/credential is present.
3. Use the exact repository revision under verification.
4. Import fixtures only through the existing SongChart fixture/import and destination writer paths.
5. Stop immediately if the target cannot be proven disposable, if `pg_dump`/`pg_restore` fails, or if pre/post canonical snapshots differ.

## Backup and restore rehearsal

The CI contract performs these bounded steps:

1. `php artisan migrate:fresh --force` on disposable PostgreSQL.
2. Import `songchart:fixture:import-artist` and `songchart:fixture:import-release`.
3. Add the deterministic verified Recording destination through `StoreDestinationLink`.
4. Generate `scripts/vs04_recovery_snapshot.php` output as the pre-backup canonical snapshot.
5. Create a PostgreSQL custom-format logical dump with `pg_dump`.
6. Stop the application container before destructive database recreation.
7. Terminate remaining connections to the disposable `songchart` database, drop it, and recreate it.
8. Restore the logical dump with `pg_restore --no-owner --no-privileges`.
9. Restart the application and generate the post-restore canonical snapshot.
10. Require byte-identical normalized snapshots and a fully applied migration repository.

The dump is temporary runner state only and is deleted during the job. It is never uploaded as an artifact. Retained evidence is limited to non-sensitive JSON/text describing the canonical fixture snapshot, migration status, SHA and rehearsal results.

## Bounded rollback and forward re-apply

After restore verification, CI runs exactly one migration rollback step and then reapplies migrations to fully-up state. At the current migration tip this can drop the latest schema object and therefore is deliberately destructive. The rehearsal occurs only after successful restore in disposable CI data.

Required sequence:

1. Confirm disposable target and successful post-restore snapshot comparison.
2. `php artisan migrate:rollback --step=1 --force`.
3. `php artisan migrate --force`.
4. Require no pending migrations.
5. Record only status output/evidence; do not interpret this as a general production rollback guarantee.

A real release must have a release-specific migration/rollback assessment. If a future migration is irreversible, data-transforming, or unsafe to roll back automatically, the production release plan must use its documented forward-fix/recovery strategy instead of this generic rehearsal.

## Stop and escalation conditions

Stop the rehearsal and fail closed when any of the following occurs: target identity is uncertain; the application cannot be isolated before DB recreation; backup/restore exits non-zero; canonical snapshots differ; restored migrations are incomplete; rollback or reapply fails; or unexpected external/provider/production connectivity is observed.

For production, stop before any destructive command and escalate to the release owner. Production database access, provider-specific backup integration, point-in-time recovery, retention policy and platform restore procedures remain gated by the deployment-target decision (#69) and G5 evidence.

## Evidence boundary

Passing this rehearsal verifies G4 backup/restore and one-step migration rollback/reapply behavior for the exact tested repository SHA on disposable PostgreSQL. It does not verify production persistence, PITR, managed-database controls, RPO/RTO, deployment rollback, or a launched service.
