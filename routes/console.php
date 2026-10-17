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
