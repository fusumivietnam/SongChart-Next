<?php

namespace App\Music\Recordings;

final readonly class RecordingWorkClaim
{
    /**
     * @param list<array{external_id:string,title:string,type:?string,disambiguation:?string,relationship_type:string}> $works
     */
    public function __construct(
        public string $recordingExternalId,
        public array $works,
    ) {}
}
