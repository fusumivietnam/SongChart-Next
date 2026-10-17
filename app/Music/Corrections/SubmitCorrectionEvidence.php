<?php

namespace App\Music\Corrections;

use App\Models\CorrectionSubmission;
use Illuminate\Support\Facades\DB;
use InvalidArgumentException;

final class SubmitCorrectionEvidence
{
    public function submit(CorrectionEvidence $evidence): CorrectionSubmission
    {
        $subjectClass = $evidence->subjectType->modelClass();

        if (! $subjectClass::query()->whereKey($evidence->subjectId)->exists()) {
            throw new InvalidArgumentException('Correction subject does not exist in the SongChart canonical database.');
        }

        return DB::transaction(static function () use ($evidence): CorrectionSubmission {
            $submission = CorrectionSubmission::query()->create([
                'subject_type' => $evidence->subjectType,
                'subject_id' => $evidence->subjectId,
                'claim' => $evidence->claim,
                'evidence_url' => $evidence->evidenceUrl,
            ]);

            return $submission->refresh();
        });
    }

    public function submitDeduplicated(CorrectionEvidence $evidence, int $withinHours = 24): CorrectionSubmission
    {
        if ($withinHours < 1) {
            throw new InvalidArgumentException('Correction duplicate window must be at least one hour.');
        }

        $subjectClass = $evidence->subjectType->modelClass();

        return DB::transaction(static function () use ($evidence, $withinHours, $subjectClass): CorrectionSubmission {
            $subject = $subjectClass::query()
                ->whereKey($evidence->subjectId)
                ->lockForUpdate()
                ->first();

            if ($subject === null) {
                throw new InvalidArgumentException('Correction subject does not exist in the SongChart canonical database.');
            }

            $query = CorrectionSubmission::query()
                ->where('subject_type', $evidence->subjectType->value)
                ->where('subject_id', $evidence->subjectId)
                ->where('claim', $evidence->claim)
                ->where('created_at', '>=', now()->subHours($withinHours));

            if ($evidence->evidenceUrl === null) {
                $query->whereNull('evidence_url');
            } else {
                $query->where('evidence_url', $evidence->evidenceUrl);
            }

            $existing = $query->latest('created_at')->first();

            if ($existing !== null) {
                return $existing;
            }

            $submission = CorrectionSubmission::query()->create([
                'subject_type' => $evidence->subjectType,
                'subject_id' => $evidence->subjectId,
                'claim' => $evidence->claim,
                'evidence_url' => $evidence->evidenceUrl,
            ]);

            return $submission->refresh();
        });
    }
}
