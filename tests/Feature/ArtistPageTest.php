<?php

namespace Tests\Feature;

use App\Music\Artists\ExternalArtistClaim;
use App\Music\Artists\ImportArtist;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Inertia\Testing\AssertableInertia as Assert;
use Tests\TestCase;

final class ArtistPageTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();

        $this->withoutVite();
    }

    public function test_public_artist_page_renders_typed_canonical_read_view(): void
    {
        $artist = app(ImportArtist::class)->handle($this->claim());

        $this->get(route('artists.show', [
            'artist' => $artist->id,
            'slug' => $artist->slug,
        ]))
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->component('artists/show')
                ->where('artist.id', $artist->id)
                ->where('artist.slug', 'aster-echo')
                ->where('artist.name', 'Aster Echo')
                ->where('artist.type', 'Group')
                ->where('artist.countryCode', 'FI')
                ->where('artist.provenance.0.provider', 'musicbrainz')
                ->where('artist.provenance.0.external_id', '8f3a5f22-4d6b-4d3f-9a62-4ca0f36a2a10'));
    }

    public function test_missing_or_stale_slug_redirects_to_canonical_artist_url(): void
    {
        $artist = app(ImportArtist::class)->handle($this->claim());
        $canonical = route('artists.show', [
            'artist' => $artist->id,
            'slug' => $artist->slug,
        ]);

        $this->get(route('artists.show', ['artist' => $artist->id]))
            ->assertRedirect($canonical)
            ->assertStatus(301);

        $this->get(route('artists.show', [
            'artist' => $artist->id,
            'slug' => 'stale-name',
        ]))
            ->assertRedirect($canonical)
            ->assertStatus(301);
    }

    private function claim(): ExternalArtistClaim
    {
        return new ExternalArtistClaim(
            provider: 'musicbrainz',
            entityType: 'artist',
            externalId: '8f3a5f22-4d6b-4d3f-9a62-4ca0f36a2a10',
            name: 'Aster Echo',
            type: 'Group',
            countryCode: 'FI',
            disambiguation: 'Deterministic VS-01a fixture',
            sourceName: 'Aster Echo',
        );
    }
}
