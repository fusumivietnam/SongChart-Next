<?php

declare(strict_types=1);

use Illuminate\Contracts\Console\Kernel;
use Illuminate\Support\Facades\DB;

require __DIR__.'/../vendor/autoload.php';

$app = require __DIR__.'/../bootstrap/app.php';
$app->make(Kernel::class)->bootstrap();

/**
 * @param list<string> $columns
 * @param list<string> $orderBy
 * @return list<array<string,mixed>>
 */
function rows(string $table, array $columns, array $orderBy): array
{
    $query = DB::table($table)->select($columns);
    foreach ($orderBy as $column) {
        $query->orderBy($column);
    }

    return $query->get()->map(static function (object $row): array {
        return array_map(static function (mixed $value): mixed {
            if (is_string($value) && ($value !== '') && (($value[0] ?? '') === '{' || ($value[0] ?? '') === '[')) {
                $decoded = json_decode($value, true);
                if (json_last_error() === JSON_ERROR_NONE) {
                    return $decoded;
                }
            }
            return $value;
        }, (array) $row);
    })->values()->all();
}

$snapshot = [
    'schema_version' => 1,
    'migrations' => rows('migrations', ['migration', 'batch'], ['migration']),
    'artists' => rows('artists', ['id', 'name', 'slug', 'type', 'country_code', 'disambiguation'], ['id']),
    'external_identities' => rows('external_identities', ['artist_id', 'provider', 'entity_type', 'external_id', 'source_name', 'provenance'], ['artist_id', 'provider', 'entity_type', 'external_id']),
    'release_groups' => rows('release_groups', ['id', 'title', 'slug', 'primary_type', 'disambiguation'], ['id']),
    'releases' => rows('releases', ['id', 'release_group_id', 'title', 'slug', 'status', 'country_code', 'release_year', 'release_month', 'release_day', 'date_precision', 'barcode'], ['id']),
    'recordings' => rows('recordings', ['id', 'title', 'slug', 'length_ms', 'disambiguation'], ['id']),
    'works' => rows('works', ['id', 'title', 'slug', 'type', 'disambiguation'], ['id']),
    'music_external_identities' => rows('music_external_identities', ['canonical_type', 'canonical_id', 'provider', 'entity_type', 'external_id', 'source_name', 'provenance'], ['canonical_type', 'canonical_id', 'provider', 'entity_type', 'external_id']),
    'recording_isrcs' => rows('recording_isrcs', ['recording_id', 'isrc'], ['recording_id', 'isrc']),
    'release_media' => rows('release_media', ['id', 'release_id', 'position', 'format', 'title'], ['release_id', 'position', 'id']),
    'release_tracks' => rows('release_tracks', ['id', 'medium_id', 'recording_id', 'position', 'number', 'title', 'length_ms'], ['medium_id', 'position', 'id']),
    'entity_credits' => rows('entity_credits', ['subject_type', 'subject_id', 'artist_id', 'role', 'credited_as', 'join_phrase', 'position'], ['subject_type', 'subject_id', 'position']),
    'recording_work' => rows('recording_work', ['recording_id', 'work_id', 'relationship_type'], ['recording_id', 'work_id', 'relationship_type']),
    'destination_links' => rows('destination_links', ['subject_type', 'subject_id', 'provider', 'destination_type', 'external_url_hash', 'source_name', 'source_reference', 'provenance', 'verification_state', 'verified_at'], ['subject_type', 'subject_id', 'provider', 'destination_type', 'external_url_hash']),
];

$json = json_encode($snapshot, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
fwrite(STDOUT, $json."\n");
