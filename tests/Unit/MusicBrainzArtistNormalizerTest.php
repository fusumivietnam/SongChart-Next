<?php

namespace Tests\Unit;

use App\Music\Artists\MusicBrainzArtistNormalizer;
use InvalidArgumentException;
use PHPUnit\Framework\TestCase;

final class MusicBrainzArtistNormalizerTest extends TestCase
{
    public function test_normalizes_a_musicbrainz_shaped_artist_claim(): void
    {
        $claim = (new MusicBrainzArtistNormalizer)->normalize([
            'id' => '8F3A5F22-4D6B-4D3F-9A62-4CA0F36A2A10',
            'name' => 'Aster Echo',
            'type' => 'Group',
            'country' => 'FI',
            'disambiguation' => 'Deterministic fixture',
        ]);

        $this->assertSame('musicbrainz', $claim->provider);
        $this->assertSame('artist', $claim->entityType);
        $this->assertSame('8f3a5f22-4d6b-4d3f-9a62-4ca0f36a2a10', $claim->externalId);
        $this->assertSame('Aster Echo', $claim->name);
        $this->assertSame('Group', $claim->type);
        $this->assertSame('FI', $claim->countryCode);
    }

    public function test_rejects_a_non_uuid_musicbrainz_identity(): void
    {
        $this->expectException(InvalidArgumentException::class);

        (new MusicBrainzArtistNormalizer)->normalize([
            'id' => 'Aster Echo',
            'name' => 'Aster Echo',
        ]);
    }

    public function test_rejects_an_invalid_country_code(): void
    {
        $this->expectException(InvalidArgumentException::class);

        (new MusicBrainzArtistNormalizer)->normalize([
            'id' => '8f3a5f22-4d6b-4d3f-9a62-4ca0f36a2a10',
            'name' => 'Aster Echo',
            'country' => 'Finland',
        ]);
    }
}
