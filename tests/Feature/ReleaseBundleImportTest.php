<?php

namespace Tests\Feature;

use App\Models\Recording;
use App\Models\Release;
use App\Music\Releases\ImportReleaseBundle;
use App\Music\Releases\MusicBrainzReleaseBundleNormalizer;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use RuntimeException;
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
    public function test_isrc_conflict_rolls_back_existing_bundle_update(): void
    {
        $release = $this->importFixture();
        $originalOwner = DB::table('recording_isrcs')->where('isrc', 'FIABC2400001')->value('recording_id');
        $originalMedium = DB::table('release_media')->where('release_id', $release->id)->value('id');
        self::assertNotNull($originalOwner);
        self::assertNotNull($originalMedium);
        $json = file_get_contents(base_path('database/fixtures/musicbrainz/release-signals-at-dawn.json'));
        self::assertIsString($json);
        $decoded = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        self::assertIsArray($decoded);
        $decoded['release']['title'] = 'Rejected update';
        $decoded['media'][0]['tracks'][1]['recording']['isrcs'] = ['FIABC2400001'];

        try {
            app(ImportReleaseBundle::class)->handle(app(MusicBrainzReleaseBundleNormalizer::class)->normalize($decoded));
            $this->fail('Conflicting ISRC was accepted.');
        } catch (RuntimeException $exception) {
            $this->assertStringContainsString('ISRC already belongs', $exception->getMessage());
        }

        $this->assertSame('Signals at Dawn', $release->refresh()->title);
        $this->assertSame($originalOwner, DB::table('recording_isrcs')->where('isrc', 'FIABC2400001')->value('recording_id'));
        $this->assertSame($originalMedium, DB::table('release_media')->where('release_id', $release->id)->value('id'));
        $this->assertDatabaseCount('recordings', 2);
        $this->assertDatabaseCount('recording_isrcs', 2);
        $this->assertDatabaseCount('release_tracks', 2);
        $this->assertDatabaseCount('entity_credits', 3);
    }

    public function test_isrc_conflict_inside_new_bundle_rolls_back_all_entities(): void
    {
        $this->artisan('songchart:fixture:import-artist')->assertSuccessful();
        $json = file_get_contents(base_path('database/fixtures/musicbrainz/release-signals-at-dawn.json'));
        self::assertIsString($json);
        $decoded = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        self::assertIsArray($decoded);
        $decoded['media'][0]['tracks'][1]['recording']['isrcs'] = ['FIABC2400001'];

        try {
            app(ImportReleaseBundle::class)->handle(app(MusicBrainzReleaseBundleNormalizer::class)->normalize($decoded));
            $this->fail('Conflicting ISRC was accepted.');
        } catch (RuntimeException $exception) {
            $this->assertStringContainsString('ISRC already belongs', $exception->getMessage());
        }

        foreach (['release_groups', 'releases', 'recordings', 'works', 'release_media', 'release_tracks', 'entity_credits', 'recording_work', 'recording_isrcs', 'music_external_identities'] as $table) {
            $this->assertDatabaseCount($table, 0);
        }
        $this->assertDatabaseCount('artists', 1);
    }
}
