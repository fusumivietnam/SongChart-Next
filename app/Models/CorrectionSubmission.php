<?php

namespace App\Models;

use App\Music\Corrections\CorrectionSubjectType;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Concerns\HasUlids;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Carbon;

/**
 * @property string $id
 * @property CorrectionSubjectType $subject_type
 * @property string $subject_id
 * @property string $claim
 * @property string|null $evidence_url
 * @property string $status
 * @property Carbon|null $created_at
 * @property Carbon|null $updated_at
 */
#[Fillable(['subject_type', 'subject_id', 'claim', 'evidence_url', 'status'])]
final class CorrectionSubmission extends Model
{
    use HasUlids;

    public $incrementing = false;

    protected $keyType = 'string';

    /** @return array<string, string> */
    protected function casts(): array
    {
        return [
            'subject_type' => CorrectionSubjectType::class,
        ];
    }
}
