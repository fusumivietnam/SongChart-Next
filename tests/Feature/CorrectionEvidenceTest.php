<?php

namespace Tests\Feature;

use App\Models\Artist;
use App\Models\CorrectionSubmission;
use App\Music\Corrections\CorrectionEvidence;
use App\Music\Corrections\CorrectionSubjectType;
use App\Music\Corrections\SubmitCorrectionEvidence;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Str;
use InvalidArgumentException;
use Tests\TestCase;

final class CorrectionEvidenceTest extends TestCase
{
    use RefreshDatabase;

    public function test_valid_correction_is_persisted_as_pending_evidence_without_canonical_mutation(): void
    {
        $artist = Artist::query()->create([
            'name' => 'Signal Atlas',
            'slug' => 'signal-atlas',
            'type' => 'group',
        ]);

        $submission = (new SubmitCorrectionEvidence())->submit(new CorrectionEvidence(
            CorrectionSubjectType::Artist,
            $artist->id,
            'The artist country should be reviewed against the linked source.',
            'https://example.test/evidence/artist-country',
        ));

        $this->assertTrue(Str::isUlid($submission->id));
        $this->assertSame('pending', $submission->status);
        $this->assertSame(CorrectionSubjectType::Artist, $submission->subject_type);
        $this->assertSame($artist->id, $submission->subject_id);

        $this->assertDatabaseHas('correction_submissions', [
            'id' => $submission->id,
            'subject_type' => 'artist',
            'subject_id' => $artist->id,
            'status' => 'pending',
        ]);

        $this->assertSame(1, CorrectionSubmission::query()->count());
        $this->assertSame(1, Artist::query()->count());
        $this->assertSame('Signal Atlas', $artist->fresh()?->name);
        $this->assertNull($artist->fresh()?->country_code);
    }

    public function test_unknown_canonical_subject_is_rejected_before_persistence(): void
    {
        $this->expectException(InvalidArgumentException::class);
        $this->expectExceptionMessage('does not exist');

        try {
            (new SubmitCorrectionEvidence())->submit(new CorrectionEvidence(
                CorrectionSubjectType::Artist,
                (string) Str::ulid(),
                'This claim points to a canonical subject that is not present.',
            ));
        } finally {
            $this->assertSame(0, CorrectionSubmission::query()->count());
        }
    }

    public function test_invalid_subject_id_is_rejected(): void
    {
        $this->expectException(InvalidArgumentException::class);
        $this->expectExceptionMessage('valid SongChart ULID');

        new CorrectionEvidence(
            CorrectionSubjectType::Artist,
            'not-a-songchart-id',
            'A correction claim.',
        );
    }

    public function test_empty_or_oversized_claim_is_rejected(): void
    {
        foreach (['   ', str_repeat('x', 4001)] as $claim) {
            try {
                new CorrectionEvidence(
                    CorrectionSubjectType::Artist,
                    (string) Str::ulid(),
                    $claim,
                );

                $this->fail('Invalid correction claim was accepted.');
            } catch (InvalidArgumentException $exception) {
                $this->assertStringContainsString('between 1 and 4000 characters', $exception->getMessage());
            }
        }
    }

    public function test_unsafe_evidence_url_is_rejected(): void
    {
        $this->expectException(InvalidArgumentException::class);
        $this->expectExceptionMessage('http or https');

        new CorrectionEvidence(
            CorrectionSubjectType::Artist,
            (string) Str::ulid(),
            'A correction claim with unsupported evidence transport.',
            'ftp://example.test/evidence',
        );
    }
}
