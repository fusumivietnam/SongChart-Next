<?php

namespace App\Music\Releases;

use InvalidArgumentException;

final readonly class MusicBrainzReleaseLookupAdapter
{
    public function __construct(private MusicBrainzReleaseBundleNormalizer $normalizer) {}

    /**
     * Adapt the documented MusicBrainz /ws/2/release/{MBID} JSON lookup shape
     * into the existing SongChart release-bundle claim boundary.
     *
     * @param array<string,mixed> $payload
     */
    public function normalize(array $payload): ReleaseBundleClaim
    {
        $releaseGroup = $payload['release-group'] ?? null;
        if (! is_array($releaseGroup)) {
            throw new InvalidArgumentException('MusicBrainz release lookup must include release-group data.');
        }

        $media = $payload['media'] ?? null;
        if (! is_array($media)) {
            throw new InvalidArgumentException('MusicBrainz release lookup must include media data.');
        }

        return $this->normalizer->normalize([
            'release-group' => $releaseGroup,
            'release' => [
                'id' => $payload['id'] ?? null,
                'title' => $payload['title'] ?? null,
                'status' => $payload['status'] ?? null,
                'country' => $payload['country'] ?? null,
                'date' => $payload['date'] ?? null,
                'barcode' => $payload['barcode'] ?? null,
            ],
            'artist-credit' => $payload['artist-credit'] ?? [],
            'media' => $media,
        ]);
    }
}
