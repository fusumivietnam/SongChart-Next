<?php

namespace Tests\Unit;

use App\Music\Recordings\OfflineRecordingProjector;
use PHPUnit\Framework\TestCase;

final class OfflineRecordingProjectorTest extends TestCase
{
    /** @return array<string,mixed> */
    private function fixture(string $name): array
    {
        $path = dirname(__DIR__).'/Fixtures/musicbrainz/offline-projection/'.$name.'.json';
        $data = json_decode((string) file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
        self::assertIsArray($data);

        return $data;
    }

    public function test_supported_work_projection_recursively_drops_supplementary_fields(): void
    {
        $projector = new OfflineRecordingProjector();
        $source = $this->fixture('recording-performance-valid');
        $copy = $source;
        $result = $projector->project($source);
        self::assertSame('candidate', $result['status']);
        self::assertSame(['recording', 'credits', 'isrcs', 'works'], array_keys($result['candidate']));
        self::assertSame(['external_id', 'title', 'length_ms', 'disambiguation'], array_keys($result['candidate']['recording']));
        self::assertSame(['artist_external_id', 'credited_as', 'join_phrase', 'position'], array_keys($result['candidate']['credits'][0]));
        self::assertSame(['external_id', 'title', 'type', 'disambiguation', 'relationship_type'], array_keys($result['candidate']['works'][0]));
        self::assertSame('33333333-3333-4333-8333-333333333333', $result['candidate']['works'][0]['external_id']);
        self::assertSame([], $result['candidate']['isrcs']);
        self::assertSame($copy, $source);
        self::assertSame($result, $projector->project($source));
        $json = json_encode($result, JSON_THROW_ON_ERROR);
        foreach (['excluded', 'tags', 'genres', 'rating', 'annotation', 'aliases', 'video', 'iswcs', 'languages'] as $forbidden) {
            self::assertStringNotContainsString($forbidden, $json);
        }
    }

    public function test_recording_without_work_has_no_invented_work_or_canonical_id(): void
    {
        $result = (new OfflineRecordingProjector())->project($this->fixture('recording-without-work'));
        self::assertSame('candidate', $result['status']);
        self::assertSame([], $result['candidate']['works']);
        self::assertSame(['USAAA2600001'], $result['candidate']['isrcs']);
        self::assertArrayNotHasKey('canonical_id', $result['candidate']['recording']);
    }

    public function test_attributed_performance_quarantines_entire_candidate(): void
    {
        self::assertSame(
            ['status' => 'quarantine', 'reason' => 'unsupported_performance_attributes'],
            (new OfflineRecordingProjector())->project($this->fixture('recording-attributed-performance'))
        );
    }

    public function test_invalid_artist_mbid_never_fuzzy_matches_name(): void
    {
        self::assertSame(
            ['status' => 'quarantine', 'reason' => 'invalid_artist_credit'],
            (new OfflineRecordingProjector())->project($this->fixture('recording-invalid-credit'))
        );
    }

    public function test_invalid_json_length_and_duplicate_isrc_quarantine(): void
    {
        $projector = new OfflineRecordingProjector();
        self::assertSame('invalid_json', $projector->projectJson('{bad')['reason']);
        self::assertSame('invalid_recording_shape', $projector->project([])['reason']);
        $row = $this->fixture('recording-performance-valid');
        $row['length'] = -1;
        self::assertSame('invalid_length', $projector->project($row)['reason']);
        $row = $this->fixture('recording-performance-valid');
        $row['isrcs'] = ['USAAA2600001', 'usaaa2600001'];
        self::assertSame('duplicate_isrc', $projector->project($row)['reason']);
    }

    public function test_invalid_work_attributes_and_direction_fail_closed(): void
    {
        $p = new OfflineRecordingProjector();
        $row = $this->fixture('recording-performance-valid');
        $row['relations'][0]['work']['id'] = 'invalid';
        self::assertSame('invalid_work_identity', $p->project($row)['reason']);
        $row = $this->fixture('recording-performance-valid');
        $row['relations'][0]['direction'] = 'backward';
        self::assertSame('unexpected_performance_relation', $p->project($row)['reason']);
        $row = $this->fixture('recording-performance-valid');
        $row['relations'][0]['attribute-values'] = ['cover' => 'yes'];
        self::assertSame('unsupported_performance_attributes', $p->project($row)['reason']);
    }

    public function test_multiple_work_relations_deduplicate_or_quarantine_conflicts(): void
    {
        $p = new OfflineRecordingProjector();
        $row = $this->fixture('recording-performance-valid');
        $row['relations'][] = $row['relations'][0];
        self::assertCount(1, $p->project($row)['candidate']['works']);
        $row['relations'][1]['work']['title'] = 'Conflicting title';
        self::assertSame('conflicting_work_identity', $p->project($row)['reason']);
        $row = $this->fixture('recording-performance-valid');
        $row['relations'][] = $this->fixture('recording-attributed-performance')['relations'][0];
        self::assertSame('unsupported_performance_attributes', $p->project($row)['reason']);
    }
}
