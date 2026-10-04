<?php

namespace App\Music\Artists;

use App\Models\Artist;
use App\Models\ExternalIdentity;

final readonly class ArtistReadView
{
    /**
     * @param list<array{provider: string, entity_type: string, external_id: string, source_name: string}> $provenance
     */
    public function __construct(
        public string $id,
        public string $slug,
        public string $name,
        public ?string $type,
        public ?string $countryCode,
        public ?string $disambiguation,
        public array $provenance,
    ) {}

    public static function fromArtist(Artist $artist): self
    {
        $artist->loadMissing('externalIdentities');

        $provenance = $artist->externalIdentities
            ->map(static fn (ExternalIdentity $identity): array => [
                'provider' => $identity->provider,
                'entity_type' => $identity->entity_type,
                'external_id' => $identity->external_id,
                'source_name' => $identity->source_name,
            ])
            ->values()
            ->all();

        return new self(
            id: $artist->id,
            slug: $artist->slug,
            name: $artist->name,
            type: $artist->type,
            countryCode: $artist->country_code,
            disambiguation: $artist->disambiguation,
            provenance: $provenance,
        );
    }

    /**
     * @return array{
     *   id: string,
     *   slug: string,
     *   name: string,
     *   type: string|null,
     *   countryCode: string|null,
     *   disambiguation: string|null,
     *   provenance: list<array{provider: string, entity_type: string, external_id: string, source_name: string}>
     * }
     */
    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'slug' => $this->slug,
            'name' => $this->name,
            'type' => $this->type,
            'countryCode' => $this->countryCode,
            'disambiguation' => $this->disambiguation,
            'provenance' => $this->provenance,
        ];
    }
}
