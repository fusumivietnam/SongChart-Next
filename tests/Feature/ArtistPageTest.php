<?php

namespace Tests\Feature;

use App\Models\Release;
use App\Music\Artists\ExternalArtistClaim;
use App\Music\Artists\ImportArtist;
use App\Music\Releases\ImportReleaseBundle;
use App\Music\Releases\MusicBrainzReleaseBundleNormalizer;
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
                ->where('artist.provenance.0.external_id', '8f3a5f22-4d6b-4d3f-9a62-4ca0f36a2a10')
                ->has('artist.releases', 0));
    }

    public function test_release_credits_surface_a_canonical_artist_to_release_link(): void
    {
        $this->artisan('songchart:fixture:import-artist')->assertSuccessful();
        $release = $this->importReleaseFixture();
        $artist = \App\Models\Artist::query()->where('name', 'Aster Echo')->firstOrFail();

        $this->get(route('artists.show', [
            'artist' => $artist->id,
            'slug' => $artist->slug,
        ]))
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->where('artist.releases.0.id', $release->id)
                ->where('artist.releases.0.title', 'Signals at Dawn')
                ->where('artist.releases.0.releaseYear', 2024)
                ->where('artist.releases.0.path', route('releases.show', [
                    'release' => $release->id,
                    'slug' => $release->slug,
                ], false))
                ->has('artist.releases', 1));
    }

    public function test_release_relationship_is_deduplicated_when_artist_has_multiple_credit_positions(): void
    {
        $this->artisan('songchart:fixture:import-artist')->assertSuccessful();
        $release = $this->importReleaseFixture();
        $artist = \App\Models\Artist::query()->where('name', 'Aster Echo')->firstOrFail();

        \Illuminate\Support\Facades\DB::table('entity_credits')->insert([
            'subject_type' => 'release',
            'subject_id' => $release->id,
            'artist_id' => $artist->id,
            'role' => 'featured',
            'credited_as' => 'Aster Echo',
            'join_phrase' => '',
            'position' => 99,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        $this->get(route('artists.show', [
            'artist' => $artist->id,
            'slug' => $artist->slug,
        ]))
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->where('artist.releases.0.id', $release->id)
                ->has('artist.releases', 1));
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

    private function importReleaseFixture(): Release
    {
        $json = file_get_contents(base_path('database/fixtures/musicbrainz/release-signals-at-dawn.json'));
        self::assertIsString($json);
        $decoded = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        self::assertIsArray($decoded);

        return app(ImportReleaseBundle::class)->handle(
            app(MusicBrainzReleaseBundleNormalizer::class)->normalize($decoded),
        );
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
