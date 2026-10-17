<?php

namespace App\Music\Corrections;

use App\Models\CorrectionSubmission;
use Illuminate\Support\Carbon;

final class PruneExpiredCorrectionEvidence
{
    public const PENDING_RETENTION_DAYS = 180;

    public function prunePending(?Carbon $now = null): int
    {
        $cutoff = ($now ?? now())->copy()->subDays(self::PENDING_RETENTION_DAYS);

        return CorrectionSubmission::query()
            ->where('status', 'pending')
            ->where('created_at', '<=', $cutoff)
            ->delete();
    }
}
