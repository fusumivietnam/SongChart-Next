<?php

namespace App\Music\Recordings;

use Illuminate\Support\Str;
use InvalidArgumentException;

final class MusicBrainzRecordingWorkAdapter
{
    private const PERFORMANCE_RELATION_TYPE_ID = 'a3005666-a872-32c3-ad06-98af558e99b0';

    /** @param array<string,mixed> $payload */
    public function normalize(array $payload): RecordingWorkClaim
    {
        $recordingId = strtolower((string) ($payload['id'] ?? ''));
        if (! Str::isUuid($recordingId)) {
            throw new InvalidArgumentException('recording.id must be a UUID.');
        }

        $relations = $payload['relations'] ?? null;
        if (! is_array($relations)) {
            throw new InvalidArgumentException('recording.relations must be an array.');
        }

        $works = [];
        foreach ($relations as $relation) {
            if (! is_array($relation)) {
                throw new InvalidArgumentException('Recording relation must be an object.');
            }

            if (($relation['target-type'] ?? null) !== 'work') {
                continue;
            }

            if (($relation['type-id'] ?? null) !== self::PERFORMANCE_RELATION_TYPE_ID) {
                continue;
            }

            if (($relation['type'] ?? null) !== 'performance' || ($relation['direction'] ?? null) !== 'forward') {
                throw new InvalidArgumentException('Recording-to-Work performance relation has unexpected type or direction.');
            }

            $attributes = $relation['attributes'] ?? [];
            if (! is_array($attributes)) {
                throw new InvalidArgumentException('Recording-to-Work relation attributes must be an array.');
            }
            if ($attributes !== []) {
                throw new InvalidArgumentException('Recording-to-Work performance attributes are not representable by the current canonical schema.');
            }

            $work = $relation['work'] ?? null;
            if (! is_array($work)) {
                throw new InvalidArgumentException('Recording-to-Work performance relation must include a work object.');
            }

            $workId = strtolower((string) ($work['id'] ?? ''));
            if (! Str::isUuid($workId)) {
                throw new InvalidArgumentException('work.id must be a UUID.');
            }

            $title = is_string($work['title'] ?? null) ? trim($work['title']) : '';
            if ($title === '') {
                throw new InvalidArgumentException('work.title is required.');
            }

            $works[$workId] = [
                'external_id' => $workId,
                'title' => $title,
                'type' => $this->nullableString($work['type'] ?? null),
                'disambiguation' => $this->nullableString($work['disambiguation'] ?? null),
                'relationship_type' => 'performance',
            ];
        }

        if ($works === []) {
            throw new InvalidArgumentException('Recording lookup contains no supported Recording-to-Work performance relation.');
        }

        return new RecordingWorkClaim($recordingId, array_values($works));
    }

    private function nullableString(mixed $value): ?string
    {
        $string = is_string($value) ? trim($value) : '';

        return $string === '' ? null : $string;
    }
}
