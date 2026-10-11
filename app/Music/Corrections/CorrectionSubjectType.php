<?php

namespace App\Music\Corrections;

use App\Models\Artist;
use App\Models\Recording;
use App\Models\Release;
use Illuminate\Database\Eloquent\Model;

enum CorrectionSubjectType: string
{
    case Artist = 'artist';
    case Release = 'release';
    case Recording = 'recording';

    /** @return class-string<Model> */
    public function modelClass(): string
    {
        return match ($this) {
            self::Artist => Artist::class,
            self::Release => Release::class,
            self::Recording => Recording::class,
        };
    }
}
