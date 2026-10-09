<?php

namespace App\Music\Artists;

use App\Models\Artist;
use App\Models\ExternalIdentity;
use Illuminate\Support\Facades\DB;

final readonly class ArtistReadView
{
    /**
     * @param list<array{provider: string, entity_type: string, external_id: string, source_name: string}> $provenance
     * @param list<array{id: string, slug: string, title: string, status: string|null, countryCode: string|null, releaseYear: int|null, path: string}> $releases
     */
    public function __construct(
        public string $id,
        public string $slug,
        public string $name,
        public ?string $type,
        public ?string $countryCode,
        public ?string $disambiguation,
        public array $provenance,
        public array $releases,
    ) {}

    public static function fromArtist(Artist $artist): self
    {
        $artist->loadMissing('externalIdentities');

        $provenance = array_values($artist->externalIdentities
            ->map(static fn (ExternalIdentity $identity): array => [
                'provider' => $identity->provider,
                'entity_type' => $identity->entity_type,
                'external_id' => $identity->external_id,
                'source_name' => $identity->source_name,
            ])
            ->all());

        $releases = array_values(DB::table('entity_credits')
            ->join('releases', 'releases.id', '=', 'entity_credits.subject_id')
            ->where('entity_credits.subject_type', 'release')
            ->where('entity_credits.artist_id', $artist->id)
            ->select([
                'releases.id',
                'releases.slug',
                'releases.title',
                'releases.status',
                'releases.country_code',
                'releases.release_year',
            ])
            ->distinct()
            ->orderByDesc('releases.release_year')
            ->orderBy('releases.title')
            ->orderBy('releases.id')
            ->limit(20)
            ->get()
            ->map(static fn (object $release): array => [
                'id' => (string) $release->id,
                'slug' => (string) $release->slug,
                'title' => (string) $release->title,
                'status' => is_string($release->status) ? $release->status : null,
                'countryCode' => is_string($release->country_code) ? $release->country_code : null,
                'releaseYear' => is_numeric($release->release_year) ? (int) $release->release_year : null,
                'path' => route('releases.show', [
                    'release' => (string) $release->id,
                    'slug' => (string) $release->slug,
                ], false),
            ])
            ->all());

        return new self(
            id: $artist->id,
            slug: $artist->slug,
            name: $artist->name,
            type: $artist->type,
            countryCode: $artist->country_code,
            disambiguation: $artist->disambiguation,
            provenance: $provenance,
            releases: $releases,
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
     *   provenance: list<array{provider: string, entity_type: string, external_id: string, source_name: string}>,
     *   releases: list<array{id: string, slug: string, title: string, status: string|null, countryCode: string|null, releaseYear: int|null, path: string}>
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
            'releases' => $this->releases,
        ];
    }
}
