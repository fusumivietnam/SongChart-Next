<?php

namespace App\Music\Releases;

use App\Models\Release;
use Illuminate\Support\Facades\DB;

final class ReleaseReadView
{
    /** @return array<string,mixed> */
    public function get(Release $release): array
    {
        $credits = DB::table('entity_credits')
            ->join('artists', 'artists.id', '=', 'entity_credits.artist_id')
            ->where('subject_type', 'release')
            ->where('subject_id', $release->id)
            ->orderBy('position')
            ->get(['artists.id as artist_id','artists.slug as artist_slug','artists.name','entity_credits.role','entity_credits.credited_as','entity_credits.join_phrase','entity_credits.position'])
            ->map(fn ($row) => (array) $row)
            ->all();

        $media = DB::table('release_media')
            ->where('release_id', $release->id)
            ->orderBy('position')
            ->get()
            ->map(function ($medium): array {
                $tracks = DB::table('release_tracks')
                    ->join('recordings', 'recordings.id', '=', 'release_tracks.recording_id')
                    ->where('medium_id', $medium->id)
                    ->orderBy('release_tracks.position')
                    ->get([
                        'release_tracks.position','release_tracks.number','release_tracks.title','release_tracks.length_ms',
                        'recordings.id as recording_id','recordings.slug as recording_slug','recordings.title as recording_title',
                    ])
                    ->map(fn ($row) => (array) $row)
                    ->all();
                return [
                    'position' => $medium->position,
                    'format' => $medium->format,
                    'title' => $medium->title,
                    'tracks' => $tracks,
                ];
            })->all();

        $group = $release->release_group_id === null ? null : DB::table('release_groups')->where('id', $release->release_group_id)->first();
        $provenance = DB::table('music_external_identities')
            ->where('canonical_type', 'release')
            ->where('canonical_id', $release->id)
            ->orderBy('id')
            ->get(['provider','entity_type','external_id','source_name'])
            ->map(fn ($row) => (array) $row)->all();

        return [
            'id' => $release->id,
            'slug' => $release->slug,
            'title' => $release->title,
            'status' => $release->status,
            'countryCode' => $release->country_code,
            'date' => $this->formatDate($release),
            'datePrecision' => $release->date_precision,
            'barcode' => $release->barcode,
            'releaseGroup' => $group === null ? null : ['id' => $group->id, 'title' => $group->title, 'type' => $group->primary_type],
            'credits' => $credits,
            'media' => $media,
            'provenance' => $provenance,
        ];
    }

    private function formatDate(Release $release): ?string
    {
        if ($release->release_year === null) {
            return null;
        }
        $date = sprintf('%04d', $release->release_year);
        if ($release->release_month !== null) {
            $date .= sprintf('-%02d', $release->release_month);
        }
        if ($release->release_day !== null) {
            $date .= sprintf('-%02d', $release->release_day);
        }
        return $date;
    }
}
