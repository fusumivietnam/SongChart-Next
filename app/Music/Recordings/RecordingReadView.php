<?php

namespace App\Music\Recordings;

use App\Models\Recording;
use Illuminate\Support\Facades\DB;

final class RecordingReadView
{
    /** @return array<string,mixed> */
    public function get(Recording $recording): array
    {
        $isrcs = DB::table('recording_isrcs')->where('recording_id', $recording->id)->orderBy('isrc')->pluck('isrc')->all();
        $works = DB::table('recording_work')
            ->join('works', 'works.id', '=', 'recording_work.work_id')
            ->where('recording_id', $recording->id)
            ->orderBy('works.title')
            ->get(['works.id','works.title','works.type','recording_work.relationship_type'])
            ->map(fn ($row) => (array) $row)->all();
        $releases = DB::table('release_tracks')
            ->join('release_media', 'release_media.id', '=', 'release_tracks.medium_id')
            ->join('releases', 'releases.id', '=', 'release_media.release_id')
            ->where('release_tracks.recording_id', $recording->id)
            ->orderBy('releases.title')
            ->get(['releases.id','releases.slug','releases.title','release_tracks.number','release_tracks.title as track_title'])
            ->map(fn ($row) => (array) $row)->all();
        $provenance = DB::table('music_external_identities')
            ->where('canonical_type', 'recording')
            ->where('canonical_id', $recording->id)
            ->orderBy('id')
            ->get(['provider','entity_type','external_id','source_name'])
            ->map(fn ($row) => (array) $row)->all();

        return [
            'id' => $recording->id,
            'slug' => $recording->slug,
            'title' => $recording->title,
            'lengthMs' => $recording->length_ms,
            'disambiguation' => $recording->disambiguation,
            'isrcs' => $isrcs,
            'works' => $works,
            'releases' => $releases,
            'provenance' => $provenance,
        ];
    }
}
