<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Concerns\HasUlids;
use Illuminate\Database\Eloquent\Model;

#[Fillable(['title', 'slug', 'primary_type', 'disambiguation'])]
class ReleaseGroup extends Model
{
    use HasUlids;

    public $incrementing = false;

    protected $keyType = 'string';
}
