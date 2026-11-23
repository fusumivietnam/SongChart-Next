<?php

namespace App\Music\Recordings;

use JsonException;

/** Pure, read-only evaluation. Candidates are NOT canonical admission claims. */
final class OfflineRecordingProjector
{
    private const PERFORMANCE_TYPE_ID = 'a3005666-a872-32c3-ad06-98af558e99b0';

    /** @return array<string,mixed> */
    public function projectJson(string $json): array
    {
        try {
            $decoded = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        } catch (JsonException) {
            return $this->quarantine('invalid_json');
        }

        return $this->project($decoded);
    }

    /** @return array<string,mixed> */
    public function project(mixed $payload): array
    {
        if (! is_array($payload) || array_is_list($payload)) {
            return $this->quarantine('invalid_recording_shape');
        }
        if (! $this->uuid($payload['id'] ?? null) || ! $this->nonempty($payload['title'] ?? null)) {
            return $this->quarantine('invalid_recording_identity');
        }
        $length = $payload['length'] ?? null;
        if ($length !== null && (! is_int($length) || $length < 0)) {
            return $this->quarantine('invalid_length');
        }
        $disambiguation = $this->optionalText($payload['disambiguation'] ?? null);
        if ($disambiguation === false) {
            return $this->quarantine('invalid_disambiguation');
        }

        $credits = $payload['artist-credit'] ?? null;
        if (! is_array($credits) || ! array_is_list($credits) || $credits === []) {
            return $this->quarantine('invalid_artist_credit');
        }
        $projectedCredits = [];
        foreach ($credits as $index => $credit) {
            if (! is_array($credit) || ! $this->uuid($credit['artist']['id'] ?? null)
                || ! $this->nonempty($credit['name'] ?? null)
                || ! is_string($credit['joinphrase'] ?? null)) {
                return $this->quarantine('invalid_artist_credit');
            }
            $projectedCredits[] = [
                'artist_external_id' => strtolower($credit['artist']['id']),
                'credited_as' => trim($credit['name']),
                'join_phrase' => $credit['joinphrase'],
                'position' => $index + 1,
            ];
        }

        $isrcs = $payload['isrcs'] ?? null;
        if (! is_array($isrcs) || ! array_is_list($isrcs)) {
            return $this->quarantine('invalid_isrc');
        }
        $projectedIsrcs = [];
        foreach ($isrcs as $isrc) {
            if (! is_string($isrc) || preg_match('/^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$/iD', $isrc) !== 1) {
                return $this->quarantine('invalid_isrc');
            }
            $normalized = strtoupper($isrc);
            if (isset($projectedIsrcs[$normalized])) {
                return $this->quarantine('duplicate_isrc');
            }
            $projectedIsrcs[$normalized] = $normalized;
        }

        $relations = $payload['relations'] ?? null;
        if (! is_array($relations) || ! array_is_list($relations)) {
            return $this->quarantine('invalid_relations');
        }
        $projectedWorks = [];
        foreach ($relations as $relation) {
            if (! is_array($relation) || array_is_list($relation)) {
                return $this->quarantine('invalid_relation');
            }
            if (($relation['target-type'] ?? null) !== 'work'
                || ($relation['type-id'] ?? null) !== self::PERFORMANCE_TYPE_ID) {
                continue;
            }
            if (($relation['type'] ?? null) !== 'performance'
                || ($relation['direction'] ?? null) !== 'forward') {
                return $this->quarantine('unexpected_performance_relation');
            }
            foreach (['attributes', 'attribute-ids', 'attribute-values'] as $key) {
                if (! isset($relation[$key]) || $relation[$key] !== []) {
                    return $this->quarantine('unsupported_performance_attributes');
                }
            }
            $work = $relation['work'] ?? null;
            if (! is_array($work) || ! $this->uuid($work['id'] ?? null)
                || ! $this->nonempty($work['title'] ?? null)) {
                return $this->quarantine('invalid_work_identity');
            }
            $type = $this->optionalText($work['type'] ?? null);
            $workDisambiguation = $this->optionalText($work['disambiguation'] ?? null);
            if ($type === false || $workDisambiguation === false) {
                return $this->quarantine('invalid_work_metadata');
            }
            $workId = strtolower($work['id']);
            $claim = [
                'external_id' => $workId,
                'title' => trim($work['title']),
                'type' => $type,
                'disambiguation' => $workDisambiguation,
                'relationship_type' => 'performance',
            ];
            if (isset($projectedWorks[$workId]) && $projectedWorks[$workId] !== $claim) {
                return $this->quarantine('conflicting_work_identity');
            }
            $projectedWorks[$workId] = $claim;
        }

        return [
            'status' => 'candidate',
            'candidate' => [
                'recording' => [
                    'external_id' => strtolower($payload['id']),
                    'title' => trim($payload['title']),
                    'length_ms' => $length,
                    'disambiguation' => $disambiguation,
                ],
                'credits' => $projectedCredits,
                'isrcs' => array_values($projectedIsrcs),
                'works' => array_values($projectedWorks),
            ],
        ];
    }

    /** @return array{status:string,reason:string} */
    private function quarantine(string $reason): array
    {
        return ['status' => 'quarantine', 'reason' => $reason];
    }

    private function uuid(mixed $value): bool
    {
        return is_string($value)
            && preg_match('/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/iD', $value) === 1;
    }

    private function nonempty(mixed $value): bool
    {
        return is_string($value) && trim($value) !== '';
    }

    private function optionalText(mixed $value): string|false|null
    {
        if ($value === null) {
            return null;
        }
        if (! is_string($value)) {
            return false;
        }
        $value = trim($value);

        return $value === '' ? null : $value;
    }
}
