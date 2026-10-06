<?php

namespace Tests\Feature;

use App\Models\Recording;
use App\Models\Release;
use App\Music\Releases\ImportReleaseBundle;
use App\Music\Releases\MusicBrainzReleaseBundleNormalizer;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Tests\TestCase;

final class ReleaseBundleImportTest extends TestCase
{
    use RefreshDatabase;

    private function importFixture(): Release
    {
        $this->artisan('songchart:fixture:import-artist')->assertSuccessful();
        $json = file_get_contents(base_path('database/fixtures/musicbrainz/release-signals-at-dawn.json'));
        self::assertIsString($json);
        $decoded = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        self::assertIsArray($decoded);

        return app(ImportReleaseBundle::class)->handle(
            app(MusicBrainzReleaseBundleNormalizer::class)->normalize($decoded),
        );
    }

    public function test_bundle_import_preserves_entity_distinctions_and_relationships(): void
    {
        $release = $this->importFixture();

        $this->assertDatabaseCount('release_groups', 1);
        $this->assertDatabaseCount('releases', 1);
        $this->assertDatabaseCount('recordings', 2);
        $this->assertDatabaseCount('works', 1);
        $this->assertDatabaseCount('release_media', 1);
        $this->assertDatabaseCount('release_tracks', 2);
        $this->assertDatabaseCount('entity_credits', 3);
        $this->assertDatabaseHas('entity_credits', ['subject_type' => 'release', 'credited_as' => 'Aster Echo', 'position' => 1]);
        $this->assertSame(2, DB::table('entity_credits')->where('subject_type', 'recording')->count());
        $this->assertDatabaseCount('recording_work', 1);
        $this->assertDatabaseCount('recording_isrcs', 2);
        $this->assertSame('month', $release->date_precision);
        $this->assertSame(2024, $release->release_year);
        $this->assertSame(5, $release->release_month);
        $this->assertNull($release->release_day);

        $track = DB::table('release_tracks')->where('position', 2)->first();
        self::assertNotNull($track);
        $recording = Recording::query()->findOrFail($track->recording_id);
        $this->assertSame('Northern Static (Album Edit)', $track->title);
        $this->assertSame('Northern Static', $recording->title);
    }

    public function test_duplicate_bundle_import_is_idempotent_by_external_identity(): void
    {
        $first = $this->importFixture();
        $second = $this->importFixture();

        $this->assertSame($first->id, $second->id);
        $this->assertDatabaseCount('release_groups', 1);
        $this->assertDatabaseCount('releases', 1);
        $this->assertDatabaseCount('recordings', 2);
        $this->assertDatabaseCount('works', 1);
        $this->assertDatabaseCount('release_tracks', 2);
        $this->assertDatabaseCount('entity_credits', 3);
    }

    public function test_same_title_with_different_provider_id_does_not_merge_release(): void
    {
        $this->importFixture();
        $json = file_get_contents(base_path('database/fixtures/musicbrainz/release-signals-at-dawn.json'));
        self::assertIsString($json);
        $decoded = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        self::assertIsArray($decoded);
        $decoded['release']['id'] = '66666666-6666-4666-8666-666666666666';
        $decoded['release']['barcode'] = '6412345678902';

        app(ImportReleaseBundle::class)->handle(app(MusicBrainzReleaseBundleNormalizer::class)->normalize($decoded));

        $this->assertDatabaseCount('releases', 2);
        $this->assertSame(2, Release::query()->where('title', 'Signals at Dawn')->count());
    }
}
