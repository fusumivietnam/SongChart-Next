<?php

namespace Tests\Feature;

use App\Models\Recording;
use App\Music\Destinations\StoreDestinationLink;
use App\Music\Releases\ImportReleaseBundle;
use App\Music\Releases\MusicBrainzReleaseBundleNormalizer;
use DateTimeImmutable;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Inertia\Testing\AssertableInertia as Assert;
use InvalidArgumentException;
use Tests\TestCase;

final class DestinationLinkTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->withoutVite();
    }

    private function recording(): Recording
    {
        $this->artisan('songchart:fixture:import-artist')->assertSuccessful();
        $json = file_get_contents(base_path('database/fixtures/musicbrainz/release-signals-at-dawn.json'));
        self::assertIsString($json);
        $decoded = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        self::assertIsArray($decoded);
        app(ImportReleaseBundle::class)->handle(app(MusicBrainzReleaseBundleNormalizer::class)->normalize($decoded));

        return Recording::query()->where('title', 'Signals at Dawn')->firstOrFail();
    }

    public function test_verified_destination_is_persisted_once_and_exposed_on_recording_page(): void
    {
        $recording = $this->recording();
        $store = app(StoreDestinationLink::class);
        $verifiedAt = new DateTimeImmutable('2026-10-09T12:00:00+00:00');

        foreach ([1, 2] as $_) {
            $store->handle(
                'recording',
                $recording->id,
                'Fixture Audio',
                'listen',
                'https://listen.example.test/recordings/signals-at-dawn',
                'vs-03c deterministic fixture',
                'fixture:signals-at-dawn',
                ['fixture' => true],
                'verified',
                $verifiedAt,
            );
        }

        self::assertSame(1, DB::table('destination_links')->count());

        $this->get(route('recordings.show', ['recording' => $recording->id, 'slug' => $recording->slug]))
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->component('recordings/show')
                ->where('recording.destinations.0.provider', 'Fixture Audio')
                ->where('recording.destinations.0.destination_type', 'listen')
                ->where('recording.destinations.0.external_url', 'https://listen.example.test/recordings/signals-at-dawn')
                ->has('recording.destinations', 1));
    }

    public function test_unverified_destination_is_not_exposed_publicly(): void
    {
        $recording = $this->recording();

        app(StoreDestinationLink::class)->handle(
            'recording',
            $recording->id,
            'Fixture Pending',
            'listen',
            'https://pending.example.test/recordings/signals-at-dawn',
            'vs-03c deterministic fixture',
        );

        $this->get(route('recordings.show', ['recording' => $recording->id, 'slug' => $recording->slug]))
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page->has('recording.destinations', 0));
    }

    public function test_unsafe_destination_scheme_fails_closed(): void
    {
        $recording = $this->recording();

        $this->expectException(InvalidArgumentException::class);
        $this->expectExceptionMessage('HTTP(S)');

        app(StoreDestinationLink::class)->handle(
            'recording',
            $recording->id,
            'Fixture Unsafe',
            'listen',
            'javascript:alert(1)',
            'vs-03c deterministic fixture',
        );
    }

    public function test_verified_state_requires_deterministic_verification_timestamp(): void
    {
        $recording = $this->recording();

        $this->expectException(InvalidArgumentException::class);
        $this->expectExceptionMessage('verified_at');

        app(StoreDestinationLink::class)->handle(
            'recording',
            $recording->id,
            'Fixture Audio',
            'listen',
            'https://listen.example.test/recordings/signals-at-dawn',
            'vs-03c deterministic fixture',
            verificationState: 'verified',
        );
    }
}
