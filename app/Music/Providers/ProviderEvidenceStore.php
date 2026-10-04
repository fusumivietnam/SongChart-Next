<?php

namespace App\Music\Providers;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Date;
use Illuminate\Support\Str;

final class ProviderEvidenceStore
{
    public function record(
        string $provider,
        string $requestIdentity,
        ?int $httpStatus,
        ?string $payload,
        string $retentionClass,
        int $retentionDays,
        string $schemaVersion,
    ): string {
        $fetchId = (string) Str::ulid();
        $fetchedAt = Date::now();
        $expiresAt = $fetchedAt->addDays($retentionDays);
        $payloadHash = $payload === null ? null : hash('sha256', $payload);

        DB::transaction(function () use (
            $fetchId,
            $provider,
            $requestIdentity,
            $httpStatus,
            $payload,
            $payloadHash,
            $retentionClass,
            $fetchedAt,
            $expiresAt,
            $schemaVersion,
        ): void {
            if ($payload !== null && $payloadHash !== null) {
                DB::table('provider_evidence_blobs')->upsert(
                    [[
                        'provider' => $provider,
                        'payload_hash' => $payloadHash,
                        'payload' => $payload,
                        'expires_at' => $expiresAt,
                        'created_at' => $fetchedAt,
                        'updated_at' => $fetchedAt,
                    ]],
                    ['provider', 'payload_hash'],
                    ['payload', 'expires_at', 'updated_at'],
                );
            }

            DB::table('provider_fetches')->insert([
                'id' => $fetchId,
                'provider' => $provider,
                'request_identity' => $requestIdentity,
                'fetched_at' => $fetchedAt,
                'http_status' => $httpStatus,
                'schema_version' => $schemaVersion,
                'payload_hash' => $payloadHash,
                'retention_class' => $retentionClass,
                'expires_at' => $expiresAt,
                'created_at' => $fetchedAt,
                'updated_at' => $fetchedAt,
            ]);
        });

        return $fetchId;
    }

    /** @return array{fetches: int, blobs: int} */
    public function purgeExpired(): array
    {
        return DB::transaction(function (): array {
            $now = Date::now();
            $fetches = DB::table('provider_fetches')
                ->where('expires_at', '<=', $now)
                ->delete();

            $blobs = DB::table('provider_evidence_blobs')
                ->where('expires_at', '<=', $now)
                ->whereNotExists(function ($query): void {
                    $query->selectRaw('1')
                        ->from('provider_fetches')
                        ->whereColumn('provider_fetches.provider', 'provider_evidence_blobs.provider')
                        ->whereColumn('provider_fetches.payload_hash', 'provider_evidence_blobs.payload_hash');
                })
                ->delete();

            return ['fetches' => $fetches, 'blobs' => $blobs];
        });
    }
}
