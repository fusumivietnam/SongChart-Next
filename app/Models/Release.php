<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Concerns\HasUlids;
use Illuminate\Database\Eloquent\Model;

#[Fillable(['release_group_id','title','slug','status','country_code','release_year','release_month','release_day','date_precision','barcode'])]
class Release extends Model
{
    use HasUlids;
    public $incrementing = false;
    protected $keyType = 'string';
}
