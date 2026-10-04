<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Carbon;

/**
 * @property int $id
 * @property string $artist_id
 * @property string $provider
 * @property string $entity_type
 * @property string $external_id
 * @property string $source_name
 * @property array<string, mixed>|null $provenance
 * @property Carbon|null $created_at
 * @property Carbon|null $updated_at
 * @property-read Artist $artist
 */
#[Fillable(['artist_id', 'provider', 'entity_type', 'external_id', 'source_name', 'provenance'])]
class ExternalIdentity extends Model
{
    /** @return BelongsTo<Artist, $this> */
    public function artist(): BelongsTo
    {
        return $this->belongsTo(Artist::class);
    }

    /** @return array<string, string> */
    protected function casts(): array
    {
        return [
            'provenance' => 'array',
        ];
    }
}
