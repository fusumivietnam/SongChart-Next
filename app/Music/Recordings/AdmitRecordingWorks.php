<?php

namespace App\Music\Recordings;

use App\Models\Recording;
use App\Models\Work;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use RuntimeException;

final class AdmitRecordingWorks
{
    public function handle(RecordingWorkClaim $claim): Recording
    {
        return DB::transaction(function () use ($claim): Recording {
            $recordingIdentity = DB::table('music_external_identities')
                ->where('provider', 'musicbrainz')
                ->where('entity_type', 'recording')
                ->where('external_id', $claim->recordingExternalId)
                ->first();

            if ($recordingIdentity === null) {
                throw new RuntimeException('Recording must be admitted before Recording-to-Work relationships.');
            }

            $recording = Recording::query()->findOrFail($recordingIdentity->canonical_id);

            foreach ($claim->works as $workData) {
                $workIdentity = DB::table('music_external_identities')
                    ->where('provider', 'musicbrainz')
                    ->where('entity_type', 'work')
                    ->where('external_id', $workData['external_id'])
                    ->first();

                if ($workIdentity === null) {
                    $work = new Work();
                    $work->fill([
                        'title' => $workData['title'],
                        'slug' => Str::slug($workData['title']),
                        'type' => $workData['type'],
                        'disambiguation' => $workData['disambiguation'],
                    ])->save();

                    DB::table('music_external_identities')->insert([
                        'canonical_type' => 'work',
                        'canonical_id' => $work->getKey(),
                        'provider' => 'musicbrainz',
                        'entity_type' => 'work',
                        'external_id' => $workData['external_id'],
                        'source_name' => $workData['title'],
                        'provenance' => json_encode(['source' => 'deterministic-fixture', 'slice' => 'VS-06'], JSON_THROW_ON_ERROR),
                        'created_at' => now(),
                        'updated_at' => now(),
                    ]);
                } else {
                    $work = Work::query()->findOrFail($workIdentity->canonical_id);
                    $work->fill([
                        'title' => $workData['title'],
                        'slug' => Str::slug($workData['title']),
                        'type' => $workData['type'],
                        'disambiguation' => $workData['disambiguation'],
                    ])->save();
                }

                DB::table('recording_work')->updateOrInsert([
                    'recording_id' => $recording->getKey(),
                    'work_id' => $work->getKey(),
                    'relationship_type' => $workData['relationship_type'],
                ], [
                    'updated_at' => now(),
                    'created_at' => now(),
                ]);
            }

            return $recording->fresh() ?? $recording;
        });
    }
}
