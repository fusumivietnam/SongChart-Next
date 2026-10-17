<?php

namespace Tests\Feature;

use App\Models\Artist;
use App\Models\CorrectionSubmission;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Schema;
use Inertia\Testing\AssertableInertia as Assert;
use Tests\TestCase;

final class PublicCorrectionIntakeTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->withoutVite();
    }

    public function test_public_form_exposes_anonymous_review_only_contract(): void
    {
        $this->get('/corrections')
            ->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->component('site/document')
                ->where('document.title', 'Corrections')
                ->where('document.action', null)
                ->where('correctionIntake.enabled', true)
                ->where('correctionIntake.status', null)
                ->where('correctionIntake.limits.claimCharacters', 4000)
                ->where('correctionIntake.limits.requestBytes', 8192));
    }

    public function test_valid_submission_creates_pending_evidence_without_canonical_mutation(): void
    {
        Http::fake();
        $artist = $this->artist();

        $response = $this->withServerVariables(['REMOTE_ADDR' => '198.51.100.10'])
            ->post('/corrections', [
                'subject_type' => 'artist',
                'subject_id' => $artist->id,
                'claim' => 'The artist country should be reviewed against this public source.',
                'evidence_url' => 'https://example.test/source',
            ]);

        $response
            ->assertRedirect(route('corrections'))
            ->assertSessionHas('correctionStatus', 'accepted');

        $this->assertDatabaseHas('correction_submissions', [
            'subject_type' => 'artist',
            'subject_id' => $artist->id,
            'status' => 'pending',
        ]);
        $this->assertSame(1, CorrectionSubmission::query()->count());
        $this->assertSame('Signal Atlas', $artist->fresh()?->name);
        $this->assertNull($artist->fresh()?->country_code);
        Http::assertNothingSent();
    }

    public function test_identical_submission_within_24_hours_is_suppressed(): void
    {
        $artist = $this->artist();
        $payload = [
            'subject_type' => 'artist',
            'subject_id' => $artist->id,
            'claim' => 'The same proposed correction.',
            'evidence_url' => 'https://example.test/same-source',
        ];

        $this->withServerVariables(['REMOTE_ADDR' => '198.51.100.11'])->post('/corrections', $payload)->assertRedirect();
        $this->withServerVariables(['REMOTE_ADDR' => '198.51.100.11'])->post('/corrections', $payload)->assertRedirect();

        $this->assertSame(1, CorrectionSubmission::query()->count());
    }

    public function test_oversized_request_fails_closed_without_persistence(): void
    {
        $artist = $this->artist();

        $this->withServerVariables([
            'REMOTE_ADDR' => '198.51.100.12',
            'CONTENT_LENGTH' => '9000',
        ])->post('/corrections', [
            'subject_type' => 'artist',
            'subject_id' => $artist->id,
            'claim' => 'Oversized request.',
        ])
            ->assertStatus(422)
            ->assertInertia(fn (Assert $page) => $page
                ->component('site/document')
                ->where('correctionIntake.status', 'validation'));

        $this->assertSame(0, CorrectionSubmission::query()->count());
    }

    public function test_anonymous_rate_limit_returns_deterministic_429(): void
    {
        $artist = $this->artist();
        $server = ['REMOTE_ADDR' => '198.51.100.13'];

        for ($attempt = 1; $attempt <= 5; $attempt++) {
            $this->withServerVariables($server)->post('/corrections', [
                'subject_type' => 'artist',
                'subject_id' => $artist->id,
                'claim' => 'Rate-limit evidence '.$attempt,
            ])->assertRedirect();
        }

        $this->withServerVariables($server)->post('/corrections', [
            'subject_type' => 'artist',
            'subject_id' => $artist->id,
            'claim' => 'Rate-limit evidence blocked',
        ])
            ->assertStatus(429)
            ->assertHeader('Retry-After')
            ->assertInertia(fn (Assert $page) => $page
                ->component('site/document')
                ->where('correctionIntake.status', 'throttled'));
    }

    public function test_storage_failure_returns_generic_unavailable_state(): void
    {
        $artist = $this->artist();
        Schema::drop('correction_submissions');

        $this->withServerVariables(['REMOTE_ADDR' => '198.51.100.14'])->post('/corrections', [
            'subject_type' => 'artist',
            'subject_id' => $artist->id,
            'claim' => 'This request should fail closed.',
        ])
            ->assertStatus(503)
            ->assertInertia(fn (Assert $page) => $page
                ->component('site/document')
                ->where('correctionIntake.status', 'unavailable'));

        $this->assertSame('Signal Atlas', $artist->fresh()?->name);
    }

    private function artist(): Artist
    {
        return Artist::query()->create([
            'name' => 'Signal Atlas',
            'slug' => 'signal-atlas',
            'type' => 'group',
        ]);
    }
}
