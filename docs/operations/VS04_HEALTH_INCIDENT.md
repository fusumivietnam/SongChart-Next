# VS-04 health and incident response

Status: repository-owned G4 operational runbook. It does not configure a production pager, monitoring vendor, deployment platform or production database.

## Owners and entry criteria

The release/incident owner is the person operating the active SongChart release process. The application owner investigates application/runtime failures; the canonical-database owner investigates PostgreSQL connectivity and integrity failures. Before declaring an incident, record the exact revision/environment under test and whether the target is disposable, staging-like or production.

Enter this runbook when `/health` returns HTTP 503, public smoke checks fail, canonical PostgreSQL is unavailable, a release verification check fails after a change, or data integrity/recovery evidence no longer matches expected canonical state.

## Health contract

`GET /health` is intentionally narrow:

- HTTP 200 with `{"status":"ok"}` only when the application can execute a bounded query against the configured canonical database;
- HTTP 503 with `{"status":"unavailable"}` when that query fails;
- no database hostname, credentials, SQL diagnostics, stack traces, package/framework versions, canonical entity data or provider information is returned;
- responses are non-cacheable (`Cache-Control: no-store`).

Laravel's framework `/up` endpoint remains a process/framework liveness signal and is not a substitute for the SongChart application+database health contract.

## Initial triage

1. Capture time, exact revision, environment identity and the failing health/status code. Do not paste secrets or full environment files into issues or logs.
2. Confirm whether the application process is responding through `/up` and whether `/health` is 200 or 503.
3. For a 503, inspect database service health and application logs through the environment's approved access path. Redact credentials and user/provider payloads before sharing diagnostics.
4. If the incident follows a release or migration, stop further rollout/mutation until the release-specific migration and recovery plan is reviewed.
5. If canonical integrity is in doubt, prefer read-only diagnosis and the documented backup/restore procedure. Never repair canonical identities by provider-name guessing or direct unreviewed table edits.

## Containment and recovery

- Application-only failure: stop the release/change, restore the last known safe immutable artifact when a production deployment system is eventually activated, then re-run health/smoke checks.
- Database connectivity failure: restore connectivity/service first; `/health` must return 200 before resuming writes or release activity.
- Suspected canonical corruption/data loss: stop canonical writes, preserve available evidence, and follow `docs/operations/VS04_RECOVERY_ROLLBACK.md`. Production restore/PITR commands depend on the future deployment target and are not supplied by this pre-deployment runbook.
- Suspected credential exposure: do not echo or attach the credential. Stop the affected integration, rotate/revoke through the credential owner using the provider/platform control plane, and assess repository/history/log exposure separately.
- Provider/external destination incident: disable or block the affected destination/evidence through the approved SongChart review path; do not fetch arbitrary destination URLs server-side.

## Stop and escalation conditions

Escalate and stop automated recovery if the environment identity is uncertain; a destructive DB command would target non-disposable data without a release-specific approved plan; backups cannot be verified; canonical snapshots diverge; a migration is irreversible; credentials may be exposed; provider/legal policy is unclear; or production platform behavior differs from repository assumptions.

## Exit criteria

Do not close the incident until the triggering symptom is understood, `/health` and required smoke checks are green, canonical database state is verified for the incident scope, any compromised credential has been handled by its owner, and follow-up work/evidence is recorded in GitHub. Production launch/recovery claims additionally require G5 evidence after #69 is resolved.
