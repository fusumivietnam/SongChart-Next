<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Concerns\HasUlids;
use Illuminate\Database\Eloquent\Model;

#[Fillable(['title','slug','type','disambiguation'])]
class Work extends Model
{
    use HasUlids;
    public $incrementing = false;
    protected $keyType = 'string';
}
