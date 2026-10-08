<?php

namespace App\Music\Discovery;

use App\Models\Artist;
use App\Models\Recording;
use App\Models\Release;
use Illuminate\Database\Eloquent\Model;

final class DiscoverySearch
{
    public const MAX_QUERY_LENGTH = 80;
    public const MAX_RESULTS = 20;
    private const CANDIDATES_PER_ENTITY = 20;

    public function search(?string $rawQuery): DiscoverySearchResult
    {
        $query = $this->normalizeQuery($rawQuery ?? '');

        if ($query === '') {
            return new DiscoverySearchResult('', []);
        }

        $pattern = '%'.$this->escapeLike($query).'%';
        $items = [];

        foreach (Artist::query()
            ->whereRaw("LOWER(name) LIKE ? ESCAPE '\\'", [$pattern])
            ->limit(self::CANDIDATES_PER_ENTITY)
            ->get() as $artist) {
            $items[] = $this->artistItem($artist, $query);
        }

        foreach (Release::query()
            ->whereRaw("LOWER(title) LIKE ? ESCAPE '\\'", [$pattern])
            ->limit(self::CANDIDATES_PER_ENTITY)
            ->get() as $release) {
            $items[] = $this->releaseItem($release, $query);
        }

        foreach (Recording::query()
            ->whereRaw("LOWER(title) LIKE ? ESCAPE '\\'", [$pattern])
            ->limit(self::CANDIDATES_PER_ENTITY)
            ->get() as $recording) {
            $items[] = $this->recordingItem($recording, $query);
        }

        usort($items, function (DiscoverySearchItem $left, DiscoverySearchItem $right): int {
            return [$left->score, $this->typeOrder($left->type), $this->normalize($left->name), $left->id]
                <=> [$right->score, $this->typeOrder($right->type), $this->normalize($right->name), $right->id];
        });

        return new DiscoverySearchResult(
            $query,
            array_slice($items, 0, self::MAX_RESULTS),
        );
    }

    private function artistItem(Artist $artist, string $query): DiscoverySearchItem
    {
        $detail = array_values(array_filter([
            $artist->type,
            $artist->country_code,
            $artist->disambiguation,
        ], static fn (?string $value): bool => $value !== null && $value !== ''));

        return new DiscoverySearchItem(
            type: 'Artist',
            id: $artist->id,
            slug: $artist->slug,
            name: $artist->name,
            detail: $detail === [] ? 'Artist' : implode(' · ', $detail),
            path: route('artists.show', ['artist' => $artist->id, 'slug' => $artist->slug], false),
            score: $this->score($artist->name, $query),
        );
    }

    private function releaseItem(Release $release, string $query): DiscoverySearchItem
    {
        $detail = array_values(array_filter([
            $release->status ? ucfirst($release->status) : null,
            $release->release_year ? (string) $release->release_year : null,
            $release->country_code,
        ], static fn (?string $value): bool => $value !== null && $value !== ''));

        return new DiscoverySearchItem(
            type: 'Release',
            id: $release->id,
            slug: $release->slug,
            name: $release->title,
            detail: $detail === [] ? 'Release' : implode(' · ', $detail),
            path: route('releases.show', ['release' => $release->id, 'slug' => $release->slug], false),
            score: $this->score($release->title, $query),
        );
    }

    private function recordingItem(Recording $recording, string $query): DiscoverySearchItem
    {
        $detail = array_values(array_filter([
            'Recording',
            $recording->disambiguation,
            $recording->length_ms ? $this->duration((int) $recording->length_ms) : null,
        ], static fn (?string $value): bool => $value !== null && $value !== ''));

        return new DiscoverySearchItem(
            type: 'Recording',
            id: $recording->id,
            slug: $recording->slug,
            name: $recording->title,
            detail: implode(' · ', $detail),
            path: route('recordings.show', ['recording' => $recording->id, 'slug' => $recording->slug], false),
            score: $this->score($recording->title, $query),
        );
    }

    private function normalizeQuery(string $query): string
    {
        $normalized = preg_replace('/\s+/u', ' ', trim($query)) ?? trim($query);

        return mb_substr($this->normalize($normalized), 0, self::MAX_QUERY_LENGTH);
    }

    private function normalize(string $value): string
    {
        return mb_strtolower($value);
    }

    private function escapeLike(string $value): string
    {
        return str_replace(['\\', '%', '_'], ['\\\\', '\\%', '\\_'], $value);
    }

    private function score(string $candidate, string $query): int
    {
        $normalized = $this->normalize($candidate);

        if ($normalized === $query) {
            return 0;
        }

        if (str_starts_with($normalized, $query)) {
            return 1;
        }

        return 2;
    }

    private function typeOrder(string $type): int
    {
        return match ($type) {
            'Artist' => 0,
            'Release' => 1,
            'Recording' => 2,
            default => 9,
        };
    }

    private function duration(int $milliseconds): string
    {
        $seconds = (int) round($milliseconds / 1000);

        return sprintf('%d:%02d', intdiv($seconds, 60), $seconds % 60);
    }
}
