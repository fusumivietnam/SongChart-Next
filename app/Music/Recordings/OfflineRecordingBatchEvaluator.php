<?php

namespace App\Music\Recordings;

use InvalidArgumentException;

/** Aggregate-only offline evaluation; never admits or persists provider records. */
final class OfflineRecordingBatchEvaluator
{
    public const MAX_RECORDS = 100;

    public function __construct(private readonly OfflineRecordingProjector $projector) {}

    /**
     * @param iterable<mixed> $lines
     * @param array<string,mixed> $source An operator-supplied reference, NOT proof of cryptographic verification.
     * @return array<string,mixed>
     */
    public function evaluate(iterable $lines, array $source, int $limit = self::MAX_RECORDS): array
    {
        if ($limit < 1 || $limit > self::MAX_RECORDS) {
            throw new InvalidArgumentException('Offline sample limit must be between 1 and 100.');
        }
        $provenance = $this->sourceReference($source);
        $counts = [
            'inspected' => 0,
            'candidates' => 0,
            'recording_only_candidates' => 0,
            'candidates_with_work' => 0,
            'candidates_with_isrc' => 0,
            'quarantined' => 0,
        ];
        $reasons = [];

        foreach ($lines as $line) {
            if ($counts['inspected'] >= $limit) {
                break;
            }
            if (! is_string($line)) {
                throw new InvalidArgumentException('Offline evaluation requires JSONL string lines.');
            }
            $counts['inspected']++;
            $result = $this->projector->projectJson($line);
            if ($result['status'] === 'quarantine') {
                $counts['quarantined']++;
                $reason = $result['reason'];
                $reasons[$reason] = ($reasons[$reason] ?? 0) + 1;
                if ($counts['inspected'] >= $limit) {
                    break;
                }
                continue;
            }
            $counts['candidates']++;
            $candidate = $result['candidate'];
            $counts[$candidate['works'] === [] ? 'recording_only_candidates' : 'candidates_with_work']++;
            if ($candidate['isrcs'] !== []) {
                $counts['candidates_with_isrc']++;
            }
            if ($counts['inspected'] >= $limit) {
                break;
            }
        }

        ksort($reasons);
        return [
            'scope' => 'offline_evaluation_only_no_admission_or_rights_clearance',
            'policy_revision' => 'offline-recording-projection-v1',
            'sample_limit' => $limit,
            'provenance' => $provenance + [
                'last_line' => $counts['inspected'] === 0
                    ? null : $provenance['first_line'] + $counts['inspected'] - 1,
            ],
            'counts' => $counts,
            'quarantine_reasons' => $reasons,
        ];
    }

    /**
     * @param array<string,mixed> $source
     * @return array<string,mixed>
     */
    private function sourceReference(array $source): array
    {
        if (($source['provider'] ?? null) !== 'musicbrainz'
            || ($source['dataset'] ?? null) !== 'json-dumps/recording') {
            throw new InvalidArgumentException('Only MusicBrainz offline Recording snapshot is supported.');
        }
        foreach ([
            'snapshot_id' => '/^\d{8}-\d{6}$/D',
            'archive_sha256' => '/^[0-9a-f]{64}$/iD',
            'manifest_signing_fingerprint' => '/^[0-9a-f]{40}$/iD',
        ] as $key => $pattern) {
            if (! is_string($source[$key] ?? null)
                || preg_match($pattern, $source[$key]) !== 1) {
                throw new InvalidArgumentException("Invalid offline provenance reference: {$key}.");
            }
        }
        if (! is_int($source['first_line'] ?? null) || $source['first_line'] < 1) {
            throw new InvalidArgumentException('Provenance first_line must be positive.');
        }
        if (! is_string($source['observed_at'] ?? null)
            || ! preg_match('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$/D', $source['observed_at'])) {
            throw new InvalidArgumentException('Provenance observed_at must be an ISO-8601 timestamp with timezone.');
        }
        // The evaluator never verifies the archive signature or checksum. The operator must
        // independently verify both before interpreting this reference as upstream evidence.
        return [
            'provider' => 'musicbrainz',
            'dataset' => 'json-dumps/recording',
            'snapshot_id' => $source['snapshot_id'],
            'archive_sha256' => strtolower($source['archive_sha256']),
            'manifest_signing_fingerprint' => strtoupper($source['manifest_signing_fingerprint']),
            'first_line' => $source['first_line'],
            'observed_at' => $source['observed_at'],
            'verification' => 'operator_supplied_not_verified_by_evaluator',
        ];
    }
}
