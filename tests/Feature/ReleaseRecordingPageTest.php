<?php

namespace Tests\Feature;

use App\Models\Recording;
use App\Music\Releases\ImportReleaseBundle;
use App\Music\Releases\MusicBrainzReleaseBundleNormalizer;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Inertia\Testing\AssertableInertia as Assert;
use Tests\TestCase;

final class ReleaseRecordingPageTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->withoutVite();
    }

    /** @return array{release:\App\Models\Release, recording:Recording} */
    private function fixture(): array
    {
        $this->artisan('songchart:fixture:import-artist')->assertSuccessful();
        $json = file_get_contents(base_path('database/fixtures/musicbrainz/release-signals-at-dawn.json'));
        self::assertIsString($json);
        $decoded = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        self::assertIsArray($decoded);
        $release = app(ImportReleaseBundle::class)->handle(app(MusicBrainzReleaseBundleNormalizer::class)->normalize($decoded));
        $recording = Recording::query()->where('title', 'Signals at Dawn')->firstOrFail();
        return ['release' => $release, 'recording' => $recording];
    }

    public function test_release_page_exposes_typed_release_track_and_credit_view(): void
    {
        ['release' => $release] = $this->fixture();
        $this->get(route('releases.show', ['release' => $release->id, 'slug' => $release->slug]))
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->component('releases/show')
                ->where('release.id', $release->id)
                ->where('release.date', '2024-05')
                ->where('release.credits.0.credited_as', 'Aster Echo')
                ->where('release.media.0.tracks.1.title', 'Northern Static (Album Edit)')
                ->where('release.media.0.tracks.1.recording_title', 'Northern Static'));
    }

    public function test_recording_page_exposes_isrc_work_and_release_relationship(): void
    {
        ['recording' => $recording] = $this->fixture();
        $this->get(route('recordings.show', ['recording' => $recording->id, 'slug' => $recording->slug]))
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->component('recordings/show')
                ->where('recording.id', $recording->id)
                ->where('recording.isrcs.0', 'FIABC2400001')
                ->where('recording.works.0.title', 'Signals at Dawn')
                ->where('recording.releases.0.title', 'Signals at Dawn'));
    }

    public function test_missing_or_stale_slugs_redirect_to_canonical_entity_urls(): void
    {
        ['release' => $release, 'recording' => $recording] = $this->fixture();

        $this->get("/releases/{$release->id}")
            ->assertRedirect(route('releases.show', ['release' => $release->id, 'slug' => $release->slug], false))
            ->assertStatus(301);
        $this->get("/recordings/{$recording->id}/stale-title")
            ->assertRedirect(route('recordings.show', ['recording' => $recording->id, 'slug' => $recording->slug], false))
            ->assertStatus(301);
    }
}
