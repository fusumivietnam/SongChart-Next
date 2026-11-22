<?php
/**
 * Read-only MusicBrainz Recording JSONL shape probe for #174.
 *
 * Reads up to 100 records from STDIN. Emits aggregate counts only.
 * No framework bootstrap, network, disk writes or canonical admission.
 */
declare(strict_types=1);

const PERFORMANCE_TYPE_ID = 'a3005666-a872-32c3-ad06-98af558e99b0';
const MAX_RECORDS = 100;

function uuid(mixed $value): bool
{
    return is_string($value)
        && preg_match('/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/iD', $value) === 1;
}

$counts = [
    'records_inspected' => 0,
    'shape_valid' => 0,
    'quarantine' => 0,
    'recordings_with_supported_work' => 0,
    'supported_work_relations' => 0,
    'unsupported_work_relations' => 0,
    'supplementary_fields_present' => 0,
    'records_with_isrc' => 0,
    'shape_valid_with_supported_work' => 0,
    'shape_valid_without_supported_work' => 0,
];
$reasons = [];

while ($counts['records_inspected'] < MAX_RECORDS && ($line = fgets(STDIN)) !== false) {
    $counts['records_inspected']++;
    $why = [];
    try {
        $row = json_decode($line, true, 512, JSON_THROW_ON_ERROR);
    } catch (JsonException) {
        $row = null;
        $why[] = 'invalid_json';
    }

    if (!is_array($row) || array_is_list($row)) {
        $why[] = 'not_an_object';
    } else {
        if (!uuid($row['id'] ?? null) || !is_string($row['title'] ?? null)
            || trim($row['title']) === '') {
            $why[] = 'invalid_recording_identity_or_title';
        }
        if (isset($row['length']) && (!is_int($row['length']) || $row['length'] < 0)) {
            $why[] = 'invalid_length';
        }
        if (isset($row['disambiguation']) && !is_string($row['disambiguation'])) {
            $why[] = 'invalid_disambiguation';
        }
        $credits = $row['artist-credit'] ?? null;
        if (!is_array($credits) || $credits === []) {
            $why[] = 'missing_artist_credit';
        } else {
            foreach ($credits as $credit) {
                if (!is_array($credit) || !uuid($credit['artist']['id'] ?? null)
                    || !is_string($credit['name'] ?? null)
                    || trim($credit['name']) === ''
                    || !is_string($credit['joinphrase'] ?? null)) {
                    $why[] = 'invalid_artist_credit';
                    break;
                }
            }
        }

        $isrcs = $row['isrcs'] ?? null;
        if (!is_array($isrcs)) {
            $why[] = 'invalid_isrc_list';
        } elseif ($isrcs !== []) {
            $counts['records_with_isrc']++;
            foreach ($isrcs as $isrc) {
                if (!is_string($isrc) || preg_match('/^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$/iD', $isrc) !== 1) {
                    $why[] = 'invalid_isrc';
                    break;
                }
            }
        }

        foreach (['genres', 'tags', 'rating', 'annotation'] as $excluded) {
            if (array_key_exists($excluded, $row)) {
                $counts['supplementary_fields_present']++;
            }
        }

        $relations = $row['relations'] ?? null;
        $hasSupportedWork = false;
        if (!is_array($relations)) {
            $why[] = 'invalid_relations_list';
        } else {
            foreach ($relations as $relation) {
                if (!is_array($relation)) {
                    $why[] = 'invalid_relation_object';
                    continue;
                }
                if (($relation['target-type'] ?? null) !== 'work') {
                    continue;
                }
                if (($relation['type-id'] ?? null) !== PERFORMANCE_TYPE_ID) {
                    $counts['unsupported_work_relations']++;
                    continue;
                }
                $work = $relation['work'] ?? null;
                if (($relation['type'] ?? null) !== 'performance'
                    || ($relation['direction'] ?? null) !== 'forward') {
                    $why[] = 'unexpected_performance_type_or_direction';
                    continue;
                }
                if (!is_array($relation['attributes'] ?? null)
                    || !is_array($relation['attribute-ids'] ?? null)
                    || !is_array($relation['attribute-values'] ?? null)) {
                    $why[] = 'invalid_performance_attribute_shape';
                    continue;
                }
                if ($relation['attributes'] !== []
                    || $relation['attribute-ids'] !== []
                    || $relation['attribute-values'] !== []) {
                    $why[] = 'unsupported_performance_attributes';
                    continue;
                }
                if (!is_array($work) || !uuid($work['id'] ?? null)
                    || !is_string($work['title'] ?? null)
                    || trim($work['title']) === '') {
                    $why[] = 'invalid_performance_work_identity';
                    continue;
                }
                $counts['supported_work_relations']++;
                $hasSupportedWork = true;
            }
        }
        if ($hasSupportedWork) {
            $counts['recordings_with_supported_work']++;
        }
    }

    if ($why === []) {
        $counts['shape_valid']++;
        $counts[$hasSupportedWork ? 'shape_valid_with_supported_work' : 'shape_valid_without_supported_work']++;
    } else {
        $counts['quarantine']++;
        foreach (array_unique($why) as $reason) {
            $reasons[$reason] = ($reasons[$reason] ?? 0) + 1;
        }
    }
}
ksort($reasons);
echo json_encode([
    'scope' => 'read_only_shape_probe_not_rights_clearance_or_admission',
    'note' => 'supplementary_fields_present counts field occurrences, not violating records; supported work counts may overlap quarantined rows',
    'sample_limit' => MAX_RECORDS,
    'counts' => $counts,
    'quarantine_reasons' => $reasons,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR), PHP_EOL;
