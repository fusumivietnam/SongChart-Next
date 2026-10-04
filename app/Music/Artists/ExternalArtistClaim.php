<?php

namespace App\Music\Artists;

final readonly class ExternalArtistClaim
{
    public function __construct(
        public string $provider,
        public string $entityType,
        public string $externalId,
        public string $name,
        public ?string $type,
        public ?string $countryCode,
        public ?string $disambiguation,
        public string $sourceName,
    ) {}

    /** @return array<string, string|null> */
    public function provenance(): array
    {
        return [
            'provider' => $this->provider,
            'entity_type' => $this->entityType,
            'external_id' => $this->externalId,
            'source_name' => $this->sourceName,
        ];
    }
}
