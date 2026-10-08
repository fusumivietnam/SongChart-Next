<?php

namespace Tests\Feature;

use App\Models\Artist;
use App\Models\Recording;
use App\Models\Release;
use App\Music\Releases\ImportReleaseBundle;
use App\Music\Releases\MusicBrainzReleaseBundleNormalizer;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Inertia\Testing\AssertableInertia as Assert;
use Tests\TestCase;

final class DiscoverySearchTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->withoutVite();
    }

    private function importFixture(): void
    {
        $this->artisan('songchart:fixture:import-artist')->assertSuccessful();
        $json = file_get_contents(base_path('database/fixtures/musicbrainz/release-signals-at-dawn.json'));
        self::assertIsString($json);
        $decoded = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        self::assertIsArray($decoded);
        app(ImportReleaseBundle::class)->handle(app(MusicBrainzReleaseBundleNormalizer::class)->normalize($decoded));
    }

    public function test_empty_query_renders_search_entry_without_results(): void
    {
        $this->get('/search')
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->component('search/index')
                ->where('search.query', '')
                ->has('search.items', 0));
    }

    public function test_home_is_the_same_primary_discovery_entry(): void
    {
        $this->get('/')
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->component('search/index')
                ->where('search.query', ''));
    }

    public function test_fixture_search_returns_disambiguated_release_and_recording_canonical_links(): void
    {
        $this->importFixture();
        $release = Release::query()->where('title', 'Signals at Dawn')->firstOrFail();
        $recording = Recording::query()->where('title', 'Signals at Dawn')->firstOrFail();

        $this->get('/search?q=Signals%20at%20Dawn')
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->component('search/index')
                ->where('search.query', 'signals at dawn')
                ->where('search.items.0.type', 'Release')
                ->where('search.items.0.id', $release->id)
                ->where('search.items.0.path', route('releases.show', ['release' => $release->id, 'slug' => $release->slug], false))
                ->where('search.items.1.type', 'Recording')
                ->where('search.items.1.id', $recording->id)
                ->where('search.items.1.path', route('recordings.show', ['recording' => $recording->id, 'slug' => $recording->slug], false)));
    }

    public function test_exact_prefix_and_substring_ranking_is_deterministic(): void
    {
        Artist::query()->create(['name' => 'Northern Echo', 'slug' => 'northern-echo', 'type' => 'Group']);
        Artist::query()->create(['name' => 'Echo Park', 'slug' => 'echo-park', 'type' => 'Group']);
        Artist::query()->create(['name' => 'Echo', 'slug' => 'echo', 'type' => 'Group']);

        $this->get('/search?q=echo')
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->where('search.items.0.name', 'Echo')
                ->where('search.items.1.name', 'Echo Park')
                ->where('search.items.2.name', 'Northern Echo'));
    }

    public function test_long_query_is_bounded_and_mixed_script_names_are_searchable(): void
    {
        Artist::query()->create([
            'name' => '青い海 Orchestra — Night Sessions',
            'slug' => 'blue-sea-orchestra-night-sessions',
            'type' => 'Group',
            'country_code' => 'JP',
            'disambiguation' => 'Mixed-script discovery fixture',
        ]);

        $this->get('/search?q='.rawurlencode('青い海'))
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->where('search.items.0.type', 'Artist')
                ->where('search.items.0.name', '青い海 Orchestra — Night Sessions'));

        $long = str_repeat('A', 120);
        $this->get('/search?q='.$long)
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->where('search.query', str_repeat('a', 80))
                ->has('search.items', 0));
    }

    public function test_unknown_query_does_not_fabricate_results(): void
    {
        $this->importFixture();

        $this->get('/search?q=definitely-not-canonical')
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->where('search.query', 'definitely-not-canonical')
                ->has('search.items', 0));
    }
}
