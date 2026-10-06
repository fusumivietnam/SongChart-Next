<?php

namespace App\Music\Releases;

use Illuminate\Support\Str;
use InvalidArgumentException;

final class MusicBrainzReleaseBundleNormalizer
{
    /** @param array<string,mixed> $payload */
    public function normalize(array $payload): ReleaseBundleClaim
    {
        $group = $this->entity($payload['release-group'] ?? null, 'release-group');
        $release = $this->entity($payload['release'] ?? null, 'release');
        $date = $this->partialDate($release['date'] ?? null);
        $credits = $this->credits($payload['artist-credit'] ?? [], 'release');

        $media = [];
        foreach ($payload['media'] ?? [] as $medium) {
            if (! is_array($medium)) {
                throw new InvalidArgumentException('Medium must be an object.');
            }
            $tracks = [];
            foreach ($medium['tracks'] ?? [] as $track) {
                if (! is_array($track) || ! is_array($track['recording'] ?? null)) {
                    throw new InvalidArgumentException('Track must contain a recording object.');
                }
                $recording = $this->entity($track['recording'], 'recording');
                $work = null;
                if (isset($track['recording']['work'])) {
                    $work = $this->entity($track['recording']['work'], 'work');
                }
                $isrcs = [];
                foreach ($track['recording']['isrcs'] ?? [] as $isrc) {
                    $value = strtoupper(trim((string) $isrc));
                    if ($value !== '') {
                        $isrcs[] = $value;
                    }
                }
                $tracks[] = [
                    'position' => max(1, (int) ($track['position'] ?? 0)),
                    'number' => trim((string) ($track['number'] ?? '')),
                    'title' => $this->requiredString($track['title'] ?? null, 'track.title'),
                    'length_ms' => isset($track['length']) ? (int) $track['length'] : null,
                    'recording' => [
                        'external_id' => strtolower((string) $recording['id']),
                        'title' => (string) $recording['title'],
                        'length_ms' => isset($recording['length']) ? (int) $recording['length'] : null,
                        'disambiguation' => $this->nullableString($recording['disambiguation'] ?? null),
                        'credits' => $this->credits($recording['artist-credit'] ?? [], 'recording'),
                        'isrcs' => $isrcs,
                        'work' => $work === null ? null : [
                            'external_id' => strtolower((string) $work['id']),
                            'title' => (string) $work['title'],
                            'type' => $this->nullableString($work['type'] ?? null),
                            'disambiguation' => $this->nullableString($work['disambiguation'] ?? null),
                        ],
                    ],
                ];
            }
            $media[] = [
                'position' => max(1, (int) ($medium['position'] ?? 0)),
                'format' => $this->nullableString($medium['format'] ?? null),
                'title' => $this->nullableString($medium['title'] ?? null),
                'tracks' => $tracks,
            ];
        }

        return new ReleaseBundleClaim(
            releaseGroup: [
                'external_id' => strtolower((string) $group['id']),
                'title' => (string) $group['title'],
                'primary_type' => $this->nullableString($group['primary-type'] ?? null),
                'disambiguation' => $this->nullableString($group['disambiguation'] ?? null),
            ],
            release: [
                'external_id' => strtolower((string) $release['id']),
                'title' => (string) $release['title'],
                'status' => $this->nullableString($release['status'] ?? null),
                'country_code' => $this->nullableCountry($release['country'] ?? null),
                'release_year' => $date['year'],
                'release_month' => $date['month'],
                'release_day' => $date['day'],
                'date_precision' => $date['precision'],
                'barcode' => $this->nullableString($release['barcode'] ?? null),
            ],
            credits: $credits,
            media: $media,
        );
    }

    /** @return list<array{artist_external_id:string,credited_as:string,join_phrase:string,role:string,position:int}> */
    private function credits(mixed $value, string $label): array
    {
        if (! is_array($value)) {
            throw new InvalidArgumentException("{$label} artist-credit must be an array.");
        }
        $credits = [];
        foreach ($value as $index => $credit) {
            if (! is_array($credit) || ! is_array($credit['artist'] ?? null)) {
                throw new InvalidArgumentException("{$label} artist credit must contain an artist object.");
            }
            $artistId = (string) ($credit['artist']['id'] ?? '');
            if (! Str::isUuid($artistId)) {
                throw new InvalidArgumentException("{$label} artist credit id must be a UUID.");
            }
            $credits[] = [
                'artist_external_id' => strtolower($artistId),
                'credited_as' => $this->requiredString($credit['name'] ?? $credit['artist']['name'] ?? null, "{$label}.credited_as"),
                'join_phrase' => (string) ($credit['joinphrase'] ?? ''),
                'role' => 'primary',
                'position' => $index + 1,
            ];
        }
        return $credits;
    }

    /** @return array<string,mixed> */
    private function entity(mixed $value, string $label): array
    {
        if (! is_array($value)) {
            throw new InvalidArgumentException("{$label} must be an object.");
        }
        $id = (string) ($value['id'] ?? '');
        if (! Str::isUuid($id)) {
            throw new InvalidArgumentException("{$label}.id must be a UUID.");
        }
        $value['title'] = $this->requiredString($value['title'] ?? null, "{$label}.title");
        return $value;
    }

    /** @return array{year:?int,month:?int,day:?int,precision:?string} */
    private function partialDate(mixed $value): array
    {
        if (! is_string($value) || trim($value) === '') {
            return ['year' => null, 'month' => null, 'day' => null, 'precision' => null];
        }
        if (! preg_match('/^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?$/', trim($value), $matches)) {
            throw new InvalidArgumentException('release.date must be YYYY, YYYY-MM or YYYY-MM-DD.');
        }
        $month = isset($matches[2]) && $matches[2] !== '' ? (int) $matches[2] : null;
        $day = isset($matches[3]) && $matches[3] !== '' ? (int) $matches[3] : null;
        return [
            'year' => (int) $matches[1],
            'month' => $month,
            'day' => $day,
            'precision' => $day !== null ? 'day' : ($month !== null ? 'month' : 'year'),
        ];
    }

    private function requiredString(mixed $value, string $label): string
    {
        $string = is_string($value) ? trim($value) : '';
        if ($string === '') {
            throw new InvalidArgumentException("{$label} is required.");
        }
        return $string;
    }

    private function nullableString(mixed $value): ?string
    {
        $string = is_string($value) ? trim($value) : '';
        return $string === '' ? null : $string;
    }

    private function nullableCountry(mixed $value): ?string
    {
        $country = strtoupper((string) ($value ?? ''));
        return preg_match('/^[A-Z]{2}$/', $country) ? $country : null;
    }
}
