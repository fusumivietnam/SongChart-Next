<?php

namespace App\Music\Corrections;

use App\Models\CorrectionSubmission;
use InvalidArgumentException;
use Illuminate\Support\Facades\DB;

final class SubmitCorrectionEvidence
{
    public function submit(CorrectionEvidence $evidence): CorrectionSubmission
    {
        $subjectClass = $evidence->subjectType->modelClass();

        if (! $subjectClass::query()->whereKey($evidence->subjectId)->exists()) {
            throw new InvalidArgumentException('Correction subject does not exist in the SongChart canonical database.');
        }

        return DB::transaction(static fn (): CorrectionSubmission => CorrectionSubmission::query()->create([
            'subject_type' => $evidence->subjectType,
            'subject_id' => $evidence->subjectId,
            'claim' => $evidence->claim,
            'evidence_url' => $evidence->evidenceUrl,
        ]));
    }
}
