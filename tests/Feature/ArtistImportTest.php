<?php

namespace Tests\Feature;

use App\Models\Artist;
use App\Models\ExternalIdentity;
use App\Music\Artists\ExternalArtistClaim;
use App\Music\Artists\ImportArtist;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Str;
use Tests\TestCase;

final class ArtistImportTest extends TestCase
{
    use RefreshDatabase;

    public function test_import_is_idempotent_by_stable_external_identity(): void
    {
        $claim = new ExternalArtistClaim(
            provider: 'musicbrainz',
            entityType: 'artist',
            externalId: '8f3a5f22-4d6b-4d3f-9a62-4ca0f36a2a10',
            name: 'Aster Echo',
            type: 'Group',
            countryCode: 'FI',
            disambiguation: 'Deterministic VS-01a fixture',
            sourceName: 'Aster Echo',
        );

        $importer = app(ImportArtist::class);
        $first = $importer->handle($claim);
        $second = $importer->handle($claim);

        $this->assertSame($first->id, $second->id);
        $this->assertTrue(Str::isUlid($first->id));
        $this->assertSame(1, Artist::query()->count());
        $this->assertSame(1, ExternalIdentity::query()->count());
        $this->assertDatabaseHas('external_identities', [
            'artist_id' => $first->id,
            'provider' => 'musicbrainz',
            'entity_type' => 'artist',
            'external_id' => $claim->externalId,
        ]);
    }

    public function test_same_external_identity_reconciles_without_changing_canonical_id(): void
    {
        $importer = app(ImportArtist::class);

        $first = $importer->handle(new ExternalArtistClaim(
            provider: 'musicbrainz',
            entityType: 'artist',
            externalId: '8f3a5f22-4d6b-4d3f-9a62-4ca0f36a2a10',
            name: 'Aster Echo',
            type: 'Group',
            countryCode: 'FI',
            disambiguation: null,
            sourceName: 'Aster Echo',
        ));

        $updated = $importer->handle(new ExternalArtistClaim(
            provider: 'musicbrainz',
            entityType: 'artist',
            externalId: '8f3a5f22-4d6b-4d3f-9a62-4ca0f36a2a10',
            name: 'Aster Echo Ensemble',
            type: 'Group',
            countryCode: 'FI',
            disambiguation: 'Updated fixture evidence',
            sourceName: 'Aster Echo Ensemble',
        ));

        $this->assertSame($first->id, $updated->id);
        $this->assertSame('Aster Echo Ensemble', $updated->name);
        $this->assertSame('aster-echo-ensemble', $updated->slug);
        $this->assertSame(1, Artist::query()->count());
    }

    public function test_same_name_with_different_external_identity_creates_a_distinct_artist(): void
    {
        $importer = app(ImportArtist::class);

        foreach ([
            '8f3a5f22-4d6b-4d3f-9a62-4ca0f36a2a10',
            '34af6708-d4b4-4fb6-a8cd-d4226322c44d',
        ] as $externalId) {
            $importer->handle(new ExternalArtistClaim(
                provider: 'musicbrainz',
                entityType: 'artist',
                externalId: $externalId,
                name: 'Aster Echo',
                type: null,
                countryCode: null,
                disambiguation: null,
                sourceName: 'Aster Echo',
            ));
        }

        $this->assertSame(2, Artist::query()->count());
        $this->assertSame(2, ExternalIdentity::query()->count());
    }
}
