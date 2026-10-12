<?php

namespace Tests\Feature;

use App\Music\Recordings\AdmitRecordingWorks;
use App\Music\Recordings\MusicBrainzRecordingWorkAdapter;
use App\Music\Releases\ImportReleaseBundle;
use App\Music\Releases\MusicBrainzReleaseLookupAdapter;
use Illuminate\Foundation\Testing\RefreshDatabase;
use InvalidArgumentException;
use RuntimeException;
use Tests\TestCase;

final class MusicBrainzRecordingWorkAdapterTest extends TestCase
{
    use RefreshDatabase;

    /** @return array<string,mixed> */
    private function recordingFixture(): array
    {
        $json = file_get_contents(base_path('database/fixtures/musicbrainz/recording-signals-at-dawn-work-lookup.json'));
        self::assertIsString($json);
        $decoded = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        self::assertIsArray($decoded);

        return $decoded;
    }

    private function admitReleaseWithoutWork(): void
    {
        $this->artisan('songchart:fixture:import-artist')->assertSuccessful();
        $json = file_get_contents(base_path('database/fixtures/musicbrainz/release-signals-at-dawn-lookup.json'));
        self::assertIsString($json);
        $payload = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        self::assertIsArray($payload);

        $claim = app(MusicBrainzReleaseLookupAdapter::class)->normalize($payload);
        app(ImportReleaseBundle::class)->handle($claim);
    }

    public function test_recording_work_performance_relation_is_admitted_idempotently(): void
    {
        $this->admitReleaseWithoutWork();
        $adapter = app(MusicBrainzRecordingWorkAdapter::class);
        $admitter = app(AdmitRecordingWorks::class);
        $claim = $adapter->normalize($this->recordingFixture());

        $this->assertSame('33333333-3333-4333-8333-333333333333', $claim->recordingExternalId);
        $this->assertCount(1, $claim->works);
        $this->assertSame('55555555-5555-4555-8555-555555555555', $claim->works[0]['external_id']);

        $admitter->handle($claim);
        $admitter->handle($claim);

        $this->assertDatabaseCount('works', 1);
        $this->assertDatabaseCount('recording_work', 1);
        $this->assertDatabaseHas('music_external_identities', [
            'provider' => 'musicbrainz',
            'entity_type' => 'work',
            'external_id' => '55555555-5555-4555-8555-555555555555',
        ]);
        $this->assertDatabaseHas('recording_work', ['relationship_type' => 'performance']);
    }

    public function test_recording_must_already_be_admitted_before_work_relationship_mutation(): void
    {
        $claim = app(MusicBrainzRecordingWorkAdapter::class)->normalize($this->recordingFixture());

        try {
            app(AdmitRecordingWorks::class)->handle($claim);
            $this->fail('Unadmitted Recording accepted a Work relationship.');
        } catch (RuntimeException $exception) {
            $this->assertStringContainsString('Recording must be admitted', $exception->getMessage());
        }

        $this->assertDatabaseCount('works', 0);
        $this->assertDatabaseCount('recording_work', 0);
    }

    public function test_unrepresentable_performance_attributes_fail_before_mutation(): void
    {
        $payload = $this->recordingFixture();
        $payload['relations'][1]['attributes'] = ['cover'];

        try {
            app(MusicBrainzRecordingWorkAdapter::class)->normalize($payload);
            $this->fail('Attributed performance relationship was accepted.');
        } catch (InvalidArgumentException $exception) {
            $this->assertStringContainsString('not representable', $exception->getMessage());
        }

        $this->assertDatabaseCount('works', 0);
        $this->assertDatabaseCount('recording_work', 0);
    }

    public function test_malformed_supported_relation_fails_instead_of_being_silently_dropped(): void
    {
        $payload = $this->recordingFixture();
        unset($payload['relations'][1]['work']);

        try {
            app(MusicBrainzRecordingWorkAdapter::class)->normalize($payload);
            $this->fail('Performance relationship without Work was accepted.');
        } catch (InvalidArgumentException $exception) {
            $this->assertStringContainsString('work object', $exception->getMessage());
        }

        $this->assertDatabaseCount('works', 0);
        $this->assertDatabaseCount('recording_work', 0);
    }
}
