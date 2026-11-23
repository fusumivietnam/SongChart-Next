<?php

namespace Tests\Unit;

use App\Music\Recordings\OfflineRecordingBatchEvaluator;
use App\Music\Recordings\OfflineRecordingProjector;
use InvalidArgumentException;
use PHPUnit\Framework\TestCase;

final class OfflineRecordingBatchEvaluatorTest extends TestCase
{
    /** @return array<string,mixed> */
    private function source(): array
    {
        return [
            'provider' => 'musicbrainz',
            'dataset' => 'json-dumps/recording',
            'snapshot_id' => '20261118-001001',
            'archive_sha256' => str_repeat('a', 64),
            'manifest_signing_fingerprint' => str_repeat('b', 40),
            'first_line' => 7,
            'observed_at' => '2026-11-24T00:00:00Z',
            'untrusted_extra_field' => 'never echoed',
        ];
    }

    private function evaluator(): OfflineRecordingBatchEvaluator
    {
        return new OfflineRecordingBatchEvaluator(new OfflineRecordingProjector());
    }

    private function fixture(string $name): string
    {
        return (string) file_get_contents(dirname(__DIR__).'/Fixtures/musicbrainz/offline-projection/'.$name.'.json');
    }

    public function test_bounded_aggregate_only_counts_synthetic_rows_and_provenance(): void
    {
        $rows = [
            $this->fixture('recording-performance-valid'),
            $this->fixture('recording-without-work'),
            $this->fixture('recording-attributed-performance'),
            $this->fixture('recording-invalid-credit'),
        ];
        $result = $this->evaluator()->evaluate($rows, $this->source());
        self::assertSame(4, $result['counts']['inspected']);
        self::assertSame(2, $result['counts']['candidates']);
        self::assertSame(1, $result['counts']['candidates_with_work']);
        self::assertSame(1, $result['counts']['recording_only_candidates']);
        self::assertSame(1, $result['counts']['candidates_with_isrc']);
        self::assertSame(2, $result['counts']['quarantined']);
        self::assertSame([
            'invalid_artist_credit' => 1,
            'unsupported_performance_attributes' => 1,
        ], $result['quarantine_reasons']);
        self::assertSame(7, $result['provenance']['first_line']);
        self::assertSame(10, $result['provenance']['last_line']);
        self::assertSame('operator_supplied_not_verified_by_evaluator', $result['provenance']['verification']);
        $json = json_encode($result, JSON_THROW_ON_ERROR);
        foreach (['Synthetic Starlight', 'Example Ensemble', 'excluded', 'never echoed', '11111111-1111'] as $secret) {
            self::assertStringNotContainsString($secret, $json);
        }
        self::assertSame($result, $this->evaluator()->evaluate($rows, $this->source()));
    }

    public function test_limit_stops_after_two_without_outputting_records(): void
    {
        $rows = [
            $this->fixture('recording-performance-valid'),
            $this->fixture('recording-without-work'),
            $this->fixture('recording-attributed-performance'),
        ];
        $result = $this->evaluator()->evaluate($rows, $this->source(), 2);
        self::assertSame(2, $result['counts']['inspected']);
        self::assertSame(2, $result['counts']['candidates']);
        self::assertSame(0, $result['counts']['quarantined']);
        self::assertSame(8, $result['provenance']['last_line']);
    }

    public function test_generator_does_not_read_beyond_limit_for_candidate_or_quarantine(): void
    {
        foreach (['recording-performance-valid', 'recording-attributed-performance'] as $fixtureName) {
            $yielded = 0;
            $fixture = $this->fixture($fixtureName);
            $rows = (function () use (&$yielded, $fixture): \Generator {
                for ($i = 0; $i < 3; $i++) {
                    $yielded++;
                    yield $fixture;
                }
            })();
            $result = $this->evaluator()->evaluate($rows, $this->source(), 2);
            self::assertSame(2, $yielded, "Source over-read for {$fixtureName}.");
            self::assertSame(2, $result['counts']['inspected']);
        }
    }

    public function test_empty_input_and_malformed_json_are_safe(): void
    {
        $empty = $this->evaluator()->evaluate([], $this->source());
        self::assertSame(0, $empty['counts']['inspected']);
        self::assertNull($empty['provenance']['last_line']);
        $bad = $this->evaluator()->evaluate(['{broken'], $this->source());
        self::assertSame(['invalid_json' => 1], $bad['quarantine_reasons']);
        self::assertSame(1, $bad['counts']['quarantined']);
    }

    public function test_invalid_limit_and_untrusted_source_are_rejected(): void
    {
        foreach ([0, 101] as $limit) {
            try {
                $this->evaluator()->evaluate([], $this->source(), $limit);
                self::fail('Accepted out-of-bounds limit.');
            } catch (InvalidArgumentException $exception) {
                self::assertStringContainsString('between 1 and 100', $exception->getMessage());
            }
        }
        $source = $this->source();
        $source['archive_sha256'] = 'not-a-checksum';
        $this->expectException(InvalidArgumentException::class);
        $this->evaluator()->evaluate([], $source);
    }
}
