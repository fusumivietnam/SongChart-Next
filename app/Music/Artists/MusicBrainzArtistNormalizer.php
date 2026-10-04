<?php

namespace App\Music\Artists;

use InvalidArgumentException;
use Illuminate\Support\Str;

final class MusicBrainzArtistNormalizer
{
    /**
     * @param array<string, mixed> $payload
     */
    public function normalize(array $payload): ExternalArtistClaim
    {
        $id = $this->requiredString($payload, 'id');
        $name = $this->requiredString($payload, 'name');

        if (! Str::isUuid($id)) {
            throw new InvalidArgumentException('MusicBrainz artist id must be a UUID.');
        }

        $country = $this->optionalString($payload, 'country');
        if ($country !== null && preg_match('/^[A-Z]{2}$/', $country) !== 1) {
            throw new InvalidArgumentException('MusicBrainz country must be an ISO 3166-1 alpha-2 code.');
        }

        return new ExternalArtistClaim(
            provider: 'musicbrainz',
            entityType: 'artist',
            externalId: strtolower($id),
            name: $name,
            type: $this->optionalString($payload, 'type'),
            countryCode: $country,
            disambiguation: $this->optionalString($payload, 'disambiguation'),
            sourceName: $name,
        );
    }

    /** @param array<string, mixed> $payload */
    private function requiredString(array $payload, string $key): string
    {
        $value = $payload[$key] ?? null;

        if (! is_string($value) || trim($value) === '') {
            throw new InvalidArgumentException("MusicBrainz payload [{$key}] must be a non-empty string.");
        }

        return trim($value);
    }

    /** @param array<string, mixed> $payload */
    private function optionalString(array $payload, string $key): ?string
    {
        $value = $payload[$key] ?? null;

        if ($value === null || $value === '') {
            return null;
        }

        if (! is_string($value)) {
            throw new InvalidArgumentException("MusicBrainz payload [{$key}] must be a string or null.");
        }

        return trim($value) === '' ? null : trim($value);
    }
}
