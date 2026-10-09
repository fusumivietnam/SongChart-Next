<?php

namespace App\Music\Destinations;

use DateTimeInterface;
use Illuminate\Support\Facades\DB;
use InvalidArgumentException;

final class StoreDestinationLink
{
    /**
     * @param array<string,mixed>|null $provenance
     */
    public function handle(
        string $subjectType,
        string $subjectId,
        string $provider,
        string $destinationType,
        string $externalUrl,
        string $sourceName,
        ?string $sourceReference = null,
        ?array $provenance = null,
        string $verificationState = 'unverified',
        ?DateTimeInterface $verifiedAt = null,
    ): void {
        $subjectTable = match ($subjectType) {
            'release' => 'releases',
            'recording' => 'recordings',
            default => throw new InvalidArgumentException('Unsupported destination subject type.'),
        };

        if (! DB::table($subjectTable)->where('id', $subjectId)->exists()) {
            throw new InvalidArgumentException('Destination subject does not exist.');
        }

        if (! in_array($destinationType, ['listen', 'watch'], true)) {
            throw new InvalidArgumentException('Unsupported destination type.');
        }

        if (! in_array($verificationState, ['verified', 'unverified', 'blocked'], true)) {
            throw new InvalidArgumentException('Unsupported destination verification state.');
        }

        if ($verificationState === 'verified' && $verifiedAt === null) {
            throw new InvalidArgumentException('Verified destinations require verified_at.');
        }

        if ($verificationState !== 'verified' && $verifiedAt !== null) {
            throw new InvalidArgumentException('Only verified destinations may store verified_at.');
        }

        $provider = trim($provider);
        $sourceName = trim($sourceName);
        $externalUrl = trim($externalUrl);

        if ($provider === '' || mb_strlen($provider) > 64) {
            throw new InvalidArgumentException('Provider identity is required and bounded.');
        }

        if ($sourceName === '' || mb_strlen($sourceName) > 128) {
            throw new InvalidArgumentException('Source name is required and bounded.');
        }

        if (mb_strlen($externalUrl) > 2048 || filter_var($externalUrl, FILTER_VALIDATE_URL) === false) {
            throw new InvalidArgumentException('Destination URL is invalid.');
        }

        $scheme = strtolower((string) parse_url($externalUrl, PHP_URL_SCHEME));
        $host = parse_url($externalUrl, PHP_URL_HOST);
        if (! in_array($scheme, ['http', 'https'], true) || ! is_string($host) || $host === '') {
            throw new InvalidArgumentException('Destination URL must use HTTP(S) with an explicit host.');
        }

        DB::table('destination_links')->updateOrInsert(
            [
                'subject_type' => $subjectType,
                'subject_id' => $subjectId,
                'provider' => $provider,
                'destination_type' => $destinationType,
                'external_url_hash' => hash('sha256', $externalUrl),
            ],
            [
                'external_url' => $externalUrl,
                'source_name' => $sourceName,
                'source_reference' => $sourceReference,
                'provenance' => $provenance === null ? null : json_encode($provenance, JSON_THROW_ON_ERROR),
                'verification_state' => $verificationState,
                'verified_at' => $verifiedAt?->format('Y-m-d H:i:sP'),
                'created_at' => now(),
                'updated_at' => now(),
            ],
        );
    }
}
