<?php

namespace App\Music\Recordings;

use App\Models\Recording;
use Illuminate\Support\Facades\DB;

final class RecordingReadView
{
    /** @return array<string,mixed> */
    public function get(Recording $recording): array
    {
        $credits = DB::table('entity_credits')
            ->join('artists', 'artists.id', '=', 'entity_credits.artist_id')
            ->where('subject_type', 'recording')
            ->where('subject_id', $recording->id)
            ->orderBy('position')
            ->get(['artists.id as artist_id','artists.slug as artist_slug','artists.name','entity_credits.role','entity_credits.credited_as','entity_credits.join_phrase','entity_credits.position'])
            ->map(fn ($row) => (array) $row)->all();
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
        $destinations = DB::table('destination_links')
            ->where('subject_type', 'recording')
            ->where('subject_id', $recording->id)
            ->where('verification_state', 'verified')
            ->orderBy('provider')
            ->orderBy('destination_type')
            ->get(['provider','destination_type','external_url','source_name','verified_at'])
            ->map(fn ($row) => (array) $row)->all();

        return [
            'id' => $recording->id,
            'slug' => $recording->slug,
            'title' => $recording->title,
            'lengthMs' => $recording->length_ms,
            'disambiguation' => $recording->disambiguation,
            'credits' => $credits,
            'isrcs' => $isrcs,
            'works' => $works,
            'releases' => $releases,
            'provenance' => $provenance,
            'destinations' => $destinations,
        ];
    }
}
