<?php

use App\Music\Corrections\PruneExpiredCorrectionEvidence;
use Illuminate\Foundation\Inspiring;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\Schedule;

Artisan::command('inspire', function () {
    $this->comment(Inspiring::quote());
})->purpose('Display an inspiring quote');

Artisan::command('songchart:corrections:prune', function (PruneExpiredCorrectionEvidence $pruner) {
    $deleted = $pruner->prunePending();

    $this->info("Pruned {$deleted} expired pending correction submission(s).");
})->purpose('Delete pending correction evidence that reached the approved retention cutoff');

Schedule::command('songchart:corrections:prune')
    ->hourly()
    ->withoutOverlapping();

Artisan::command('songchart:corrections:moderation-demand', function () {
    // Aggregate-only, operator-invoked evidence for issue #173. No claim content,
    // supporting URLs, subject identities or reviewer/customer data in output.
    $pending = \\App\\Models\\CorrectionSubmission::query()
        ->where('status', 'pending')
        ->count();
    $expired = \\App\\Models\\CorrectionSubmission::query()
        ->where('status', 'pending')
        ->where('created_at', '<=', now()->subDays(180))
        ->count();

    $this->line("Pending correction evidence: {$pending}");
    $this->line("Pending beyond 180-day retention: {$expired}");
    $this->line('Aggregate counts alone do not establish real unresolved moderation need or authorize admin-review.');
})->purpose('Read-only aggregate correction intake demand; does not activate reviewer access');
