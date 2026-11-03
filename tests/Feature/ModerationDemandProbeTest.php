<?php

namespace Tests\Feature;

use App\Models\CorrectionSubmission;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

final class ModerationDemandProbeTest extends TestCase
{
    use RefreshDatabase;

    public function test_operator_probe_is_read_only_and_reports_only_aggregate_counts(): void
    {
        $this->artisan('songchart:corrections:moderation-demand')
            ->expectsOutput('Pending correction evidence: 0')
            ->expectsOutput('Pending beyond 180-day retention: 0')
            ->assertExitCode(0);

        $this->assertSame(0, CorrectionSubmission::query()->count());
    }
}
