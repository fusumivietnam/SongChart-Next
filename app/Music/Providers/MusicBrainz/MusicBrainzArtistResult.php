<?php

namespace App\Music\Providers\MusicBrainz;

use App\Music\Artists\ExternalArtistClaim;
use App\Music\Providers\ProviderFetchStatus;

final readonly class MusicBrainzArtistResult
{
    public function __construct(
        public ProviderFetchStatus $status,
        public ?ExternalArtistClaim $claim = null,
        public ?string $evidenceFetchId = null,
        public ?string $errorCode = null,
    ) {}

    public function succeeded(): bool
    {
        return $this->status === ProviderFetchStatus::Success && $this->claim !== null;
    }
}
