<?php

namespace Tests\Feature;

use App\Models\CorrectionSubmission;
use App\Music\Corrections\PruneExpiredCorrectionEvidence;
use Illuminate\Console\Scheduling\Schedule;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\Artisan;
use Tests\TestCase;

final class CorrectionRetentionTest extends TestCase
{
    use RefreshDatabase;

    protected function tearDown(): void
    {
        Carbon::setTestNow();

        parent::tearDown();
    }

    public function test_prune_command_deletes_only_pending_evidence_at_or_beyond_the_180_day_cutoff(): void
    {
        Carbon::setTestNow(Carbon::parse('2026-10-17 12:00:00'));

        $expired = $this->submission('pending', now()->subDays(181));
        $boundary = $this->submission('pending', now()->subDays(PruneExpiredCorrectionEvidence::PENDING_RETENTION_DAYS));
        $fresh = $this->submission('pending', now()->subDays(179));
        $nonPending = $this->submission('resolved', now()->subDays(400));

        $exitCode = Artisan::call('songchart:corrections:prune');

        $this->assertSame(0, $exitCode);
        $this->assertStringContainsString('Pruned 2 expired pending correction submission(s).', Artisan::output());
        $this->assertDatabaseMissing('correction_submissions', ['id' => $expired->id]);
        $this->assertDatabaseMissing('correction_submissions', ['id' => $boundary->id]);
        $this->assertDatabaseHas('correction_submissions', ['id' => $fresh->id, 'status' => 'pending']);
        $this->assertDatabaseHas('correction_submissions', ['id' => $nonPending->id, 'status' => 'resolved']);
    }

    public function test_retention_command_is_scheduled_hourly_without_overlap(): void
    {
        $events = collect(app(Schedule::class)->events());
        $event = $events->first(fn ($candidate) => str_contains($candidate->command ?? '', 'songchart:corrections:prune'));

        $this->assertNotNull($event);
        $this->assertSame('0 * * * *', $event->expression);
        $this->assertTrue($event->withoutOverlapping);
    }

    private function submission(string $status, Carbon $createdAt): CorrectionSubmission
    {
        return CorrectionSubmission::query()->forceCreate([
            'subject_type' => 'artist',
            'subject_id' => (string) \Illuminate\Support\Str::ulid(),
            'claim' => 'Retention fixture claim.',
            'evidence_url' => null,
            'status' => $status,
            'created_at' => $createdAt,
            'updated_at' => $createdAt,
        ]);
    }
}
