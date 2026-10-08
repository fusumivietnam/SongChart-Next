<?php

namespace App\Music\Releases;

final readonly class ReleaseBundleClaim
{
    /**
     * @param array{external_id:string,title:string,primary_type:?string,disambiguation:?string} $releaseGroup
     * @param array{external_id:string,title:string,status:?string,country_code:?string,release_year:?int,release_month:?int,release_day:?int,date_precision:?string,barcode:?string} $release
     * @param list<array{artist_external_id:string, credited_as:string, join_phrase:string, role:string, position:int}> $credits
     * @param list<array{position:int, format:?string, title:?string, tracks:list<array{position:int, number:string, title:string, length_ms:?int, recording:array{external_id:string,title:string,length_ms:?int,disambiguation:?string,credits:list<array{artist_external_id:string,credited_as:string,join_phrase:string,role:string,position:int}>,isrcs:list<string>,work:?array{external_id:string,title:string,type:?string,disambiguation:?string}}}>}> $media
     */
    public function __construct(
        public array $releaseGroup,
        public array $release,
        public array $credits,
        public array $media,
    ) {}
}
