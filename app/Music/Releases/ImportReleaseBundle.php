<?php

namespace App\Music\Releases;

use App\Models\ExternalIdentity;
use App\Models\Recording;
use App\Models\Release;
use App\Models\ReleaseGroup;
use App\Models\Work;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use RuntimeException;

final class ImportReleaseBundle
{
    public function handle(ReleaseBundleClaim $claim): Release
    {
        return DB::transaction(function () use ($claim): Release {
            $group = $this->resolveEntity('release_group', $claim->releaseGroup, ReleaseGroup::class, [
                'title' => $claim->releaseGroup['title'],
                'slug' => Str::slug((string) $claim->releaseGroup['title']),
                'primary_type' => $claim->releaseGroup['primary_type'],
                'disambiguation' => $claim->releaseGroup['disambiguation'],
            ]);

            $release = $this->resolveEntity('release', $claim->release, Release::class, [
                'release_group_id' => $group->getKey(),
                'title' => $claim->release['title'],
                'slug' => Str::slug((string) $claim->release['title']),
                'status' => $claim->release['status'],
                'country_code' => $claim->release['country_code'],
                'release_year' => $claim->release['release_year'],
                'release_month' => $claim->release['release_month'],
                'release_day' => $claim->release['release_day'],
                'date_precision' => $claim->release['date_precision'],
                'barcode' => $claim->release['barcode'],
            ]);

            $this->replaceCredits('release', (string) $release->getKey(), $claim->credits);

            DB::table('release_media')->where('release_id', $release->getKey())->delete();
            foreach ($claim->media as $mediumData) {
                $mediumId = (string) Str::ulid();
                DB::table('release_media')->insert([
                    'id' => $mediumId,
                    'release_id' => $release->getKey(),
                    'position' => $mediumData['position'],
                    'format' => $mediumData['format'],
                    'title' => $mediumData['title'],
                    'created_at' => now(),
                    'updated_at' => now(),
                ]);

                foreach ($mediumData['tracks'] as $track) {
                    $recordingData = $track['recording'];
                    $recording = $this->resolveEntity('recording', $recordingData, Recording::class, [
                        'title' => $recordingData['title'],
                        'slug' => Str::slug((string) $recordingData['title']),
                        'length_ms' => $recordingData['length_ms'],
                        'disambiguation' => $recordingData['disambiguation'],
                    ]);

                    $this->replaceCredits('recording', (string) $recording->getKey(), $recordingData['credits']);

                    foreach ($recordingData['isrcs'] as $isrc) {
                        DB::table('recording_isrcs')->updateOrInsert(
                            ['isrc' => $isrc],
                            ['recording_id' => $recording->getKey(), 'updated_at' => now(), 'created_at' => now()],
                        );
                    }

                    if ($recordingData['work'] !== null) {
                        $workData = $recordingData['work'];
                        $work = $this->resolveEntity('work', $workData, Work::class, [
                            'title' => $workData['title'],
                            'slug' => Str::slug((string) $workData['title']),
                            'type' => $workData['type'],
                            'disambiguation' => $workData['disambiguation'],
                        ]);
                        DB::table('recording_work')->updateOrInsert([
                            'recording_id' => $recording->getKey(),
                            'work_id' => $work->getKey(),
                            'relationship_type' => 'performance',
                        ], ['updated_at' => now(), 'created_at' => now()]);
                    }

                    DB::table('release_tracks')->insert([
                        'id' => (string) Str::ulid(),
                        'medium_id' => $mediumId,
                        'recording_id' => $recording->getKey(),
                        'position' => $track['position'],
                        'number' => $track['number'],
                        'title' => $track['title'],
                        'length_ms' => $track['length_ms'],
                        'created_at' => now(),
                        'updated_at' => now(),
                    ]);
                }
            }

            return $release->fresh() ?? $release;
        });
    }

    /** @param list<array{artist_external_id:string,credited_as:string,join_phrase:string,role:string,position:int}> $credits */
    private function replaceCredits(string $subjectType, string $subjectId, array $credits): void
    {
        DB::table('entity_credits')->where('subject_type', $subjectType)->where('subject_id', $subjectId)->delete();

        foreach ($credits as $credit) {
            $artistIdentity = ExternalIdentity::query()
                ->where('provider', 'musicbrainz')
                ->where('entity_type', 'artist')
                ->where('external_id', $credit['artist_external_id'])
                ->first();
            if ($artistIdentity === null) {
                throw new RuntimeException(ucfirst($subjectType).' credit references an Artist that has not been admitted yet.');
            }
            DB::table('entity_credits')->insert([
                'subject_type' => $subjectType,
                'subject_id' => $subjectId,
                'artist_id' => $artistIdentity->artist_id,
                'role' => $credit['role'],
                'credited_as' => $credit['credited_as'],
                'join_phrase' => $credit['join_phrase'],
                'position' => $credit['position'],
                'created_at' => now(),
                'updated_at' => now(),
            ]);
        }
    }

    /**
     * @template TModel of Model
     * @param array<string,mixed> $source
     * @param class-string<TModel> $modelClass
     * @param array<string,mixed> $attributes
     * @return TModel
     */
    private function resolveEntity(string $canonicalType, array $source, string $modelClass, array $attributes): Model
    {
        $externalId = (string) $source['external_id'];
        $identity = DB::table('music_external_identities')
            ->where('provider', 'musicbrainz')
            ->where('entity_type', $canonicalType)
            ->where('external_id', $externalId)
            ->first();

        if ($identity !== null) {
            $model = $modelClass::query()->findOrFail($identity->canonical_id);
            $model->fill($attributes)->save();
            return $model;
        }

        $model = new $modelClass();
        $model->fill($attributes)->save();
        DB::table('music_external_identities')->insert([
            'canonical_type' => $canonicalType,
            'canonical_id' => $model->getKey(),
            'provider' => 'musicbrainz',
            'entity_type' => $canonicalType,
            'external_id' => $externalId,
            'source_name' => (string) $source['title'],
            'provenance' => json_encode(['source' => 'deterministic-fixture', 'slice' => 'VS-02'], JSON_THROW_ON_ERROR),
            'created_at' => now(),
            'updated_at' => now(),
        ]);
        return $model;
    }
}