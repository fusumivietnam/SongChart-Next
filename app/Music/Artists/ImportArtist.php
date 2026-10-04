<?php

namespace App\Music\Artists;

use App\Models\Artist;
use App\Models\ExternalIdentity;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

final class ImportArtist
{
    public function handle(ExternalArtistClaim $claim): Artist
    {
        return DB::transaction(function () use ($claim): Artist {
            $identity = ExternalIdentity::query()
                ->where('provider', $claim->provider)
                ->where('entity_type', $claim->entityType)
                ->where('external_id', $claim->externalId)
                ->lockForUpdate()
                ->first();

            if ($identity !== null) {
                $artist = $identity->artist;
                $this->applyClaim($artist, $claim);

                $identity->update([
                    'source_name' => $claim->sourceName,
                    'provenance' => $claim->provenance(),
                ]);

                return $artist->refresh();
            }

            $artist = Artist::query()->create([
                'name' => $claim->name,
                'slug' => $this->slug($claim->name),
                'type' => $claim->type,
                'country_code' => $claim->countryCode,
                'disambiguation' => $claim->disambiguation,
            ]);

            ExternalIdentity::query()->create([
                'artist_id' => $artist->id,
                'provider' => $claim->provider,
                'entity_type' => $claim->entityType,
                'external_id' => $claim->externalId,
                'source_name' => $claim->sourceName,
                'provenance' => $claim->provenance(),
            ]);

            return $artist->refresh();
        });
    }

    private function applyClaim(Artist $artist, ExternalArtistClaim $claim): void
    {
        $artist->update([
            'name' => $claim->name,
            'slug' => $this->slug($claim->name),
            'type' => $claim->type,
            'country_code' => $claim->countryCode,
            'disambiguation' => $claim->disambiguation,
        ]);
    }

    private function slug(string $name): string
    {
        $slug = Str::slug($name);

        return $slug !== '' ? $slug : 'artist';
    }
}
