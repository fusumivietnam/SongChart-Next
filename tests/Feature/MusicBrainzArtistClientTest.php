<?php

namespace Tests\Feature;

use App\Models\Artist;
use App\Music\Artists\MusicBrainzArtistNormalizer;
use App\Music\Providers\MusicBrainz\MusicBrainzArtistClient;
use App\Music\Providers\ProviderDelay;
use App\Music\Providers\ProviderEvidenceStore;
use App\Music\Providers\ProviderFetchStatus;
use App\Music\Providers\ProviderRequestGate;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\Client\Request;
use Illuminate\Support\Facades\Date;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

final class MusicBrainzArtistClientTest extends TestCase
{
    use RefreshDatabase;

    private const MBID = '8f3a5f22-4d6b-4d3f-9a62-4ca0f36a2a10';

    protected function setUp(): void
    {
        parent::setUp();

        config()->set('services.musicbrainz.live_enabled', true);
        config()->set('services.musicbrainz.base_url', 'https://musicbrainz.test/ws/2');
        config()->set('services.musicbrainz.user_agent', 'SongChartNext/0.1 (+https://example.test/contact)');
        config()->set('services.musicbrainz.max_attempts', 3);
    }

    public function test_success_normalizes_only_approved_artist_fields_and_records_30_day_evidence(): void
    {
        Http::fake([
            '*' => Http::response([
                'id' => self::MBID,
                'name' => 'Aster Echo',
                'type' => 'Group',
                'country' => 'FI',
                'disambiguation' => 'Live provider fixture',
                'tags' => [['name' => 'not-approved-for-ingestion']],
                'rating' => ['value' => 5],
            ], 200),
        ]);

        [$client, $gate] = $this->client();
        $result = $client->fetch(self::MBID);

        $this->assertSame(ProviderFetchStatus::Success, $result->status);
        $this->assertNotNull($result->claim);
        $this->assertSame(self::MBID, $result->claim->externalId);
        $this->assertSame('Aster Echo', $result->claim->name);
        $this->assertSame('FI', $result->claim->countryCode);
        $this->assertSame(1, $gate->acquisitions);
        $this->assertSame(0, Artist::query()->count(), 'Provider fetch must not write canonical Artist rows.');

        Http::assertSent(fn (Request $request): bool =>
            $request->hasHeader('User-Agent', 'SongChartNext/0.1 (+https://example.test/contact)')
            && str_contains($request->url(), '/artist/'.self::MBID)
            && str_contains($request->url(), 'fmt=json'));

        $this->assertDatabaseHas('provider_fetches', [
            'id' => $result->evidenceFetchId,
            'provider' => 'musicbrainz',
            'http_status' => 200,
            'retention_class' => 'approved-core-success-30d',
        ]);
        $this->assertSame(1, DB::table('provider_evidence_blobs')->count());
    }

    public function test_404_returns_typed_not_found_without_canonical_mutation(): void
    {
        Http::fake(['*' => Http::response(['error' => 'Not Found'], 404)]);

        [$client] = $this->client();
        $result = $client->fetch(self::MBID);

        $this->assertSame(ProviderFetchStatus::NotFound, $result->status);
        $this->assertSame('not_found', $result->errorCode);
        $this->assertSame(0, Artist::query()->count());
        $this->assertDatabaseHas('provider_fetches', [
            'id' => $result->evidenceFetchId,
            'retention_class' => 'provider-error-7d',
            'http_status' => 404,
        ]);
    }

    public function test_malformed_success_response_is_rejected_and_retained_for_7_days(): void
    {
        Http::fake(['*' => Http::response('{"id":', 200, ['Content-Type' => 'application/json'])]);

        [$client] = $this->client();
        $result = $client->fetch(self::MBID);

        $this->assertSame(ProviderFetchStatus::Malformed, $result->status);
        $this->assertSame('malformed_provider_response', $result->errorCode);
        $this->assertNull($result->claim);
        $this->assertSame(0, Artist::query()->count());
        $this->assertDatabaseHas('provider_fetches', [
            'id' => $result->evidenceFetchId,
            'retention_class' => 'provider-error-7d',
        ]);
    }

