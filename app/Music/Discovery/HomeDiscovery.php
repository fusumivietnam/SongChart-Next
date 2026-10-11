<?php

namespace App\Music\Discovery;

use App\Models\Artist;
use App\Models\Recording;
use App\Models\Release;

final class HomeDiscovery
{
    public const PER_ENTITY_LIMIT = 3;

    /**
     * @return array{
     *   artists:list<array{type:string,id:string,name:string,detail:string,path:string}>,
     *   releases:list<array{type:string,id:string,name:string,detail:string,path:string}>,
     *   recordings:list<array{type:string,id:string,name:string,detail:string,path:string}>
     * }
     */
    public function toArray(): array
    {
        return [
            'artists' => $this->artists(),
            'releases' => $this->releases(),
            'recordings' => $this->recordings(),
        ];
    }

    /** @return list<array{type:string,id:string,name:string,detail:string,path:string}> */
    private function artists(): array
    {
        return array_values(Artist::query()
            ->orderByRaw('LOWER(name)')
            ->orderBy('id')
            ->limit(self::PER_ENTITY_LIMIT)
            ->get()
            ->map(function (Artist $artist): array {
                $detail = array_values(array_filter([
                    $artist->type,
                    $artist->country_code,
                    $artist->disambiguation,
                ], static fn (?string $value): bool => $value !== null && $value !== ''));

                return [
                    'type' => 'Artist',
                    'id' => $artist->id,
                    'name' => $artist->name,
                    'detail' => $detail === [] ? 'Artist' : implode(' · ', $detail),
                    'path' => route('artists.show', ['artist' => $artist->id, 'slug' => $artist->slug], false),
                ];
            })
            ->all());
    }

    /** @return list<array{type:string,id:string,name:string,detail:string,path:string}> */
    private function releases(): array
    {
        return array_values(Release::query()
            ->orderByRaw('LOWER(title)')
            ->orderBy('id')
            ->limit(self::PER_ENTITY_LIMIT)
            ->get()
            ->map(function (Release $release): array {
                $detail = array_values(array_filter([
                    $release->status ? ucfirst($release->status) : null,
                    $release->release_year ? (string) $release->release_year : null,
                    $release->country_code,
                ], static fn (?string $value): bool => $value !== null && $value !== ''));

                return [
                    'type' => 'Release',
                    'id' => $release->id,
                    'name' => $release->title,
                    'detail' => $detail === [] ? 'Release' : implode(' · ', $detail),
                    'path' => route('releases.show', ['release' => $release->id, 'slug' => $release->slug], false),
                ];
            })
            ->all());
    }

    /** @return list<array{type:string,id:string,name:string,detail:string,path:string}> */
    private function recordings(): array
    {
        return array_values(Recording::query()
            ->orderByRaw('LOWER(title)')
            ->orderBy('id')
            ->limit(self::PER_ENTITY_LIMIT)
            ->get()
            ->map(function (Recording $recording): array {
                $detail = array_filter([
                    'Recording',
                    $recording->disambiguation,
                ], static fn (?string $value): bool => $value !== null && $value !== '');

                return [
                    'type' => 'Recording',
                    'id' => $recording->id,
                    'name' => $recording->title,
                    'detail' => implode(' · ', $detail),
                    'path' => route('recordings.show', ['recording' => $recording->id, 'slug' => $recording->slug], false),
                ];
            })
            ->all());
    }
}
