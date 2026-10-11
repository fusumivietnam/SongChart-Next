<?php

namespace App\Music\Corrections;

use InvalidArgumentException;
use Illuminate\Support\Str;

final readonly class CorrectionEvidence
{
    public string $subjectId;

    public string $claim;

    public ?string $evidenceUrl;

    public function __construct(
        public CorrectionSubjectType $subjectType,
        string $subjectId,
        string $claim,
        ?string $evidenceUrl = null,
    ) {
        $subjectId = trim($subjectId);
        $claim = trim($claim);
        $evidenceUrl = $evidenceUrl === null ? null : trim($evidenceUrl);

        if (! Str::isUlid($subjectId)) {
            throw new InvalidArgumentException('Correction subject ID must be a valid SongChart ULID.');
        }

        if ($claim === '' || mb_strlen($claim) > 4000) {
            throw new InvalidArgumentException('Correction claim must contain between 1 and 4000 characters.');
        }

        if ($evidenceUrl === '') {
            $evidenceUrl = null;
        }

        if ($evidenceUrl !== null) {
            if (mb_strlen($evidenceUrl) > 2048 || filter_var($evidenceUrl, FILTER_VALIDATE_URL) === false) {
                throw new InvalidArgumentException('Correction evidence URL must be a valid URL no longer than 2048 characters.');
            }

            $scheme = strtolower((string) parse_url($evidenceUrl, PHP_URL_SCHEME));
            if (! in_array($scheme, ['http', 'https'], true)) {
                throw new InvalidArgumentException('Correction evidence URL must use http or https.');
            }
        }

        $this->subjectId = $subjectId;
        $this->claim = $claim;
        $this->evidenceUrl = $evidenceUrl;
    }
}
