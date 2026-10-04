<?php

namespace App\Music\Providers\MusicBrainz;

use App\Music\Artists\MusicBrainzArtistNormalizer;
use App\Music\Providers\ProviderDelay;
use App\Music\Providers\ProviderEvidenceStore;
use App\Music\Providers\ProviderFetchStatus;
use App\Music\Providers\ProviderRequestGate;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Str;
use InvalidArgumentException;
use JsonException;
use RuntimeException;
use Throwable;

final readonly class MusicBrainzArtistClient
{
    private const PROVIDER = 'musicbrainz';

    private const SCHEMA_VERSION = 'musicbrainz-ws2-artist-json-v1';

    public function __construct(
        private ProviderRequestGate $requestGate,
        private ProviderDelay $delay,
        private ProviderEvidenceStore $evidence,
        private MusicBrainzArtistNormalizer $normalizer,
    ) {}

    public function fetch(string $mbid): MusicBrainzArtistResult
    {
        $mbid = strtolower(trim($mbid));

        if (! Str::isUuid($mbid)) {
            throw new InvalidArgumentException('MusicBrainz artist id must be a UUID.');
        }

        if (! $this->liveEnabled()) {
            return new MusicBrainzArtistResult(
                status: ProviderFetchStatus::Disabled,
                errorCode: 'live_provider_disabled',
            );
        }

        $requestIdentity = "/artist/{$mbid}?fmt=json";
        $maxAttempts = $this->maxAttempts();
        $lastEvidenceId = null;

        for ($attempt = 1; $attempt <= $maxAttempts; $attempt++) {
            $this->requestGate->acquire(self::PROVIDER);

            try {
                $response = Http::withHeaders([
                    'User-Agent' => $this->userAgent(),
                    'Accept' => 'application/json',
                ])
                    ->timeout($this->timeoutSeconds())
                    ->get($this->baseUrl().'/artist/'.$mbid, ['fmt' => 'json']);
            } catch (ConnectionException $exception) {
                $lastEvidenceId = $this->evidence->record(
                    provider: self::PROVIDER,
                    requestIdentity: $requestIdentity,
                    httpStatus: null,
                    payload: null,
                    retentionClass: 'provider-error-7d',
                    retentionDays: $this->errorRetentionDays(),
                    schemaVersion: self::SCHEMA_VERSION,
                );

                return new MusicBrainzArtistResult(
                    status: ProviderFetchStatus::Unavailable,
                    evidenceFetchId: $lastEvidenceId,
                    errorCode: 'network_failure',
                );
            }

            $status = $response->status();
            $body = $response->body();

            if ($status === 404) {
                $lastEvidenceId = $this->recordErrorEvidence($requestIdentity, $status, $body);

                return new MusicBrainzArtistResult(
                    status: ProviderFetchStatus::NotFound,
                    evidenceFetchId: $lastEvidenceId,
                    errorCode: 'not_found',
                );
            }

            if ($status === 503) {
                $lastEvidenceId = $this->recordErrorEvidence($requestIdentity, $status, $body);

                if ($attempt < $maxAttempts) {
                    $this->delay->sleepMilliseconds($this->backoffMilliseconds($requestIdentity, $attempt));

                    continue;
                }

                return new MusicBrainzArtistResult(
                    status: ProviderFetchStatus::Unavailable,
                    evidenceFetchId: $lastEvidenceId,
                    errorCode: 'provider_throttled',
                );
            }

            if ($status < 200 || $status >= 300) {
                $lastEvidenceId = $this->recordErrorEvidence($requestIdentity, $status, $body);

                return new MusicBrainzArtistResult(
                    status: ProviderFetchStatus::Unavailable,
                    evidenceFetchId: $lastEvidenceId,
                    errorCode: 'provider_http_error',
                );
            }

            try {
                $decoded = json_decode($body, true, 512, JSON_THROW_ON_ERROR);
                if (! is_array($decoded)) {
                    throw new RuntimeException('MusicBrainz response must decode to a JSON object.');
                }

                /** @var array<string, mixed> $decoded */
                $claim = $this->normalizer->normalize($decoded);
            } catch (JsonException|InvalidArgumentException|RuntimeException $exception) {
                $lastEvidenceId = $this->recordErrorEvidence($requestIdentity, $status, $body);

                return new MusicBrainzArtistResult(
                    status: ProviderFetchStatus::Malformed,
                    evidenceFetchId: $lastEvidenceId,
                    errorCode: 'malformed_provider_response',
                );
            } catch (Throwable $exception) {
                throw $exception;
            }

            $lastEvidenceId = $this->evidence->record(
                provider: self::PROVIDER,
                requestIdentity: $requestIdentity,
                httpStatus: $status,
                payload: $body,
                retentionClass: 'approved-core-success-30d',
                retentionDays: $this->successRetentionDays(),
                schemaVersion: self::SCHEMA_VERSION,
            );

            return new MusicBrainzArtistResult(
                status: ProviderFetchStatus::Success,
                claim: $claim,
                evidenceFetchId: $lastEvidenceId,
            );
        }

        return new MusicBrainzArtistResult(
            status: ProviderFetchStatus::Unavailable,
            evidenceFetchId: $lastEvidenceId,
            errorCode: 'provider_unavailable',
        );
    }

    private function recordErrorEvidence(string $requestIdentity, int $status, string $body): string
    {
        return $this->evidence->record(
            provider: self::PROVIDER,
            requestIdentity: $requestIdentity,
            httpStatus: $status,
            payload: $body,
            retentionClass: 'provider-error-7d',
            retentionDays: $this->errorRetentionDays(),
            schemaVersion: self::SCHEMA_VERSION,
        );
    }

    private function backoffMilliseconds(string $requestIdentity, int $attempt): int
    {
        $base = min(4000, 500 * (2 ** ($attempt - 1)));
        $jitter = abs(crc32($requestIdentity.'|'.$attempt)) % 251;

        return $base + $jitter;
    }

    private function liveEnabled(): bool
    {
        return filter_var(config('services.musicbrainz.live_enabled', false), FILTER_VALIDATE_BOOL);
    }

    private function baseUrl(): string
    {
        $value = config('services.musicbrainz.base_url');
        if (! is_string($value) || $value === '') {
            throw new RuntimeException('MusicBrainz base URL is not configured.');
        }

        return rtrim($value, '/');
    }

    private function userAgent(): string
    {
        $value = config('services.musicbrainz.user_agent');
        if (! is_string($value) || trim($value) === '') {
            throw new RuntimeException('MusicBrainz User-Agent is not configured.');
        }

        return trim($value);
    }

    private function timeoutSeconds(): int
    {
        return max(1, (int) config('services.musicbrainz.timeout_seconds', 8));
    }

    private function maxAttempts(): int
    {
        return max(1, min(3, (int) config('services.musicbrainz.max_attempts', 3)));
    }

    private function successRetentionDays(): int
    {
        return (int) config('services.musicbrainz.success_retention_days', 30);
    }

    private function errorRetentionDays(): int
    {
        return (int) config('services.musicbrainz.error_retention_days', 7);
    }
}
