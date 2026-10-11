<?php

namespace Tests\Feature;

use App\Models\Release;
use App\Music\Releases\ImportReleaseBundle;
use App\Music\Releases\MusicBrainzReleaseLookupAdapter;
use Illuminate\Foundation\Testing\RefreshDatabase;
use InvalidArgumentException;
use Tests\TestCase;

final class MusicBrainzReleaseLookupAdapterTest extends TestCase
{
    use RefreshDatabase;

    /** @return array<string,mixed> */
    private function lookupFixture(): array
    {
        $json = file_get_contents(base_path('database/fixtures/musicbrainz/release-signals-at-dawn-lookup.json'));
        self::assertIsString($json);
        $decoded = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        self::assertIsArray($decoded);

        return $decoded;
    }

    public function test_documented_release_lookup_shape_maps_to_existing_bundle_claim(): void
    {
        $claim = app(MusicBrainzReleaseLookupAdapter::class)->normalize($this->lookupFixture());

        $this->assertSame('22222222-2222-4222-8222-222222222222', $claim->release['external_id']);
        $this->assertSame('11111111-1111-4111-8111-111111111111', $claim->releaseGroup['external_id']);
        $this->assertSame('Signals at Dawn', $claim->release['title']);
        $this->assertSame('month', $claim->release['date_precision']);
        $this->assertSame(2024, $claim->release['release_year']);
        $this->assertSame(5, $claim->release['release_month']);
        $this->assertCount(1, $claim->media);
        $this->assertCount(2, $claim->media[0]['tracks']);
        $this->assertSame(['FIABC2400001'], $claim->media[0]['tracks'][0]['recording']['isrcs']);
        $this->assertNull($claim->media[0]['tracks'][0]['recording']['work']);
    }

    public function test_release_lookup_import_is_idempotent_without_inventing_work_relationships(): void
    {
        $this->artisan('songchart:fixture:import-artist')->assertSuccessful();
        $adapter = app(MusicBrainzReleaseLookupAdapter::class);
        $importer = app(ImportReleaseBundle::class);
        $claim = $adapter->normalize($this->lookupFixture());

        $first = $importer->handle($claim);
        $second = $importer->handle($claim);

        $this->assertSame($first->id, $second->id);
        $this->assertDatabaseCount('release_groups', 1);
        $this->assertDatabaseCount('releases', 1);
        $this->assertDatabaseCount('recordings', 2);
        $this->assertDatabaseCount('release_tracks', 2);
        $this->assertDatabaseCount('recording_isrcs', 2);
        $this->assertDatabaseCount('works', 0);
        $this->assertDatabaseCount('recording_work', 0);
    }

    public function test_missing_release_group_fails_before_canonical_mutation(): void
    {
        $payload = $this->lookupFixture();
        unset($payload['release-group']);

        try {
            app(MusicBrainzReleaseLookupAdapter::class)->normalize($payload);
            $this->fail('Release lookup without release-group was accepted.');
        } catch (InvalidArgumentException $exception) {
            $this->assertStringContainsString('release-group', $exception->getMessage());
        }

        $this->assertSame(0, Release::query()->count());
    }

    public function test_missing_media_fails_before_canonical_mutation(): void
    {
        $payload = $this->lookupFixture();
        unset($payload['media']);

        try {
            app(MusicBrainzReleaseLookupAdapter::class)->normalize($payload);
            $this->fail('Release lookup without media was accepted.');
        } catch (InvalidArgumentException $exception) {
            $this->assertStringContainsString('media', $exception->getMessage());
        }

        $this->assertSame(0, Release::query()->count());
    }
}