    public function test_network_failure_returns_unavailable_without_raw_blob_or_canonical_mutation(): void
    {
        Http::fake(['*' => Http::failedConnection('simulated timeout')]);

        [$client] = $this->client();
        $result = $client->fetch(self::MBID);

        $this->assertSame(ProviderFetchStatus::Unavailable, $result->status);
        $this->assertSame('network_failure', $result->errorCode);
        $this->assertSame(0, Artist::query()->count());
        $this->assertSame(0, DB::table('provider_evidence_blobs')->count());
        $this->assertDatabaseHas('provider_fetches', [
            'id' => $result->evidenceFetchId,
            'http_status' => null,
            'retention_class' => 'provider-error-7d',
        ]);
    }

    public function test_503_retries_are_bounded_jittered_and_rate_gated_on_every_attempt(): void
    {
        Http::fakeSequence()
            ->push('busy-1', 503)
            ->push('busy-2', 503)
            ->push('busy-3', 503);

        [$client, $gate, $delay] = $this->client();
        $result = $client->fetch(self::MBID);

        $this->assertSame(ProviderFetchStatus::Unavailable, $result->status);
        $this->assertSame('provider_throttled', $result->errorCode);
        $this->assertSame(3, $gate->acquisitions);
        $this->assertCount(2, $delay->milliseconds);
        $this->assertGreaterThanOrEqual(500, $delay->milliseconds[0]);
        $this->assertLessThanOrEqual(750, $delay->milliseconds[0]);
        $this->assertGreaterThanOrEqual(1000, $delay->milliseconds[1]);
        $this->assertLessThanOrEqual(1250, $delay->milliseconds[1]);
        $this->assertSame(3, DB::table('provider_fetches')->count());
        $this->assertSame(0, Artist::query()->count());
    }

    public function test_live_provider_is_disabled_by_default_contract(): void
    {
        config()->set('services.musicbrainz.live_enabled', false);
        Http::preventStrayRequests();

        [$client, $gate] = $this->client();
        $result = $client->fetch(self::MBID);

        $this->assertSame(ProviderFetchStatus::Disabled, $result->status);
        $this->assertSame(0, $gate->acquisitions);
        Http::assertNothingSent();
    }

    public function test_retention_cleanup_removes_expired_fetch_and_unreferenced_blob(): void
    {
        Date::setTestNow('2026-10-04 00:00:00');
        $store = app(ProviderEvidenceStore::class);
        $store->record(
            provider: 'musicbrainz',
            requestIdentity: '/artist/'.self::MBID.'?fmt=json',
            httpStatus: 200,
            payload: '{"id":"'.self::MBID.'"}',
            retentionClass: 'approved-core-success-30d',
            retentionDays: 30,
            schemaVersion: 'musicbrainz-ws2-artist-json-v1',
        );

        $this->assertSame(1, DB::table('provider_fetches')->count());
        $this->assertSame(1, DB::table('provider_evidence_blobs')->count());

        Date::setTestNow('2026-11-04 00:00:01');
        $deleted = $store->purgeExpired();

        $this->assertSame(1, $deleted['fetches']);
        $this->assertSame(1, $deleted['blobs']);
        $this->assertSame(0, DB::table('provider_fetches')->count());
        $this->assertSame(0, DB::table('provider_evidence_blobs')->count());
    }

    /**
     * @return array{0: MusicBrainzArtistClient, 1: object, 2: object}
     */
    private function client(): array
    {
        $gate = new class implements ProviderRequestGate
        {
            public int $acquisitions = 0;

            public function acquire(string $provider): void
            {
                $this->acquisitions++;
            }
        };

        $delay = new class implements ProviderDelay
        {
            /** @var list<int> */
            public array $milliseconds = [];

            public function sleepMilliseconds(int $milliseconds): void
            {
                $this->milliseconds[] = $milliseconds;
            }
        };

        return [
            new MusicBrainzArtistClient(
                requestGate: $gate,
                delay: $delay,
                evidence: app(ProviderEvidenceStore::class),
                normalizer: app(MusicBrainzArtistNormalizer::class),
            ),
            $gate,
            $delay,
        ];
    }
}
